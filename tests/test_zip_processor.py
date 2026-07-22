from zip_processor.zip_scanner import process_input_zip


def main():

    input_zip = "input/CustomerResults.zip"

    server_folders = process_input_zip(
        input_zip
    )

    print("=" * 60)
    print("SERVER FOLDERS DISCOVERED")
    print("=" * 60)

    if not server_folders:
        print("No server folders were found.")
        return

    for number, folder in enumerate(
        server_folders,
        start=1
    ):
        print(
            f"{number}. {folder}"
        )

    print("=" * 60)
    print(
        f"Total servers found: "
        f"{len(server_folders)}"
    )


if __name__ == "__main__":
    main()