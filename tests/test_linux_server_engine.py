from analyzers.linux_server_engine import evaluate_linux_server


def main():

    server_folder = "extracted/linux"
    result = evaluate_linux_server(
        server_folder
    )

    print("=" * 60)
    print("LINUX SERVER EVALUATION RESULT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()