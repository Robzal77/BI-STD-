@echo off
TITLE AB InBev BI Factory - Generate Live Documentation
COLOR 07

:: Generate comprehensive live documentation for all reports in Project/

cd /d "%~dp0"

echo.
echo ========================================================
echo       AB INBEV - LIVE DOCUMENTATION GENERATOR
echo ========================================================
echo.
echo  This tool automatically generates comprehensive
echo  markdown documentation for all Power BI reports.
echo.
echo  Generated documentation includes:
echo    - Overview and metadata
echo    - Data model relationships
echo    - All measures with DAX formulas
echo    - Governance compliance status
echo.
echo ========================================================
echo.
echo  Generating documentation...
echo.

:: Run documentation generator on Project directory
python "%~dp0scripts\generate_live_docs.py" "%~dp0Project"

echo.
echo ========================================================
echo  Documentation generation complete!
echo  Check each report folder for DOCUMENTATION.md
echo ========================================================
echo.
pause
