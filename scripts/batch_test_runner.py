"""
Batch Test Runner for Power BI Reports

This script runs governance checks on all PBIP files in the BatchTesting folder,
generates a comprehensive summary report,  and logs results to a separate CSV file.

Usage:
    python scripts/batch_test_runner.py
"""

import os
import sys
import csv
import re
from datetime import datetime

BATCH_TEST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'BatchTesting')
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
BATCH_LOG_FILE = os.path.join(LOGS_DIR, 'batch_run_results.csv')

# Color codes for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_colored(text, color=''):
    """Print colored text to console"""
    try:
        os.system('')  # Enable ANSI support in Windows 10+
        print(f"{color}{text}{Colors.RESET}")
    except:
        print(text)

def check_auto_datetime(model_path):
    """Check if autoDateTime is enabled in model.tmdl"""
    try:
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for autoDateQTable property
            match = re.search(r'autoDateQTable\s*=\s*\{([^}]*)\}', content, re.DOTALL)
            if match:
                # If property exists and not explicitly empty, it's enabled
                table_content = match.group(1).strip()
                return bool(table_content)
    except Exception:
        pass
    return False

def check_bidirectional_relationships(definition_dir):
    """Check for bidirectional relationships in relationships.tmdl"""
    bidirectional_rels = []
    relationships_file = os.path.join(definition_dir, 'relationships.tmdl')
    
    if os.path.exists(relationships_file):
        try:
            with open(relationships_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for crossFilteringBehavior = bothDirections
                matches = re.finditer(r'relationship\s+([^\{]+)\s*\{([^\}]*crossFilteringBehavior\s*=\s*bothDirections[^\}]*)\}', 
                                     content, re.DOTALL)
                for match in matches:
                    rel_name = match.group(1).strip()
                    bidirectional_rels.append(rel_name)
        except Exception:
            pass
    
    return bidirectional_rels

def check_measure_descriptions(definition_dir):
    """Check for measures missing descriptions"""
    missing_descriptions = []
    
    # Look for measures in tables directory
    tables_dir = os.path.join(definition_dir, 'tables')
    if not os.path.exists(tables_dir):
        return missing_descriptions
    
    for table_file in os.listdir(tables_dir):
        if table_file.endswith('.tmdl'):
            table_path = os.path.join(tables_dir, table_file)
            try:
                with open(table_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Find measures
                    measure_blocks = re.finditer(r'measure\s+([^\s=]+)\s*=', content)
                    for measure_match in measure_blocks:
                        measure_name = measure_match.group(1).strip('\'\"')
                        # Check if this measure has a description
                        measure_start = measure_match.start()
                        # Look ahead for description property within reasonable distance
                        snippet = content[measure_start:measure_start+500]
                        if not re.search(r'description\s*[:=]\s*["\']', snippet):
                            table_name = table_file.replace('.tmdl', '')
                            missing_descriptions.append(f"{table_name}.{measure_name}")
            except Exception:
                pass
    
    return missing_descriptions

def scan_batch_folder():
    """Scan BatchTesting folder for all PBIP files"""
    
    if not os.path.exists(BATCH_TEST_DIR):
        return []
    
    reports = []
    
    for item in os.listdir(BATCH_TEST_DIR):
        item_path = os.path.join(BATCH_TEST_DIR, item)
        
        if os.path.isdir(item_path) and item.endswith('.SemanticModel'):
            # Find model.tmdl file
            definition_dir = os.path.join(item_path, 'definition')
            model_file = os.path.join(definition_dir, 'model.tmdl')
            
            if os.path.exists(model_file):
                report_name = item.replace('.SemanticModel', '')
                reports.append({
                    'name': report_name,
                    'model_path': model_file,
                    'definition_dir': definition_dir
                })
    
    return reports

def run_governance_check(report):
    """Run governance checks on a single report"""
    
    result = {
        'report_name': report['name'],
        'status': 'PASS',
        'auto_datetime': 'PASS',
        'bidirectional_count': 0,
        'missing_descriptions': 0,
        'failure_reasons': []
    }
    
    try:
        # Check 1: Auto Date/Time
        auto_dt_enabled = check_auto_datetime(report['model_path'])
        if auto_dt_enabled:
            result['auto_datetime'] = 'FAIL'
            result['status'] = 'FAIL'
            result['failure_reasons'].append('Auto Date/Time is ENABLED (should be disabled)')
        
        # Check 2: Bidirectional Relationships
        bidir_rels = check_bidirectional_relationships(report['definition_dir'])
        result['bidirectional_count'] = len(bidir_rels)
        if bidir_rels:
            result['status'] = 'FAIL'
            result['failure_reasons'].append(f'{len(bidir_rels)} Bidirectional relationship(s)')
        
        # Check 3: Measure Descriptions
        missing_descs = check_measure_descriptions(report['definition_dir'])
        result['missing_descriptions'] = len(missing_descs)
        if missing_descs:
            result['status'] = 'FAIL'
            result['failure_reasons'].append(f'{len(missing_descs)} Measure(s) without descriptions')
    
    except Exception as e:
        result['status'] = 'ERROR'
        result['failure_reasons'].append(f'Error: {str(e)}')
    
    return result

def save_batch_results(batch_id, results):
    """Save batch test results to CSV"""
    
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(BATCH_LOG_FILE)
    
    with open(BATCH_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        fieldnames = [
            'batch_id', 'timestamp', 'report_name', 'status',
            'auto_datetime', 'bidirectional_count', 'missing_descriptions',
            'failure_reasons'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.headerheader()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for result in results:
            writer.writerow({
                'batch_id': batch_id,
                'timestamp': timestamp,
                'report_name': result['report_name'],
                'status': result['status'],
                'auto_datetime': result['auto_datetime'],
                'bidirectional_count': result['bidirectional_count'],
                'missing_descriptions': result['missing_descriptions'],
                'failure_reasons': '; '.join(result['failure_reasons'])
            })

def print_summary_report(batch_id, results):
    """Print comprehensive summary report to console"""
    
    total = len(results)
    passed = [r for r in results if r['status'] == 'PASS']
    failed = [r for r in results if r['status'] == 'FAIL']
    errors = [r for r in results if r['status'] == 'ERROR']
    
    pass_count = len(passed)
    fail_count = len(failed)
    error_count = len(errors)
    pass_rate = (pass_count / total * 100) if total > 0 else 0
    
    print()
    print("=" * 70)
    print_colored("  BATCH TEST SUMMARY", Colors.BOLD + Colors.BLUE)
    print("=" * 70)
    print()
    print(f"Batch ID: {batch_id}")
    print(f"Test Folder: {BATCH_TEST_DIR}")
    print()
    print(f"Total Reports Tested: {total}")
    print_colored(f"[PASS] Passed: {pass_count} ({pass_rate:.0f}%)", Colors.GREEN)
    
    if fail_count > 0:
        print_colored(f"[FAIL] Failed: {fail_count} ({fail_count/total*100:.0f}%)", Colors.RED)
    
    if error_count > 0:
        print_colored(f"[ERROR] Errors: {error_count}", Colors.YELLOW)
    
    # Passed Reports
    if passed:
        print()
        print("-" * 70)
        print_colored("PASSED REPORTS ({})".format(pass_count), Colors.GREEN + Colors.BOLD)
        print("-" * 70)
        for report in passed:
            print_colored(f"  [PASS] {report['report_name']}", Colors.GREEN)
    
    # Failed Reports with Action Items
    if failed:
        print()
        print("-" * 70)
        print_colored("FAILED REPORTS ({})".format(fail_count), Colors.RED + Colors.BOLD)
        print("-" * 70)
        
        for report in failed:
            print_colored(f"\n  [FAIL] {report['report_name']}", Colors.RED + Colors.BOLD)
            print()
            
            # Show failures
            for reason in report['failure_reasons']:
                print(f"         {reason}")
            
            print()
            print_colored("         ACTION ITEMS FOR DEVELOPER:", Colors.YELLOW + Colors.BOLD)
            
            # Generate specific action items based on failures
            action_count = 0
            
            # Action for Auto Date/Time
            if report['auto_datetime'] == 'FAIL':
                action_count += 1
                print()
                print_colored(f"         [{action_count}] Fix Auto Date/Time Setting", Colors.YELLOW)
                print(f"             File: {report['name']}.SemanticModel/definition/model.tmdl")
                print()
                print("             Steps to fix:")
                print("              1. Open this report in Power BI Desktop")
                print("              2. Go to File > Options and settings > Options")
                print("              3. Under 'Current File' section, click 'Data Load'")
                print("              4. UNCHECK 'Auto date/time'")
                print("              5. Click OK and save the report")
            
            # Action for Bidirectional Relationships
            if report['bidirectional_count'] > 0:
                action_count += 1
                print()
                print_colored(f"         [{action_count}] Change Bidirectional Relationships to Single-Direction", Colors.YELLOW)
                print(f"             File: {report['name']}.SemanticModel/definition/relationships.tmdl")
                print(f"             Count: {report['bidirectional_count']} relationship(s) to fix")
                print()
                print("             Steps to fix:")
                print("              1. Open this report in Power BI Desktop")
                print("              2. Switch to Model view (left sidebar)")
                print("              3. Click on each relationship line in the diagram")
                print("              4. In the Properties pane (right side):")
                print("                 - Find 'Cross filter direction'")
                print("                 - Change from 'Both' to 'Single'")
                print(f"              5. Repeat for all {report['bidirectional_count']} relationships")
                print("              6. Save the report")
            
            # Action for Missing Descriptions
            if report['missing_descriptions'] > 0:
                action_count += 1
                print()
                print_colored(f"         [{action_count}] Add Descriptions to Measures", Colors.YELLOW)
                print(f"             Files: {report['name']}.SemanticModel/definition/tables/*.tmdl")
                print(f"             Count: {report['missing_descriptions']} measure(s) need descriptions")
                print()
                print("             Steps to fix:")
                print("              1. Open this report in Power BI Desktop")
                print("              2. Switch to Data view or Model view")
                print("              3. In the Fields pane (right side), locate each measure")
                print("              4. Right-click the measure > Properties")
                print("              5. Add a meaningful 'Description' explaining what it calculates")
                print(f"              6. Repeat for all {report['missing_descriptions']} measures")
                print("              7. Save the report")
            
            print()
            print("-" * 70)
    
    # Error Reports
    if errors:
        print()
        print("-" * 70)
        print_colored("ERROR REPORTS ({})".format(error_count), Colors.YELLOW + Colors.BOLD)
        print("-" * 70)
        
        for report in errors:
            print_colored(f"  [ERROR] {report['report_name']}", Colors.YELLOW + Colors.BOLD)
            for reason in report['failure_reasons']:
                print(f"          - {reason}")
            print()
    
    print("=" * 70)
    print(f"Detailed results saved to: {BATCH_LOG_FILE}")
    print("=" * 70)
    print()

def run_batch_test():
    """Main batch test execution"""
    
    print()
    print("=" * 70)
    print_colored("  POWER BI BATCH GOVERNANCE TEST", Colors.BOLD + Colors.BLUE)
    print("=" * 70)
    print()
    
    # Generate batch ID
    batch_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Scan for reports
    print_colored(f"Scanning: {BATCH_TEST_DIR}", Colors.GREY)
    reports = scan_batch_folder()
    
    if not reports:
        print_colored("\n[!] No PBIP files found in BatchTesting folder", Colors.YELLOW)
        print_colored("\nTo use batch testing:", Colors.GREY)
        print_colored("  1. Copy .pbip folders to 'BatchTesting' folder", Colors.GREY)
        print_colored("  2. Each report should have a .SemanticModel folder", Colors.GREY)
        print_colored("  3. Run this script again\n", Colors.GREY)
        return
    
    print(f"Found {len(reports)} report(s) to test\n")
    
    # Run tests
    results = []
    
    for i, report in enumerate(reports, 1):
        print(f"[{i}/{len(reports)}] Testing: {report['name']}", end=' ... ')
        
        result = run_governance_check(report)
        results.append(result)
        
        if result['status'] == 'PASS':
            print_colored("[PASS]", Colors.GREEN)
        elif result['status'] == 'FAIL':
            print_colored("[FAIL]", Colors.RED)
        else:
            print_colored("[ERROR]", Colors.YELLOW)
    
    # Save results
    save_batch_results(batch_id, results)
    
    # Print summary
    print_summary_report(batch_id, results)

if __name__ == "__main__":
    run_batch_test()
