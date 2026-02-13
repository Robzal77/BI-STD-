import re

content = open('ActiveReports/Production/CEA Reporting ADB.SemanticModel/definition/tables/AGR History.tmdl', 'r', encoding='utf-8-sig').read()
pattern = r"measure\s+'([^']+)'\s*=([^}]+?)(?=\n\nmeasure|\n\ncolumn|\n\ntable|\Z)"
matches = list(re.finditer(pattern, content, re.DOTALL | re.MULTILINE))
print(f'Found {len(matches)} measures')

# Print first few matches
for i, match in enumerate(matches[:3]):
    print(f"\nMeasure {i+1}: {match.group(1)}")
    desc_match = re.search(r'description\s*=\s*"([^"]*)"', match.group(2))
    if desc_match:
        print(f"  Description: {desc_match.group(1)}")
    else:
        print(f"  Description: NONE")
