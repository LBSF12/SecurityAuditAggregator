from analyzers.file_reader import read_all_files
from parsers.windows_parser import parse_audit_policy
from analyzers.mapper import normalize


def load_windows_audit(server_folder, config):
    """
    Load and normalize Windows audit-policy files.

    The filenames are obtained from the workflow configuration.

    Example:
        3.1 -> 3-1_AuditPolicy.txt
        7   -> 7_PrivilegedAuditPolicy.txt
        9.1 -> 9-1_AccountManagementAudit.txt
               9-1_PasswordReset_AuditPolicy.txt
    """

    all_files = read_all_files(server_folder)

    combined_audit_settings = {}

    configured_files = config.get("files", [])

    for file_name in configured_files:

        file_data = all_files.get(file_name)

        if file_data is None:
            continue

        file_content = file_data.get("content", "")

        parsed_settings = parse_audit_policy(file_content)

        combined_audit_settings.update(parsed_settings)

    mapping_file = config.get(
        "mapping",
        "config/mappings/audit_policy.json"
    )

    normalized = normalize(
        combined_audit_settings,
        mapping_file
    )

    return normalized