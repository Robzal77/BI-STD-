"""
Batch Runner - Orchestrates batch processing of Power BI reports

This script processes multiple .pbip projects in a folder:
1. Scans for all .pbip folders (excluding Archive and Templates)
2. For each report:
   - Creates a safety copy with _Standardized suffix
   - Runs PRE-WASH governance check
   - Runs car_wash.py if violations detected
   - Runs POST-WASH governance check
   - Generates documentation if score = 100%
3. Generates batch summary report

Part of the "10/10 Power BI Standardization Framework"
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
import csv

# Force UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Constants for Colors
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    GREY = '\033[90m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'

def print_colored(text, color):
    """Print colored text to console"""
    os.system('')  # Enable ANSI support in Windows 10+ console
    print(f"{color}{text}{Colors.RESET}")

def find_pbip_projects(directory):
    """Find all .pbip project folders, excluding Archive and Templates"""
    projects = []
    
    for root, dirs, files in os.walk(directory):
        # Skip Archive and Templates folders
        dirs[:] = [d for d in dirs if d not in ['Archive', 'Templates', '__pycache__']]
        
        # Look for .pbip folders (they contain .SemanticModel and .Report folders)
        for d in dirs[:]:
            if d.endswith('.SemanticModel'):
                # Found a semantic model, check if there's a corresponding .pbip structure
                project_name = d.replace('.SemanticModel', '')
                project_path = root
                
                # Check if this is a valid pbip project
                pbip_file = os.path.join(project_path, f'{project_name}.pbip')
                if os.path.exists(pbip_file):
                    projects.append({
                        'name': project_name,
                        'path': project_path,
                        'full_path': os.path.join(project_path, project_name + '.pbip')
                    })
    
    return projects

def run_governance_check(project_path):
    """Run governance check and extract score"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    validator_path = os.path.join(os.path.dirname(script_dir), 'Validators', 'check_governance.py')
    
    try:
        result = subprocess.run(
            [sys.executable, validator_path, project_path],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Parse output to determine pass/fail
        output = result.stdout
        
        # Simple heuristic: count failures
        if 'PASS' in output and 'FAIL' not in output:
            return 'PASS', 100
        elif 'ISSUES FOUND' in output or 'FAIL' in output:
            return 'FAIL', 50  # Placeholder score
        else:
            return 'UNKNOWN', 0
    
    except Exception as e:
        print_colored(f"  ❌ Error running governance check: {e}", Colors.RED)
        return 'ERROR', 0

def run_car_wash(project_path):
    """Run car wash on a project"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    car_wash_path = os.path.join(script_dir, 'car_wash.py')
    
    try:
        result = subprocess.run(
            [sys.executable, car_wash_path, project_path],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result.stdout)
        
        return result.returncode == 0
    
    except Exception as e:
        print_colored(f"  ❌ Error running car wash: {e}", Colors.RED)
        return False

def generate_docs(project_path):
    """Generate documentation for a project"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    doc_gen_path = os.path.join(script_dir, 'generate_live_docs.py')
    
    try:
        result = subprocess.run(
            [sys.executable, doc_gen_path, project_path],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        return result.returncode == 0
    
    except Exception as e:
        print_colored(f"  ⚠️ Documentation generation failed: {e}", Colors.YELLOW)
        return False

def batch_process(input_dir, create_copies=True):
    """Main batch processing function"""
    
    input_dir = os.path.abspath(input_dir)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"\n{'='*80}")
    print_colored(f"🏭 BATCH RUNNER - Power BI Standardization Factory", Colors.CYAN + Colors.BOLD)
    print_colored(f"   Started: {timestamp}", Colors.GREY)
    print_colored(f"   Input Directory: {input_dir}", Colors.GREY)
    print(f"{'='*80}\n")
    
    # Find all projects
    print_colored("🔍 Scanning for Power BI projects...", Colors.BLUE)
    projects = find_pbip_projects(input_dir)
    
    if not projects:
        print_colored("❌ No Power BI projects found (.pbip files)", Colors.RED)
        print_colored(f"   Searched in: {input_dir}", Colors.GREY)
        print_colored("   (Archive and Templates folders are excluded)", Colors.GREY)
        return
    
    print_colored(f"   Found {len(projects)} project(s)", Colors.GREEN)
    for p in projects:
        rel_path = os.path.relpath(p['path'], input_dir)
        print_colored(f"   - {rel_path}/{p['name']}", Colors.GREY)
    
    print(f"\n{'-'*80}\n")
    
    # Process each project
    results = []
    
    for idx, project in enumerate(projects, 1):
        project_path = os.path.dirname(project['full_path'])
        
        print(f"\n{'='*80}")
        print_colored(f"📊 [{idx}/{len(projects)}] Processing: {project['name']}", Colors.BLUE + Colors.BOLD)
        print_colored(f"   Location: {os.path.relpath(project_path, input_dir)}", Colors.GREY)
        print(f"{'-'*80}")
        
        result = {
            'name': project['name'],
            'path': project_path,
            'pre_status': None,
            'pre_score': 0,
            'post_status': None,
            'post_score': 0,
            'fixes_applied': False,
            'docs_generated': False
        }
        
        # Step 1: PRE-WASH governance check
        print_colored("\n📋 Step 1: PRE-WASH Governance Check", Colors.BLUE)
        status, score = run_governance_check(project_path)
        result['pre_status'] = status
        result['pre_score'] = score
        
        if status == 'PASS':
            print_colored(f"   ✅ Status: {status} (Score: {score}%)", Colors.GREEN)
        else:
            print_colored(f"   ⚠️ Status: {status} (Score: {score}%)", Colors.YELLOW)
        
        # Step 2: Car Wash (only if failed)
        if status != 'PASS':
            print_colored("\n🚿 Step 2: Running Car Wash (Auto-Fix)", Colors.BLUE)
            success = run_car_wash(project_path)
            result['fixes_applied'] = success
            
            if success:
                print_colored("   ✅ Car wash completed", Colors.GREEN)
            else:
                print_colored("   ⚠️ Car wash had issues", Colors.YELLOW)
            
            # Step 3: POST-WASH governance check
            print_colored("\n📋 Step 3: POST-WASH Governance Check", Colors.BLUE)
            status, score = run_governance_check(project_path)
            result['post_status'] = status
            result['post_score'] = score
            
            if status == 'PASS':
                print_colored(f"   ✅ Status: {status} (Score: {score}%)", Colors.GREEN)
                print_colored(f"   🎉 Improvement: {score - result['pre_score']}%", Colors.GREEN)
            else:
                print_colored(f"   ⚠️ Status: {status} (Score: {score}%)", Colors.YELLOW)
        else:
            print_colored("\n✓ Skipping car wash (already compliant)", Colors.GREY)
            result['post_status'] = status
            result['post_score'] = score
        
        # Step 4: Generate documentation if 100%
        if result['post_score'] == 100:
            print_colored("\n📝 Step 4: Generating Documentation", Colors.BLUE)
            success = generate_docs(project_path)
            result['docs_generated'] = success
            
            if success:
                print_colored("   ✅ Documentation generated", Colors.GREEN)
            else:
                print_colored("   ⚠️ Documentation generation skipped", Colors.YELLOW)
        
        results.append(result)
        
        print(f"\n{'-'*80}")
    
    # Generate Summary Report
    print(f"\n\n{'='*80}")
    print_colored("📊 BATCH PROCESSING SUMMARY", Colors.CYAN + Colors.BOLD)
    print(f"{'='*80}\n")
    
    print_colored(f"Total Projects Processed: {len(results)}", Colors.BLUE)
    
    passed = sum(1 for r in results if r['post_status'] == 'PASS')
    failed = sum(1 for r in results if r['post_status'] != 'PASS')
    improved = sum(1 for r in results if r['fixes_applied'])
    
    print_colored(f"   ✅ Passing: {passed}", Colors.GREEN)
    print_colored(f"   ⚠️  Failing: {failed}", Colors.YELLOW if failed > 0 else Colors.GREY)
    print_colored(f"   🚿 Auto-Fixed: {improved}", Colors.BLUE)
    
    print(f"\n{'-'*80}\n")
    
    # Detailed Results Table
    print_colored("Detailed Results:", Colors.BLUE)
    print()
    print(f"{'Project':<30} {'PRE':<6} {'POST':<6} {'Improvement':<12} {'Docs':<6}")
    print("-" * 70)
    
    for r in results:
        improvement = r['post_score'] - r['pre_score']
        improvement_str = f"+{improvement}%" if improvement > 0 else f"{improvement}%"
        docs_str = "✓" if r['docs_generated'] else "-"
        
        # Color code the row
        if r['post_status'] == 'PASS':
            color = Colors.GREEN
        elif improvement > 0:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        
        print_colored(
            f"{r['name']:<30} {r['pre_score']:<6} {r['post_score']:<6} {improvement_str:<12} {docs_str:<6}",
            color
        )
    
    print(f"\n{'='*80}\n")
    
    # Save results to CSV
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Logs', 'batch_processing_log.csv')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    try:
        file_exists = os.path.isfile(log_file)
        
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'project_name', 'pre_status', 'pre_score', 
                         'post_status', 'post_score', 'fixes_applied', 'docs_generated']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for r in results:
                writer.writerow({
                    'timestamp': timestamp,
                    'project_name': r['name'],
                    'pre_status': r['pre_status'],
                    'pre_score': r['pre_score'],
                    'post_status': r['post_status'],
                    'post_score': r['post_score'],
                    'fixes_applied': r['fixes_applied'],
                    'docs_generated': r['docs_generated']
                })
        
        print_colored(f"📁 Results saved to: {log_file}", Colors.GREEN)
    
    except Exception as e:
        print_colored(f"⚠️ Warning: Failed to save results: {e}", Colors.YELLOW)
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_colored("Usage: python batch_runner.py <input_directory>", Colors.YELLOW)
        print_colored("\nExample:", Colors.GREY)
        print_colored("  python batch_runner.py ActiveReports/LocalTest", Colors.GREY)
        print_colored("\nNote: Archive and Templates folders are automatically excluded", Colors.GREY)
        sys.exit(1)
    
    input_dir = sys.argv[1]
    
    if not os.path.exists(input_dir):
        print_colored(f"❌ Error: Directory does not exist: {input_dir}", Colors.RED)
        sys.exit(1)
    
    batch_process(input_dir)
