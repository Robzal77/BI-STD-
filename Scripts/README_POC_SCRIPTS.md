# 🚿 Car Wash - Quick Reference

## What It Does

Automatically fixes common Power BI governance violations:
- **Auto Date/Time**: Disables in TMDL
- **AB InBev Theme**: Injects corporate theme
- **Visual Colors**: Scans for hardcoded overrides

## Usage

```bash
# Fix a single project
python Scripts/car_wash.py "ActiveReports/LocalTest/MyReport.pbip"

# With custom theme
python Scripts/car_wash.py "ActiveReports/LocalTest/MyReport.pbip" "Themes/CustomTheme.json"
```

## What Gets Fixed

✅ `autoDateTime: true` → `autoDateTime: false` in model.tmdl  
✅ Theme injected to StaticResources/RegisteredResources  
✅ Visual JSON files scanned for color overrides

## Safety

- Never modifies `.pbip` files directly
- Works on folder structure only
- Validates paths before changes
- Colored output shows what was fixed

---

# 🏭 Batch Runner - Quick Reference

## What It Does

Processes multiple Power BI reports in one run:
1. Scans for all .pbip projects
2. Runs PRE-WASH governance check
3. Runs car wash if needed
4. Runs POST-WASH governance check
5. Generates docs for 100% compliant reports
6. Creates summary report with scores

## Usage

```bash
# Process all reports in a folder
python Scripts/batch_runner.py "ActiveReports/LocalTest"

# Process production reports
python Scripts/batch_runner.py "ActiveReports/Production"
```

## What You Get

📊 **Console Summary Table**:
- Project name
- PRE/POST scores
- Improvement percentage
- Docs generated (✓/-)

📁 **CSV Log**: `Logs/batch_processing_log.csv`
- Timestamp
- Pre/post scores
- Fixes applied (True/False)
- Docs generated (True/False)

## Exclusions

The batch runner automatically skips:
- `Archive/` folder
- `Templates/` folder
- `__pycache__/` folders

---

# 📊 Scoring System

## How Scores Work

Start at **100 points**, deduct for violations:

| Violation | Deduction |
|---|---|
| Auto Date/Time enabled | **-15 points** |
| Each bidirectional relationship | **-10 points** |
| Each missing measure description | **-5 points** |

**Example:**
- Auto datetime ON + 2 bidirectional + 3 missing descriptions
- Score = 100 - 15 - 20 - 15 = **50/100**

## Score Display

- **100**: 🎉 Perfect! (Green)
- **70-99**: ⚠️ Good (Yellow)
- **0-69**: ❌ Needs Improvement (Red)

## Where Scores Appear

✅ Console output (colored)  
✅ `Logs/governance_log.csv` (new `score` column)  
✅ `Logs/batch_processing_log.csv` (pre/post scores)

---

*Part of the BI Factory - "10/10 Power BI Standardization Framework"*
