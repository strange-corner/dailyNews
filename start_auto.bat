
: Erstellt die heutige Ausgabe vollautomatisch

@echo off
cd /d "%~dp0"

"python.exe" "src\mainauto.py"

if errorlevel 1 (
    echo.
    echo Fehler beim Ausfuehren!
)

pause
