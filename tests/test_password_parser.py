from parsers.password_policy_parser import load_password_policy

server = "extracted/Server01"

result = load_password_policy(server)

for file, content in result.items():

    print("=" * 70)

    print(file)

    print("=" * 70)

    print(content[:500])

    print()