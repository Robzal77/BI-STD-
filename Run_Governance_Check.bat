@echo off
TITLE AB InBev BI Factory - Compliance Officer
COLOR 07

:: 1. Set the "Working Directory" to wherever this file is right now
cd /d "%~dp0"

echo.
echo ========================================================
echo       AB INBEV - BI COMPLIANCE CHECKER
echo ========================================================
echo.
echo Factory Location: "%~dp0"
echo.
echo  This tool will scan the 'Project' directory for
echo  Power BI Project (.pbip) semantic models.
echo.
echo  CHECKS PERFORMED:
echo    1. Performance: Auto Date/Time must be DISABLED.
echo    2. Logic: No Bi-Directional Relationships allowed.
echo    3. Documentation: All Measures must have Description properties.
echo.
echo ========================================================
echo.
echo  Running Validation Script...
echo.

:: 2. Run Python using "Relative Paths"
:: Scan the 'Project' directory specifically
python "%~dp0validators\check_governance.py" "%~dp0Project"

echo.
echo ========================================================
echo  Validation Complete.
echo ========================================================
echo.
pause
