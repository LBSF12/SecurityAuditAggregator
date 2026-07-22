from analyzers.server_engine import evaluate_windows_server


server = evaluate_windows_server(
    "extracted/Server01"
)

print("=" * 60)
print("SERVER EVALUATION RESULT")
print("=" * 60)
print(server.to_dict())