from pathlib import Path

from analyzers.file_reader import read_file


def parse_password_policy(content):
    """
    Parse password policy values from a Windows SecurityPolicy.inf file.

    Parameters
    ----------
    content : str
        Content of SecurityPolicy.inf.

    Returns
    -------
    dict
        Parsed password policy values.
    """

    password_policy = {}

    supported_settings = [
        "MinimumPasswordAge",
        "MaximumPasswordAge",
        "MinimumPasswordLength",
        "PasswordComplexity",
        "PasswordHistorySize",
        "LockoutBadCount",
        "ResetLockoutCount",
        "LockoutDuration"
    ]

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        key = key.strip()
        value = value.strip()

        if key not in supported_settings:
            continue

        try:
            password_policy[key] = int(value)
        except ValueError:
            password_policy[key] = value

    return password_policy


def load_password_policy(server_folder):
    """
    Locate and parse the Windows SecurityPolicy.inf file.

    Parameters
    ----------
    server_folder : str or Path
        Folder containing the extracted audit files.

    Returns
    -------
    dict
        Parsed password policy.
    """

    server_folder = Path(server_folder)

    policy_file = server_folder / "4-1_SecurityPolicy.inf"

    if not policy_file.exists():
        raise FileNotFoundError(
            f"Password policy file not found: {policy_file}"
        )

    content, _ = read_file(policy_file)

    return parse_password_policy(content)