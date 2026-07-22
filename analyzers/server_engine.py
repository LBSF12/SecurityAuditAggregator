from analyzers.requirement_executor import execute_requirement
from analyzers.server_loader import load_server
from utils.workflow_loader import load_workflow


def evaluate_windows_server(server_folder):
    """
    Evaluate all configured Windows requirements for one server.

    The server hostname, IP addresses, and execution time are
    loaded automatically from ServerInfo.txt.
    """

    server = load_server(server_folder)

    workflow = load_workflow(
        "config/workflows/windows.json"
    )

    for requirement, config in workflow.items():

        print(f"Evaluating Requirement {requirement}")

        if config.get("manual"):

            manual_result = {
                "requirement": requirement,
                "description": config.get(
                    "description",
                    "Manual verification required"
                ),
                "status": "MANUAL",
                "details": []
            }

            server.add_result(
                requirement,
                manual_result
            )

            continue

        result = execute_requirement(
            server_folder,
            config
        )

        server.add_result(
            requirement,
            result
        )

    return server