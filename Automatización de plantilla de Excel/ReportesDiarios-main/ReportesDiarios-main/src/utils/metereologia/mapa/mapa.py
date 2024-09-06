import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.cm import ScalarMappable
from windrose import WindroseAxes
import base64
from io import BytesIO
from PIL import Image
import folium
from folium import CustomIcon
from playwright.sync_api import sync_playwright
import time
import os
import json
import sys
sys.path.append('../')
from functions import load_data, poner_brujula_mapa

file_cfg_path = '../../../../configuracion.json'
with open(file_cfg_path, 'r') as file:
    data_dict = json.load(file)
ESTACIONES=data_dict["ESTACIONES"]
FECHA_INICIO = data_dict["FECHA_INICIO"]
FECHA_FINAL = data_dict["FECHA_FINAL"]
PATH_DATOS = f"../../../../{data_dict["PATH_DATOS"]}"
ESTACIONES = load_data(PATH_DATOS,ESTACIONES,FECHA_INICIO,FECHA_FINAL)
for ESTACION in ESTACIONES:
    ESTACION["DIRECCION_VIENTO"]=ESTACION['DF_DATOS']["DIRECCION VIENTO"].interpolate()
    ESTACION["DIRECCION_VIENTO"]=ESTACION["DIRECCION_VIENTO"].bfill().ffill()
    ESTACION["DIRECCION_VIENTO"]=np.array(ESTACION['DIRECCION_VIENTO'])
    ESTACION["VELOCIDAD_VIENTO"]=ESTACION['DF_DATOS']["VELOCIDAD VIENTO"].interpolate()
    ESTACION["VELOCIDAD_VIENTO"]=ESTACION["VELOCIDAD_VIENTO"].bfill().ffill()
    ESTACION["VELOCIDAD_VIENTO"]=np.array(ESTACION['VELOCIDAD_VIENTO'])


# Definimos los colores para cada rango de velocidad
colores = ['#2EAFFF', '#5450C1', '#05DD71', '#F36B36', '#6588B9', '#D763F2', 
           '#31DACD', '#F6473C', '#F8B062', '#8BE5D9', '#29ADF6', '#524DC1', 
           '#00E06E', '#FF6347']  

# Creamos un mapa de colores personalizado
cmap = ListedColormap(colores)

# Definimos los límites para cada rango de velocidad
limites = [0, 0.3, 1.6, 3.4, 5.5, 8, 10.9, 13.9, 16.9, 17, 20.5, 24.1, 28.3, 32.6, np.inf]

# Crear la normalización entre los límites
norm = BoundaryNorm(limites, cmap.N)

def generar_rosa_vientos(direccion_viento, velocidad_viento, nombre_estacion, serial):
    labels = ['E', 'ENE', 'NE', 'NNE', 'N', 'NNW', 'NW', 'WNW', 'W', 'WSW', 'SW', 'SSW', 'S','SSE', 'SE', 'ESE' ]
   
    angles = np.linspace(0, 360, len(labels), endpoint=False)
    fig = plt.figure(figsize=(4, 4), dpi=300)
    ax = WindroseAxes.from_ax(fig=fig)
    ax.bar(direccion_viento, velocidad_viento, normed=True, opening=0.8, edgecolor='white',
           bins=limites, cmap=cmap, nsector=16)
    plt.title(nombre_estacion, fontsize=16, color='black',
              bbox={'facecolor': 'white', 'alpha': 1.0, 'pad': 5, 'edgecolor': 'none'}, y=1.2)
    ax.set_thetagrids(angles, labels)
    # Guardar la imagen usando el número de serie
    filename = f"rosa_vientos_{serial}.png"
    fig.savefig(filename, format='png')

    # Convertir la imagen a base64 para usarla en el mapa (opcional)
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    
    plt.close(fig)  # Cerrar la figura para liberar memoria
    
    return img_base64


def generar_barra_colores():
    rangos = [
    (0, 0.2),
    (0.3, 1.6),
    (1.6, 3.4),
    (3.4, 5.5),
    (5.5, 8),
    (8, 10.9),
    (10.9, 13.9),
    (13.9, 16.9),
    (17, 20.5),
    (20.6, 24.1),
    (24.2, 28.3),
    (28.4, 32.6),
    (32.7, 100)
    ]
    # Definimos los límites de los rangos para el mapa de colores
    bounds = [rango[0] for rango in rangos] + [rangos[-1][1]]
    norm = BoundaryNorm(bounds, cmap.N)

    # Creamos la figura
    fig, ax = plt.subplots(figsize=(1.5, 4))

    # Creamos un objeto ScalarMappable y dibujamos la barra de colores
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # Solo para poder llamar a "fig.colorbar()"
    cbar = fig.colorbar(sm, ax=ax)

    # Establecemos las etiquetas de los ticks como los rangos de velocidades
    cbar.set_ticks([(b1 + b2) / 2 for b1, b2 in zip(bounds[:-1], bounds[1:])])
    cbar.set_ticklabels([f'{b1} - {b2} m/s' for b1, b2 in rangos[:-1]] + [f'> {bounds[-2]} m/s'])

    # Establecemos el título de la barra de colores
    cbar.set_label('Velocidad del viento (m/s)', rotation=270, labelpad=15)

    # Guardamos la imagen de la barra de colores
    colorbar_path = 'wind_speed_colorbar.png'
    plt.savefig(colorbar_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()


def agregar_marcador_mapa(mapa, latitud, longitud, img_base64):
    # Convertir la imagen base64 a una URL que Folium pueda usar directamente
    icon_url = f"data:image/png;base64,{img_base64}"
    
    # Definir las dimensiones del ícono
    icon = CustomIcon(
        icon_url,
        icon_size=(200, 200)  # Puedes ajustar el tamaño según tus necesidades
    )

    # Agregar el marcador con el ícono personalizado
    folium.Marker(
        [latitud, longitud],
        icon=icon
    ).add_to(mapa)

def crear_mapa(estaciones):
    mapa = folium.Map(location=[7.1193, -73.1227], zoom_start=14, control_scale=False, zoom_control=False)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False,
        control=False
    ).add_to(mapa)
    coordenadas = []
    
    for estacion in estaciones:
        coordenadas.append([estacion["LATITUD"], estacion["LONGITUD"]])
        img_base64 = generar_rosa_vientos(estacion["DIRECCION_VIENTO"], estacion["VELOCIDAD_VIENTO"], estacion["ESTACION"], estacion["SERIAL"])
        agregar_marcador_mapa(mapa, estacion["LATITUD"], estacion["LONGITUD"], img_base64)
    
    if len(coordenadas) > 1:
        mapa.fit_bounds([min(coordenadas), max(coordenadas)], padding=(200, 200))
    
    return mapa




def recortar_colorbar(path_colorbar="wind_speed_colorbar.png"):
    # Cargar la imagen de la barra de colores
    colorbar_image = Image.open(path_colorbar)

    # Definir las coordenadas para el recorte (ajusta según sea necesario)
    left = 140  # Ajusta según sea necesario
    top = 0  # Ajusta según sea necesario
    right = colorbar_image.width  # Ajusta según sea necesario
    bottom = colorbar_image.height - 30  # Ajusta según sea necesario

    # Recortar la imagen
    colorbar_cropped = colorbar_image.crop((left, top, right, bottom))

    # Guardar la imagen recortada en la misma ubicación, reemplazando la original
    colorbar_cropped.save(path_colorbar)

    # Retornar la imagen recortada (opcional)
    return colorbar_cropped

generar_barra_colores()
# Crear y mostrar el mapa
mapa = crear_mapa(ESTACIONES)
mapa.save('mapa_vientos.html')
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # Ajustar el tamaño de la página a la resolución deseada
    alto_img_mapa = 510*3
    ancho_img_mapa = 600*3
    page.set_viewport_size({"width": ancho_img_mapa, "height": alto_img_mapa})

    # Navegar a la URL del archivo HTML guardado
    # Obtén el directorio actual de trabajo
    current_dir = os.getcwd()
    # Construye la ruta al archivo HTML
    file_name = 'mapa_vientos.html'
    file_path = os.path.join(current_dir, file_name)
    # Convierte la ruta del archivo a una URL que pueda ser usada por Playwright
    file_url = f'file:///{file_path}'.replace('\\', '/')
    page.goto(file_url)
    time.sleep(3)
    page.screenshot(path="mapa_vientos.png", full_page=True)
    browser.close()
    # Cargar la imagen generada
    imagen = Image.open("mapa_vientos.png")
    # Definir el recorte: ajusta la altura para quitar un poco de la parte inferior
    ancho, alto = imagen.size
    recorte_inferior = 20  # Ajusta este valor según sea necesario
    area_recorte = (0, 0, ancho, alto - recorte_inferior)
    # Recortar y guardar la imagen
    imagen_recortada = imagen.crop(area_recorte)
    imagen_recortada.save("mapa_vientos.png")

# poner_brujula_mapa(path_mapa="mapa_vientos.png",path_brujula="../../image/brujula.jpg",brujula_size=(150,150))
recortar_colorbar("wind_speed_colorbar.png")
