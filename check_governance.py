import os
import re

def check_governance(start_dir):
    print(f"Scanning {start_dir} for model.tmdl files...\n")
    
    models_found = 0
    
    for root, dirs, files in os.walk(start_dir):
        if 'model.tmdl' in files:
            models_found += 1
            model_path = os.path.join(root, 'model.tmdl')
            print(f"--------------------------------------------------")
            print(f"Checking Model: {model_path}")
            
            # 1. Check autoDateTime (Time Intelligence)
            # Check model.tmdl for annotation or property
            time_intel_enabled = True # Default is True in PBI
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for annotation style
                    if '__PBI_TimeIntelligenceEnabled = 0' in content:
                        time_intel_enabled = False
                    # Check for property style (if passes to TOM)
                    if 'autoDateTime: false' in content:
                        time_intel_enabled = False
            except Exception as e:
                print(f"  [ERROR] Could not read model.tmdl: {e}")

            if time_intel_enabled:
                print("  [FAIL] autoDateTime is Enabled (Performance Risk)")
            else:
                print("  [PASS] autoDateTime is Disabled")

            # 2. Check Relationships (Bi-directional)
            # Usually in relationships.tmdl in same dir
            rel_path = os.path.join(root, 'relationships.tmdl')
            bidirectional_found = False
            if os.path.exists(rel_path):
                try:
                    with open(rel_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if 'crossFilteringBehavior: bothDirections' in line:
                                print(f"  [FAIL] Bi-directional relationship found at line {i+1} in relationships.tmdl")
                                bidirectional_found = True
                except Exception as e:
                    print(f"  [ERROR] Could not read relationships.tmdl: {e}")
            
            if not bidirectional_found:
                print("  [PASS] No Bi-directional relationships found")

            # 3. Check Measures (Missing Description)
            # Recursively check 'tables' subdirectory
            tables_dir = os.path.join(root, 'tables')
            measures_missing_desc = []
            
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
                                
                                for line in lines:
                                    stripped = line.strip()
                                    
                                    # Detect start of measure (indent 1 tab or 4 spaces usually, but we check keyword)
                                    # Tmdl objects usually start with type keyword.
                                    # e.g. "	measure 'My Measure' ="
                                    match = re.search(r'^\s*measure\s+[\'"]?([^\'"=]+)[\'"]?', line)
                                    
                                    if match:
                                        # New object started. Check previous measure.
                                        if current_measure and not has_description:
                                            measures_missing_desc.append(f"{t_file}: {current_measure}")
                                        
                                        current_measure = match.group(1).strip()
                                        has_description = False
                                        continue
                                    
                                    # If we are parsing a measure, look for description
                                    # Also check if we hit a new top-level object (column, partition, etc) which ends the measure
                                    if current_measure:
                                        # Check if line defines a new object at same or lower indent (ignoring empty lines)
                                        if stripped and not stripped.startswith('description:') and not stripped.startswith('lineageTag') and not stripped.startswith('formatString') and not stripped.startswith('sourceColumn') and not stripped.startswith('expression'): 
                                            # Simple heuristic: if it starts with a keyword like column, partition, etc.
                                            # TMDL is keyword-first. 
                                            first_word = stripped.split()[0]
                                            if first_word in ['column', 'partition', 'hierarchy', 'measure']:
                                                # measure ended without description
                                                if not has_description:
                                                    measures_missing_desc.append(f"{t_file}: {current_measure}")
                                                current_measure = None
                                                has_description = False
                                                # If it was a measure, we need to process it (but loop continues, so we catch it next iteration if regex matches)
                                                # Actually, we need to re-parse this line if it matches 'measure'.
                                                # but simplifying, the next loop iteration catches 'measure' because of regex match.
                                                if first_word == 'measure':
                                                    continue 
                                                
                                                continue

                                        if 'description:' in line:
                                            has_description = True
                                
                                # Check last measure in file
                                if current_measure and not has_description:
                                    measures_missing_desc.append(f"{t_file}: {current_measure}")

                            except Exception as e:
                                print(f"  [ERROR] checking file {t_file}: {e}")
            
            if measures_missing_desc:
                print(f"  [FAIL] {len(measures_missing_desc)} measures missing descriptions:")
                for m in measures_missing_desc[:5]: # Show first 5
                    print(f"    - {m}")
                if len(measures_missing_desc) > 5:
                    print(f"    ... and {len(measures_missing_desc) - 5} more.")
            else:
                print("  [PASS] All measures have descriptions")
            
            print(f"--------------------------------------------------\n")

    if models_found == 0:
        print("No model.tmdl files found.")

if __name__ == "__main__":
    check_governance(".") or check_governance("BI-STD") # Fallback to subfolder
