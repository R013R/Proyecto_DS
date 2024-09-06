import pandas as pd
import sys
sys.path.append('../')
from functions import load_data, poner_brujula_mapa
import json
import os
import subprocess
from PIL import Image
import folium
from playwright.sync_api import sync_playwright
import time

file_cfg_path = '../../../../configuracion.json'
with open(file_cfg_path, 'r') as file:
    data_dict = json.load(file)
ESTACIONES=data_dict["ESTACIONES"]
FECHA_INICIO = data_dict["FECHA_INICIO"]
FECHA_FINAL = data_dict["FECHA_FINAL"]
PATH_DATOS = f"../../../../{data_dict["PATH_DATOS"]}"
ESTACIONES = load_data(PATH_DATOS,ESTACIONES,FECHA_INICIO,FECHA_FINAL)

# for ESTACION in ESTACIONES:
#     df= pd.DataFrame(ESTACION["DF_DATOS"])
#     df.index = pd.to_datetime(df.index)
#     df.index = df.index.map(lambda x: x.strftime('%d/%m/%Y ') + str(x.hour) + x.strftime(':%M'))
#     df.index.names = ['date']
#     df.rename(columns={'VELOCIDAD VIENTO': 'ws', 'DIRECCION VIENTO': 'wd'}, inplace=True)
#     df.to_csv(f"{ESTACION["SERIAL"]}.csv")

#     # Ruta completa al ejecutable Rscript
#     rscript_path = r'C:\Program Files\R\R-4.3.3\bin\Rscript.exe'
#     # Ruta al script de R
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     ruta_script_R = os.path.join(dir_path, 'script.R')
#     # Nombre del archivo CSV que será variable
#     nombre_csv = f"{ESTACION["ESTACION"]}.csv"
#     # Comando para ejecutar el script de R
#     comando = [rscript_path, ruta_script_R, nombre_csv]
#     # Ejecutar el comando
#     result = subprocess.run(comando, capture_output=True, text=True)
#     # Imprimir la salida y errores
#     print("STDOUT:", result.stdout)
#     print("STDERR:", result.stderr)


for ESTACION in ESTACIONES:
    df = pd.DataFrame(ESTACION["DF_DATOS"])
    df.index = pd.to_datetime(df.index)
    df.index = df.index.map(lambda x: x.strftime('%d/%m/%Y ') + str(x.hour) + x.strftime(':%M'))
    df.index.names = ['date']
    df.rename(columns={'VELOCIDAD VIENTO': 'ws', 'DIRECCION VIENTO': 'wd'}, inplace=True)
    
    # Guardar el DataFrame en CSV
    csv_filename = f"{ESTACION['SERIAL']}.csv"
    df.to_csv(csv_filename)

    # Ruta completa al ejecutable Rscript
    rscript_path=data_dict["R_PATH"]
    # rscript_path = r'C:\Program Files\R\R-4.3.3\bin\Rscript.exe'
    # Ruta al script de R
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ruta_script_R = os.path.join(dir_path, 'script.R')
    
    # Nombre base para los archivos, sin la extensión
    nombre_base = ESTACION["SERIAL"]

    # Comando para ejecutar el script de R
    comando = [rscript_path, ruta_script_R, nombre_base]

    # Ejecutar el comando
    result = subprocess.run(comando, capture_output=True, text=True)
    
    # Imprimir la salida y errores
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)


    # Cargar la imagen
    img = Image.open(f"{nombre_base}.png")

    # Primer recorte: desde el pixel 50 al 600 en x, y desde el pixel 50 al 650 en y
    xi=50
    xf=850
    yi=100
    yf=900

    crop_1 = img.crop((xi, yi, xf, yf))  # left, upper, right, lower

    xi=860
    xf=1024
    yi=180
    yf=910
    # Segundo recorte: desde el pixel 660 al 720 en x, y desde el pixel 50 al 650 en y
    crop_2 = img.crop((xi, yi, xf, yf))

    # Crear una nueva imagen con fondo blanco
    crop_2_with_background = Image.new("RGB", crop_2.size, (255, 255, 255))
    crop_2_with_background.paste(crop_2, (0, 0), mask=crop_2.split()[3] if crop_2.mode == 'RGBA' else None)

    # Guardar las imágenes recortadas
    crop_1.save(f"{nombre_base}.png")
    crop_2_with_background.save("barra.png")



def crear_mapa(estaciones):
    
    mapa = folium.Map(location=[estaciones[0]["LATITUD"], estaciones[0]["LONGITUD"]], zoom_start=14)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False,
        control=True
    ).add_to(mapa)
    coordenadas = []
    
    for estacion in estaciones:
        coordenadas.append([estacion["LATITUD"], estacion["LONGITUD"]])
        icon_path = f"{estacion['SERIAL']}.png"
        icon = folium.CustomIcon(icon_path, icon_size=(200, 200))
        folium.Marker(
            location=[estacion["LATITUD"], estacion["LONGITUD"]],
            icon=icon
        ).add_to(mapa)
    if len(coordenadas)>1:
        mapa.fit_bounds([min(coordenadas), max(coordenadas)], padding=(200, 200))
    return mapa


mapa = crear_mapa(ESTACIONES)
mapa.save('mapa_rosa_contaminacion.html')



with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    current_dir = os.getcwd()
    file_name = 'mapa_rosa_contaminacion.html'
    file_path = os.path.join(current_dir, file_name)
    # Convierte la ruta del archivo a una URL que pueda ser usada por Playwright
    file_url = f'file:///{file_path}'.replace('\\', '/')
    page.goto(file_url)
    time.sleep(3)
    page.screenshot(path='mapa_rosa_contaminacion.png')
    browser.close()


# poner_brujula_mapa(path_mapa='mapa_rosa_contaminacion.png')
