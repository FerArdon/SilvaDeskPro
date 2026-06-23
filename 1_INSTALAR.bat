@echo off
title SilvaDesk Pro – Instalacion
color 1F
echo.
echo  ============================================================
echo   SilvaDesk Pro v1.0.0 – Instalador de dependencias
echo   SEDCAF / FEMA Honduras
echo  ============================================================
echo.
python --version
if errorlevel 1 (echo ERROR: Instala Python desde https://python.org y marca "Add to PATH" & pause & exit /b 1)
echo.
echo  Instalando dependencias...
pip install customtkinter reportlab Pillow openpyxl pyinstaller --upgrade --quiet
if errorlevel 1 (echo ERROR al instalar. Ejecuta como Administrador. & pause & exit /b 1)
echo.
echo  Instalacion completada. Ejecuta: 2_EJECUTAR.bat
echo.
pause
