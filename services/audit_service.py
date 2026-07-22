from datetime import datetime
from pathlib import Path
from typing import Any

from analyzers.customer_engine import evaluate_customer_zip
from reports.excel_report import generate_excel_report


def run_customer_audit(
    zip_path: str | Path,
    output_directory: str | Path = "output"
) -> dict[str, Any]:
    """
    Run a complete customer security assessment.

    The function:
        1. Validates the customer ZIP file.
        2. Evaluates every discovered server.
        3. Generates a timestamped Excel report.
        4. Returns the results and report location.

    Args:
        zip_path:
            Path to the customer ZIP file.

        output_directory:
            Folder where the Excel report will be saved.

    Returns:
        Dictionary containing:
            server_results:
                Windows and Linux evaluation results.

            server_count:
                Number of successfully evaluated servers.

            report_path:
                Path to the generated Excel report.
    """

    zip_path = Path(zip_path)
    output_directory = Path(output_directory)

    if not zip_path.exists():
        raise FileNotFoundError(
            f"Customer ZIP file was not found: {zip_path}"
        )

    if not zip_path.is_file():
        raise ValueError(
            f"The specified input is not a file: {zip_path}"
        )

    if zip_path.suffix.lower() != ".zip":
        raise ValueError(
            "The customer audit package must be a ZIP file."
        )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report_path = output_directory / (
        f"Customer_Security_Report_{timestamp}.xlsx"
    )

    server_results = evaluate_customer_zip(
        zip_path
    )

    if not server_results:
        raise RuntimeError(
            "No valid Windows or Linux server audit "
            "results were found inside the ZIP file."
        )

    generated_report_path = generate_excel_report(
        server_results,
        str(report_path)
    )

    # Some report generators return the output path,
    # while others save the file without returning anything.
    if generated_report_path is None:
        generated_report_path = str(report_path)

    return {
        "server_results": server_results,
        "server_count": len(server_results),
        "report_path": str(generated_report_path)
    }