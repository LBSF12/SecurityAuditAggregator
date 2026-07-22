from parsers.password_policy_parser import load_password_policy


password_policy = load_password_policy(
    "extracted/Server01"
)

print("=" * 60)
print("PASSWORD POLICY")
print("=" * 60)

for setting, value in password_policy.items():
    print(f"{setting}: {value}")