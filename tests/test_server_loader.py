from analyzers.server_loader import load_server


server = load_server("extracted/Server01")

print("=" * 60)
print("SERVER LOADER RESULT")
print("=" * 60)
print(server.to_dict())