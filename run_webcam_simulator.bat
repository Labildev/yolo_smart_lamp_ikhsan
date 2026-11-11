@echo off
title Simulator Webcam Real-Time - Lampu Pintar YOLOv8
color 0e

echo ==============================================================================
echo   SIMULATOR WEBCAM REAL-TIME (PENGUJIAN TANPA ESP32-S3)
echo   Peneliti: Ikhsan Wahyudi (235520110043) - Universitas Almuslim
echo ==============================================================================
echo.
echo Pastikan server Flask sudah berjalan sebelum memulai simulator ini!
echo Petunjuk:
echo  - Tekan SPASI pada jendela kamera untuk mensimulasikan gerakan PIR
echo  - Tekan Q atau ESC untuk keluar
echo.

set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"

cd /d "%~dp0"

if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe tools\webcam_simulator.py
) else if exist server\venv\Scripts\python.exe (
    server\venv\Scripts\python.exe tools\webcam_simulator.py
) else (
    python tools\webcam_simulator.py
)

pause

