@echo off
title SilvaDesk Pro
cd /d "%~dp0"
python main.py
if errorlevel 1 (echo ERROR. Ejecuta primero 1_INSTALAR.bat & pause)
