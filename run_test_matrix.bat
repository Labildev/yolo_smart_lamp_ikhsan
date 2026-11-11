@echo off
title Pengujian Matriks Bab V - Lampu Pintar YOLOv8
color 0b

echo ==============================================================================
echo   SUITE PENGUJIAN OTOMATIS MATRIKS BAB V SKRIPSI (YOLOV8)
echo   Peneliti: Ikhsan Wahyudi (235520110043) - Universitas Almuslim
echo ==============================================================================
echo.
echo Pastikan server Flask sudah berjalan sebelum memulai pengujian ini!
echo.

set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"

cd /d "%~dp0"

if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe tools\test_bab5_matrix.py %*
) else if exist server\venv\Scripts\python.exe (
    server\venv\Scripts\python.exe tools\test_bab5_matrix.py %*
) else (
    python tools\test_bab5_matrix.py %*
)

pause

