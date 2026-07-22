import json


def load_workflow(file_path):
    """
    Load workflow configuration.
    """

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)