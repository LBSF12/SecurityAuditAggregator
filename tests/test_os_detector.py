from analyzers.os_detector import detect_operating_system


def main():

    server_folder = "extracted/Server01"

    operating_system = detect_operating_system(
        server_folder
    )

    print("=" * 60)
    print("OPERATING SYSTEM DETECTION")
    print("=" * 60)
    print(f"Folder: {server_folder}")
    print(f"Detected OS: {operating_system}")


if __name__ == "__main__":
    main()