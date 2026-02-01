@echo off
REM ================================================================
REM Power BI Batch Governance Test
REM ================================================================
REM
REM This script runs governance checks on all PBIP files in the
REM "Batch Test PBI" folder and generates a comprehensive summary.
REM
REM Results are saved to: logs\batch_run_results.csv
REM
REM ================================================================

echo.
echo ================================================================
echo  POWER BI BATCH GOVERNANCE TEST
echo ================================================================
echo.
echo This will test all reports in: Batch Test PBI\
echo.
echo Press Ctrl+C to cancel, or
pause

python "%~dp0scripts\batch_test_runner.py"

echo.
echo ================================================================
echo  Batch test complete
echo ================================================================
echo.
echo Review the summary above, or check:
echo   - logs\batch_run_results.csv (detailed results)
echo.
pause
