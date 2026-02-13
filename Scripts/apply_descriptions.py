"""
Bulk Description Apply Tool

Applies descriptions from CSV file and re-runs governance check to verify.
This is a convenience script that combines import + verification in one command.

Usage:
    python Scripts/apply_descriptions.py "path/to/ReportName_missing_descriptions.csv"
    
Workflow:
    1. Imports descriptions from CSV to TMDL files
    2. Re-runs governance check on the project
    3. Shows updated results
"""

import os
import sys
import importlib.util

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREY = '\033[90m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color):
    """Print colored text to console"""
    try:
        print(f"{color}{text}{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{color}{text.encode('ascii', 'ignore').decode()}{Colors.ENDC}")

def apply_descriptions(csv_file_path):
    """Import descriptions and re-run governance check"""
    
    if not os.path.exists(csv_file_path):
        print_colored(f"[ERROR] CSV file not found: {csv_file_path}", Colors.RED)
        return False
    
    csv_file_path = os.path.abspath(csv_file_path)
    project_dir = os.path.dirname(csv_file_path)
    
    print_colored(f"\n{'='*70}", Colors.BLUE)
    print_colored("📝 APPLYING BULK DESCRIPTIONS", Colors.BLUE + Colors.BOLD)
    print_colored(f"{'='*70}", Colors.BLUE)
    
    # Step 1: Import descriptions
    print_colored(f"\n[STEP 1/2] Importing descriptions from CSV...", Colors.BLUE)
    print_colored(f"   File: {os.path.basename(csv_file_path)}", Colors.GREY)
    
    try:
        # Import the import_descriptions module
        spec = importlib.util.spec_from_file_location("import_desc",
            os.path.join(os.path.dirname(__file__), 'import_descriptions.py'))
        import_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(import_module)
        
        # Call import function
        success = import_module.import_descriptions(csv_file_path)
        
        if not success:
            print_colored("\n[ERROR] Failed to import descriptions", Colors.RED)
            return False
            
    except Exception as e:
        print_colored(f"\n[ERROR] Import failed: {e}", Colors.RED)
        return False
    
    # Step 2: Re-run governance check
    print_colored(f"\n[STEP 2/2] Re-running governance check to verify...", Colors.BLUE)
    
    try:
        # Import the governance check module
        spec = importlib.util.spec_from_file_location("governance",
            os.path.join(os.path.dirname(__file__), '..', 'Validators', 'check_governance.py'))
        governance_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(governance_module)
        
        # Run governance check on the project directory
        governance_module.check_governance(project_dir, enable_logging=True)
        
    except Exception as e:
        print_colored(f"\n[WARNING] Could not re-run governance check: {e}", Colors.YELLOW)
        print_colored(f"Run manually: python Validators/check_governance.py \"{project_dir}\"", Colors.YELLOW)
    
    print_colored(f"\n{'='*70}", Colors.GREEN)
    print_colored("✅ DONE! Descriptions applied and verified", Colors.GREEN + Colors.BOLD)
    print_colored(f"{'='*70}\n", Colors.GREEN)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_colored("Usage: python apply_descriptions.py \"path/to/ReportName_missing_descriptions.csv\"", Colors.RED)
        print_colored("Example: python apply_descriptions.py \"ActiveReports/Production/Sales_Report_missing_descriptions.csv\"", Colors.BLUE)
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    apply_descriptions(csv_file_path)
