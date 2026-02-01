import os
import json
import argparse
import shutil
import sys
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def create_backup(report_folder_path):
    """Creates a backup of the Report directory."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(os.path.dirname(report_folder_path), ".backups")
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        report_name = os.path.basename(report_folder_path)
        backup_path = os.path.join(backup_dir, f"{report_name}_{timestamp}")
        
        print(f"📦 Backing up to: {backup_path}")
        shutil.copytree(report_folder_path, backup_path)
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def remove_color_properties(obj):
    """Recursively remove specific color properties from a JSON object."""
    if isinstance(obj, dict):
        # List of keys to remove related to hardcoded colors
        # We want to remove 'solid' color definitions inside 'fill' or similar
        # But broadly, let's look for known color props in visuals
        keys_to_remove = []
        for key, value in obj.items():
            # Nuclear: Remove Shadows
            if key in ["dropShadow", "shadow"]:
                keys_to_remove.append(key)
                continue
                
            if key in ["dataColors", "background", "fill", "fillColor", "defaultColor", "sectionTitleColor", "titleColor"]:
                 if isinstance(value, dict) and "solid" in value:
                      # This is a specific color override (e.g. { "solid": { "color": "#123456" } })
                      keys_to_remove.append(key)
                 elif isinstance(value, list):
                      # Sometimes it's a list? Recursively check
                      obj[key] = remove_color_properties(value)
                 elif key == "defaultColor":
                      # Often a direct object or string
                      keys_to_remove.append(key)
            else:
                 obj[key] = remove_color_properties(value)
        
        for k in keys_to_remove:
            del obj[k]
            
        return obj
    elif isinstance(obj, list):
        return [remove_color_properties(item) for item in obj]
    else:
        return obj

def reset_colors_in_file(visual_file_path):
    """Reads a visual.json file, removes color properties, and writes it back if changed."""
    try:
        with open(visual_file_path, 'r', encoding='utf-8') as f:
            visual_data = json.load(f)
        
        original = json.dumps(visual_data, sort_keys=True)
        
        # We want to target the 'formatting' section specifically usually?
        # But 'visual.json' structure varies. 
        # Safest is to recurse the whole thing but be careful?
        # Let's try to remove 'single' color overrides in 'objects'.
        
        # Structure: { "name":..., "objects": { "general": [...], "dataPoint": [...] } }
        visual_data = remove_color_properties(visual_data)
        
        modified = json.dumps(visual_data, sort_keys=True)
        
        if original != modified:
            with open(visual_file_path, 'w', encoding='utf-8') as f:
                json.dump(visual_data, f, indent=2)
            
            visual_name = os.path.basename(os.path.dirname(os.path.dirname(visual_file_path))) # definitions/pages/pageName/visuals/visualName/visual.json roughly? 
            # Actually path is .../pages/PageX/visuals/VisualY/visual.json
            # visual_file_path.parent.name is VisualName
            print(f"   OK Reset colors in {os.path.basename(os.path.dirname(visual_file_path))}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error processing {visual_file_path}: {e}")
        return False

def process_report_folder(report_folder_path):
    # Backup first
    if not create_backup(report_folder_path):
        print("❌ Aborting due to backup failure.")
        return

    visual_files = []
    # walk definition/pages
    pages_dir = os.path.join(report_folder_path, "definition", "pages")
    if not os.path.exists(pages_dir):
         print(f"⚠️  No definition/pages found in {report_folder_path}")
         return

    for root, dirs, files in os.walk(pages_dir):
        for file in files:
            if file == "visual.json":
                visual_files.append(os.path.join(root, file))
    
    print(f"📁 Found {len(visual_files)} visuals to check.")
    
    reset_count = 0
    for visual_file in visual_files:
        if reset_colors_in_file(visual_file):
            reset_count += 1
            
    print(f"✅ Reset colors in {reset_count} visuals.")

def main():
    parser = argparse.ArgumentParser(description="Reset hardcoded colors in Power BI Report visuals")
    parser.add_argument("pbip_path", help="Path to PBIP folder OR .pbip file")
    args = parser.parse_args()

    print("======================================================================")
    print("🎨 Visual Color Reset Tool")
    print("======================================================================")

    # Handle file vs folder input
    input_path = args.pbip_path
    if os.path.isfile(input_path) and input_path.endswith(".pbip"):
        pbip_folder = os.path.dirname(input_path) 
        print(f"🎯 Target Project Root: {pbip_folder}")
    else:
        pbip_folder = input_path

    # Define report visual folder: *.Report
    report_dirs = [d for d in os.listdir(pbip_folder) if d.endswith(".Report")]
    
    if not report_dirs:
         if pbip_folder.endswith(".Report"): 
             # User passed the Report folder directly
             process_report_folder(pbip_folder)
             return
         else:
             print(f"❌ No .Report folder found in {pbip_folder}")
             return
    
    # Process all report folders found
    for report_dir in report_dirs:
         full_report_path = os.path.join(pbip_folder, report_dir)
         print(f"   >> Processing Report: {report_dir}")
         process_report_folder(full_report_path)

    print("======================================================================")

if __name__ == "__main__":
    main()
