@echo off
REM ================================================================
REM Build Wiki Knowledge Base
REM ================================================================
REM
REM This script generates/updates the Wiki from Power BI project 
REM documentation. Can be used for local testing or ADO integration.
REM
REM ================================================================

echo.
echo ================================================================
echo  Building Wiki Knowledge Base
echo ================================================================
echo.
:: Run Wiki builder
python "%~dp0Scripts\wiki_builder.py"

echo.
echo ================================================================
echo  Wiki build complete!
echo ================================================================
echo.
echo Wiki Location: %~dp0wiki\
echo.
echo To view the Wiki:
echo   1. Open wiki\Home.md in VS Code or Markdown viewer
echo   2. Or push to Azure DevOps Wiki repository
echo.
pause
