"""
Bulk Measure Description Importer

Reads a CSV file with measure descriptions and updates the TMDL files automatically.

Usage:
    python Scripts/import_descriptions.py "path/to/ReportName_missing_descriptions.csv"
    
CSV Format Expected:
    table_file, measure_name, current_description, new_description
    
The script will:
1. Read the CSV file
2. For each row, find the measure in the TMDL file
3. Add/update the description
4. Save the updated TMDL file
"""

import os
import sys
import csv
import re
from datetime import datetime

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color):
    """Print colored text to console"""
    try:
        print(f"{color}{text}{Colors.ENDC}")
    except UnicodeEncodeError:
        # Fallback for Windows console without UTF-8 support
        print(f"{color}{text.encode('ascii', 'ignore').decode()}{Colors.ENDC}")

def update_measure_description(file_path, measure_name, new_description):
    """Update or add description to a measure in a TMDL file"""
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # Find the measure block
    # Pattern: measure 'name' = ... (everything until next measure/column/table or end)
    measure_pattern = rf"(measure\s+'{re.escape(measure_name)}'\s*=\s*[^\n]+(?:\n(?:    |\t)[^\n]+)*)"
    
    match = re.search(measure_pattern, content, re.MULTILINE)
    
    if not match:
        print_colored(f"    ⚠️  Warning: Could not find measure '{measure_name}' in {os.path.basename(file_path)}", Colors.YELLOW)
        return False
    
    measure_block = match.group(1)
    
    # Check if description already exists
    if 'description' in measure_block:
        # Replace existing description
        updated_block = re.sub(
            r'description\s*=\s*"[^"]*"',
            f'description = "{new_description}"',
            measure_block
        )
    else:
        # Add description after the measure definition line
        lines = measure_block.split('\n')
        # Insert description after first line
        lines.insert(1, f'    description = "{new_description}"')
        updated_block = '\n'.join(lines)
    
    # Replace in content
    updated_content = content.replace(measure_block, updated_block)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8-sig') as f:
        f.write(updated_content)
    
    return True

def import_descriptions(csv_file_path):
    """Import descriptions from CSV and update TMDL files"""
    
    if not os.path.exists(csv_file_path):
        print_colored(f"[ERROR] CSV file not found: {csv_file_path}", Colors.RED)
        return False
    
    # Get the project directory (CSV is in same folder as report)
    project_dir = os.path.dirname(csv_file_path)
    
    # Find the .SemanticModel folder
    semantic_model_dir = None
    for item in os.listdir(project_dir):
        if item.endswith('.SemanticModel'):
            semantic_model_dir = os.path.join(project_dir, item)
            break
    
    if not semantic_model_dir:
        print_colored(f"[ERROR] Could not find .SemanticModel folder in {project_dir}", Colors.RED)
        return False
    
    tables_dir = os.path.join(semantic_model_dir, 'definition', 'tables')
    
    print_colored(f"\n[IMPORT] Importing measure descriptions...", Colors.BLUE + Colors.BOLD)
    print_colored(f"   CSV File: {os.path.basename(csv_file_path)}", Colors.BLUE)
    
    # Read CSV
    updates = []
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only process if new_description is provided
            if row['new_description'].strip():
                updates.append(row)
    
    if not updates:
        print_colored(f"\n[WARNING] No descriptions to import (new_description column is empty)", Colors.YELLOW)
        return False
    
    print_colored(f"\n   Found {len(updates)} descriptions to import", Colors.BLUE)
    
    # Update each measure
    success_count = 0
    for row in updates:
        table_file = row['table_file']
        measure_name = row['measure_name']
        new_description = row['new_description']
        
        file_path = os.path.join(tables_dir, table_file)
        
        if not os.path.exists(file_path):
            print_colored(f"    [WARNING] File not found: {table_file}", Colors.YELLOW)
            continue
        
        print(f"    [UPDATE] {table_file}: '{measure_name}'")
        
        if update_measure_description(file_path, measure_name, new_description):
            success_count += 1
    
    print_colored(f"\n[SUCCESS] Successfully updated {success_count}/{len(updates)} measure descriptions!", Colors.GREEN + Colors.BOLD)
    print_colored(f"\n[NEXT STEP]", Colors.YELLOW + Colors.BOLD)
    print_colored(f"   Run governance check to verify: python Validators/check_governance.py \"{project_dir}\"", Colors.YELLOW)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_colored("Usage: python import_descriptions.py \"path/to/ReportName_missing_descriptions.csv\"", Colors.RED)
        print_colored("Example: python import_descriptions.py \"ActiveReports/LocalTest/Sales_Report_missing_descriptions.csv\"", Colors.BLUE)
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    import_descriptions(csv_file_path)
