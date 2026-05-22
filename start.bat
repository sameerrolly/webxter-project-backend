@echo off
echo Starting Django backend with Python 3.12 venv...
echo.

REM Always use the venv Python explicitly — never the system Python
venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
