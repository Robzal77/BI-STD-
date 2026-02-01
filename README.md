# 🎯 BI Factory - Developer Guide

> **AB InBev Power BI Governance & Automation Toolkit**

## 📁 Folder Structure

```
BI-STD/
├── 📂 Project/                    # Active development reports
│   └── [ReportName]_Documentation.md (auto-generated)
│
├── 📂 Batch Test PBI/             # Batch testing folder
│   └── [Test Reports]
│
├── 📂 REFERECNE FILES/            # Archive & reference materials
│   ├── projects/                  # Example reports
│   └── scripts/                   # Legacy/archived scripts
│
├── 📂 validators/                 # Governance validation logic
│   ├── check_governance.py        # Main governance checker
│   └── validators.py              # Validation rules
│
├── 📂 scripts/                    # Automation scripts
│   └── generate_live_docs.py      # Documentation generator
│
├── 📂 themes/                     # Power BI theme files
│   └── AbinBev_Theme.json
│
├── 📂 Figma Theme/                # Design assets
│   └── Report Home Page/
│
└── 📂 logs/                       # Governance check logs
    └── governance_log.csv
```

## 🚀 Quick Start

### Running Governance Checks

**For Active Projects:**
```bash
Run_Governance_Check.bat
```
- Validates all reports in `Project/` folder
- Checks: Auto Date/Time, Bidirectional relationships, Measure descriptions
- Logs results to `logs/governance_log.csv`
- **Auto-generates documentation for 100% passing reports**

**For Reference Files (Batch):**
```bash
Run_Governance_CarWash.bat
```
- Validates all reports in `REFERECNE FILES/` folder
- Use for establishing baseline compliance

**For Batch Testing:**
```bash
Run_Batch_Test.bat
```
- Tests all reports in `Batch Test PBI/` folder
- Generates comprehensive summary with pass/fail breakdown
- Saves results to `logs/batch_run_results.csv`
- Perfect for regression testing and bulk validation

### Generating Documentation

Documentation is **automatically generated** when governance checks pass.

To regenerate documentation manually:
```bash
Generate_Documentation.bat
```

**Output:** `{ReportName}_Documentation.md` (in project folder)

## 📊 Documentation Format

Auto-generated documentation includes:
- **Quick Navigation** - Table of contents
- **Relationship Map** - Mermaid ER diagram
- **Model Blueprint** - Table overview (Facts/Dimensions)
- **Factory Data (Facts)** - Tables with measures
- **Business Context (Dimensions)** - Reference tables
- **All measures** with collapsible DAX formulas
- **All columns** with types and descriptions

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
- `logs/governance_log.csv`

**Columns:**
- Timestamp
- Developer (Windows username)
- Report name
- Auto DateTime status
- Bidirectional filter count
- Missing descriptions count
- Overall status (PASS/FAIL)

## 🎨 Themes

Official AB InBev theme: `themes/AbinBev_Theme.json`

Apply theme in Power BI:
1. View → Themes → Browse for themes
2. Select `AbinBev_Theme.json`

## 🔧 For Developers

### Adding New Reports

1. Create `.pbip` file in `Project/` folder
2. Develop report following governance rules
3. Run `Run_Governance_Check.bat`
4. Fix any governance failures
5. Documentation auto-generates on 100% pass

### Best Practices

- **Always** add descriptions to measures
- **Never** use bidirectional relationships
- **Always** disable Auto Date/Time in model settings
- **Check** governance before committing to Git

## 📚 Additional Resources

- Reference reports: `REFERECNE FILES/projects/`
- Design assets: `Figma Theme/`

---

*This BI Factory ensures consistent, high-quality Power BI reports across the organization.*
