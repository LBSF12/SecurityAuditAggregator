from analyzers.evaluator import evaluate_requirement
from utils.config_loader import load_json

parsed = {

    "LOGON": "Success and Failure",

    "USER_ACCOUNT_MANAGEMENT": "Success and Failure",

    "AUDIT_POLICY_CHANGE": "Success",

    "SENSITIVE_PRIVILEGE_USE": "No Auditing"

}

requirement = load_json(
    "config/requirements/3_1.json"
)

result = evaluate_requirement(
    parsed,
    requirement
)

print(result)