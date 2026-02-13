import os
import re
import sys
import csv
from datetime import datetime

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

def print_colored(text, color):
    # Enable ANSI support in Windows 10+ console
    os.system('') 
    print(f"{color}{text}{Colors.RESET}")

def get_developer_name():
    """Get developer name from Windows username"""
    return os.getenv('USERNAME', 'Unknown')

def generate_documentation_for_report(semantic_model_dir, report_dir, developer):
    """Generate documentation for a single report"""
    try:
        # Import documentation generator functions
        import importlib.util
        spec = importlib.util.spec_from_file_location("doc_generator", 
            os.path.join(os.path.dirname(__file__), '..', 'scripts', 'generate_live_docs.py'))
        doc_gen = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(doc_gen)
        
        md_path, html_path = doc_gen.generate_report_documentation(semantic_model_dir, report_dir)
        return md_path
    except Exception as e:
        print_colored(f"  ⚠️ Warning: Failed to generate documentation: {e}", Colors.YELLOW)
        return None

def log_to_csv(log_data, log_file='logs/governance_log.csv'):
    """Append governance check results to CSV log file"""
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_exists = os.path.isfile(log_file)
        
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'developer', 'report_name', 'model_path', 
                         'auto_datetime_status', 'bidirectional_count', 'missing_descriptions_count',
                         'missing_descriptions_list', 'overall_status', 'failure_count', 'score']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(log_data)
    except Exception as e:
        print_colored(f"  ⚠️ Warning: Failed to write log: {e}", Colors.YELLOW)

def check_governance(start_dir, enable_logging=True):
    start_dir = os.path.abspath(start_dir)
    developer = get_developer_name()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Print general info in Grey
    print_colored(f"\n🔍 Scanning directory: {start_dir}", Colors.GREY)
    print_colored(f"   Developer: {developer}", Colors.GREY)
    print_colored(f"   (Looking for 'model.tmdl' files recursively)", Colors.GREY)
    
    models_found = 0
    total_failures = 0
    
    for root, dirs, files in os.walk(start_dir):
        # Skip Archive and Templates folders
        dirs[:] = [d for d in dirs if d not in ['Archive', 'Templates']]
        
        if 'model.tmdl' in files:
            models_found += 1
            model_path = os.path.join(root, 'model.tmdl')
            # Get readable project name
            project_name = "Unknown Project"
            if ".SemanticModel" in root:
                parts = root.split(os.sep)
                for p in parts:
                    if p.endswith(".SemanticModel"):
                        project_name = p.replace(".SemanticModel", "")
                        break
            
            # Header Report Name
            print(f"\n{'='*70}")
            print_colored(f"📊 REPORT: {project_name}", Colors.BLUE + Colors.BOLD)
            print_colored(f"   File: {model_path}", Colors.GREY)
            print(f"{'-'*70}")
            
            model_failures = 0

            # 1. Check autoDateTime (Time Intelligence)
            time_intel_enabled = True # Default True
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '__PBI_TimeIntelligenceEnabled = 0' in content or 'autoDateTime: false' in content:
                        time_intel_enabled = False
            except Exception as e:
                print_colored(f"  ❌ ERROR reading model.tmdl: {e}", Colors.RED)

            if time_intel_enabled:
                print_colored("  ❌ [FAIL] Performance: Auto Date/Time is ENABLED", Colors.RED)
                print_colored("      💡 FIX: Open Project Settings -> Data Load -> Uncheck 'Auto date/time'", Colors.YELLOW)
                model_failures += 1
            else:
                print_colored("  ✅ [PASS] Performance: Auto Date/Time is Disabled", Colors.GREEN)

            # 2. Check Relationships (Bi-directional)
            rel_path = os.path.join(root, 'relationships.tmdl')
            bidirectional_count = 0
            if os.path.exists(rel_path):
                try:
                    with open(rel_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if 'crossFilteringBehavior: bothDirections' in line:
                                print_colored(f"  ❌ [FAIL] Logic: Bi-directional relationship found (Line {i+1})", Colors.RED)
                                print_colored("      💡 FIX: Change filter direction to 'Single' in Model View.", Colors.YELLOW)
                                bidirectional_count += 1
                except Exception as e:
                     print_colored(f"  ❌ ERROR reading relationships.tmdl: {e}", Colors.RED)
            
            if bidirectional_count > 0:
                model_failures += bidirectional_count
            else:
                print_colored("  ✅ [PASS] Logic: No Bi-directional relationships found", Colors.GREEN)

            # 3. Check Measures (Missing Description)
            tables_dir = os.path.join(root, 'tables')
            missing_desc_list = []
            
            if os.path.exists(tables_dir):
                for t_root, t_dirs, t_files in os.walk(tables_dir):
                    for t_file in t_files:
                        if t_file.endswith('.tmdl'):
                            t_path = os.path.join(t_root, t_file)
                            try:
                                with open(t_path, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                
                                current_measure = None
                                has_description = False
                                
                                # Initialize description buffer (for /// comments)
                                description_buffer = False

                                for line in lines:
                                    stripped = line.strip()

                                    # Check for /// comments (documentation style used by some models)
                                    if stripped.startswith('///'):
                                        description_buffer = True
                                        continue
                                    
                                    match = re.search(r'^\s*measure\s+[\'"]?([^\'"=]+)[\'"]?', line)
                                    
                                    if match:
                                        if current_measure and not has_description:
                                            missing_desc_list.append(f"{t_file}: {current_measure}")
                                        current_measure = match.group(1).strip()
                                        has_description = description_buffer
                                        description_buffer = False # Consumed
                                        continue
                                    
                                    # If not a comment and not a measure start, reset buffer? 
                                    # Actually, let's keep it simple: if line is not empty and not a comment, clear it.
                                    if stripped and not stripped.startswith('///'):
                                        description_buffer = False
                                    
                                    if current_measure:
                                        first_word = stripped.split()[0] if stripped else ""
                                        if first_word in ['column', 'partition', 'hierarchy', 'measure', 'evaluator']: 
                                            if first_word != 'measure':
                                                if not has_description:
                                                    missing_desc_list.append(f"{t_file}: {current_measure}")
                                                current_measure = None
                                                has_description = False
                                            continue

                                        # Case-insensitive check for description property
                                        if stripped.lower().startswith('description'):
                                            has_description = True
                                
                                if current_measure and not has_description:
                                    missing_desc_list.append(f"{t_file}: {current_measure}")

                            except Exception as e:
                                pass 
            
            if missing_desc_list:
                print_colored(f"  ⚠️ [WARN] Documentation: {len(missing_desc_list)} measures missing descriptions", Colors.YELLOW)
                for m in missing_desc_list[:3]:
                    print_colored(f"      - {m}", Colors.YELLOW)
                if len(missing_desc_list) > 3:
                     print_colored(f"      ...and {len(missing_desc_list)-3} more", Colors.YELLOW)
                print_colored("      💡 FIX: Add 'Description' to these measures in the Properties pane.", Colors.YELLOW)
                # Warning doesn't count as failure for now? User said "if warning orange".
                # But typically documentation gaps are governance failures.
                # Let's count it as failure for final summary but show as orange.
                model_failures += 1 
            else:
                 print_colored("  ✅ [PASS] Documentation: All measures described", Colors.GREEN)

            total_failures += model_failures
            
            # Calculate Score (0-100 scale)
            # Start at 100, deduct points for violations
            score = 100
            if time_intel_enabled:
                score -= 15
            score -= (bidirectional_count * 10)
            score -= (len(missing_desc_list) * 5)
            score = max(0, score)  # Floor at 0
            
            # Display score
            if score == 100:
                print_colored(f"\n  📊 SCORE: {score}/100 - Perfect!", Colors.GREEN + Colors.BOLD)
            elif score >= 70:
                print_colored(f"\n  📊 SCORE: {score}/100 - Good", Colors.YELLOW)
            else:
                print_colored(f"\n  📊 SCORE: {score}/100 - Needs Improvement", Colors.RED)
            
            # Log results to CSV
            if enable_logging:
                log_data = {
                    'timestamp': timestamp,
                    'developer': developer,
                    'report_name': project_name,
                    'model_path': model_path,
                    'auto_datetime_status': 'PASS' if not time_intel_enabled else 'FAIL',
                    'bidirectional_count': bidirectional_count,
                    'missing_descriptions_count': len(missing_desc_list),
                    'missing_descriptions_list': '; '.join(missing_desc_list[:5]) if missing_desc_list else '',
                    'overall_status': 'PASS' if model_failures == 0 else 'FAIL',
                    'failure_count': model_failures,
                    'score': score
                }
                log_to_csv(log_data)
            
            # Auto-generate documentation for this report ONLY if all checks passed
            if '.SemanticModel' in root and model_failures == 0:
                # Extract the parent directory (where .pbip lives)
                parts = root.split(os.sep)
                for i, part in enumerate(parts):
                    if part.endswith('.SemanticModel'):
                        parent_dir = os.sep.join(parts[:i])
                        semantic_model_name = part.replace('.SemanticModel', '')
                        potential_report_dir = os.path.join(parent_dir, f"{semantic_model_name}.Report")
                        break
                
                if os.path.exists(potential_report_dir):
                    print_colored("  📝 Generating documentation...", Colors.GREY)
                    doc_path = generate_documentation_for_report(root, potential_report_dir, developer)
                    if doc_path:
                        print_colored(f"  ✅ Documentation: {os.path.basename(doc_path)}", Colors.GREEN)
            elif '.SemanticModel' in root and model_failures > 0:
                print_colored("  ⚠️  Documentation not generated (governance checks must pass)", Colors.YELLOW)
    
    print(f"\n{'='*70}")
    if models_found == 0:
        print_colored("❌ No Power BI semantic models found (looking for 'model.tmdl')", Colors.RED)
        print_colored(f"   Searched in: {start_dir}", Colors.GREY)
    elif total_failures == 0:
        print_colored("🎉 SUCCESS: All governance checks PASSED! Great job.", Colors.GREEN)
    else:
        print_colored(f"🛑 ISSUES FOUND: Please review the {total_failures} failures above.", Colors.RED)
    print(f"{'='*70}\n")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    check_governance(target_dir)
