@echo off
echo Instalando dependencias con pip...
python3 -m pip install -r requirements.txt

echo Instalando Playwright...
python3 -m playwright install

echo Ejecutando la aplicación...
python3 interfaz.py

pause
