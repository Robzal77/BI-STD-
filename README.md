# 🎯 BI Factory - Developer Guide

> **AB InBev Power BI Governance & Automation Toolkit**

## 📁 Folder Structure

```
BI-STD/
├── 📂 ActiveReports/              # All your reports (flexible structure!)
│   ├── [YourFolders]/             # ← Organize however you want
│   ├── LocalTest/                 # Example: test reports
│   ├── Production/                # Example: production reports
│   ├── Templates/                 # ← SKIP: Reference only
│   └── Archive/                   # ← SKIP: Not scanned
│
├── 📂 BatchTesting/               # Batch testing folder
│   ├── README.md
│   └── [Test Reports]
│
├── 📂 Automation/                 # Automated batch scripts
│   ├── Generate_Docs.bat          # Auto-doc generation
│   ├── Sharable Documents.bat     # Auto-Wiki build
│   └── README.md
│
├── 📂 Validators/                 # Governance validation logic
│   ├── check_governance.py        # Skips Archive & Templates
│   └── validators.py
│
├── 📂 Scripts/                    # Automation scripts (all scan recursively)
│   ├── generate_live_docs.py      # Skips Archive & Templates
│   ├── batch_test_runner.py
│   ├── wiki_builder.py            # Skips Archive & Templates
│   ├── car_wash.py                # 🚿 NEW: Auto-fix governance violations
│   ├── batch_runner.py            # 🏭 NEW: Batch process multiple reports
│   └── markdown_to_html.py
│
├── 📂 Themes/                     # Power BI themes
├── 📂 Figma Theme/                # Design assets
├── 📂 Logs/                       # Governance check logs
├── 📂 Wiki/                       # Knowledge base
│
├── Report Governance Run.bat      # ← Main: Check reports (all folders)
├── Bulk PBI Analysis.bat          # ← Main: Batch testing
└── README.md
```

> **💡 Simple Rule:** Create any folders you want in ActiveReports/.  
> Everything scanned **except** Archive/ and Templates/. Move reports freely!

## 🚀 Quick Start

### Running Governance Checks

**For Active Projects:**
```bash
Report Governance Run.bat
```
- Validates all reports in `ActiveReports/` folder
- Checks: Auto Date/Time, Bidirectional relationships, Measure descriptions
- Logs results to `Logs/governance_log.csv`
- **Auto-generates Markdown + HTML documentation for 100% passing reports**

**For Batch Testing:**
```bash
Bulk PBI Analysis.bat
```
- Tests all reports in `BatchTesting/` folder
- Generates comprehensive summary with pass/fail breakdown
- Shows **detailed action items** for each failure
- Saves results to `Logs/batch_run_results.csv`
- Perfect for regression testing and bulk validation

### Generating Documentation

Documentation is **automatically generated** in **both Markdown and HTML** when governance checks pass.

**Manual regeneration** (if needed):
```bash
cd Automation
Generate_Docs.bat
```

**Output:** 
- `{ReportName}_DOCUMENTATION.md` - Markdown version
- `{ReportName}_DOCUMENTATION.html` - ✨ **HTML version for easy browser viewing**

> **Note**: This runs automatically after `Report Governance Run.bat`, so manual use is rarely needed.

### Building Wiki

**Manual build** (if needed):
```bash
cd Automation
Sharable Documents.bat
```
- Syncs all project documentation to Wiki
- Updates compliance status
- Generates `Wiki/Home.md` with project index

> **Note**: This is typically run on a schedule or before publishing to Azure DevOps.

## 📊 Documentation Format

Auto-generated documentation includes:
- **Quick Navigation** - Table of contents
- **Relationship Map** - Mermaid ER diagram
- **Model Blueprint** - Table overview (Facts/Dimensions)
- **Factory Data (Facts)** - Tables with measures
- **Business Context (Dimensions)** - Reference tables
- **All measures** with collapsible DAX formulas
- **All columns** with types and descriptions

**✨ NEW: HTML Version**
- Professional styling
- Syntax highlighting for DAX
- Responsive design
- Print-friendly
- No special tools needed - open in any browser!

## ✅ Governance Rules

Reports must pass all checks to get documentation:

1. **Performance**
   - Auto Date/Time must be DISABLED
   
2. **Logic**
   - No bidirectional relationships allowed
   
3. **Documentation**
   - All measures must have descriptions

## 📊 Quality Scoring System (NEW!)

Every governance check now provides a **0-100 score** for precise quality tracking:

**How Scores Work:**
- Start at **100 points**
- **-15 points** if Auto Date/Time is enabled
- **-10 points** per bidirectional relationship
- **-5 points** per missing measure description

**Score Categories:**
- 🎉 **100**: Perfect! (Green)
- ⚠️ **70-99**: Good (Yellow)  
- ❌ **0-69**: Needs Improvement (Red)

**Example:**
```
Auto DateTime ON + 2 bidirectional + 3 missing descriptions
= 100 - 15 - 20 - 15 = 50/100
```

## 📝 Logs

All governance check results are logged to:
- `Logs/governance_log.csv` - Individual governance checks **+ Scores**
- `Logs/batch_run_results.csv` - Batch test results
- `Logs/batch_processing_log.csv` - **NEW:** Batch runner pre/post scores

**governance_log.csv Columns:**
- Timestamp
- Developer (Windows username)
- Report name
- Auto DateTime status
- Bidirectional filter count
- Missing descriptions count
- Overall status (PASS/FAIL)
- **Score (0-100)** ← NEW!

## 🎨 Themes

Official AB InBev theme: `Themes/AbinBev_Theme.json`

Apply theme in Power BI:
1. View → Themes → Browse for themes
2. Select `AbinBev_Theme.json`

## 🔧 For Developers

### Workflow 1: Adding New Reports (Standard)

1. Create `.pbip` file in `ActiveReports/` folder
2. Develop report following governance rules
3. Run `Report Governance Run.bat`
4. Check your **score** (aim for 100/100)
5. Fix any governance failures
6. Documentation auto-generates on 100% pass (Markdown + HTML)

### Workflow 2: Auto-Fix Single Report 🚿 **NEW!**

If your report has governance violations, use the **Car Wash** to auto-fix:

```bash
# Step 1: Check current score
python Validators/check_governance.py "ActiveReports/YourFolder/YourReport"
# Output: 📊 SCORE: 85/100 - Good

# Step 2: Auto-fix violations
python Scripts/car_wash.py "ActiveReports/YourFolder/YourReport"
# Fixes: Auto Date/Time, injects AB InBev theme, removes color overrides

# Step 3: Verify improvement
python Validators/check_governance.py "ActiveReports/YourFolder/YourReport"
# Output: 📊 SCORE: 100/100 - Perfect!
```

**What Car Wash Fixes Automatically:**
- ✅ Disables Auto Date/Time in TMDL
- ✅ Injects AB InBev corporate theme
- ✅ Scans visuals for hardcoded color overrides

### Workflow 3: Batch Process Multiple Reports 🏭 **NEW!**

Process multiple reports at once with pre/post scoring:

```bash
# Process all reports in a folder
python Scripts/batch_runner.py "ActiveReports/Production"
```

**What Happens:**

For **EACH** report:
1. 📋 PRE-WASH governance check → Record score
2. 🚿 Car Wash (if score < 100) → Auto-fix violations
3. 📋 POST-WASH governance check → Record new score
4. 📝 Auto-generate docs (if score = 100) → Live documentation created

**Example Output:**
```
📊 BATCH PROCESSING SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Projects: 5
   ✅ Passing: 4
   🚿 Auto-Fixed: 3

Detailed Results:
Project          PRE   POST   Improvement   Docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sales_Report     85    100    +15%          ✓
Inventory_Dash   70    100    +30%          ✓
Customer_KPIs    100   100    0%            ✓
Finance_Report   90    100    +10%          ✓
HR_Dashboard     65    95     +30%          -

📁 Results saved to: Logs/batch_processing_log.csv
```

**Benefits:**
- ✅ Process 10+ reports in minutes
- ✅ Track before/after quality improvements
- ✅ Auto-generate documentation for all compliant reports
- ✅ Clear CSV logs for audit trails

### Workflow 4: Traditional Batch Testing

1. Copy reports to `BatchTesting/` folder
2. Run `Bulk PBI Analysis.bat`
3. Review summary with detailed action items per failure
4. Fix issues following the step-by-step instructions
5. Re-run until all pass

**Action Items Feature**: For every failed report, you'll see:
- What failed (specific counts)
- Which files to check
- Step-by-step fix instructions
- Exact Power BI menu paths

### Best Practices

- **Always** add descriptions to measures
- **Never** use bidirectional relationships
- **Always** disable Auto Date/Time in model settings
- **Use Car Wash** for quick fixes before committing
- **Run batch_runner** for multiple reports at once
- **Check scores** - aim for 100/100 before deployment

## 🆕 What's New

### 🎉 POC Framework (February 2026) - "10/10 Standardization"
- ✅ **Quality Scoring (0-100)**: Quantitative metrics replace PASS/FAIL
- ✅ **Car Wash Script**: Auto-fix governance violations in seconds
- ✅ **Batch Runner**: Process multiple reports with before/after tracking
- ✅ **Live Documentation**: Auto-generated for 100% compliant reports
- ✅ **CSV Audit Trails**: Complete score history and batch run logs

### Previous Improvements:
- ✅ **Folder Reorganization**: Cleaner, more professional naming
- ✅ **HTML Documentation**: Auto-generated HTML alongside Markdown
- ✅ **Enhanced Batch Testing**: Detailed action items for developers
- ✅ **Wiki Knowledge Base**: Auto-sync documentation to Wiki
- ✅ **Improved UX**: Better error messages and guidance

### Removed:
- ❌ `REFERENCE FILES/` folder (no longer needed)

## 📚 Additional Resources

- Design assets: `Figma Theme/`
- Knowledge Base: `Wiki/Home.md`
- Batch Testing Guide: `BatchTesting/README.md`

---

*This BI Factory ensures consistent, high-quality Power BI reports across the organization.*
