@echo off
set EXE=busqueda_app_desktop.exe
set SRC_DIR=%~dp0dist
set DST_DIR=%USERPROFILE%\Desktop

if not exist "%SRC_DIR%\%EXE%" (
    echo No se encontró %EXE% en la carpeta dist. Asegúrate de haberlo generado con PyInstaller.
    pause
    exit /b
)

copy /Y "%SRC_DIR%\%EXE%" "%DST_DIR%\%EXE%"
echo ¡Instalación completada! El acceso directo está en tu escritorio.
pause
