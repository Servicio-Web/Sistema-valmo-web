@echo off

rem Activa el entorno virtual
call "C:\Users\Servicio Web\Documents\SistemaValmoV5\venv\Scripts\activate"

rem Navega al directorio del proyecto Django
cd "C:\Users\Servicio Web\Documents\SistemaValmoV5\Servicio-web-valmo"

timeout /t 10 > nul

rem Ejecuta el servidor de Django
python manage.py runserver 0.0.0.0:8000

rem Desactiva el entorno virtual al salir
deactivate

rem Pausa para mantener la ventana abierta
pause
