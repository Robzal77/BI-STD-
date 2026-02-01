@echo off
TITLE AB InBev BI Factory - Governance Car Wash
COLOR 07

:: Car Wash Mode: Batch validate ALL reports in REFERECNE FILES
:: This logs all results to CSV for analysis

cd /d "%~dp0"

echo.
echo ========================================================
echo       AB INBEV - GOVERNANCE CAR WASH
echo ========================================================
echo.
echo  This tool scans ALL reports in 'REFERECNE FILES'
echo  and logs governance check results to CSV.
echo.
echo  Use this to:
echo    - Get statistics on report compliance
echo    - Track which reports need cleanup
echo    - Audit existing report quality
echo.
echo ========================================================
echo.
echo  Running batch validation...
echo.

:: Run governance check on REFERECNE FILES
python "%~dp0validators\check_governance.py" "%~dp0REFERECNE FILES"

echo.
echo ========================================================
echo  Car Wash Complete.
echo  Results logged to: logs\governance_log.csv
echo ========================================================
echo.
pause
