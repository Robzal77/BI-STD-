# BI Factory - Standards Toolkit

A governance engine for Power BI that automates compliance checks, theming, and documentation.

## 🚀 Quick Start (3 Steps)

### Step 1: Save your report as PBIP
In Power BI Desktop: **File → Save As → Power BI Project (.pbip)**

### Step 2: Run the Governance Check
```batch
BI_Governance_Check.bat
```
Or manually:
```powershell
python scripts/bi_governance_check.py "path/to/your/project.pbip"
```

### Step 3: Fix errors until you get 100%
Review the output. Each error shows:
- **What's wrong**
- **Why it matters**
- **How to fix it**

---

## 📁 Folder Structure

```
BI_Factory/
├── BI_Governance_Check.bat     ← One-click entry point
├── README.md                   ← Quick start guide
├── config.json                 ← Global governance rules
│
├── docs/                       ← Numbered Technical Documentation
│   ├── 1 - Developer Setup Guide.md
│   ├── 2 - Intro Session Presentation.md
│   ├── 3 - Live Demo Script.md
│   ├── 4 - Governance Rulebook.md
│   ├── 5 - Script Reference Manual.md
│   ├── 6 - Admin Analytics Strategy.md
│   └── 7 - Collaboration & Git Workflow.md
│
├── scripts/                    ← Python automation tools
│   ├── bi_governance_check.py  ← Compliance checker
│   ├── bi_model_fixer.py       ← Auto-fix common issues
│   ├── bi_doc_generator.py     ← Documentation generator
│   └── bi_theme_builder.py     ← Theme file generator
│
├── themes/                     ← Theme JSON files
│   ├── ABInBev_Standard.json
│   └── Corporate_Standard.json
│
├── starter_template/           ← Golden template for new projects
│   └── OFFICIAL_TEMPLATE/
│
├── projects/                   ← Your PBIP projects go here
│   ├── YourProject.pbip
│   ├── YourProject.SemanticModel/
│   └── YourProject.Report/
│
└── .archive/                   ← Old/archived files (ignored)
```

---

## 🛠️ Available Scripts

| Script | Purpose |
|--------|---------|
| `bi_governance_check.py <folder>` | Check PBIP against governance rules |
| `bi_model_fixer.py <folder>` | Auto-fix common issues (theme, autoDateTime) |
| `bi_doc_generator.py <folder>` | Generate live documentation from model |
| `bi_theme_builder.py` | Create theme file from config.json |
| `bi_color_reset.py <folder>` | Remove hardcoded visual colors |

---

## 📊 Governance Rules

Configured in `config.json`:

| Rule | Default | Impact |
|------|---------|--------|
| Auto Date/Time | ❌ Forbidden | +20-40% file size, slow refresh |
| Bi-Directional Filters | ❌ Forbidden | Performance issues, ambiguous paths |
| Hardcoded Colors | ❌ Forbidden | Won't adapt to theme changes |
| Measure Descriptions | ✅ Required | Documentation compliance |

---

## 🔄 Workflow

1. **New Report**: Clone from `OFFICIAL_TEMPLATE.pbip`
2. **Development**: Build your report
3. **Pre-Commit**: Run `bi_governance_check.py`
4. **Commit**: Push to Git
5. **Auto-Doc**: `bi_doc_generator.py` generates latest documentation

---

## 🎛️ Project-Level Overrides

Some reports may legitimately require bi-directional filters or other "forbidden" patterns. Rather than fail validation, you can create a `project_config.json` in your PBIP folder to allow specific exceptions.

### Setup
1. Copy `templates/project_config_template.json` to your PBIP folder
2. Rename to `project_config.json`
3. Set overrides to `true` for checks you want to skip

### Example
```json
{
  "project_name": "Special Logistics Report",
  "overrides": {
    "allow_bi_directional_filters": true,
    "allow_auto_date_time": false
  },
  "approved_by": "Manager Name",
  "approval_date": "2026-01-31"
}
```

### Available Overrides
| Override | Effect |
|----------|--------|
| `allow_auto_date_time` | Skip Auto Date/Time check |
| `allow_bi_directional_filters` | Skip Bi-Directional filter check |
| `allow_hardcoded_colors` | Skip hardcoded visual colors check |

### Inline Skip Comments

For granular control, you can add skip comments directly in TMDL files:

```
// SKIP_CHECK: bi_di_filter - Approved by Manager for cross-filtering requirement
```

**Syntax:** `// SKIP_CHECK: <check_code> - <reason>`

**Supported codes:**
- `auto_date_time` / `auto_datetime`
- `bi_di_filter` / `bi_directional_filters`
- `hardcoded_colors`
- `measure_description`

This is useful when only one specific relationship or measure needs an exception, rather than the entire project.

---

## 📞 Support

For issues or feature requests, contact the BI Governance Team.
