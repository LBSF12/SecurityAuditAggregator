from analyzers.file_reader import read_all_files
from parsers.windows_parser import parse_audit_policy
from analyzers.mapper import normalize_audit_policy
from analyzers.evaluator import evaluate_requirement
from utils.config_loader import load_json

files = read_all_files("extracted/Server01")

parsed = parse_audit_policy(
    files["3-1_AuditPolicy.txt"]["content"]
)

normalized = normalize_audit_policy(parsed)

requirement = load_json(
    "config/requirements/3_1.json"
)

result = evaluate_requirement(
    normalized,
    requirement
)

print("=" * 70)
print(f"Requirement : {result['requirement']}")
print(f"Description : {result['description']}")
print(f"Overall     : {result['status']}")
print("=" * 70)

for detail in result["details"]:
    print(
        f"{detail['setting']:<35}"
        f"{detail['actual']:<22}"
        f"{detail['result']}"
    )