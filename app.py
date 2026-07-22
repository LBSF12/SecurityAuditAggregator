from pathlib import Path
import tempfile
from typing import Any

import pandas as pd
import streamlit as st

from services.audit_service import run_customer_audit


# ============================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Enterprise Security Audit Aggregator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM APPLICATION STYLE
# ============================================================

st.markdown(
    """
    <style>
        .main-header {
            padding: 1.4rem 1.6rem;
            border-radius: 14px;
            background: linear-gradient(
                135deg,
                #0f172a,
                #1e3a5f
            );
            margin-bottom: 1.5rem;
        }

        .main-header h1 {
            color: white;
            margin: 0;
            font-size: 2rem;
        }

        .main-header p {
            color: #cbd5e1;
            margin-top: 0.5rem;
            margin-bottom: 0;
        }

        .section-card {
            padding: 1.2rem;
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 12px;
            margin-bottom: 1rem;
        }

        .small-muted-text {
            color: #64748b;
            font-size: 0.9rem;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.25);
            padding: 1rem;
            border-radius: 12px;
        }

        div[data-testid="stFileUploader"] {
            border-radius: 12px;
        }

        .stDownloadButton button {
            min-height: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """
    Initialize values that must remain available when
    Streamlit reruns the application.
    """

    default_values = {
        "audit_result": None,
        "report_bytes": None,
        "report_filename": None,
        "uploaded_filename": None,
        "last_error": None
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_assessment() -> None:
    """
    Remove the current assessment from session state.
    """

    st.session_state.audit_result = None
    st.session_state.report_bytes = None
    st.session_state.report_filename = None
    st.session_state.uploaded_filename = None
    st.session_state.last_error = None


# ============================================================
# GENERIC VALUE HELPERS
# ============================================================

def get_value(
    source: Any,
    field_name: str,
    default_value: Any = None
) -> Any:
    """
    Read a value from either a dictionary or an object.
    """

    if isinstance(source, dict):
        return source.get(
            field_name,
            default_value
        )

    return getattr(
        source,
        field_name,
        default_value
    )


def get_first_available_value(
    source: Any,
    possible_field_names: list[str],
    default_value: Any = ""
) -> Any:
    """
    Read the first available value from several possible
    dictionary keys or object attributes.
    """

    for field_name in possible_field_names:
        value = get_value(
            source,
            field_name,
            None
        )

        if value is not None and value != "":
            return value

    return default_value


def convert_value_for_display(
    value: Any
) -> str:
    """
    Convert lists, dictionaries and other Python values
    into text suitable for display in a table.
    """

    if value is None:
        return ""

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, list):
        return ", ".join(
            convert_value_for_display(item)
            for item in value
        )

    if isinstance(value, tuple):
        return ", ".join(
            convert_value_for_display(item)
            for item in value
        )

    if isinstance(value, dict):
        return "; ".join(
            f"{key}: {convert_value_for_display(item_value)}"
            for key, item_value in value.items()
        )

    return str(value)


def normalize_status(
    status: Any
) -> str:
    """
    Convert different status formats into a standard value.

    Examples:
        ComplianceStatus.PASS -> PASS
        PASSED                -> PASS
        NON_COMPLIANT         -> FAIL
        MANUAL_REVIEW         -> MANUAL
    """

    if status is None:
        return "UNKNOWN"

    status_text = str(status).strip()

    if "." in status_text:
        status_text = status_text.split(".")[-1]

    status_text = status_text.upper()

    status_aliases = {
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
        "NA": "N/A"
    }

    return status_aliases.get(
        status_text,
        status_text
    )


def determine_operating_system(
    server_result: Any
) -> str:
    """
    Determine the operating system from a server result.
    """

    operating_system = get_first_available_value(
        server_result,
        [
            "operating_system",
            "os",
            "os_name",
            "platform"
        ],
        ""
    )

    operating_system = convert_value_for_display(
        operating_system
    ).strip()

    if operating_system:
        return operating_system

    # Existing Windows results may be ServerResult objects
    # without an operating_system field.
    if not isinstance(server_result, dict):
        return "Windows"

    return "Unknown"


def determine_os_family(
    operating_system: str
) -> str:
    """
    Convert a detailed OS name into a general OS family.
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
        "amazon linux"
    ]

    if "windows" in os_text:
        return "Windows"

    if any(
        linux_name in os_text
        for linux_name in linux_names
    ):
        return "Linux"

    return "Unknown"


# ============================================================
# SERVER INVENTORY
# ============================================================

def build_server_inventory_rows(
    server_results: list
) -> list[dict]:
    """
    Convert all server results into a common inventory format.
    """

    rows = []

    for index, server_result in enumerate(
        server_results,
        start=1
    ):
        hostname = get_first_available_value(
            server_result,
            [
                "hostname",
                "computer_name",
                "server_name",
                "name"
            ],
            "Unknown"
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
                "ips"
            ],
            []
        )

        rows.append(
            {
                "No.": index,
                "Hostname": convert_value_for_display(
                    hostname
                ),
                "OS Family": os_family,
                "Operating System": operating_system,
                "IP Address": convert_value_for_display(
                    ip_addresses
                )
            }
        )

    return rows


# ============================================================
# REQUIREMENT DETAILS
# ============================================================

def build_requirement_rows(
    server_results: list
) -> list[dict]:
    """
    Convert Windows and Linux requirement results into
    one common table structure.
    """

    rows = []

    for server_result in server_results:
        hostname = get_first_available_value(
            server_result,
            [
                "hostname",
                "computer_name",
                "server_name",
                "name"
            ],
            "Unknown"
        )

        operating_system = determine_operating_system(
            server_result
        )

        os_family = determine_os_family(
            operating_system
        )

        requirements = get_first_available_value(
            server_result,
            [
                "requirements",
                "requirement_results",
                "results",
                "checks",
                "controls"
            ],
            {}
        )

        if isinstance(requirements, dict):
            requirement_items = requirements.items()

        elif isinstance(requirements, list):
            requirement_items = enumerate(
                requirements,
                start=1
            )

        else:
            continue

        for requirement_key, requirement_result in (
            requirement_items
        ):
            requirement_id = get_first_available_value(
                requirement_result,
                [
                    "requirement_id",
                    "id",
                    "control_id",
                    "check_id",
                    "rule_id"
                ],
                str(requirement_key)
            )

            requirement_name = get_first_available_value(
                requirement_result,
                [
                    "requirement_name",
                    "name",
                    "title",
                    "control_name",
                    "check_name",
                    "description"
                ],
                str(requirement_key)
            )

            category = get_first_available_value(
                requirement_result,
                [
                    "category",
                    "section",
                    "group",
                    "control_family"
                ],
                ""
            )

            status = get_first_available_value(
                requirement_result,
                [
                    "status",
                    "result",
                    "compliance_status",
                    "assessment_status"
                ],
                "UNKNOWN"
            )

            expected_value = get_first_available_value(
                requirement_result,
                [
                    "expected_value",
                    "expected",
                    "required_value",
                    "requirement",
                    "target_value"
                ],
                ""
            )

            actual_value = get_first_available_value(
                requirement_result,
                [
                    "actual_value",
                    "actual",
                    "detected_value",
                    "current_value",
                    "value",
                    "observed_value"
                ],
                ""
            )

            evidence = get_first_available_value(
                requirement_result,
                [
                    "evidence",
                    "details",
                    "message",
                    "reason",
                    "observation",
                    "raw_value"
                ],
                ""
            )

            recommendation = get_first_available_value(
                requirement_result,
                [
                    "recommendation",
                    "remediation",
                    "solution",
                    "action",
                    "recommended_action"
                ],
                ""
            )

            rows.append(
                {
                    "Server": convert_value_for_display(
                        hostname
                    ),
                    "OS Family": os_family,
                    "Operating System": operating_system,
                    "Requirement ID":
                        convert_value_for_display(
                            requirement_id
                        ),
                    "Category":
                        convert_value_for_display(
                            category
                        ),
                    "Requirement":
                        convert_value_for_display(
                            requirement_name
                        ),
                    "Status": normalize_status(
                        status
                    ),
                    "Expected Value":
                        convert_value_for_display(
                            expected_value
                        ),
                    "Actual Value":
                        convert_value_for_display(
                            actual_value
                        ),
                    "Evidence / Details":
                        convert_value_for_display(
                            evidence
                        ),
                    "Recommendation":
                        convert_value_for_display(
                            recommendation
                        )
                }
            )

    return rows


def count_requirement_statuses(
    requirement_rows: list[dict]
) -> dict[str, int]:
    """
    Count each compliance status.
    """

    counts = {
        "PASS": 0,
        "FAIL": 0,
        "MANUAL": 0,
        "N/A": 0,
        "UNKNOWN": 0,
        "OTHER": 0
    }

    for row in requirement_rows:
        status = normalize_status(
            row.get(
                "Status",
                "UNKNOWN"
            )
        )

        if status in counts:
            counts[status] += 1
        else:
            counts["OTHER"] += 1

    return counts


def calculate_compliance_score(
    status_counts: dict[str, int]
) -> float:
    """
    Calculate compliance using automatic PASS and FAIL
    results only.

    MANUAL, N/A and UNKNOWN results are excluded.
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
        1
    )


# ============================================================
# DASHBOARD COMPONENTS
# ============================================================

def display_application_header() -> None:
    """
    Display the main application title.
    """

    st.markdown(
        """
        <div class="main-header">
            <h1>🛡️ Enterprise Security Audit Aggregator</h1>
            <p>
                Automated Windows and Linux security compliance
                assessment and enterprise reporting platform
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_sidebar() -> None:
    """
    Display application information in the sidebar.
    """

    with st.sidebar:
        st.title("🛡️ ESAA")

        st.caption(
            "Enterprise Security Audit Aggregator"
        )

        st.markdown("---")

        st.subheader("Application")

        st.write("Version: **1.1.0**")
        st.write("Status: **Development**")

        st.markdown("---")

        st.subheader("Supported Platforms")

        st.write("🪟 Windows Server")
        st.write("🐧 Linux Server")

        st.markdown("---")

        st.subheader("Workflow")

        st.write(
            """
            1. Upload audit ZIP  
            2. Discover servers  
            3. Detect operating systems  
            4. Evaluate requirements  
            5. Review dashboard  
            6. Download Excel report
            """
        )

        if st.session_state.audit_result is not None:
            st.markdown("---")

            if st.button(
                "🗑️ Clear Current Assessment",
                use_container_width=True
            ):
                reset_assessment()
                st.rerun()


def display_upload_section() -> None:
    """
    Display the ZIP upload and audit execution area.
    """

    st.subheader("📁 Upload Customer Audit Package")

    st.write(
        """
        Upload a ZIP package containing security evidence
        collected from one or more Windows or Linux servers.
        """
    )

    uploaded_file = st.file_uploader(
        "Select or drag and drop a ZIP file",
        type=["zip"],
        help=(
            "The uploaded ZIP package may contain audit "
            "results from multiple servers."
        )
    )

    if uploaded_file is None:
        st.info(
            "Upload a customer ZIP file to begin the assessment."
        )
        return

    file_size_mb = uploaded_file.size / (
        1024 * 1024
    )

    information_col1, information_col2 = st.columns(
        2
    )

    information_col1.metric(
        "Selected File",
        uploaded_file.name
    )

    information_col2.metric(
        "File Size",
        f"{file_size_mb:.2f} MB"
    )

    run_button = st.button(
        "🚀 Run Security Assessment",
        type="primary",
        use_container_width=True
    )

    if not run_button:
        return

    temporary_zip_path = None

    try:
        reset_assessment()

        with st.spinner(
            "Analyzing the customer audit package..."
        ):
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".zip"
            ) as temporary_file:
                temporary_file.write(
                    uploaded_file.getbuffer()
                )

                temporary_zip_path = Path(
                    temporary_file.name
                )

            result = run_customer_audit(
                zip_path=temporary_zip_path,
                output_directory="output"
            )

            report_path = Path(
                result["report_path"]
            )

            if not report_path.exists():
                raise FileNotFoundError(
                    "The assessment completed, but the "
                    "generated Excel report was not found."
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

        st.success(
            "Security assessment completed successfully."
        )

    except FileNotFoundError as error:
        st.session_state.last_error = str(error)

        st.error(
            f"File error: {error}"
        )

    except ValueError as error:
        st.session_state.last_error = str(error)

        st.error(
            f"Invalid input: {error}"
        )

    except RuntimeError as error:
        st.session_state.last_error = str(error)

        st.error(
            f"Assessment error: {error}"
        )

    except PermissionError as error:
        st.session_state.last_error = str(error)

        st.error(
            "The Excel report could not be created. "
            "Close any open report files and run the "
            "assessment again."
        )

        st.caption(
            f"Technical details: {error}"
        )

    except Exception as error:
        st.session_state.last_error = str(error)

        st.error(
            "An unexpected error occurred while processing "
            "the audit package."
        )

        st.exception(error)

    finally:
        if (
            temporary_zip_path is not None
            and temporary_zip_path.exists()
        ):
            temporary_zip_path.unlink(
                missing_ok=True
            )


def display_overview_metrics(
    server_rows: list[dict],
    requirement_rows: list[dict]
) -> None:
    """
    Display the main dashboard metrics.
    """

    status_counts = count_requirement_statuses(
        requirement_rows
    )

    compliance_score = calculate_compliance_score(
        status_counts
    )

    windows_count = sum(
        1
        for row in server_rows
        if row["OS Family"] == "Windows"
    )

    linux_count = sum(
        1
        for row in server_rows
        if row["OS Family"] == "Linux"
    )

    metric_col1, metric_col2, metric_col3 = st.columns(
        3
    )

    metric_col1.metric(
        "Compliance Score",
        f"{compliance_score}%"
    )

    metric_col2.metric(
        "Servers Evaluated",
        len(server_rows)
    )

    metric_col3.metric(
        "Requirements Evaluated",
        len(requirement_rows)
    )

    st.progress(
        min(
            max(
                compliance_score / 100,
                0.0
            ),
            1.0
        )
    )

    st.markdown("#### Platform Summary")

    platform_col1, platform_col2, platform_col3 = (
        st.columns(3)
    )

    platform_col1.metric(
        "Windows Servers",
        windows_count
    )

    platform_col2.metric(
        "Linux Servers",
        linux_count
    )

    platform_col3.metric(
        "Unknown Platforms",
        len(server_rows)
        - windows_count
        - linux_count
    )

    st.markdown("#### Compliance Status")

    status_col1, status_col2, status_col3, status_col4 = (
        st.columns(4)
    )

    status_col1.metric(
        "PASS",
        status_counts["PASS"]
    )

    status_col2.metric(
        "FAIL",
        status_counts["FAIL"]
    )

    status_col3.metric(
        "MANUAL",
        status_counts["MANUAL"]
    )

    status_col4.metric(
        "N/A or Unknown",
        (
            status_counts["N/A"]
            + status_counts["UNKNOWN"]
            + status_counts["OTHER"]
        )
    )


def display_status_chart(
    requirement_rows: list[dict]
) -> None:
    """
    Display a compliance status bar chart.
    """

    status_counts = count_requirement_statuses(
        requirement_rows
    )

    chart_data = pd.DataFrame(
        {
            "Status": [
                "PASS",
                "FAIL",
                "MANUAL",
                "N/A",
                "UNKNOWN"
            ],
            "Count": [
                status_counts["PASS"],
                status_counts["FAIL"],
                status_counts["MANUAL"],
                status_counts["N/A"],
                (
                    status_counts["UNKNOWN"]
                    + status_counts["OTHER"]
                )
            ]
        }
    )

    st.markdown("#### Requirement Status Distribution")

    st.bar_chart(
        chart_data,
        x="Status",
        y="Count",
        use_container_width=True
    )


def display_server_inventory(
    server_rows: list[dict]
) -> None:
    """
    Display the server inventory table.
    """

    st.subheader("🖥️ Server Inventory")

    if not server_rows:
        st.warning(
            "No server inventory information was found."
        )
        return

    st.dataframe(
        server_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "No.": st.column_config.NumberColumn(
                "No.",
                width="small"
            ),
            "Hostname": st.column_config.TextColumn(
                "Hostname",
                width="medium"
            ),
            "OS Family": st.column_config.TextColumn(
                "OS Family",
                width="small"
            ),
            "Operating System":
                st.column_config.TextColumn(
                    "Operating System",
                    width="large"
                ),
            "IP Address":
                st.column_config.TextColumn(
                    "IP Address",
                    width="medium"
                )
        }
    )


def display_requirement_details(
    requirement_rows: list[dict]
) -> None:
    """
    Display the interactive requirement assessment table.
    """

    st.subheader("📋 Requirement Assessment Details")

    if not requirement_rows:
        st.warning(
            "No requirement details were found in the "
            "assessment results."
        )
        return

    server_names = sorted(
        {
            row["Server"]
            for row in requirement_rows
        }
    )

    os_families = sorted(
        {
            row["OS Family"]
            for row in requirement_rows
        }
    )

    status_values = sorted(
        {
            row["Status"]
            for row in requirement_rows
        }
    )

    category_values = sorted(
        {
            row["Category"]
            for row in requirement_rows
            if row["Category"]
        }
    )

    filter_row1_col1, filter_row1_col2 = st.columns(
        2
    )

    with filter_row1_col1:
        selected_servers = st.multiselect(
            "Filter by server",
            options=server_names,
            placeholder="All servers"
        )

    with filter_row1_col2:
        selected_statuses = st.multiselect(
            "Filter by status",
            options=status_values,
            placeholder="All statuses"
        )

    filter_row2_col1, filter_row2_col2 = st.columns(
        2
    )

    with filter_row2_col1:
        selected_os_families = st.multiselect(
            "Filter by operating-system family",
            options=os_families,
            placeholder="All platforms"
        )

    with filter_row2_col2:
        selected_categories = st.multiselect(
            "Filter by category",
            options=category_values,
            placeholder="All categories",
            disabled=not category_values
        )

    search_text = st.text_input(
        "Search requirement details",
        placeholder=(
            "Search by requirement ID, name, value, "
            "evidence or recommendation"
        )
    )

    filtered_rows = []

    for row in requirement_rows:
        server_matches = (
            not selected_servers
            or row["Server"] in selected_servers
        )

        status_matches = (
            not selected_statuses
            or row["Status"] in selected_statuses
        )

        os_matches = (
            not selected_os_families
            or row["OS Family"] in selected_os_families
        )

        category_matches = (
            not selected_categories
            or row["Category"] in selected_categories
        )

        searchable_text = " ".join(
            str(value)
            for value in row.values()
        ).lower()

        search_matches = (
            not search_text
            or search_text.lower() in searchable_text
        )

        if (
            server_matches
            and status_matches
            and os_matches
            and category_matches
            and search_matches
        ):
            filtered_rows.append(row)

    result_col1, result_col2 = st.columns(2)

    result_col1.metric(
        "Displayed Requirements",
        len(filtered_rows)
    )

    result_col2.metric(
        "Total Requirements",
        len(requirement_rows)
    )

    if not filtered_rows:
        st.warning(
            "No requirements match the selected filters."
        )
        return

    st.dataframe(
        filtered_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Server": st.column_config.TextColumn(
                "Server",
                width="medium"
            ),
            "OS Family": st.column_config.TextColumn(
                "OS Family",
                width="small"
            ),
            "Operating System":
                st.column_config.TextColumn(
                    "Operating System",
                    width="medium"
                ),
            "Requirement ID":
                st.column_config.TextColumn(
                    "Requirement ID",
                    width="small"
                ),
            "Category": st.column_config.TextColumn(
                "Category",
                width="medium"
            ),
            "Requirement":
                st.column_config.TextColumn(
                    "Requirement",
                    width="large"
                ),
            "Status": st.column_config.TextColumn(
                "Status",
                width="small"
            ),
            "Expected Value":
                st.column_config.TextColumn(
                    "Expected Value",
                    width="medium"
                ),
            "Actual Value":
                st.column_config.TextColumn(
                    "Actual Value",
                    width="medium"
                ),
            "Evidence / Details":
                st.column_config.TextColumn(
                    "Evidence / Details",
                    width="large"
                ),
            "Recommendation":
                st.column_config.TextColumn(
                    "Recommendation",
                    width="large"
                )
        }
    )


def display_failed_requirements(
    requirement_rows: list[dict]
) -> None:
    """
    Display only failed requirements requiring remediation.
    """

    st.subheader("⚠️ Failed Requirements")

    failed_rows = [
        row
        for row in requirement_rows
        if row["Status"] == "FAIL"
    ]

    if not failed_rows:
        st.success(
            "No failed automatic requirements were found."
        )
        return

    st.warning(
        f"{len(failed_rows)} failed requirement(s) "
        "require review or remediation."
    )

    st.dataframe(
        failed_rows,
        use_container_width=True,
        hide_index=True
    )


def display_report_download() -> None:
    """
    Display report information and the Excel download button.
    """

    st.subheader("📄 Assessment Report")

    if (
        st.session_state.report_bytes is None
        or st.session_state.report_filename is None
    ):
        st.warning(
            "No generated report is currently available."
        )
        return

    report_col1, report_col2 = st.columns(
        [2, 1]
    )

    with report_col1:
        st.write(
            f"**Report file:** "
            f"{st.session_state.report_filename}"
        )

        if st.session_state.uploaded_filename:
            st.write(
                f"**Source package:** "
                f"{st.session_state.uploaded_filename}"
            )

        report_size_mb = (
            len(st.session_state.report_bytes)
            / 1024
            / 1024
        )

        st.write(
            f"**Report size:** "
            f"{report_size_mb:.2f} MB"
        )

    with report_col2:
        st.download_button(
            label="⬇️ Download Excel Report",
            data=st.session_state.report_bytes,
            file_name=st.session_state.report_filename,
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
            type="primary",
            use_container_width=True
        )


def display_assessment_dashboard() -> None:
    """
    Display all dashboard tabs after a successful assessment.
    """

    audit_result = st.session_state.audit_result

    server_results = audit_result.get(
        "server_results",
        []
    )

    server_rows = build_server_inventory_rows(
        server_results
    )

    requirement_rows = build_requirement_rows(
        server_results
    )

    st.success(
        f"{audit_result.get('server_count', len(server_rows))} "
        "server(s) were successfully evaluated."
    )

    (
        overview_tab,
        servers_tab,
        requirements_tab,
        failures_tab,
        report_tab
    ) = st.tabs(
        [
            "📊 Overview",
            "🖥️ Servers",
            "📋 Requirements",
            "⚠️ Failures",
            "📄 Report"
        ]
    )

    with overview_tab:
        display_overview_metrics(
            server_rows,
            requirement_rows
        )

        st.markdown("---")

        display_status_chart(
            requirement_rows
        )

    with servers_tab:
        display_server_inventory(
            server_rows
        )

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
    Start the Streamlit application.
    """

    initialize_session_state()

    display_sidebar()

    display_application_header()

    display_upload_section()

    if st.session_state.audit_result is not None:
        st.markdown("---")

        display_assessment_dashboard()


if __name__ == "__main__":
    main()