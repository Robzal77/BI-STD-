# 📝 Bulk Measure Description Update - Quick Guide

## Problem Solved
Instead of updating measure descriptions **one-by-one** in Power BI Desktop, update **ALL of them at once** in Excel!

## Simple 4-Step Workflow

### Step 1: Export Missing Descriptions
```bash
python Scripts/export_missing_descriptions.py "ActiveReports/YourFolder/YourReport"
```
**Output:** Creates `YourReport_missing_descriptions.csv` in the same folder

### Step 2: Fill Descriptions in Excel
1. Open the CSV file in Excel
2. Fill in the `new_description` column for each measure
3. Save the file

**CSV Format:**
| table_file | measure_name | current_description | new_description |
|---|---|---|---|
| Sales.tmdl | Total Revenue | _(empty)_ | **Sum of all sales in USD** |
| Sales.tmdl | Total Units | _(empty)_ | **Count of units sold** |

### Step 3: Import Descriptions Back
```bash
python Scripts/import_descriptions.py "ActiveReports/YourFolder/YourReport_missing_descriptions.csv"
```
**Result:** Automatically updates all TMDL files with your descriptions!

### Step 4: Verify with Governance Check
```bash
python Validators/check_governance.py "ActiveReports/YourFolder/YourReport"
```
**Expected:** 📊 SCORE: 100/100 - Perfect! ✅

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
- ✅ **Audit trail** - CSV file shows what changed

---

## Tips
- Leave `new_description` empty for measures you want to skip
- Use Excel's fill-down for similar measures
- The CSV is UTF-8 encoded (supports all characters)
- You can re-run import multiple times safely

---

*Part of the BI Factory - "10/10 Power BI Standardization Framework"*
