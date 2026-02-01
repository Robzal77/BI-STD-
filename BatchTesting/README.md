# Batch Test PBI Folder

This folder is for **batch governance testing** of Power BI reports.

## 📁 Purpose

Use this folder to:
- Test multiple PBIP files at once
- Run regression tests before releases
- Validate reports from external sources
- Batch-validate reports before moving to production

## 🚀 How to Use

1. **Copy PBIP folders** to this directory
   ```
   Batch Test PBI/
   ├── Report1.pbip/
   ├── Report2.pbip/
   └── Report3.pbip/
   ```

2. **Run batch test**
   - Double-click `Run_Batch_Test.bat` in the parent directory
   - Or run: `python scripts/batch_test_runner.py`

3. **Review results**
   - Summary appears in console
   - Detailed results in `logs/batch_run_results.csv`

## 📊 What Gets Tested

Each report is checked for:
- ✅ Auto Date/Time (must be DISABLED)
- ✅ Bidirectional relationships (must be 0)
- ✅ Measure descriptions (all measures must have descriptions)

## 📝 Results

### Console Summary
Shows:
- Total reports tested
- Pass/fail counts and percentages
- List of passed reports
- **Detailed failure breakdown** for each failed report

### CSV Log (`logs/batch_run_results.csv`)
Contains:
- Batch ID (for tracking runs over time)
- Timestamp
- Report name
- Pass/fail status
- Specific failure reasons
- Check details

## 💡 Tips

- **Keep this folder clean** - Only add reports you want to test
- **Compare over time** - Use Batch ID to track improvements
- **Fix and re-test** - Run again after fixing failures to verify

---

*This folder is separate from `Project/` (active development) and `REFERECNE FILES/` (examples).*
