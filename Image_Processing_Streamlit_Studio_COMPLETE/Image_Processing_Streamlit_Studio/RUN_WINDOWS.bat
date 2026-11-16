@echo off
setlocal
cd /d "%~dp0"
echo Image Processing Studio - Setup and Launch
echo.
where py >nul 2>&1
if %errorlevel%==0 (
    set "PY=py"
) else (
    set "PY=python"
)
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
    echo Could not install requirements. Check Python installation and internet access.
    pause
    exit /b 1
)
%PY% -m streamlit run app.py
if errorlevel 1 pause
