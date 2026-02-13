# 🚀 Developer Quick Start - Power BI Governance & Bulk Descriptions

## 📋 What This Does

This guide shows you how to:
1. ✅ Check your Power BI report for governance issues
2. 📝 Bulk-add descriptions to all measures at once (in Excel/VSCode)
3. ✅ Verify everything is fixed

---

## 🎯 The 3-Step Workflow

### **Step 1: Run Governance Check**

Open VSCode terminal in the `BI-STD` folder and run:

```bash
python Validators/check_governance.py "ActiveReports/Production/YourReport"
```

**What happens**:
- ✅ Checks your report for issues
- ✅ Creates `YourReport_GOVERNANCE_REPORT.txt` (detailed results)
- ✅ **Auto-creates CSV** if missing descriptions found
- 🟡 Shows what needs fixing

**Example Output**:
```
⚠️ [WARN] Documentation: 68 measures missing descriptions
📄 Created: CEA Reporting ADB_missing_descriptions.csv
➡️  Next: Fill descriptions in CSV and run: python Scripts/apply_descriptions.py "..."
```

---

### **Step 2: Fill Descriptions**

**Option A: In VSCode**
```bash
code "ActiveReports/Production/YourReport_missing_descriptions.csv"
```

**Option B: In Excel**
- Navigate to the project folder
- Open `YourReport_missing_descriptions.csv`

**CSV Format**:
```csv
table_file,measure_name,current_description,new_description
Sales.tmdl,Total Revenue,,"Sum of all sales revenue in USD"
Sales.tmdl,Total Units,,"Count of units sold"
```

✏️ **Fill the `new_description` column** for each measure  
💾 **Save the file** when done

---

### **Step 3: Apply Changes**

Run this command to import descriptions and re-check:

```bash
python Scripts/apply_descriptions.py "ActiveReports/Production/YourReport_missing_descriptions.csv"
```

**What happens**:
- ✅ Imports all descriptions to TMDL files
- ✅ Re-runs governance check automatically
- ✅ Shows updated results

**Example Output**:
```
[STEP 1/2] Importing descriptions from CSV...
✅ Successfully updated 68/68 measure descriptions!

[STEP 2/2] Re-running governance check to verify...
✅ [PASS] Documentation: All measures described
📊 SCORE: 85/100 - Good

✅ DONE! Descriptions applied and verified
```

---

## 📊 Understanding Governance Scores

| Score | Status | Meaning |
|-------|--------|---------|
| 100/100 | ✅ Perfect | No issues found |
| 70-99 | 🟡 Good | Minor issues (usually descriptions) |
| <70 | 🔴 Needs Work | Multiple governance failures |

**Common Issues**:
- ❌ **Auto Date/Time Enabled** (-15 points) → Fix in Power BI: File > Options > Data Load > Uncheck "Auto date/time"
- ❌ **Bi-directional Relationships** (-10 each) → Fix in Model View: Change to Single direction
- ⚠️ **Missing Descriptions** (-5 each) → Fix with bulk tool (this guide!)

---

## 💡 Tips & Best Practices

### ✅ Good Description Examples
```
"Total sales revenue in USD for the selected period"
"Number of active customers as of report refresh date"
"Year-over-year growth percentage for revenue"
```

### ❌ Avoid
```
"Total"  (too vague)
"Measure1"  (not descriptive)
```

### 📝 Description Writing Tips
- Start with **what** the measure shows
- Include **units** (USD, %, count, etc.)
- Mention **time context** if relevant
- Keep it **concise** but **clear** (1-2 sentences max)

---

## 🔄 Full Workflow Example

Here's a complete real-world example:

```bash
# 1. Check governance
python Validators/check_governance.py "ActiveReports/Production/Sales_Dashboard"

# Output:
# ⚠️ [WARN] Documentation: 25 measures missing descriptions
# 📄 Created: Sales_Dashboard_missing_descriptions.csv
# ➡️  Next: Fill descriptions...

# 2. Open CSV and fill descriptions
code "ActiveReports/Production/Sales_Dashboard_missing_descriptions.csv"

# (Edit the CSV, fill descriptions, save)

# 3. Apply changes
python Scripts/apply_descriptions.py "ActiveReports/Production/Sales_Dashboard_missing_descriptions.csv"

# Output:
# ✅ Successfully updated 25/25 measure descriptions!
# ✅ [PASS] Documentation: All measures described
# 📊 SCORE: 100/100 - Perfect!
```

---

## ❓ FAQ

**Q: What if the CSV already exists?**  
A: Governance check won't overwrite it (protects your work). Delete the old CSV if you want a fresh export.

**Q: Can I skip measures I don't want to describe?**  
A: Yes! Leave the `new_description` column empty for those rows.

**Q: Do I need to close Power BI Desktop?**  
A: No, but you'll need to refresh the data model to see the descriptions in Power BI.

**Q: Where are the governance reports saved?**  
A: In the same folder as your `.pbip` file: `YourReport_GOVERNANCE_REPORT.txt`

**Q: Can I run this on multiple reports at once?**  
A: Yes! Run governance check on a folder:
```bash
python Validators/check_governance.py "ActiveReports/Production"
```
This creates separate CSVs for each report with missing descriptions.

---

## 🆘 Troubleshooting

**CSV not created?**  
→ No missing descriptions! Your report is already compliant.

**Import says "File not found"?**  
→ Make sure you saved the CSV after editing.

**Governance still showing failures after import?**  
→ Check the console output for specific errors. Some measures might not have been updated.

---

## 📚 Additional Resources

- **Bulk Descriptions Guide**: `Scripts/BULK_DESCRIPTIONS_GUIDE.md`
- **Governance Report**: Check `YourReport_GOVERNANCE_REPORT.txt` after each run
- **CSV Log**: View all checks in `logs/governance_log.csv`

---

*Part of the BI Factory - Power BI Standardization Framework*
