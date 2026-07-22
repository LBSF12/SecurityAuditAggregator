from analyzers.file_reader import read_all_files
from parsers.server_info_parser import parse_server_info


files = read_all_files("extracted/Server01")

server_info_filename = "server_info.txt"

if server_info_filename not in files:
    raise FileNotFoundError(
        f"{server_info_filename} was not found in extracted/Server01"
    )

server_info = parse_server_info(
    files[server_info_filename]["content"]
)

print("=" * 60)
print("SERVER INFORMATION")
print("=" * 60)
print(f"Hostname       : {server_info['hostname']}")
print(f"Execution Time : {server_info['execution_time']}")
print(f"IPv4 Addresses : {server_info['ip_addresses']}")