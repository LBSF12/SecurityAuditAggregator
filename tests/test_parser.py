from analyzers.file_reader import read_all_files
from parsers.windows_parser import parse_audit_policy

files = read_all_files("extracted/Server01")

audit = parse_audit_policy(
    files["3-1_AuditPolicy.txt"]["content"]
)

print("=" * 70)

for name, value in audit.items():
    print(f"{name:<50} {value}")