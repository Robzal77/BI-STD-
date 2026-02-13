# 📝 Bulk Measure Description Update - Quick Guide

## Problem Solved
Instead of updating measure descriptions **one-by-one** in Power BI Desktop, update **ALL of them at once** in Excel!

## 🚀 NEW Automated 3-Step Workflow

### Step 1: Run Governance Check (Auto-Creates CSV)
```bash
python Validators/check_governance.py "ActiveReports/YourFolder/YourReport"
```
**Output**: 
- Checks your report for governance issues
- ✅ **Automatically creates** `YourReport_missing_descriptions.csv` if missing descriptions found
- Shows next steps in console

### Step 2: Fill Descriptions in Excel/VSCode
1. Open `YourReport_missing_descriptions.csv` in Excel or VSCode
2. Fill in the `new_description` column for each measure
3. Save the file

**CSV Format:**
| table_file | measure_name | current_description | new_description |
|---|---|---|---|
| Sales.tmdl | Total Revenue | _(empty)_ | **Sum of all sales in USD** |
| Sales.tmdl | Total Units | _(empty)_ | **Count of units sold** |

### Step 3: Apply Changes (Auto-Imports + Re-Checks)
```bash
python Scripts/apply_descriptions.py "ActiveReports/YourFolder/YourReport_missing_descriptions.csv"
```
**Result**: 
- Automatically updates all TMDL files with your descriptions
- Re-runs governance check to verify
- Shows final score and status

---

## 🎯 What's New?
✅ **Auto-create CSV** - Governance check now creates CSV automatically  
✅ **One-command apply** - New `apply_descriptions.py` imports + verifies in one go  
✅ **Faster workflow** - Reduced from 5 steps to just 3!

---

## 📖 Old Manual Workflow (Still Works)

If you prefer manual control, you can still use the original scripts:

### Manual Export
```bash
python Scripts/export_missing_descriptions.py "ActiveReports/YourFolder/YourReport"
```

### Manual Import
```bash
python Scripts/import_descriptions.py "ActiveReports/YourFolder/YourReport_missing_descriptions.csv"
```

---

## What Gets Updated?
The import script modifies your `.tmdl` files like this:

**Before:**
```
measure 'Total Revenue' = SUM(Sales[Amount])
```

**After:**
```
measure 'Total Revenue' = SUM(Sales[Amount])
    description = "Sum of all sales in USD"
```

---

## Benefits
- ✅ **Bulk editing** - Update 50+ measures in minutes
- ✅ **Excel-friendly** - Use familiar tools
- ✅ **Copy/Paste** - Duplicate similar descriptions easily
- ✅ **Safe** - Only updates what you fill in
- ✅ **Automated** - CSV creation and verification built-in
- ✅ **Audit trail** - CSV file shows what changed

---

## Tips
- Leave `new_description` empty for measures you want to skip
- Use Excel's fill-down for similar measures
- The CSV is UTF-8 encoded (supports all characters)
- CSV won't be overwritten if it already exists (protects your work)
- You can re-run import multiple times safely

---

*Part of the BI Factory - "10/10 Power BI Standardization Framework"*
