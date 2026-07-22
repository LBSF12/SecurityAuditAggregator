from analyzers.file_reader import read_all_files
from parsers.windows_parser import parse_audit_policy
from analyzers.mapper import normalize

files = read_all_files("extracted/Server01")

parsed = parse_audit_policy(
    files["3-1_AuditPolicy.txt"]["content"]
)

normalized = normalize(
    parsed,
    "config/mappings/audit_policy.json"
)

print("=" * 60)

for key, value in normalized.items():
    print(f"{key:<35}{value}")