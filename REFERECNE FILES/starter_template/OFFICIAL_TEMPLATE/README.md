# OFFICIAL_TEMPLATE

This is the **Golden Starter Template** for all new Power BI reports.

## How to Use

1. **Copy this entire folder** to `projects/` (or your project directory)
2. **Rename all files** from `OFFICIAL_TEMPLATE` to your project name:
   - `OFFICIAL_TEMPLATE.pbip` → `YourProjectName.pbip`
   - `OFFICIAL_TEMPLATE.SemanticModel/` → `YourProjectName.SemanticModel/`
   - `OFFICIAL_TEMPLATE.Report/` → `YourProjectName.Report/`
3. **Update** `database.tmdl` and PBIP file to match your new project name
4. **Replace** `Sample_Data` table with your actual data sources
5. **Run governance check**: `python scripts/bi_governance_check.py "path/to/your/project"`

## What's Included

| Component | Description |
|-----------|-------------|
| **DateTable** | Standard date dimension (2020-2030) with proper hierarchy |
| **Measures** | Central measures table with documentation pattern |
| **Sample_Data** | Placeholder data to demonstrate structure |
| **CorporateTheme.json** | Official corporate theme pre-applied |
| **project_config.json** | Governance config with all checks enabled |

## Settings Pre-Configured

✅ Auto Date/Time: **DISABLED**  
✅ Bi-Directional Filters: **NOT USED**  
✅ Hardcoded Colors: **NOT USED** (theme applied)  
✅ Measure Descriptions: **PATTERN PROVIDED**  

## Support

Questions? Contact the BI Governance Team.
