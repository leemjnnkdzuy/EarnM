@echo off
setlocal enabledelayedexpansion

if not exist "venv" (
    echo Môi trường ảo chưa được tạo. Đang tạo...
    python setup_env.py
    if errorlevel 1 (
        echo Lỗi khi tạo môi trường ảo!
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Lỗi khi kích hoạt môi trường ảo!
    pause
    exit /b 1
)

echo Môi trường đã sẵn sàng!
echo.
echo Đang chạy chương trình...
echo.

python main.py
if errorlevel 1 (
    echo.
    echo Chương trình kết thúc với lỗi!
) else (
    echo.
    echo Chương trình đã chạy xong!
)

deactivate
pause
