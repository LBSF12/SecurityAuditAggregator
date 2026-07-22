def parse_audit_policy(file_content):
    """
    Parse Windows audit policy.

    Returns:
        {
            audit_name : setting
        }
    """

    audit_settings = {}

    lines = file_content.splitlines()

    possible_settings = [

        "Success and Failure",
        "Success",
        "Failure",
        "No Auditing"

    ]

    for line in lines:

        line = line.strip()

        if not line:
            continue

        for setting in possible_settings:

            if line.endswith(setting):

                audit_name = line[:-len(setting)].strip()

                audit_settings[audit_name] = setting

                break

    return audit_settings