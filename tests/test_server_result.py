from models.server_result import ServerResult


server = ServerResult(
    hostname="DC-VM001",
    ip_addresses=["10.5.0.5"],
    execution_time="Tue 07/21/2026 3:06:30.83"
)

server.add_result("3.1", "FAIL")
server.add_result("4.1", "PASS")
server.add_result("4.2", "MANUAL")

print(server.to_dict())