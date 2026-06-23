@echo off
chcp 65001 >nul
title SilvaDesk Pro – Compilar Generador de Licencias

echo.
echo ============================================================
echo   SilvaDesk Pro – Generador de Licencias
echo   Compilando a .EXE standalone con PyInstaller...
echo ============================================================
echo.

REM Verificar que PyInstaller esté disponible
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller no encontrado. Instalando...
    pip install pyinstaller
)

REM Compilar el generador privado
echo [1/1] Compilando license_generator_PRIVADO.exe ...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "SilvaDesk_KeyGen_PRIVADO" ^
    --distpath "dist\KeyGen" ^
    --workpath "build\KeyGen" ^
    --specpath "build\KeyGen" ^
    --clean ^
    license_generator_PRIVADO.py

echo.
if exist "dist\KeyGen\SilvaDesk_KeyGen_PRIVADO.exe" (
    echo ============================================================
    echo   [OK] EXE generado exitosamente:
    echo   dist\KeyGen\SilvaDesk_KeyGen_PRIVADO.exe
    echo.
    echo   IMPORTANTE: Guarda este .exe en un lugar seguro.
    echo   NO lo compartas ni lo subas a GitHub.
    echo ============================================================
    echo.
    start "" "dist\KeyGen\"
) else (
    echo [ERROR] No se pudo generar el .exe. Revisa los mensajes arriba.
)

pause
