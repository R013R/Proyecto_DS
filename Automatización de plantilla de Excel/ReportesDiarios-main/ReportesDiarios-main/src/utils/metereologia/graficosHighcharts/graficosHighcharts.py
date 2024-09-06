import sys
sys.path.append('../')
from functions import load_data, graficas_highchart
import os
from playwright.sync_api import sync_playwright
import time
from PIL import Image
import json
from datetime import datetime, timedelta

file_cfg_path = '../../../../configuracion.json'

# Leer el archivo JSON en un diccionario
with open(file_cfg_path, 'r') as file:
    data_dict = json.load(file)

ESTACIONES=data_dict["ESTACIONES"]
FECHA_INICIO = data_dict["FECHA_INICIO"]
FECHA_FINAL = data_dict["FECHA_FINAL"]
PATH_DATOS = f"../../../../{data_dict["PATH_DATOS"]}"
ESTACIONES = load_data(PATH_DATOS,ESTACIONES,FECHA_INICIO,FECHA_FINAL)

# Generar las gráficas de PM10 y PM25 con PRECIPITACIÓN
graficas_highchart(ESTACIONES, RESAMPLE_TIME="h", POLLUTION="PM10", variable="PRECIPITACION")
graficas_highchart(ESTACIONES, RESAMPLE_TIME="h", POLLUTION="PM25", variable="PRECIPITACION")

# Generar las gráficas de PM10 y PM25 con VELOCIDAD VIENTO
graficas_highchart(ESTACIONES, RESAMPLE_TIME="h", POLLUTION="PM10", variable="VELOCIDAD VIENTO")
graficas_highchart(ESTACIONES, RESAMPLE_TIME="h", POLLUTION="PM25", variable="VELOCIDAD VIENTO")

ESTACIONES=data_dict["ESTACIONES"]
# Modificación de las fechas
fecha_final_dt = datetime.strptime(data_dict["FECHA_FINAL"], "%Y-%m-%d %H:%M")
fecha_inicio_dt = fecha_final_dt - timedelta(days=7)
fecha_inicio_dt = fecha_inicio_dt.replace(hour=0, minute=0, second=0)

# Ajustar las fechas para el nuevo período
data_dict["FECHA_INICIO"] = fecha_inicio_dt.strftime("%Y-%m-%d %H:%M")
data_dict["FECHA_FINAL"] = (fecha_final_dt - timedelta(days=1)).replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M")

# Recargar las estaciones con las nuevas fechas
ESTACIONES = load_data(PATH_DATOS, ESTACIONES, data_dict["FECHA_INICIO"], data_dict["FECHA_FINAL"])


graficas_highchart(ESTACIONES, RESAMPLE_TIME="D", POLLUTION= "PM10")


for pagina in ["PM10_HORA", "PM25_HORA", "WS_PM10_HORA", "WS_PM25_HORA","PM10_DIA"]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        current_dir = os.getcwd()
        file_name = F'{pagina}.html'
        file_path = os.path.join(current_dir, file_name)
        file_url = f'file:///{file_path}'.replace('\\', '/')
        page.goto(file_url)
        time.sleep(3)
        screenshot_path = os.path.join(current_dir, f'imagen_{pagina}.png')
        page.screenshot(path=screenshot_path)
        browser.close()
        img = Image.open(screenshot_path)
        cropped_img = img.crop((0, 0, 800, 400))  # Recorta la imagen a 800x400 desde la esquina superior izquierda
        cropped_img.save(screenshot_path)  # Sobrescribe la imagen original con la recortada