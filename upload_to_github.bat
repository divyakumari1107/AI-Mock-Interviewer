@echo off
echo ========================================================
echo Uploading AI-Mock-Interviewer to GitHub
echo ========================================================
echo.
cd /d "%~dp0"

echo Current Git Status:
git status
echo.

echo Pushing to GitHub repository...
git push -u origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo SUCCESS: All files have been uploaded to GitHub!
    echo ========================================================
) else (
    echo ========================================================
    echo If push failed, ensure you created the repo on GitHub:
    echo https://github.com/new
    echo ========================================================
)

pause
