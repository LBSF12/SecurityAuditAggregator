from analyzers.file_reader import read_all_files

files = read_all_files("extracted/Server01")

print("=" * 60)
print(f"Found {len(files)} files")
print("=" * 60)

for filename, info in files.items():
    print(f"{filename:<40} Encoding: {info['encoding']}")