import os
from datetime import datetime
from pathlib import Path
from pprint import pprint

from analyzers.customer_engine import evaluate_customer_zip
from reports.excel_report import generate_excel_report


def build_output_path() -> Path:
    """
    Generate a unique report filename using the current timestamp.
    """

    output_folder = Path("output")

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return output_folder / (
        f"Customer_Security_Report_{timestamp}.xlsx"
    )


def get_server_value(
    server_result,
    field_name,
    default_value=None
):
    """
    Read a field from either a dictionary
    or a ServerResult object.
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


def display_server_results(
    server_results: list
) -> None:
    """
    Display every server result before sending
    the data to the Excel generator.
    """

    print()
    print("=" * 60)
    print("SERVER RESULTS SENT TO EXCEL")
    print("=" * 60)

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
            None
        )

        if not operating_system:
            operating_system = (
                "Windows"
                if not isinstance(
                    server_result,
                    dict
                )
                else "Unknown"
            )

        ip_addresses = get_server_value(
            server_result,
            "ip_addresses",
            []
        )

        print(
            f"{index}. Hostname: {hostname}"
        )

        print(
            f"   OS: {operating_system}"
        )

        print(
            f"   IP: {ip_addresses}"
        )


def display_raw_results(
    server_results: list
) -> None:
    """
    Print the raw server results for troubleshooting.
    """

    print()
    print("=" * 80)
    print("SERVER RESULTS BEFORE EXCEL")
    print("=" * 80)
    print(
        f"Total server results: "
        f"{len(server_results)}"
    )

    for index, server_result in enumerate(
        server_results,
        start=1
    ):
        print()
        print(
            f"SERVER {index}"
        )

        if hasattr(
            server_result,
            "to_dict"
        ):
            pprint(
                server_result.to_dict()
            )
        else:
            pprint(
                server_result
            )


def open_generated_report(
    report_path: str
) -> None:
    """
    Open the exact Excel report generated
    during the current test execution.
    """

    absolute_report_path = Path(
        report_path
    ).resolve()

    if not absolute_report_path.exists():
        print(
            "The report was generated, but the "
            "file could not be found."
        )
        return

    print()
    print(
        "Opening generated report:"
    )
    print(
        absolute_report_path
    )

    try:
        os.startfile(
            absolute_report_path
        )

    except AttributeError:
        print(
            "Automatic opening is only available "
            "on Windows."
        )

    except OSError as error:
        print(
            "The report could not be opened "
            "automatically."
        )
        print(
            f"Error: {error}"
        )


def main() -> None:

    input_zip = Path(
        "input/CustomerResults.zip"
    )

    output_path = build_output_path()

    try:
        server_results = evaluate_customer_zip(
            input_zip
        )

        display_server_results(
            server_results
        )

        display_raw_results(
            server_results
        )

        report_path = generate_excel_report(
            server_results,
            str(output_path)
        )

    except PermissionError as error:
        print()
        print("=" * 60)
        print("REPORT FILE PERMISSION ERROR")
        print("=" * 60)
        print(
            "Excel may have the report file open."
        )
        print(
            "Close the Excel workbook and "
            "run the test again."
        )
        print(
            f"Technical details: {error}"
        )
        return

    except Exception as error:
        print()
        print("=" * 60)
        print("CUSTOMER REPORT FAILED")
        print("=" * 60)
        print(
            f"Error type: "
            f"{type(error).__name__}"
        )
        print(
            f"Error details: "
            f"{error}"
        )
        raise

    print()
    print("=" * 60)
    print("CUSTOMER REPORT GENERATED")
    print("=" * 60)
    print(
        f"Servers evaluated: "
        f"{len(server_results)}"
    )
    print(
        f"Report: {report_path}"
    )

    open_generated_report(
        report_path
    )


if __name__ == "__main__":
    main()