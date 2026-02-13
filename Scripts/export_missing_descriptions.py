"""
Bulk Measure Description Exporter

Scans a Power BI project and exports all measures without descriptions to a CSV file.
Developers can fill in the descriptions in Excel and then use the importer to update the TMDL files.

Usage:
    python Scripts/export_missing_descriptions.py "ActiveReports/LocalTest/MyReport"
    
Output:
    Creates: MyReport_missing_descriptions.csv
    
CSV Format:
    table_file, measure_name, current_description, new_description
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

def extract_measures_from_tmdl(file_path):
    """Extract all measures and their descriptions from a TMDL file"""
    measures = []
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # Find all measure blocks
    # Match: measure 'Name' = ... (until next measure/column/table or end)
    # Using negative lookahead to stop at next top-level element (not indented)
    measure_pattern = r"measure\s+'([^']+)'\s*=(.*?)(?=\n(?:measure|column|table|partition)\s|$)"
    matches = re.finditer(measure_pattern, content, re.DOTALL | re.MULTILINE)
    
    for match in matches:
        measure_name = match.group(1)
        measure_block = match.group(2)
        
        # Check if description exists
        desc_match = re.search(r'description\s*=\s*"([^"]*)"', measure_block)
        description = desc_match.group(1) if desc_match else ""
        
        measures.append({
            'name': measure_name,
            'description': description,
            'has_description': bool(description.strip())
        })
    
    return measures

def export_missing_descriptions(project_path):
    """Export all measures without descriptions to CSV"""
    
    # Normalize path
    project_path = os.path.abspath(project_path)
    
    # Find the .SemanticModel folder
    if project_path.endswith('.pbip'):
        project_path = project_path[:-5]  # Remove .pbip extension
    
    # Look for SemanticModel folder matching the project name
    project_name = os.path.basename(project_path)
    expected_semantic_model = f"{project_name}.SemanticModel"
    semantic_model_dir = os.path.join(os.path.dirname(project_path), expected_semantic_model)
    
    if not os.path.exists(semantic_model_dir):
        print_colored(f"[ERROR] Could not find {expected_semantic_model} in {os.path.dirname(project_path)}", Colors.RED)
        return None
    
    tables_dir = os.path.join(semantic_model_dir, 'definition', 'tables')
    
    if not os.path.exists(tables_dir):
        print_colored(f"[ERROR] Tables directory not found: {tables_dir}", Colors.RED)
        return None
    
    print_colored(f"\n[SCAN] Scanning for measures without descriptions...", Colors.BLUE + Colors.BOLD)
    print_colored(f"   Project: {os.path.basename(project_path)}", Colors.BLUE)
    
    # Collect all measures
    all_measures = []
    missing_count = 0
    
    for table_file in os.listdir(tables_dir):
        if table_file.endswith('.tmdl'):
            file_path = os.path.join(tables_dir, table_file)
            measures = extract_measures_from_tmdl(file_path)
            
            for measure in measures:
                if not measure['has_description']:
                    all_measures.append({
                        'table_file': table_file,
                        'measure_name': measure['name'],
                        'current_description': measure['description'],
                        'new_description': ''  # Empty for user to fill
                    })
                    missing_count += 1
    
    if missing_count == 0:
        print_colored(f"\n[SUCCESS] Great! All measures already have descriptions!", Colors.GREEN + Colors.BOLD)
        return None
    
    # Generate output CSV filename
    report_name = os.path.basename(project_path)
    output_file = os.path.join(os.path.dirname(project_path), f"{report_name}_missing_descriptions.csv")
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['table_file', 'measure_name', 'current_description', 'new_description']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(all_measures)
    
    print_colored(f"\n[SUCCESS] Exported {missing_count} measures without descriptions", Colors.GREEN + Colors.BOLD)
    print_colored(f"   File: {output_file}", Colors.GREEN)
    print_colored(f"\n[NEXT STEPS]", Colors.YELLOW + Colors.BOLD)
    print_colored(f"   1. Open the CSV file in Excel", Colors.YELLOW)
    print_colored(f"   2. Fill in the 'new_description' column", Colors.YELLOW)
    print_colored(f"   3. Save the file", Colors.YELLOW)
    print_colored(f"   4. Run: python Scripts/import_descriptions.py \"{output_file}\"", Colors.YELLOW)
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_colored("Usage: python export_missing_descriptions.py \"path/to/report\"", Colors.RED)
        print_colored("Example: python export_missing_descriptions.py \"ActiveReports/LocalTest/Sales_Report\"", Colors.BLUE)
        sys.exit(1)
    
    project_path = sys.argv[1]
    export_missing_descriptions(project_path)
