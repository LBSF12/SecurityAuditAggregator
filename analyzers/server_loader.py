from pathlib import Path

from analyzers.file_reader import read_all_files
from models.server_result import ServerResult
from parsers.server_info_parser import parse_server_info


def load_server(server_folder):
    """
    Read ServerInfo.txt and create a ServerResult object.

    Parameters
    ----------
    server_folder : str | Path
        Extracted audit-results folder for one server.

    Returns
    -------
    ServerResult
        Server object containing hostname, IP addresses,
        execution time, and an empty requirements dictionary.
    """

    server_folder = Path(server_folder)

    files = read_all_files(server_folder)

    server_info_filename = "server_info.txt"

    if server_info_filename not in files:
        raise FileNotFoundError(
            f"{server_info_filename} was not found in: "
            f"{server_folder.resolve()}"
        )

    server_info = parse_server_info(
        files[server_info_filename]["content"]
    )

    if not server_info["hostname"]:
        raise ValueError(
            f"Hostname could not be extracted from "
            f"{server_info_filename}"
        )

    return ServerResult(
        hostname=server_info["hostname"],
        ip_addresses=server_info["ip_addresses"],
        execution_time=server_info["execution_time"]
    )