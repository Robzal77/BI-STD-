# 🎯 BI Factory - Developer Guide

> **AB InBev Power BI Governance & Automation Toolkit**

## 📁 Folder Structure

```
BI-STD/
├── 📂 ActiveReports/              # Active development reports
│   ├── [Report].SemanticModel/
│   ├── [Report]_DOCUMENTATION.md
│   └── [Report]_DOCUMENTATION.html  ← Auto-generated
│
├── 📂 BatchTesting/               # Batch testing folder
│   ├── README.md
│   └── [Test Reports]
│
├── 📂 Automation/                 # Automated batch scripts ← NEW
│   ├── Generate_Docs.bat          # Auto-doc generation
│   ├── Sharable Documents.bat     # Auto-Wiki build
│   └── README.md
│
├── 📂 Validators/                 # Governance validation logic
│   ├── check_governance.py
│   └── validators.py
│
├── 📂 Scripts/                    # Automation scripts
│   ├── generate_live_docs.py
│   ├── batch_test_runner.py
│   ├── wiki_builder.py
│   └── markdown_to_html.py
│
├── 📂 Themes/                     # Power BI themes
├── 📂 Figma Theme/                # Design assets
├── 📂 Logs/                       # Governance check logs
├── 📂 Wiki/                       # Knowledge base
│
├── Report Governance Run.bat      # ← Main: Check active reports
├── Bulk PBI Analysis.bat          # ← Main: Batch testing
└── README.md
```

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

To regenerate documentation manually:
```bash
Generate_Docs.bat
```

**Output:** 
- `{ReportName}_DOCUMENTATION.md` - Markdown version
- `{ReportName}_DOCUMENTATION.html` - ✨ **HTML version for easy browser viewing**

### Building Wiki

```bash
Sharable Documents.bat
```
- Syncs all project documentation to Wiki
- Updates compliance status
- Generates `Wiki/Home.md` with project index

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

## 📝 Logs

All governance check results are logged to:
- `Logs/governance_log.csv` - Individual governance checks
- `Logs/batch_run_results.csv` - Batch test results

**Columns:**
- Timestamp
- Developer (Windows username)
- Report name
- Auto DateTime status
- Bidirectional filter count
- Missing descriptions count
- Overall status (PASS/FAIL)

## 🎨 Themes

Official AB InBev theme: `Themes/AbinBev_Theme.json`

Apply theme in Power BI:
1. View → Themes → Browse for themes
2. Select `AbinBev_Theme.json`

## 🔧 For Developers

### Adding New Reports

1. Create `.pbip` file in `ActiveReports/` folder
2. Develop report following governance rules
3. Run `Report Governance Run.bat`
4. Fix any governance failures
5. Documentation auto-generates on 100% pass (Markdown + HTML)

### Best Practices

- **Always** add descriptions to measures
- **Never** use bidirectional relationships
- **Always** disable Auto Date/Time in model settings
- **Check** governance before committing to Git

### Batch Testing Workflow

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

## 🆕 What's New

### Recent Improvements:
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
