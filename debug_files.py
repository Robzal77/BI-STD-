import os

# Check what the export script found
tables_dir = r"c:\Users\robza\OneDrive\BI_Ops_Factory\BI-STD\ActiveReports\Production\CEA Reporting ADB.SemanticModel\definition\tables"

print("Files in tables directory:")
for file in sorted(os.listdir(tables_dir)):
    if file.endswith('.tmdl'):
        print(f"  - {file}")

# Check if Operations Extract.tmdl exists
target_file = "Operations Extract.tmdl"
full_path = os.path.join(tables_dir, target_file)
print(f"\nDoes '{target_file}' exist? {os.path.exists(full_path)}")

# Check for similar names
print("\nSearching for files containing 'Operation':")
for file in os.listdir(tables_dir):
    if 'operation' in file.lower():
        print(f"  - {file}")
