import os
import json
import re
import argparse
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def load_config(config_path='config.json'):
    with open(config_path, 'r') as f:
        return json.load(f)

def update_theme(report_root, theme_path, project_name=None):
    # If project_name is known, look for specific folder
    if project_name:
         target_folder = f"{project_name}.Report"
         potential_path = os.path.join(report_root, target_folder)
         if os.path.isdir(potential_path):
              theme_dest = os.path.join(potential_path, "StaticResources", "SharedResources", "BaseThemes")
         else:
              print(f"⚠️  Report folder not found: {potential_path}")
              return
    else:
        # Fallback: look for ANY .Report folder (Legacy behavior)
        report_dirs = [d for d in os.listdir(report_root) if d.endswith(".Report") and os.path.isdir(os.path.join(report_root, d))]
        
        if not report_dirs:
            if report_root.endswith(".Report"):
                 theme_dest = os.path.join(report_root, "StaticResources", "SharedResources", "BaseThemes")
            else:
                 theme_dest = os.path.join(report_root, "Report", "StaticResources", "SharedResources", "BaseThemes")
        else:
            theme_dest = os.path.join(report_root, report_dirs[0], "StaticResources", "SharedResources", "BaseThemes")
    
    if not os.path.exists(theme_dest):
        print(f"⚠️  Theme folder not found: {theme_dest}")
        print(f"   (Scanned: {report_root})")
        return

    # Find the existing json file (usually CypressTheme.json or similar)
    for file in os.listdir(theme_dest):
        if file.endswith(".json"):
            full_path = os.path.join(theme_dest, file)
            
            # Read our corporate template
            with open(theme_path, 'r') as src:
                new_theme_content = src.read()
            
            # Overwrite the existing file
            with open(full_path, 'w') as dest:
                dest.write(new_theme_content)
            
            print(f"🎨 Theme updated: {file}")
            return

def fix_tmdl_files(semantic_model_folder):
    # Walker to find all TMDL files
    fixed_count = 0
    
    for root, dirs, files in os.walk(semantic_model_folder):
        for file in files:
            if file.endswith(".tmdl"):
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                new_lines = []
                modified = False
                
                for i, line in enumerate(lines):
                    # 1. Fix Auto Date/Time
                    # Logic: In 'database.tmdl', it is FORBIDDEN (must remove). In 'model.tmdl', it can be 'false'.
                    if "autoDateTime:" in line:
                         is_database_file = os.path.basename(file_path).lower() == "database.tmdl"
                         if is_database_file:
                              # Remove completely from database.tmdl
                              # Skip appending this line
                              modified = True
                              fixed_count += 1
                              continue 
                         elif "true" in line:
                              # Toggle to false in other files (model.tmdl)
                              new_lines.append(line.replace("true", "false"))
                              modified = True
                              fixed_count += 1
                              continue
                    
                    new_lines.append(line)

                # Write back if changed
                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                        
    print(f"✅ Fixed {fixed_count} configuration issues in TMDL files.")

def main():
    parser = argparse.ArgumentParser(description="BI Model Fixer - Auto-fix common governance issues")
    parser.add_argument("pbip_folder", help="Path to the PBIP folder")
    args = parser.parse_args()

    config = load_config()
    
    # Handle both File and Folder inputs
    target_path = args.pbip_folder
    if os.path.isfile(target_path) and target_path.endswith(".pbip"):
        root_folder = os.path.dirname(target_path)
        project_name = os.path.basename(target_path).replace(".pbip", "")
        print(f"🎯 Target Project: {project_name}")
    else:
        root_folder = target_path
        project_name = None
    
    # 1. Apply Theme
    print("🔧 Starting BI Model Fixer...")
    # Switched to ABInBev Theme
    update_theme(root_folder, "themes/ABInBev_Standard.json", project_name)
    
    # 2. Fix Model Settings (Auto Date/Time)
    # If project name is known, target specific semantic model
    if project_name:
         target_model = os.path.join(root_folder, f"{project_name}.SemanticModel")
         if os.path.exists(target_model):
              print(f"   >> Processing model: {project_name}.SemanticModel")
              fix_tmdl_files(target_model)
         else:
              print(f"⚠️  Semantic Model not found at: {target_model}")
              
              # Fallback scan
              print("   Scanning subfolders just in case...")
              for root, dirs, files in os.walk(root_folder):
                   if root.endswith(".SemanticModel"):
                        print(f"   >> Found model: {os.path.basename(root)}")
                        fix_tmdl_files(root)

    else:
        semantic_model = os.path.join(root_folder, os.path.basename(root_folder).replace(".pbip", ".SemanticModel"))
        if os.path.exists(semantic_model):
            fix_tmdl_files(semantic_model)
        else:
            # Fallback for different folder naming structures
            print("⚠️  Semantic Model folder not found immediately. Scanning subfolders...")
            found_any = False
            for root, dirs, files in os.walk(root_folder):
                if root.endswith(".SemanticModel"):
                    # Don't break immediately, process all models found
                    print(f"   >> Found model: {os.path.basename(root)}")
                    fix_tmdl_files(root)
                    found_any = True
            
            if not found_any:
                print("   ❌ No .SemanticModel folders found in walk.")

if __name__ == "__main__":
    main()
