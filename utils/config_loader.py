import json
from pathlib import Path


def load_json(file_path):

    file_path = Path(file_path)

    with open(file_path, encoding="utf-8") as f:

        return json.load(f)