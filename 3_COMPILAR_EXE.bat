@echo off
chcp 65001 >nul
title SilvaDesk Pro - Compilar .exe
color 1F
cd /d "%~dp0"

echo.
echo ============================================================
echo  SilvaDesk Pro - Generando ejecutable con PyInstaller
echo  Sistema de Licencias incluido (utils\license.py)
echo ============================================================
echo.

REM Verificar PyInstaller
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] PyInstaller no encontrado. Instalando...
    pip install pyinstaller
)

echo [1/1] Compilando SilvaDesk Pro.exe ...
echo.

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "SilvaDesk Pro" ^
  --icon "assets\icon.ico" ^
  --add-data "assets;assets" ^
  --add-data "tabs;tabs" ^
  --add-data "utils;utils" ^
  --hidden-import customtkinter ^
  --hidden-import PIL ^
  --hidden-import PIL._tkinter_finder ^
  --hidden-import tkinter ^
  --hidden-import tkinter.ttk ^
  --hidden-import sqlite3 ^
  --hidden-import json ^
  --hidden-import reportlab ^
  --hidden-import reportlab.graphics ^
  --hidden-import reportlab.platypus ^
  --hidden-import reportlab.lib ^
  --hidden-import docx ^
  --hidden-import docx.oxml ^
  --hidden-import docx.shared ^
  --hidden-import lxml ^
  --hidden-import lxml.etree ^
  --hidden-import winreg ^
  --hidden-import hmac ^
  --hidden-import hashlib ^
  --hidden-import base64 ^
  --collect-all customtkinter ^
  --collect-all reportlab ^
  --collect-all docx ^
  --exclude-module PyQt5 ^
  --exclude-module PyQt6 ^
  --exclude-module PySide2 ^
  --exclude-module PySide6 ^
  --exclude-module kivy ^
  --exclude-module kivymd ^
  --noconfirm ^
  main.py

echo.
if exist "dist\SilvaDesk Pro.exe" (
    echo ============================================================
    echo  [OK] Ejecutable generado exitosamente:
    echo  dist\SilvaDesk Pro.exe
    echo ============================================================
    echo.
    start "" "dist\"
) else (
    echo ============================================================
    echo  [ERROR] No se genero el .exe. Revisa los mensajes arriba.
    echo ============================================================
)

pause
