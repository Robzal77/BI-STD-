import json
import pandas as pd
from datetime import datetime
import os

# --- DYNAMIC CONFIGURATION (OneDrive Friendly) ---
# Get the folder where this script is running
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the Root (BI_Ops_Factory)
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# Define paths relative to Root
# ADJUST THIS NAME: Change 'Sales_Report.pbip' to your actual folder name
MODEL_REL_PATH = os.path.join("Sales_Report.pbip", "Sales_Report.Dataset", "model.bim")
MODEL_FULL_PATH = os.path.join(ROOT_DIR, MODEL_REL_PATH)

LOG_DIR = os.path.join(ROOT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "governance.csv")

# Your Corp Theme Hex Codes
ALLOWED_THEME = ["#118DFF", "#12239E", "#E66C37", "#FFFFFF", "#000000"] 

# --- THE CHECKS ---

def check_relationships(model_json):
    """Flag Bi-Directional Relationships"""
    issues = []
    relationships = model_json.get("model", {}).get("relationships", [])
    
    for rel in relationships:
        if rel.get("crossFilteringBehavior") == "Both":
            issues.append({
                "Check": "Bi-Directional Risk",
                "Object": f"{rel['fromTable']} -> {rel['toTable']}",
                "Status": "Failed",
                "Severity": "High",
                "Message": "Bi-directional filtering detected. High memory cost."
            })
    return issues

def check_measure_descriptions(model_json):
    """Warn if Measures lack descriptions"""
    issues = []
    tables = model_json.get("model", {}).get("tables", [])
    
    for table in tables:
        measures = table.get("measures", [])
        for measure in measures:
            desc = measure.get("description", "").strip()
            name = measure.get("name")
            
            # If description is missing or is just whitespace
            if not desc:
                issues.append({
                    "Check": "Documentation Gap",
                    "Object": f"{table['name']}[{name}]",
                    "Status": "Warning",
                    "Severity": "Medium",
                    "Message": "Measure description is empty."
                })
    return issues

def check_theme_compliance(model_json):
    """Basic check to ensure no hardcoded hex codes exist in measures (FormatStrings)"""
    issues = []
    # This is a basic check. Real theme checking scans the report.json, 
    # but we can scan measure format strings for forbidden hex codes here.
    # For now, we will just log a reminder to check the JSON theme.
    issues.append({
        "Check": "Theme Validity",
        "Object": "Report Theme",
        "Status": "Info",
        "Severity": "Low",
        "Message": f"Manual Verification: Ensure Theme matches {ALLOWED_THEME}"
    })
    return issues

# --- EXECUTION ---

def run_anti_gravity():
    print(f"📂 Root Directory detected: {ROOT_DIR}")
    print(f"🔍 Looking for model at: {MODEL_REL_PATH}")
    
    if not os.path.exists(MODEL_FULL_PATH):
        print(f"❌ ERROR: Could not find model file. Check your paths!")
        return

    # 1. Load Model
    with open(MODEL_FULL_PATH, "r", encoding="utf-8-sig") as f:
        model_data = json.load(f)

    # 2. Run Checks
    logs = []
    logs.extend(check_relationships(model_data))
    logs.extend(check_measure_descriptions(model_data))
    logs.extend(check_theme_compliance(model_data))

    # 3. Add Context
    run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for log in logs:
        log['Timestamp'] = run_time
        log['Source_File'] = MODEL_REL_PATH

    # 4. Save Logs (Ensure 'logs' folder exists)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    df_new = pd.DataFrame(logs)
    
    # Append if file exists, else create new
    if os.path.exists(LOG_FILE):
        df_old = pd.read_csv(LOG_FILE)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new
        
    df_final.to_csv(LOG_FILE, index=False)
    print(f"✅ Anti-Gravity Complete. {len(logs)} issues logged to {LOG_FILE}")

if __name__ == "__main__":
    run_anti_gravity()