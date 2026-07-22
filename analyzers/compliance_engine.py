from analyzers.evaluator import evaluate_requirement
from utils.config_loader import load_json


def evaluate(normalized_data, requirement_json):
    """
    Evaluate one requirement.

    Parameters
    ----------
    normalized_data : dict

    requirement_json : str

    Returns
    -------
    dict
    """

    requirement = load_json(requirement_json)

    checks = requirement.get("checks", [])

    if not checks:
        return {
            "requirement": requirement.get("requirement"),
            "status": "NOT_IMPLEMENTED",
            "details": []
        }

    return evaluate_requirement(
        normalized_data,
        requirement
    )