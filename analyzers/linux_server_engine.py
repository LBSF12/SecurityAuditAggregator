from analyzers.requirement_executor import execute_requirement
from parsers.linux_server_info_parser import parse_linux_server_info
from utils.workflow_loader import load_workflow


def evaluate_linux_server(server_folder):
    """
    Evaluate all configured Linux requirements
    for one Linux server.
    """

    server_info = parse_linux_server_info(
        server_folder
    )

    server_result = {
        "hostname": server_info["hostname"],
        "ip_addresses": server_info["ip_addresses"],
        "execution_time": server_info["execution_time"],
        "operating_system": server_info["operating_system"],
        "requirements": {},
    }

    workflow = load_workflow(
        "config/workflows/linux.json"
    )

    for requirement, config in workflow.items():

        print(
            f"Evaluating Linux Requirement "
            f"{requirement}"
        )

        if config.get("manual"):

            server_result["requirements"][
                requirement
            ] = {
                "requirement": requirement,
                "description": config.get(
                    "description",
                    "Manual verification required"
                ),
                "status": "MANUAL",
                "details": [],
            }

            continue

        result = execute_requirement(
            server_folder,
            config
        )

        server_result["requirements"][
            requirement
        ] = result

    return server_result