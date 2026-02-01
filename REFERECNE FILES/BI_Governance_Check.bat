@echo off
TITLE AB InBev BI Factory - Compliance Officer
COLOR 0A

:: 1. Set the "Working Directory" to wherever this file is right now
cd /d "%~dp0"

echo ========================================================
echo      AB INBEV - BI COMPLIANCE CHECKER
echo ========================================================
echo.
echo Factory Location: "%~dp0"
echo.

:: 2. Run Python using "Relative Paths" 
:: (It looks for 'scripts' inside the current folder, not C:\)
python "%~dp0scripts\bi_governance_check.py" "%~dp0projects"

:: 3. Pause for user review
echo.
echo ========================================================
echo Check complete.
echo ========================================================
pause