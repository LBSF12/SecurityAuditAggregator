from analyzers.server_engine import evaluate_windows_server
from reports.excel_report import generate_excel_report


def main():

    # Use the extracted folder containing ServerInfo.txt
    # and the other audit result files.
    server_folder = "extracted/Server01"

    server_result = evaluate_windows_server(
        server_folder
    )

    all_server_results = [
        server_result
    ]

    report_path = generate_excel_report(
        all_server_results,
        "output/Windows_Security_Verification_Report.xlsx"
    )

    print("=" * 60)
    print("CONSOLIDATED EXCEL REPORT GENERATED")
    print("=" * 60)
    print(report_path)


if __name__ == "__main__":
    main()