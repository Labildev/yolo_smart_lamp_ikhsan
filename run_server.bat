@echo off
title Peladen Flask dan Web Dashboard - Lampu Pintar YOLOv8
color 0a

echo ==============================================================================
echo   PELADEN LOKAL SISTEM KENDALI LAMPU PINTAR (FLASK + YOLOV8)
echo   Peneliti: Ikhsan Wahyudi (235520110043) - Universitas Almuslim
echo ==============================================================================
echo.

set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"

cd /d "%~dp0server"

if exist "%~dp0venv\Scripts\python.exe" (
    echo [OK] Menggunakan Virtual Environment: venv
    "%~dp0venv\Scripts\python.exe" app.py
) else if exist venv\Scripts\python.exe (
    echo [OK] Menggunakan Virtual Environment: server\venv
    venv\Scripts\python.exe app.py
) else (
    echo [INFO] Menjalankan dengan Python sistem global...
    python app.py
)

pause

