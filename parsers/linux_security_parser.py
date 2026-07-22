import re
from pathlib import Path
from typing import Any


def read_text_file(file_path: Path) -> str:
    """
    Read Linux evidence files using several possible encodings.
    """

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp932",
        "shift_jis",
        "latin-1",
    ]

    for encoding in encodings:
        try:
            return file_path.read_text(
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue
        except OSError:
            return ""

    return file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def get_configured_contents(
    server_folder: str | Path,
    config: dict
) -> dict[str, str]:
    """
    Load every evidence file configured in the workflow.
    """

    folder = Path(server_folder)

    results = {}

    for file_name in config.get("files", []):

        file_path = folder / file_name

        if not file_path.exists():
            results[file_name] = ""
            continue

        results[file_name] = read_text_file(
            file_path
        )

    return results


def extract_integer(
    content: str,
    setting_name: str
) -> int | None:
    """
    Extract values such as:

        minlen = 16
        rotate 4
        num_logs = 52
    """

    pattern = rf"\b{re.escape(setting_name)}\s*(?:=|\s)\s*(\d+)"

    match = re.search(
        pattern,
        content,
        re.IGNORECASE
    )

    if not match:
        return None

    return int(match.group(1))


def extract_signed_integer(
    content: str,
    setting_name: str
) -> int | None:
    """
    Extract positive or negative integers such as:

        dcredit = -1
    """

    pattern = rf"\b{re.escape(setting_name)}\s*=\s*(-?\d+)"

    match = re.search(
        pattern,
        content,
        re.IGNORECASE
    )

    if not match:
        return None

    return int(match.group(1))


def load_linux_retention(
    server_folder: str | Path,
    config: dict
) -> dict[str, Any]:
    """
    Parse auditd and logrotate retention settings
    for Requirement 3.1.
    """

    files = get_configured_contents(
        server_folder,
        config
    )

    combined_content = "\n".join(
        files.values()
    )

    max_log_file = extract_integer(
        combined_content,
        "max_log_file"
    )

    num_logs = extract_integer(
        combined_content,
        "num_logs"
    )

    rotate_count = extract_integer(
        combined_content,
        "rotate"
    )

    weekly = bool(
        re.search(
            r"^\s*weekly\s*$",
            combined_content,
            re.IGNORECASE | re.MULTILINE
        )
    )

    monthly = bool(
        re.search(
            r"^\s*monthly\s*$",
            combined_content,
            re.IGNORECASE | re.MULTILINE
        )
    )

    max_log_file_action_rotate = bool(
        re.search(
            r"max_log_file_action\s*=\s*ROTATE",
            combined_content,
            re.IGNORECASE
        )
    )

    if weekly and rotate_count is not None:
        retention_weeks = rotate_count

    elif monthly and rotate_count is not None:
        retention_weeks = rotate_count * 4

    else:
        retention_weeks = None

    return {
        "AUDITD_MAX_LOG_FILE": max_log_file,
        "AUDITD_NUM_LOGS": num_logs,
        "AUDITD_ROTATION_ENABLED": (
            max_log_file_action_rotate
        ),
        "LOGROTATE_RETENTION_WEEKS": retention_weeks,
    }


def load_linux_password_policy(
    server_folder: str | Path,
    config: dict
) -> dict[str, Any]:
    """
    Parse PAM and pwquality password-policy evidence.
    """

    files = get_configured_contents(
        server_folder,
        config
    )

    combined_content = "\n".join(
        files.values()
    )

    pam_pwquality_enabled = bool(
        re.search(
            r"pam_pwquality\.so",
            combined_content,
            re.IGNORECASE
        )
    )

    badwords_match = re.search(
        r"^\s*badwords\s*=\s*(.+)$",
        combined_content,
        re.IGNORECASE | re.MULTILINE
    )

    badwords = []

    if badwords_match:
        badwords = badwords_match.group(1).split()

    return {
        "PAM_PWQUALITY_ENABLED": pam_pwquality_enabled,
        "MINIMUM_PASSWORD_LENGTH": extract_integer(
            combined_content,
            "minlen"
        ),
        "DIGIT_CREDIT": extract_signed_integer(
            combined_content,
            "dcredit"
        ),
        "UPPERCASE_CREDIT": extract_signed_integer(
            combined_content,
            "ucredit"
        ),
        "LOWERCASE_CREDIT": extract_signed_integer(
            combined_content,
            "lcredit"
        ),
        "OTHER_CHARACTER_CREDIT": extract_signed_integer(
            combined_content,
            "ocredit"
        ),
        "PASSWORD_HISTORY": extract_integer(
            combined_content,
            "remember"
        ),
        "BADWORDS_CONFIGURED": len(badwords) > 0,
        "BADWORDS_COUNT": len(badwords),
    }


def load_linux_privileged_audit(
    server_folder: str | Path,
    config: dict
) -> dict[str, Any]:
    """
    Parse Linux privileged-command audit rules.
    """

    files = get_configured_contents(
        server_folder,
        config
    )

    combined_content = "\n".join(
        files.values()
    )

    su_audit_enabled = bool(
        re.search(
            r"exe=/usr/bin/su\b",
            combined_content
        )
    )

    sudo_audit_enabled = bool(
        re.search(
            r"exe=/usr/bin/sudo\b",
            combined_content
        )
    )

    privilege_key_configured = bool(
        re.search(
            r"(?:key=|-k\s+)priv_esc\b",
            combined_content
        )
    )

    return {
        "SU_AUDIT_ENABLED": su_audit_enabled,
        "SUDO_AUDIT_ENABLED": sudo_audit_enabled,
        "PRIVILEGE_AUDIT_KEY_CONFIGURED": (
            privilege_key_configured
        ),
    }


def load_linux_account_audit(
    server_folder: str | Path,
    config: dict
) -> dict[str, Any]:
    """
    Parse account-management audit rules and sample logs.
    """

    files = get_configured_contents(
        server_folder,
        config
    )

    combined_content = "\n".join(
        files.values()
    )

    useradd_rule = bool(
        re.search(
            r"exe=/usr/sbin/useradd\b",
            combined_content
        )
    )

    usermod_rule = bool(
        re.search(
            r"exe=/usr/sbin/usermod\b",
            combined_content
        )
    )

    userdel_rule = bool(
        re.search(
            r"exe=/usr/sbin/userdel\b",
            combined_content
        )
    )

    sample_log_exists = bool(
        re.search(
            r"\b(?:useradd|usermod|userdel)\b",
            combined_content,
            re.IGNORECASE
        )
    )

    return {
        "USERADD_AUDIT_ENABLED": useradd_rule,
        "USERMOD_AUDIT_ENABLED": usermod_rule,
        "USERDEL_AUDIT_ENABLED": userdel_rule,
        "ACCOUNT_LOG_SAMPLE_EXISTS": sample_log_exists,
    }


def load_linux_auth_log_retention(
    server_folder: str | Path,
    config: dict
) -> dict[str, Any]:
    """
    Parse authentication-log retention settings
    for Requirement 9.2.
    """

    files = get_configured_contents(
        server_folder,
        config
    )

    combined_content = "\n".join(
        files.values()
    )

    auth_log_configured = bool(
        re.search(
            r"/var/log/auth\.log",
            combined_content,
            re.IGNORECASE
        )
    )

    rotate_count = extract_integer(
        combined_content,
        "rotate"
    )

    weekly = bool(
        re.search(
            r"^\s*weekly\s*$",
            combined_content,
            re.IGNORECASE | re.MULTILINE
        )
    )

    monthly = bool(
        re.search(
            r"^\s*monthly\s*$",
            combined_content,
            re.IGNORECASE | re.MULTILINE
        )
    )

    if weekly and rotate_count is not None:
        retention_weeks = rotate_count

    elif monthly and rotate_count is not None:
        retention_weeks = rotate_count * 4

    else:
        retention_weeks = None

    return {
        "AUTH_LOG_CONFIGURED": auth_log_configured,
        "AUTH_LOG_RETENTION_WEEKS": retention_weeks,
    }