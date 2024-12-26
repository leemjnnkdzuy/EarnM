@echo off
setlocal enabledelayedexpansion

echo Danh sách Python đã cài đặt:
echo [1] Python 3.9
echo [2] Python 3.10
echo [3] Python 3.11
echo [4] Python 3.12
echo.

set /p choice="Chọn phiên bản Python (1-4): "

if "%choice%"=="1" (
    set "PYTHON_PATH=C:\Python39"
) else if "%choice%"=="2" (
    set "PYTHON_PATH=C:\Python310"
) else if "%choice%"=="3" (
    set "PYTHON_PATH=C:\Python311"
) else if "%choice%"=="4" (
    set "PYTHON_PATH=C:\Python312"
) else (
    echo Lựa chọn không hợp lệ!
    pause
    exit /b 1
)

if not exist "!PYTHON_PATH!\python.exe" (
    echo Không tìm thấy Python tại !PYTHON_PATH!
    pause
    exit /b 1
)

set "PATH=!PYTHON_PATH!;!PYTHON_PATH!\Scripts;!PATH!"
echo Đã chuyển sang !PYTHON_PATH!
python --version

rmdir /s /q venv 2>nul
echo Đang tạo lại môi trường ảo...
python setup_env.py

pause
