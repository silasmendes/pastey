@echo off
echo Starting Pastey Clipboard Manager...
echo.
echo Make sure you have installed the requirements:
echo   pip install -r requirements.txt
echo.
echo Press Ctrl+Shift+V to open clipboard history
echo Press Ctrl+C to exit the application
echo.

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    echo Using virtual environment...
    venv\Scripts\python.exe pastey.py
) else if exist "X:\Repos\pastey\venv\Scripts\python.exe" (
    echo Using configured virtual environment...
    X:\Repos\pastey\venv\Scripts\python.exe pastey.py
) else (
    echo Using system Python...
    python pastey.py
)

echo.
echo Pastey has been closed.
pause
