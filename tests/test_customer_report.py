from services.audit_service import run_customer_audit


def main() -> None:
    """
    Run a complete customer security audit from the command line.

    The audit service will:
        1. Read the customer ZIP file.
        2. Discover all server folders.
        3. Detect Windows or Linux.
        4. Evaluate security requirements.
        5. Generate the Excel report.
    """

    try:
        result = run_customer_audit(
            zip_path="input/CustomerResults.zip",
            output_directory="output"
        )

    except FileNotFoundError as error:
        print()
        print("=" * 60)
        print("INPUT FILE NOT FOUND")
        print("=" * 60)
        print(error)
        return

    except ValueError as error:
        print()
        print("=" * 60)
        print("INVALID INPUT")
        print("=" * 60)
        print(error)
        return

    except RuntimeError as error:
        print()
        print("=" * 60)
        print("AUDIT PROCESSING ERROR")
        print("=" * 60)
        print(error)
        return

    except PermissionError as error:
        print()
        print("=" * 60)
        print("REPORT FILE PERMISSION ERROR")
        print("=" * 60)
        print(
            "The Excel report may already be open. "
            "Close the file and run the command again."
        )
        print(f"Technical details: {error}")
        return

    except Exception as error:
        print()
        print("=" * 60)
        print("UNEXPECTED ERROR")
        print("=" * 60)
        print(f"Error type: {type(error).__name__}")
        print(f"Error details: {error}")
        raise

    print()
    print("=" * 60)
    print("CUSTOMER SECURITY AUDIT COMPLETED")
    print("=" * 60)

    print(
        f"Servers evaluated: "
        f"{result['server_count']}"
    )

    print(
        f"Excel report: "
        f"{result['report_path']}"
    )

    print()
    print("Evaluated servers:")
    print("-" * 60)

    for index, server_result in enumerate(
        result["server_results"],
        start=1
    ):
        if isinstance(server_result, dict):
            hostname = server_result.get(
                "hostname",
                "Unknown"
            )

            operating_system = server_result.get(
                "operating_system",
                "Unknown"
            )

            ip_addresses = server_result.get(
                "ip_addresses",
                []
            )

        else:
            hostname = getattr(
                server_result,
                "hostname",
                "Unknown"
            )

            operating_system = getattr(
                server_result,
                "operating_system",
                "Windows"
            )

            ip_addresses = getattr(
                server_result,
                "ip_addresses",
                []
            )

        print(
            f"{index}. Hostname: {hostname}"
        )

        print(
            f"   Operating system: {operating_system}"
        )

        print(
            f"   IP addresses: {ip_addresses}"
        )


if __name__ == "__main__":
    main()