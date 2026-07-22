from pathlib import Path
import tempfile

import streamlit as st

from services.audit_service import run_customer_audit


st.set_page_config(
    page_title="Enterprise Security Audit Aggregator",
    page_icon="🛡️",
    layout="wide"
)


def initialize_session_state() -> None:
    """
    Initialize values that must remain available
    when Streamlit reruns the page.
    """

    if "audit_result" not in st.session_state:
        st.session_state.audit_result = None

    if "report_bytes" not in st.session_state:
        st.session_state.report_bytes = None

    if "report_filename" not in st.session_state:
        st.session_state.report_filename = None


def get_server_value(
    server_result,
    field_name: str,
    default_value=None
):
    """
    Read a value from either:
        - a dictionary
        - a ServerResult object
    """

    if isinstance(server_result, dict):
        return server_result.get(
            field_name,
            default_value
        )

    return getattr(
        server_result,
        field_name,
        default_value
    )


def display_server_inventory(
    server_results: list
) -> None:
    """
    Display the evaluated servers in the Streamlit page.
    """

    st.subheader("🖥️ Detected Servers")

    server_rows = []

    for index, server_result in enumerate(
        server_results,
        start=1
    ):
        hostname = get_server_value(
            server_result,
            "hostname",
            "Unknown"
        )

        operating_system = get_server_value(
            server_result,
            "operating_system",
            "Unknown"
        )

        ip_addresses = get_server_value(
            server_result,
            "ip_addresses",
            []
        )

        if not operating_system or operating_system == "Unknown":
            if not isinstance(server_result, dict):
                operating_system = "Windows"

        if isinstance(ip_addresses, list):
            ip_display = ", ".join(ip_addresses)
        else:
            ip_display = str(ip_addresses)

        server_rows.append(
            {
                "No.": index,
                "Hostname": hostname,
                "Operating System": operating_system,
                "IP Address": ip_display
            }
        )

    st.dataframe(
        server_rows,
        use_container_width=True,
        hide_index=True
    )


def count_requirement_statuses(
    server_results: list
) -> dict[str, int]:
    """
    Count PASS, FAIL, MANUAL and other statuses
    across all evaluated servers.
    """

    counts = {
        "PASS": 0,
        "FAIL": 0,
        "MANUAL": 0,
        "OTHER": 0
    }

    for server_result in server_results:
        requirements = get_server_value(
            server_result,
            "requirements",
            {}
        )

        if not isinstance(requirements, dict):
            continue

        for requirement_result in requirements.values():
            if isinstance(requirement_result, dict):
                status = requirement_result.get(
                    "status",
                    "OTHER"
                )
            else:
                status = getattr(
                    requirement_result,
                    "status",
                    "OTHER"
                )

            status = str(status).upper()

            if status in counts:
                counts[status] += 1
            else:
                counts["OTHER"] += 1

    return counts


def display_compliance_summary(
    server_results: list
) -> None:
    """
    Display high-level assessment metrics.
    """

    counts = count_requirement_statuses(
        server_results
    )

    total_automatic_checks = (
        counts["PASS"] +
        counts["FAIL"]
    )

    if total_automatic_checks > 0:
        compliance_score = round(
            counts["PASS"]
            / total_automatic_checks
            * 100,
            1
        )
    else:
        compliance_score = 0.0

    st.subheader("📊 Compliance Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Compliance Score",
        f"{compliance_score}%"
    )

    col2.metric(
        "PASS",
        counts["PASS"]
    )

    col3.metric(
        "FAIL",
        counts["FAIL"]
    )

    col4.metric(
        "MANUAL",
        counts["MANUAL"]
    )

    st.progress(
        compliance_score / 100
    )


initialize_session_state()


st.title("🛡️ Enterprise Security Audit Aggregator")

st.caption(
    "Automated Windows and Linux security compliance assessment"
)

st.markdown("---")

st.subheader("📁 Upload Customer Audit Package")

uploaded_file = st.file_uploader(
    "Select or drag and drop the customer ZIP file",
    type=["zip"],
    help=(
        "The ZIP package may contain audit evidence "
        "from multiple Windows and Linux servers."
    )
)

if uploaded_file is None:
    st.info(
        "Upload a customer ZIP file to begin the assessment."
    )

else:
    file_size_mb = uploaded_file.size / (
        1024 * 1024
    )

    st.success(
        f"Selected file: {uploaded_file.name}"
    )

    st.write(
        f"File size: {file_size_mb:.2f} MB"
    )

    run_audit_button = st.button(
        "🚀 Run Security Assessment",
        type="primary",
        use_container_width=True
    )

    if run_audit_button:
        temporary_zip_path = None

        try:
            with st.spinner(
                "Processing the customer package..."
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
                        "The audit completed, but the "
                        "Excel report could not be found."
                    )

                with report_path.open("rb") as report_file:
                    report_bytes = report_file.read()

                st.session_state.audit_result = result
                st.session_state.report_bytes = report_bytes
                st.session_state.report_filename = (
                    report_path.name
                )

            st.success(
                "Security assessment completed successfully."
            )

        except FileNotFoundError as error:
            st.error(
                f"File error: {error}"
            )

        except ValueError as error:
            st.error(
                f"Invalid input: {error}"
            )

        except RuntimeError as error:
            st.error(
                f"Assessment error: {error}"
            )

        except PermissionError as error:
            st.error(
                "The Excel report could not be written. "
                "Close any open report files and try again."
            )

            st.caption(
                f"Technical details: {error}"
            )

        except Exception as error:
            st.error(
                "An unexpected error occurred while "
                "processing the audit package."
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


if st.session_state.audit_result is not None:
    st.markdown("---")

    audit_result = st.session_state.audit_result

    server_results = audit_result[
        "server_results"
    ]

    st.success(
        f"{audit_result['server_count']} server(s) "
        "were successfully evaluated."
    )

    display_compliance_summary(
        server_results
    )

    st.markdown("---")

    display_server_inventory(
        server_results
    )

    st.markdown("---")

    st.subheader("📄 Download Assessment Report")

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