@echo off
REM Build DevSync standalone executable for Windows

echo ================================
echo DevSync Build Script
echo ================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

echo Building DevSync executable...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build with PyInstaller
pyinstaller --name="DevSync" ^
    --windowed ^
    --onefile ^
    --add-data "version.txt;." ^
    --add-data "CHANGELOG.md;." ^
    --add-data "config.yaml;." ^
    --hidden-import="PyQt6.QtCore" ^
    --hidden-import="PyQt6.QtGui" ^
    --hidden-import="PyQt6.QtWidgets" ^
    --hidden-import="github" ^
    --hidden-import="git" ^
    --hidden-import="yaml" ^
    --hidden-import="markdown" ^
    --hidden-import="keyring" ^
    devsync_gui.py

if errorlevel 1 (
    echo.
    echo Build FAILED!
    pause
    exit /b 1
)

echo.
echo ================================
echo Build completed successfully!
echo ================================
echo.
echo Executable location: dist\DevSync.exe
echo.
echo You can now distribute the single DevSync.exe file.
echo No Python installation required on target machines.
echo.
pause
