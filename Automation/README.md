# 🤖 Automation Scripts

This folder contains batch files that run automatically as part of the governance workflow. 

**Developers typically don't need to run these manually** - they are triggered automatically when needed.

---

## 📝 Generate_Docs.bat

**Purpose**: Generate documentation for all reports

**When it runs automatically**:
- After `Report Governance Run.bat` completes successfully
- When all governance checks pass

**Manual use** (if needed):
```bash
cd Automation
Generate_Docs.bat
```

**What it does**:
- Scans `ActiveReports/` folder
- Generates both Markdown and HTML documentation
- Creates `[ReportName]_DOCUMENTATION.md` and `.html`

---

## 📚 Sharable Documents.bat

**Purpose**: Build Wiki knowledge base

**When it runs automatically**:
- Can be scheduled via task scheduler
- After major documentation updates
- Before publishing to Azure DevOps

**Manual use** (if needed):
```bash
cd Automation
Sharable Documents.bat
```

**What it does**:
- Syncs all documentation to `Wiki/` folder
- Updates compliance status
- Generates `Wiki/Home.md` with project index
- Creates `.order` files for ADO Wiki

---

## 🎯 When to Use These Manually

You might need to run these manually if:
- Documentation generation failed during governance check
- You want to rebuild the Wiki without running checks
- You're setting up a new environment
- You need to regenerate docs for a specific reason

---

## 📂 File Paths

These scripts use relative paths, so they work from anywhere:
- They reference `../ActiveReports/`
- They reference `../Scripts/`
- They reference `../Wiki/`

---

*For regular development, just use `Report Governance Run.bat` or `Bulk PBI Analysis.bat` from the main folder.*
