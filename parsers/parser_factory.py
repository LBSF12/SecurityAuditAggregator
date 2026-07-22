from analyzers.audit_engine import load_windows_audit

from parsers.password_policy_parser import load_password_policy
from parsers.log_retention_parser import parse_log_retention

from analyzers.file_reader import read_all_files
from parsers.linux_security_parser import (
    load_linux_account_audit,
    load_linux_auth_log_retention,
    load_linux_password_policy,
    load_linux_privileged_audit,
    load_linux_retention,
)

def load_password_policy_from_workflow(server_folder, config):
    """
    Compatibility wrapper for the existing password-policy loader.
    """

    return load_password_policy(server_folder)


def load_log_retention_from_workflow(server_folder, config):
    """
    Read the log configuration file specified in the workflow
    and parse its content.
    """

    all_files = read_all_files(server_folder)

    configured_files = config.get("files", [])

    if not configured_files:
        return {}

    file_name = configured_files[0]

    file_data = all_files.get(file_name)

    if file_data is None:
        return {}

    file_content = file_data.get("content", "")

    return parse_log_retention(file_content)


def get_parser(parser_name):

    parsers = {
        "audit_policy": load_windows_audit,
        "password_policy": load_password_policy_from_workflow,
        "log_retention": load_log_retention_from_workflow,

        "linux_retention": load_linux_retention,
        "linux_password_policy": load_linux_password_policy,
        "linux_privileged_audit": load_linux_privileged_audit,
        "linux_account_audit": load_linux_account_audit,
        "linux_auth_log_retention": load_linux_auth_log_retention,
    }

    return parsers.get(parser_name)