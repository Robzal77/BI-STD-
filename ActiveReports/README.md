# 📊 ActiveReports - Organized Report Repository

This folder contains all Power BI reports. **You can organize reports however you want** - create folders for projects, teams, or purposes.

## 📁 Folder Structure (Flexible!)

```
ActiveReports/
├── LocalTest/             # Your development/testing reports
├── Production/            # Your production-ready reports
├── [ProjectName]/         # Create any folder you need!
├── [TeamName]/            # Organize by team
├── [YourFolder]/          # Whatever works for you!
│
├── Templates/             # ← SPECIAL: Reference only (not scanned)
└── Archive/               # ← SPECIAL: Not scanned by governance
```

## 🎯 How It Works

**Flexible Organization:**
- ✅ Create ANY folder structure you want
- ✅ Move reports between folders anytime
- ✅ Nothing breaks when you reorganize
- ✅ All folders scanned automatically

**Special Folders (Not Scanned):**
- `Templates/` - Reference templates only
- `Archive/` - Old/deprecated reports

**Everything Else:**
- Gets scanned by `Report Governance Run.bat`
- Documentation auto-generates in same folder
- Synced to Wiki automatically

## 🆕 Creating Folders

Just create a folder and put your reports in it!

```
ActiveReports/
├── Sales-Reports/        # Create this
│   └── Monthly-Sales.pbip
├── Marketing/            # Or this
│   └── Campaign-Analysis.pbip
├── LocalTest/            # Or keep it simple
│   └── Test-Report.pbip
```

**All workflows work regardless of folder structure!**

## 🔄 Simple Workflow

```
1. Create/use any folder you want
2. Develop your report
3. Run Report Governance Run.bat
4. Documentation auto-generates
5. Move between folders freely
```

**That's it!** No complex rules.

## ✅ Governance Rules

All reports (except Archive/ and Templates/) are checked for:
1. **Performance:** Auto Date/Time = DISABLED
2. **Logic:** No bidirectional relationships
3. **Documentation:** All measures have descriptions

## 🛠️ Tools

**Check all reports:**
```bash
Report Governance Run.bat
```
- Scans ALL folders (except Archive & Templates)
- Shows which folder each report is in
- Generates docs for passing reports

**Batch test:**
```bash
Bulk PBI Analysis.bat
```

## 📝 Documentation

- Auto-generates in **same folder** as report
- Both `.md` and `.html` created
- Move report = docs move with it
- No manual work needed

## 💡 Tips

**Organize by:**
- Project: `Sales-Dashboard/`, `Marketing-Reports/`
- Team: `FinanceTeam/`, `OperationsTeam/`  
- Client: `ClientA/`, `ClientB/`
- Status: `LocalTest/`, `Production/`, `InReview/`
- Whatever makes sense for your workflow!

**Remember:**
- Move reports anytime - nothing breaks
- Documentation stays with report
- All folders scanned (except Archive & Templates)
- Create/delete folders as needed

---

*Keep it simple. Organize however works best for you.*
