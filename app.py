from pathlib import Path
import tempfile
from typing import Any

import pandas as pd
import streamlit as st

from config.language import LANGUAGE_OPTIONS
from config.language import translate
from config.theme import apply_application_theme
from services.audit_service import run_customer_audit


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ESAA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """
    Initialize application values that must remain available
    across Streamlit reruns.
    """

    default_values = {
        "language": "en",
        "language_display": "English",
        "audit_result": None,
        "report_bytes": None,
        "report_filename": None,
        "uploaded_filename": None,
        "customer_name": "",
        "last_error": None,
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_assessment() -> None:
    """
    Remove the current assessment while preserving the
    selected interface language.
    """

    st.session_state.audit_result = None
    st.session_state.report_bytes = None
    st.session_state.report_filename = None
    st.session_state.uploaded_filename = None
    st.session_state.customer_name = ""
    st.session_state.last_error = None


def t(key: str, **values: Any) -> str:
    """
    Translate a user-interface key using the language stored
    in Streamlit Session State.
    """

    return translate(
        key,
        st.session_state.get("language", "en"),
        **values,
    )


# ============================================================
# GENERIC HELPERS
# ============================================================

def get_value(
    source: Any,
    field_name: str,
    default_value: Any = None,
) -> Any:
    """
    Read a value from either a dictionary or an object.
    """

    if isinstance(source, dict):
        return source.get(field_name, default_value)

    return getattr(source, field_name, default_value)


def get_first_available_value(
    source: Any,
    possible_field_names: list[str],
    default_value: Any = "",
) -> Any:
    """
    Return the first available non-empty value from a list of
    possible dictionary keys or object attributes.
    """

    for field_name in possible_field_names:
        value = get_value(source, field_name, None)

        if value is not None and value != "":
            return value

    return default_value


def convert_value_for_display(value: Any) -> str:
    """
    Convert Python values into readable table text.
    """

    if value is None:
        return ""

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, (list, tuple, set)):
        return ", ".join(
            convert_value_for_display(item)
            for item in value
        )

    if isinstance(value, dict):
        return "; ".join(
            (
                f"{key}: "
                f"{convert_value_for_display(item_value)}"
            )
            for key, item_value in value.items()
        )

    return str(value)


def normalize_status(status: Any) -> str:
    """
    Normalize status values returned by different audit
    engines into a common internal status.
    """

    if status is None:
        return "UNKNOWN"

    status_text = str(status).strip()

    if "." in status_text:
        status_text = status_text.split(".")[-1]

    status_text = status_text.upper()

    aliases = {
        "PASSED": "PASS",
        "SUCCESS": "PASS",
        "SUCCESSFUL": "PASS",
        "COMPLIANT": "PASS",
        "OK": "PASS",

        "FAILED": "FAIL",
        "FAILURE": "FAIL",
        "NON-COMPLIANT": "FAIL",
        "NON_COMPLIANT": "FAIL",
        "NOT COMPLIANT": "FAIL",
        "NOT_COMPLIANT": "FAIL",

        "REVIEW": "MANUAL",
        "MANUAL REVIEW": "MANUAL",
        "MANUAL_REVIEW": "MANUAL",
        "NOT CHECKED": "MANUAL",
        "NOT_CHECKED": "MANUAL",
        "REQUIRES REVIEW": "MANUAL",
        "REQUIRES_REVIEW": "MANUAL",

        "NOT APPLICABLE": "N/A",
        "NOT_APPLICABLE": "N/A",
        "NA": "N/A",
    }

    return aliases.get(status_text, status_text)


def translated_status(status: str) -> str:
    """
    Return a translated display name for an internal status.
    """

    status_map = {
        "PASS": t("pass"),
        "FAIL": t("fail"),
        "MANUAL": t("manual"),
        "N/A": t("not_applicable"),
        "UNKNOWN": t("unknown"),
    }

    return status_map.get(status, status)


def determine_operating_system(server_result: Any) -> str:
    """
    Determine the operating system from a server result.
    """

    operating_system = get_first_available_value(
        server_result,
        [
            "operating_system",
            "os",
            "os_name",
            "platform",
            "distribution",
        ],
        "",
    )

    operating_system_text = convert_value_for_display(
        operating_system
    ).strip()

    if operating_system_text:
        return operating_system_text

    if not isinstance(server_result, dict):
        return "Windows"

    return t("unknown_value")


def determine_os_family(operating_system: str) -> str:
    """
    Convert a detailed operating-system value into a general
    Windows, Linux or Unknown family.
    """

    os_text = operating_system.lower()

    linux_names = [
        "linux",
        "ubuntu",
        "debian",
        "centos",
        "red hat",
        "rhel",
        "rocky",
        "alma",
        "suse",
        "oracle linux",
        "amazon linux",
    ]

    if "windows" in os_text:
        return "Windows"

    if any(name in os_text for name in linux_names):
        return "Linux"

    return "Unknown"


def translated_os_family(os_family: str) -> str:
    """
    Translate the general operating-system family.
    """

    if os_family == "Windows":
        return "Windows"

    if os_family == "Linux":
        return "Linux"

    return t("unknown_value")


# ============================================================
# DATA TRANSFORMATION
# ============================================================

def build_server_inventory_rows(
    server_results: list[Any],
) -> list[dict[str, Any]]:
    """
    Convert all server results into a standard inventory
    structure.
    """

    rows: list[dict[str, Any]] = []

    for index, server_result in enumerate(
        server_results,
        start=1,
    ):
        hostname = get_first_available_value(
            server_result,
            [
                "hostname",
                "computer_name",
                "server_name",
                "name",
            ],
            t("unknown_value"),
        )

        operating_system = determine_operating_system(
            server_result
        )

        os_family = determine_os_family(
            operating_system
        )

        ip_addresses = get_first_available_value(
            server_result,
            [
                "ip_addresses",
                "ip_address",
                "ipv4_addresses",
                "ipv4_address",
                "ips",
            ],
            [],
        )

        rows.append(
            {
                "number": index,
                "hostname": convert_value_for_display(
                    hostname
                ),
                "os_family": os_family,
                "operating_system": operating_system,
                "ip_address": convert_value_for_display(
                    ip_addresses
                ),
            }
        )

    return rows


def get_requirement_collection(
    server_result: Any,
) -> Any:
    """
    Locate the requirement result collection within a server
    assessment object.
    """

    return get_first_available_value(
        server_result,
        [
            "requirements",
            "requirement_results",
            "results",
            "checks",
            "controls",
        ],
        {},
    )


def build_requirement_rows(
    server_results: list[Any],
) -> list[dict[str, Any]]:
    """
    Convert Windows and Linux assessment results into one
    standard requirement table structure.
    """

    rows: list[dict[str, Any]] = []

    for server_result in server_results:
        hostname = get_first_available_value(
            server_result,
            [
                "hostname",
                "computer_name",
                "server_name",
                "name",
            ],
            t("unknown_value"),
        )

        operating_system = determine_operating_system(
            server_result
        )

        os_family = determine_os_family(
            operating_system
        )

        requirements = get_requirement_collection(
            server_result
        )

        if isinstance(requirements, dict):
            requirement_items = requirements.items()
        elif isinstance(requirements, list):
            requirement_items = enumerate(
                requirements,
                start=1,
            )
        else:
            continue

        for requirement_key, result in requirement_items:
            requirement_id = get_first_available_value(
                result,
                [
                    "requirement_id",
                    "id",
                    "control_id",
                    "check_id",
                    "rule_id",
                ],
                str(requirement_key),
            )

            requirement_name = get_first_available_value(
                result,
                [
                    "requirement_name",
                    "name",
                    "title",
                    "control_name",
                    "check_name",
                    "description",
                ],
                str(requirement_key),
            )

            category = get_first_available_value(
                result,
                [
                    "category",
                    "section",
                    "group",
                    "control_family",
                ],
                "",
            )

            status = normalize_status(
                get_first_available_value(
                    result,
                    [
                        "status",
                        "result",
                        "compliance_status",
                        "assessment_status",
                    ],
                    "UNKNOWN",
                )
            )

            expected_value = get_first_available_value(
                result,
                [
                    "expected_value",
                    "expected",
                    "required_value",
                    "requirement",
                    "target_value",
                ],
                "",
            )

            actual_value = get_first_available_value(
                result,
                [
                    "actual_value",
                    "actual",
                    "detected_value",
                    "current_value",
                    "value",
                    "observed_value",
                ],
                "",
            )

            evidence = get_first_available_value(
                result,
                [
                    "evidence",
                    "details",
                    "message",
                    "reason",
                    "observation",
                    "raw_value",
                ],
                "",
            )

            recommendation = get_first_available_value(
                result,
                [
                    "recommendation",
                    "remediation",
                    "solution",
                    "action",
                    "recommended_action",
                ],
                "",
            )

            rows.append(
                {
                    "server": convert_value_for_display(
                        hostname
                    ),
                    "os_family": os_family,
                    "operating_system": operating_system,
                    "requirement_id":
                        convert_value_for_display(
                            requirement_id
                        ),
                    "category":
                        convert_value_for_display(category),
                    "requirement":
                        convert_value_for_display(
                            requirement_name
                        ),
                    "status": status,
                    "expected_value":
                        convert_value_for_display(
                            expected_value
                        ),
                    "actual_value":
                        convert_value_for_display(
                            actual_value
                        ),
                    "evidence":
                        convert_value_for_display(evidence),
                    "recommendation":
                        convert_value_for_display(
                            recommendation
                        ),
                }
            )

    return rows


def count_requirement_statuses(
    requirement_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """
    Count requirement results by normalized status.
    """

    counts = {
        "PASS": 0,
        "FAIL": 0,
        "MANUAL": 0,
        "N/A": 0,
        "UNKNOWN": 0,
        "OTHER": 0,
    }

    for row in requirement_rows:
        status = normalize_status(
            row.get("status", "UNKNOWN")
        )

        if status in counts:
            counts[status] += 1
        else:
            counts["OTHER"] += 1

    return counts


def calculate_compliance_score(
    status_counts: dict[str, int],
) -> float:
    """
    Calculate compliance using automatic PASS and FAIL
    results only.
    """

    automatic_checks = (
        status_counts["PASS"]
        + status_counts["FAIL"]
    )

    if automatic_checks == 0:
        return 0.0

    return round(
        status_counts["PASS"]
        / automatic_checks
        * 100,
        1,
    )


# ============================================================
# LOCALIZED TABLES
# ============================================================

def localize_server_rows(
    server_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert internal server inventory rows into translated
    table columns.
    """

    localized_rows = []

    for row in server_rows:
        localized_rows.append(
            {
                t("number"): row["number"],
                t("hostname"): row["hostname"],
                t("os_family"): translated_os_family(
                    row["os_family"]
                ),
                t("operating_system"):
                    row["operating_system"],
                t("ip_address"): row["ip_address"],
            }
        )

    return localized_rows


def localize_requirement_rows(
    requirement_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert internal requirement rows into translated table
    columns and status names.
    """

    localized_rows = []

    for row in requirement_rows:
        localized_rows.append(
            {
                t("server"): row["server"],
                t("os_family"): translated_os_family(
                    row["os_family"]
                ),
                t("operating_system"):
                    row["operating_system"],
                t("requirement_id"):
                    row["requirement_id"],
                t("category"): row["category"],
                t("requirement"): row["requirement"],
                t("status"): translated_status(
                    row["status"]
                ),
                t("expected_value"):
                    row["expected_value"],
                t("actual_value"):
                    row["actual_value"],
                t("evidence"): row["evidence"],
                t("recommendation"):
                    row["recommendation"],
            }
        )

    return localized_rows


# ============================================================
# INTERFACE COMPONENTS
# ============================================================

def display_sidebar() -> None:
    """
    Display branding, language selection and application
    information in the sidebar.
    """

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-title">
                    🛡️ ESAA
                </div>
                <div class="sidebar-brand-subtitle">
                    Enterprise Security Audit Aggregator
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        selected_display_language = st.selectbox(
            f"🌐 {t('language')}",
            options=list(LANGUAGE_OPTIONS.keys()),
            index=list(LANGUAGE_OPTIONS.keys()).index(
                st.session_state.language_display
            ),
            key="language_selector",
        )

        selected_language = LANGUAGE_OPTIONS[
            selected_display_language
        ]

        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.session_state.language_display = (
                selected_display_language
            )
            st.rerun()

        st.markdown("---")

        st.markdown(
            (
                f'<div class="sidebar-section-title">'
                f'⚙️ {t("application")}'
                f"</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                f'<div class="sidebar-item">'
                f'{t("version")}: <strong>2.0.0</strong>'
                f"</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                f'<div class="sidebar-item">'
                f'Status: <strong>{t("development")}</strong>'
                f"</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown("---")

        st.markdown(
            (
                f'<div class="sidebar-section-title">'
                f'🖥️ {t("supported_platforms")}'
                f"</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                f'<div class="sidebar-item">'
                f'🪟 {t("windows_server")}'
                f"</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                f'<div class="sidebar-item">'
                f'🐧 {t("linux_server")}'
                f"</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown("---")

        st.markdown(
            (
                f'<div class="sidebar-section-title">'
                f'🔄 {t("workflow")}'
                f"</div>"
            ),
            unsafe_allow_html=True,
        )

        workflow_items = [
            t("step_upload"),
            t("step_discover"),
            t("step_detect"),
            t("step_evaluate"),
            t("step_review"),
            t("step_download"),
        ]

        for number, item in enumerate(
            workflow_items,
            start=1,
        ):
            st.markdown(
                (
                    f'<div class="sidebar-item">'
                    f"{number}. {item}"
                    f"</div>"
                ),
                unsafe_allow_html=True,
            )

        if st.session_state.audit_result is not None:
            st.markdown("---")

            if st.button(
                f"🗑️ {t('clear_assessment')}",
                width="stretch",
            ):
                reset_assessment()
                st.rerun()


def display_header() -> None:
    """
    Display the ESAA application header.
    """

    st.markdown(
        f"""
        <div class="esaa-header">
            <div class="esaa-brand-row">
                <div class="esaa-logo">🛡️</div>
                <div>
                    <h1>{t("app_title")}</h1>
                    <p>{t("app_subtitle")}</p>
                </div>
            </div>
            <div class="esaa-badge">
                ESAA · Security Compliance Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_upload_section() -> None:
    """
    Display the customer information, ZIP upload and
    assessment execution controls.
    """

    st.markdown(
        f"""
        <div class="esaa-section">
            <div class="esaa-section-title">
                📁 {t("upload_title")}
            </div>
            <div class="esaa-section-description">
                {t("upload_description")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    customer_name = st.text_input(
        t("customer_name"),
        value=st.session_state.customer_name,
        placeholder=t("customer_placeholder"),
        help=t("customer_help"),
    )

    uploaded_file = st.file_uploader(
        t("select_zip"),
        type=["zip"],
        help=t("upload_help"),
    )

    if uploaded_file is None:
        st.info(t("upload_information"))
        return

    file_size_mb = uploaded_file.size / 1024 / 1024

    information_col1, information_col2 = st.columns(2)

    information_col1.metric(
        t("selected_file"),
        uploaded_file.name,
    )

    information_col2.metric(
        t("file_size"),
        f"{file_size_mb:.2f} MB",
    )

    run_button = st.button(
        f"🚀 {t('run_assessment')}",
        type="primary",
        width="stretch",
    )

    if not run_button:
        return

    temporary_zip_path: Path | None = None

    try:
        reset_assessment()

        st.session_state.customer_name = (
            customer_name.strip()
        )

        with st.spinner(t("processing")):
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".zip",
            ) as temporary_file:
                temporary_file.write(
                    uploaded_file.getbuffer()
                )

                temporary_zip_path = Path(
                    temporary_file.name
                )

            result = run_customer_audit(
                zip_path=temporary_zip_path,
                output_directory="output",
            )

            report_path = Path(result["report_path"])

            if not report_path.exists():
                raise FileNotFoundError(
                    t("report_not_found")
                )

            with report_path.open("rb") as report_file:
                report_bytes = report_file.read()

            st.session_state.audit_result = result
            st.session_state.report_bytes = report_bytes
            st.session_state.report_filename = (
                report_path.name
            )
            st.session_state.uploaded_filename = (
                uploaded_file.name
            )
            st.session_state.last_error = None

        st.success(t("completed_successfully"))

    except FileNotFoundError as error:
        st.session_state.last_error = str(error)
        st.error(f"{t('file_error')}: {error}")

    except ValueError as error:
        st.session_state.last_error = str(error)
        st.error(f"{t('invalid_input')}: {error}")

    except RuntimeError as error:
        st.session_state.last_error = str(error)
        st.error(f"{t('assessment_error')}: {error}")

    except PermissionError as error:
        st.session_state.last_error = str(error)
        st.error(t("permission_error"))
        st.caption(
            f"{t('technical_details')}: {error}"
        )

    except Exception as error:
        st.session_state.last_error = str(error)
        st.error(t("unexpected_error"))
        st.exception(error)

    finally:
        if (
            temporary_zip_path is not None
            and temporary_zip_path.exists()
        ):
            temporary_zip_path.unlink(
                missing_ok=True
            )


def display_overview(
    server_rows: list[dict[str, Any]],
    requirement_rows: list[dict[str, Any]],
) -> None:
    """
    Display the main compliance overview.
    """

    status_counts = count_requirement_statuses(
        requirement_rows
    )

    compliance_score = calculate_compliance_score(
        status_counts
    )

    windows_count = sum(
        row["os_family"] == "Windows"
        for row in server_rows
    )

    linux_count = sum(
        row["os_family"] == "Linux"
        for row in server_rows
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    metric_col1.metric(
        t("compliance_score"),
        f"{compliance_score}%",
    )

    metric_col2.metric(
        t("servers_evaluated"),
        len(server_rows),
    )

    metric_col3.metric(
        t("requirements_evaluated"),
        len(requirement_rows),
    )

    st.progress(
        min(
            max(compliance_score / 100, 0.0),
            1.0,
        )
    )

    st.markdown(f"#### {t('platform_summary')}")

    platform_col1, platform_col2, platform_col3 = (
        st.columns(3)
    )

    platform_col1.metric(
        t("windows_servers"),
        windows_count,
    )

    platform_col2.metric(
        t("linux_servers"),
        linux_count,
    )

    platform_col3.metric(
        t("unknown_platforms"),
        (
            len(server_rows)
            - windows_count
            - linux_count
        ),
    )

    st.markdown(f"#### {t('compliance_status')}")

    status_col1, status_col2, status_col3, status_col4 = (
        st.columns(4)
    )

    status_col1.metric(
        t("pass"),
        status_counts["PASS"],
    )

    status_col2.metric(
        t("fail"),
        status_counts["FAIL"],
    )

    status_col3.metric(
        t("manual"),
        status_counts["MANUAL"],
    )

    status_col4.metric(
        t("na_unknown"),
        (
            status_counts["N/A"]
            + status_counts["UNKNOWN"]
            + status_counts["OTHER"]
        ),
    )

    st.markdown(f"#### {t('status_distribution')}")

    chart_data = pd.DataFrame(
        {
            t("status"): [
                t("pass"),
                t("fail"),
                t("manual"),
                t("not_applicable"),
                t("unknown"),
            ],
            "Count": [
                status_counts["PASS"],
                status_counts["FAIL"],
                status_counts["MANUAL"],
                status_counts["N/A"],
                (
                    status_counts["UNKNOWN"]
                    + status_counts["OTHER"]
                ),
            ],
        }
    )

    st.bar_chart(
        chart_data,
        x=t("status"),
        y="Count",
        width="stretch",
    )


def display_server_inventory(
    server_rows: list[dict[str, Any]],
) -> None:
    """
    Display the localized server inventory.
    """

    st.subheader(f"🖥️ {t('server_inventory')}")

    if not server_rows:
        st.warning(t("no_server_information"))
        return

    st.dataframe(
        localize_server_rows(server_rows),
        width="stretch",
        hide_index=True,
    )


def display_requirement_details(
    requirement_rows: list[dict[str, Any]],
) -> None:
    """
    Display requirement details with interactive filters.
    """

    st.subheader(f"📋 {t('requirement_details')}")

    if not requirement_rows:
        st.warning(t("no_requirement_details"))
        return

    server_names = sorted(
        {row["server"] for row in requirement_rows}
    )

    os_families = sorted(
        {row["os_family"] for row in requirement_rows}
    )

    status_values = sorted(
        {row["status"] for row in requirement_rows}
    )

    categories = sorted(
        {
            row["category"]
            for row in requirement_rows
            if row["category"]
        }
    )

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        selected_servers = st.multiselect(
            t("filter_server"),
            options=server_names,
            placeholder=t("all_servers"),
        )

    with filter_col2:
        selected_statuses = st.multiselect(
            t("filter_status"),
            options=status_values,
            format_func=translated_status,
            placeholder=t("all_statuses"),
        )

    filter_col3, filter_col4 = st.columns(2)

    with filter_col3:
        selected_os_families = st.multiselect(
            t("filter_os"),
            options=os_families,
            format_func=translated_os_family,
            placeholder=t("all_platforms"),
        )

    with filter_col4:
        selected_categories = st.multiselect(
            t("filter_category"),
            options=categories,
            placeholder=t("all_categories"),
            disabled=not categories,
        )

    search_text = st.text_input(
        t("search_requirements"),
        placeholder=t("search_placeholder"),
    )

    filtered_rows = []

    for row in requirement_rows:
        matches_server = (
            not selected_servers
            or row["server"] in selected_servers
        )

        matches_status = (
            not selected_statuses
            or row["status"] in selected_statuses
        )

        matches_os = (
            not selected_os_families
            or row["os_family"]
            in selected_os_families
        )

        matches_category = (
            not selected_categories
            or row["category"]
            in selected_categories
        )

        searchable_text = " ".join(
            str(value)
            for value in row.values()
        ).lower()

        matches_search = (
            not search_text
            or search_text.lower()
            in searchable_text
        )

        if (
            matches_server
            and matches_status
            and matches_os
            and matches_category
            and matches_search
        ):
            filtered_rows.append(row)

    result_col1, result_col2 = st.columns(2)

    result_col1.metric(
        t("displayed_requirements"),
        len(filtered_rows),
    )

    result_col2.metric(
        t("total_requirements"),
        len(requirement_rows),
    )

    if not filtered_rows:
        st.warning(t("no_filter_results"))
        return

    st.dataframe(
        localize_requirement_rows(filtered_rows),
        width="stretch",
        hide_index=True,
    )


def display_failed_requirements(
    requirement_rows: list[dict[str, Any]],
) -> None:
    """
    Display requirements whose normalized status is FAIL.
    """

    st.subheader(f"⚠️ {t('failed_requirements')}")

    failed_rows = [
        row
        for row in requirement_rows
        if row["status"] == "FAIL"
    ]

    if not failed_rows:
        st.success(t("no_failed_requirements"))
        return

    st.warning(
        t(
            "failures_require_attention",
            count=len(failed_rows),
        )
    )

    st.dataframe(
        localize_requirement_rows(failed_rows),
        width="stretch",
        hide_index=True,
    )


def display_report_download() -> None:
    """
    Display assessment metadata and the Excel download button.
    """

    st.subheader(f"📄 {t('assessment_report')}")

    if (
        st.session_state.report_bytes is None
        or st.session_state.report_filename is None
    ):
        st.warning(t("no_report"))
        return

    report_col1, report_col2 = st.columns([2, 1])

    with report_col1:
        st.markdown(
            f"**{t('customer_project')}:** "
            f"{st.session_state.customer_name or t('not_provided')}"
        )

        st.markdown(
            f"**{t('report_file')}:** "
            f"{st.session_state.report_filename}"
        )

        if st.session_state.uploaded_filename:
            st.markdown(
                f"**{t('source_package')}:** "
                f"{st.session_state.uploaded_filename}"
            )

        report_size_mb = (
            len(st.session_state.report_bytes)
            / 1024
            / 1024
        )

        st.markdown(
            f"**{t('report_size')}:** "
            f"{report_size_mb:.2f} MB"
        )

    with report_col2:
        st.download_button(
            label=f"⬇️ {t('download_report')}",
            data=st.session_state.report_bytes,
            file_name=st.session_state.report_filename,
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
            type="primary",
            width="stretch",
        )


def display_assessment_dashboard() -> None:
    """
    Display all dashboard tabs after a successful audit.
    """

    audit_result = st.session_state.audit_result

    server_results = audit_result.get(
        "server_results",
        [],
    )

    server_rows = build_server_inventory_rows(
        server_results
    )

    requirement_rows = build_requirement_rows(
        server_results
    )

    server_count = audit_result.get(
        "server_count",
        len(server_rows),
    )

    st.success(
        t(
            "servers_successfully_evaluated",
            count=server_count,
        )
    )

    (
        overview_tab,
        servers_tab,
        requirements_tab,
        failures_tab,
        report_tab,
    ) = st.tabs(
        [
            f"📊 {t('tab_overview')}",
            f"🖥️ {t('tab_servers')}",
            f"📋 {t('tab_requirements')}",
            f"⚠️ {t('tab_failures')}",
            f"📄 {t('tab_report')}",
        ]
    )

    with overview_tab:
        display_overview(
            server_rows,
            requirement_rows,
        )

    with servers_tab:
        display_server_inventory(server_rows)

    with requirements_tab:
        display_requirement_details(
            requirement_rows
        )

    with failures_tab:
        display_failed_requirements(
            requirement_rows
        )

    with report_tab:
        display_report_download()


# ============================================================
# MAIN APPLICATION
# ============================================================

def main() -> None:
    """
    Start the ESAA Streamlit application.
    """

    initialize_session_state()
    apply_application_theme()
    display_sidebar()
    display_header()
    display_upload_section()

    if st.session_state.audit_result is not None:
        st.markdown("---")
        display_assessment_dashboard()


if __name__ == "__main__":
    main()