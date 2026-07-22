from pathlib import Path
from typing import Any

from analyzers.generic_server_engine import evaluate_server
from zip_processor.zip_scanner import process_input_zip


def get_result_value(
    server_result: Any,
    field_name: str,
    default_value: Any = None
) -> Any:
    """
    Read a value from either a dictionary result
    or a server result object.
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


def evaluate_customer_zip(
    input_zip: str | Path
) -> list:
    """
    Extract and evaluate all Windows and Linux server
    audit folders found inside one customer ZIP file.

    Returns only successfully evaluated server results.
    """

    input_zip = Path(
        input_zip
    )

    if not input_zip.exists():
        raise FileNotFoundError(
            "Customer ZIP file was not found: "
            f"{input_zip}"
        )

    if not input_zip.is_file():
        raise ValueError(
            "The supplied customer ZIP path is not a file: "
            f"{input_zip}"
        )

    server_folders = process_input_zip(
        input_zip
    )

    print()
    print("=" * 60)
    print("DISCOVERED SERVER FOLDERS")
    print("=" * 60)

    for server_folder in server_folders:
        print(server_folder)

    print(
        "Total discovered folders: "
        f"{len(server_folders)}"
    )

    if not server_folders:
        raise ValueError(
            "No valid Windows or Linux server audit folders "
            f"were found inside: {input_zip}"
        )

    successful_results = []
    failed_servers = []

    total_servers = len(
        server_folders
    )

    for index, server_folder in enumerate(
        server_folders,
        start=1
    ):
        print()
        print("=" * 60)
        print(
            f"Processing server {index}/"
            f"{total_servers}"
        )
        print(
            f"Folder: {server_folder}"
        )
        print("=" * 60)

        try:
            server_result = evaluate_server(
                server_folder
            )

            successful_results.append(
                server_result
            )

            hostname = get_result_value(
                server_result,
                "hostname",
                Path(server_folder).name
            )

            operating_system = get_result_value(
                server_result,
                "operating_system",
                "Unknown"
            )

            print()
            print(
                "Successfully evaluated: "
                f"{hostname}"
            )
            print(
                "Operating system: "
                f"{operating_system}"
            )

        except Exception as error:
            error_type = type(
                error
            ).__name__

            print()
            print(
                "Failed to evaluate server: "
                f"{server_folder}"
            )
            print(
                f"Error type: {error_type}"
            )
            print(
                f"Error details: {error}"
            )

            failed_servers.append(
                {
                    "folder": str(
                        server_folder
                    ),
                    "error_type": error_type,
                    "error": str(
                        error
                    ),
                }
            )

    print()
    print("=" * 60)
    print("CUSTOMER EVALUATION SUMMARY")
    print("=" * 60)
    print(
        "Discovered servers: "
        f"{total_servers}"
    )
    print(
        "Successfully evaluated: "
        f"{len(successful_results)}"
    )
    print(
        "Failed or skipped: "
        f"{len(failed_servers)}"
    )

    if failed_servers:
        print()
        print("FAILED SERVER DETAILS")

        for failed_server in failed_servers:
            print(
                "- "
                f"{failed_server['folder']}"
            )
            print(
                "  "
                f"{failed_server['error_type']}: "
                f"{failed_server['error']}"
            )

    if not successful_results:
        raise RuntimeError(
            "Server folders were discovered, but none of them "
            "could be evaluated successfully."
        )

    return successful_results