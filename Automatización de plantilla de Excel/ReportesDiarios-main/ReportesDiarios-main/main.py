import subprocess
import concurrent.futures
import json
import pandas as pd
import os
from src.utils.metereologia.functions import load_data, escala_precipitacion, escala_vientos, tabla_promedio_metereologia,hourly_wind_speed_all_stations, hourly_precipitation_all_stations, get_texto_viento, texto_rosa_contaminacion
from datetime import datetime, timedelta
import xlwings as xw

def run_script(script):
    script_dir = f"./src/utils/metereologia/{script}/"
    try:
        result = subprocess.run(['python', f"{script}.py"], cwd=script_dir, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error en la ejecución de {script}.py:\n{e.stderr}"

scripts = ["mapa", "windy", "rosaContaminacion", "graficosHighcharts"]

# Utilizar ThreadPoolExecutor para ejecutar scripts en paralelo
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(run_script, scripts)
    for result in results:
        print(result)

print("Todos los scripts han finalizado.")

directorio_actual = os.getcwd()
file_cfg_path = 'configuracion.json'

# Leer el archivo JSON en un diccionario
with open(file_cfg_path, 'r') as file:
    data_dict = json.load(file)

ESTACIONES = data_dict["ESTACIONES"]
FECHA_INICIO = data_dict["FECHA_INICIO"]
FECHA_FINAL = data_dict["FECHA_FINAL"]
PATH_DATOS = data_dict["PATH_DATOS"]

ESTACIONES = load_data(PATH_DATOS, ESTACIONES, FECHA_INICIO, FECHA_FINAL)

df_precipitacion = escala_precipitacion()
df_viento = escala_vientos(ESTACIONES)
dfs_estaciones = tabla_promedio_metereologia(ESTACIONES)
dfs_precipitation_hourly = hourly_precipitation_all_stations(ESTACIONES)
dfs_wind_speed_hourly = hourly_wind_speed_all_stations(ESTACIONES)
TEXTO_VIENTO = get_texto_viento(FECHA_INICIO, FECHA_FINAL, ESTACIONES)

# Abre el archivo Excel existente
wb = xw.Book('reporte_diario_CAL.xlsm')
sheet_1 = wb.sheets['MET']
sheet_2 = wb.sheets["PNS- EF. - EM."]
sheet_3 = wb.sheets["MET (2)"]

sheet_1.activate()

# METEOROLOGY - REPORTING PERIOD
sheet_1.range('C2').value = f"METEOROLOGY - REPORTING PERIOD: {FECHA_INICIO} to {FECHA_FINAL}"

# Promedio de Meteorología - MLJ MET VI
sheet_1.range('O4').value = f"{FECHA_INICIO} to {FECHA_FINAL}"
for i, (medicion, estacion) in enumerate(zip(dfs_estaciones.iloc[:, 1], dfs_estaciones.iloc[:, 0]), start=5):
    sheet_1.range(f'L{i}').value = estacion
    sheet_1.range(f'O{i}').value = medicion

# Porcentaje rango de velocidades
for i, valor in enumerate(df_viento.iloc[:, 2], start=6):
    sheet_1.range(f'T{i}').value = valor

# Texto viento
sheet_1.range('L23').value = TEXTO_VIENTO

# GRAFICO PRECIPITACIONES 
nombres_estaciones = list(dfs_precipitation_hourly.keys())
sheet_1.range('AG4').value = nombres_estaciones[0]
sheet_1.range('AH4').value = nombres_estaciones[1]
columnas = ['AG', 'AH']
for i, (nombre, df) in enumerate(dfs_precipitation_hourly.items()):
    inicio_celda = f'{columnas[i]}5'
    valores_precipitacion = df.values
    sheet_1.range(inicio_celda).options(transpose=True).value = valores_precipitacion

# GRAFICO VELOCIDAD VIENTO 
nombres_estaciones = list(dfs_wind_speed_hourly.keys())
sheet_1.range('G70').value = nombres_estaciones[0]
sheet_1.range('H70').value = nombres_estaciones[1]
columnas = ['G', 'H']
for i, (nombre, df) in enumerate(dfs_wind_speed_hourly.items()):
    inicio_celda = f'{columnas[i]}71'
    valores_velocidad = df.values
    sheet_1.range(inicio_celda).options(transpose=True).value = valores_velocidad

# AÑADIR MAPA
ruta_relativa_mapa = 'src/utils/metereologia/mapa/mapa_vientos.png'
ruta_absoluta_mapa = os.path.join(directorio_actual, ruta_relativa_mapa)
alto_img_mapa = 510
ancho_img_mapa = 600
sheet_1.api.Application.Run("InsertPicture", ruta_absoluta_mapa, "C3", ancho_img_mapa, alto_img_mapa)

# DETERMINAR Y AÑADIR TODAS LAS ROSAS DE LOS VIENTOS AUTOMÁTICAMENTE
ruta_carpeta_mapas = os.path.join(directorio_actual, 'src/utils/metereologia/mapa/')
archivos = os.listdir(ruta_carpeta_mapas)

# Filtrar los archivos que comienzan con 'rosa_vientos_'
rosas_vientos = [archivo for archivo in archivos if archivo.startswith('rosa_vientos_')]
alto_img_mapa = 200
ancho_img_mapa = 200
# Insertar las imágenes de las rosas de los vientos en el Excel
for index, rosa_viento_file in enumerate(rosas_vientos):
    rosa_viento_path = os.path.join(ruta_carpeta_mapas, rosa_viento_file)
    coordenada = f"C{5 + index * 10}"  # Ajusta la posición de la celda si es necesario
    sheet_1.api.Application.Run("InsertPicture", rosa_viento_path, coordenada, ancho_img_mapa, alto_img_mapa)

# AÑADIR BARRA DE COLORES
ruta_relativa_barra_colores = 'src/utils/metereologia/mapa/wind_speed_colorbar.png'
ruta_absoluta_barra_colores = os.path.join(directorio_actual, ruta_relativa_barra_colores)
alto_barra_colores = 200  # Ajusta el tamaño según sea necesario
ancho_barra_colores = 100  # Ajusta el tamaño según sea necesario
sheet_1.api.Application.Run("InsertPicture", ruta_absoluta_barra_colores, "C15", ancho_barra_colores, alto_barra_colores)

# AÑADIR BRÚJULA
ruta_relativa_brujula = 'src/utils/image/brujula.jpg'
ruta_absoluta_brujula = os.path.join(directorio_actual, ruta_relativa_brujula)
alto_brujula = 100  # Ajusta el tamaño según sea necesario
ancho_brujula = 100  # Ajusta el tamaño según sea necesario
sheet_1.api.Application.Run("InsertPicture", ruta_absoluta_brujula, "C3", ancho_brujula, alto_brujula)

# AÑADIR FORECAST WINDY
ruta_relativa_windy = 'src/utils/metereologia/windy/windy.png'
ruta_absoluta_windy = os.path.join(directorio_actual, ruta_relativa_windy)
alto_img_windy = 160
ancho_img_windy = 1300
sheet_1.api.Application.Run("InsertPicture", ruta_absoluta_windy, "C50", ancho_img_windy, alto_img_windy)

sheet_2.activate()

# AÑADIR MAPA
ruta_relativa_mapa = 'src/utils/metereologia/mapa/mapa_vientos.png'
ruta_absoluta_mapa = os.path.join(directorio_actual, ruta_relativa_mapa)
alto_img_mapa = 315
ancho_img_mapa = 540
sheet_2.api.Application.Run("InsertPicture", ruta_absoluta_mapa, "B3", ancho_img_mapa, alto_img_mapa)

# DETERMINAR Y AÑADIR TODAS LAS ROSAS DE LOS VIENTOS AUTOMÁTICAMENTE
ruta_carpeta_mapas = os.path.join(directorio_actual, 'src/utils/metereologia/mapa/')
archivos = os.listdir(ruta_carpeta_mapas)

# Filtrar los archivos que comienzan con 'rosa_vientos_'
rosas_vientos = [archivo for archivo in archivos if archivo.startswith('rosa_vientos_')]
alto_img_mapa = 120
ancho_img_mapa = 120
# Insertar las imágenes de las rosas de los vientos en el Excel
for index, rosa_viento_file in enumerate(rosas_vientos):
    rosa_viento_path = os.path.join(ruta_carpeta_mapas, rosa_viento_file)
    coordenada = f"C{5 + index * 10}"  # Ajusta la posición de la celda si es necesario
    sheet_2.api.Application.Run("InsertPicture", rosa_viento_path, coordenada, ancho_img_mapa, alto_img_mapa)

# AÑADIR BARRA DE COLORES
ruta_relativa_barra_colores = 'src/utils/metereologia/mapa/wind_speed_colorbar.png'
ruta_absoluta_barra_colores = os.path.join(directorio_actual, ruta_relativa_barra_colores)
alto_barra_colores = 180  # Ajusta el tamaño según sea necesario
ancho_barra_colores = 90  # Ajusta el tamaño según sea necesario
sheet_2.api.Application.Run("InsertPicture", ruta_absoluta_barra_colores, "C15", ancho_barra_colores, alto_barra_colores)

# AÑADIR BRÚJULA
ruta_relativa_brujula = 'src/utils/image/brujula.jpg'
ruta_absoluta_brujula = os.path.join(directorio_actual, ruta_relativa_brujula)
alto_brujula = 60  # Ajusta el tamaño según sea necesario
ancho_brujula = 60  # Ajusta el tamaño según sea necesario
sheet_2.api.Application.Run("InsertPicture", ruta_absoluta_brujula, "C3", ancho_brujula, alto_brujula)


# PM10 HORA
alto_img_PM10_hora = 220
ancho_img_PM10_hora = 470
#WS
ruta_relativa_PM10_hora = 'src/utils/metereologia/graficosHighcharts/imagen_WS_PM10_HORA.png'
ruta_absoluta_PM10_hora = os.path.join(directorio_actual, ruta_relativa_PM10_hora)
sheet_2.api.Application.Run("InsertPicture", ruta_absoluta_PM10_hora, "L3", ancho_img_PM10_hora, alto_img_PM10_hora)

ruta_relativa_PM10_hora = 'src/utils/metereologia/graficosHighcharts/imagen_PM10_HORA.png'
ruta_absoluta_PM10_hora = os.path.join(directorio_actual, ruta_relativa_PM10_hora)
sheet_2.api.Application.Run("InsertPicture", ruta_absoluta_PM10_hora, "L3", ancho_img_PM10_hora, alto_img_PM10_hora)

# PM2.5 HORA
alto_img_PM25_hora = 230
ancho_img_PM25_hora = 470
#WS
ruta_relativa_PM25_hora = 'src/utils/metereologia/graficosHighcharts/imagen_WS_PM25_HORA.png'
ruta_absoluta_PM25_hora = os.path.join(directorio_actual, ruta_relativa_PM25_hora)
sheet_2.api.Application.Run("InsertPicture", ruta_absoluta_PM25_hora, "L21", ancho_img_PM25_hora, alto_img_PM25_hora)

ruta_relativa_PM25_hora = 'src/utils/metereologia/graficosHighcharts/imagen_PM25_HORA.png'
ruta_absoluta_PM25_hora = os.path.join(directorio_actual, ruta_relativa_PM25_hora)
sheet_2.api.Application.Run("InsertPicture", ruta_absoluta_PM25_hora, "L21", ancho_img_PM25_hora, alto_img_PM25_hora)

# PM10 DIA
ruta_relativa_PM10_dia = 'src/utils/metereologia/graficosHighcharts/imagen_PM10_DIA.png'
ruta_absoluta_PM10_dia = os.path.join(directorio_actual, ruta_relativa_PM10_dia)
alto_img_PM10_dia = 265
ancho_img_PM10_dia = 485
sheet_2.api.Application.Run("InsertPicture", ruta_absoluta_PM10_dia, "C38", ancho_img_PM10_dia, alto_img_PM10_dia)

# TEXTO 1
TEXTO_PG_2 = f"Durante el periodo analizado, las concentraciones horarias en las estación de "
NAME_ESTATION_0 = ESTACIONES[0]["ESTACION"]
PRECIPITACION_0 = ESTACIONES[0]["DF_DATOS"]['PRECIPITACION'].sum()
PM10_MIN_0 = ESTACIONES[0]["DF_DATOS"]['PM10'].min()
PM10_MAX_0 = ESTACIONES[0]["DF_DATOS"]['PM10'].max()
PM25_MIN_0 = ESTACIONES[0]["DF_DATOS"]['PM25'].min()
PM25_MAX_0 = ESTACIONES[0]["DF_DATOS"]['PM25'].max()
VELVIENTO_MAX_0 = ESTACIONES[0]["DF_DATOS"]['VELOCIDAD VIENTO'].max()

TEXTO_PG_2 += f"{NAME_ESTATION_0}, presentaron valores de PM10 que oscilaron entre {PM10_MIN_0:.2f} y {PM10_MAX_0:.2f} μg/m³ y de PM2.5 entre {PM25_MIN_0:.2f} y {PM25_MAX_0:.2f} μg/m³. "

NAME_ESTATION_1 = ESTACIONES[1]["ESTACION"]
PRECIPITACION_1 = ESTACIONES[1]["DF_DATOS"]['PRECIPITACION'].sum()
PM10_MIN_1 = ESTACIONES[1]["DF_DATOS"]['PM10'].min()
PM10_MAX_1 = ESTACIONES[1]["DF_DATOS"]['PM10'].max()
PM25_MIN_1 = ESTACIONES[1]["DF_DATOS"]['PM25'].min()
PM25_MAX_1 = ESTACIONES[1]["DF_DATOS"]['PM25'].max()
VELVIENTO_MAX_1 = ESTACIONES[1]["DF_DATOS"]['VELOCIDAD VIENTO'].max()

TEXTO_PG_2 += f"Para la estación {NAME_ESTATION_1} presentaron valores de PM10 entre {PM10_MIN_1:.2f} y {PM10_MAX_1:.2f} μg/m³ y de PM2.5 entre {PM25_MIN_1:.2f} y {PM25_MAX_1:.2f} μg/m³. "

if PM10_MAX_0 > PM10_MAX_1:
    PM10_MAX_T = PM10_MAX_0
    NAME_ESTATION_T = NAME_ESTATION_0
    PM10_MAX_TIME = ESTACIONES[0]["DF_DATOS"][ESTACIONES[0]["DF_DATOS"]['PM10'] == PM10_MAX_0].index[0]
else:
    PM10_MAX_T = PM10_MAX_1
    NAME_ESTATION_T = NAME_ESTATION_1
    PM10_MAX_TIME = ESTACIONES[1]["DF_DATOS"][ESTACIONES[1]["DF_DATOS"]['PM10'] == PM10_MAX_1].index[0]

TEXTO_PG_2 += f"El registro más alto de PM10 se obtuvo en la estación {NAME_ESTATION_T} a las {PM10_MAX_TIME}. "
TEXTO_PG_2 += f"Durante el periodo de estudio las estaciones presentaron registros de precipitación, en {NAME_ESTATION_0} se obtuvo un acumulado de {PRECIPITACION_0:.2f} mm, mientras que {NAME_ESTATION_1} registró un volumen de {PRECIPITACION_1:.2f} mm. "

if VELVIENTO_MAX_0 > VELVIENTO_MAX_1:
    VEL_VIENTO_MAX = VELVIENTO_MAX_0
else:
    VEL_VIENTO_MAX = VELVIENTO_MAX_1
TEXTO_PG_2 += f"Por último, los registros de velocidad del viento en la estación de mayor registro alcanzaron valores de {VEL_VIENTO_MAX:.2f} m/s."
sheet_2.range('B25').value = TEXTO_PG_2

# NUEVO DF CON 7 DIAS PARA SACAR PROMEDIO Y SUMA
ESTACIONES_PG_2 = data_dict["ESTACIONES"]

# Modificación de las fechas
fecha_final_dt = datetime.strptime(data_dict["FECHA_FINAL"], "%Y-%m-%d %H:%M")
fecha_final_dt=fecha_final_dt - timedelta(days=1)
fecha_inicio_pg_2_dt = fecha_final_dt - timedelta(days=6)  # 7 días de diferencia
fecha_inicio_pg_2_dt = fecha_inicio_pg_2_dt.replace(hour=0, minute=0, second=0)
FECHA_INICIO_PG_2 = fecha_inicio_pg_2_dt.strftime("%Y-%m-%d %H:%M")
FECHA_FINAL_PG_2 = fecha_final_dt.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M")
ESTACIONES_PG_2 = load_data(PATH_DATOS, ESTACIONES_PG_2, FECHA_INICIO_PG_2, FECHA_FINAL_PG_2)

sheet_2.range('L50').value = f"{FECHA_INICIO_PG_2} to {FECHA_FINAL_PG_2}"
# PM10 DATA
df_resultado_final = pd.DataFrame()
for estacion in ESTACIONES_PG_2:
    df_datos = estacion["DF_DATOS"]
    NAME_STATION = estacion["ESTACION"]
    df_datos.index = pd.to_datetime(df_datos.index)
    media_diaria = df_datos['PM10'].resample('D').mean()
    df_temporal = media_diaria.to_frame().T
    df_temporal.columns = df_temporal.columns.strftime('%d/%m/%Y')
    df_temporal['Promedio del periodo'] = df_temporal.mean(axis=1)
    df_temporal.index = [NAME_STATION]
    df_resultado_final = pd.concat([df_resultado_final, df_temporal])

# Escribir los nombres de las estaciones en la columna B
sheet_2.range('B52').value = df_resultado_final.index[0]
sheet_2.range('B53').value = df_resultado_final.index[1]
# Escribir los nombres de las columnas de fechas y el promedio del periodo
sheet_2.range('C51:I51').value = df_resultado_final.columns[:-1].to_list()
sheet_2.range('J50').value = "Promedio del periodo"
# Escribir los valores correspondientes en cada celda desde C52 a I53
sheet_2.range('C52').options(expand='table').value = df_resultado_final.iloc[:, :-1].values
sheet_2.range('J52').value = df_resultado_final.iloc[0, -1]
sheet_2.range('J53').value = df_resultado_final.iloc[1, -1]

# PRECIPITACION DATA
df_resultado_final_precipitacion = pd.DataFrame()
for estacion in ESTACIONES_PG_2:
    df_datos = estacion["DF_DATOS"]
    NAME_STATION = estacion["ESTACION"]
    df_datos.index = pd.to_datetime(df_datos.index)
    suma_diaria = df_datos['PRECIPITACION'].resample('D').sum()
    df_temporal = suma_diaria.to_frame().T
    df_temporal.columns = df_temporal.columns.strftime('%d/%m/%Y')
    df_temporal['Total del periodo'] = df_temporal.sum(axis=1)
    df_temporal.index = [NAME_STATION]
    df_resultado_final_precipitacion = pd.concat([df_resultado_final_precipitacion, df_temporal])

# Escribir los nombres de las estaciones en la columna B
sheet_2.range('B57').value = df_resultado_final_precipitacion.index[0]
sheet_2.range('B58').value = df_resultado_final_precipitacion.index[1]
# Escribir los nombres de las columnas de fechas y el total del periodo
sheet_2.range('C56:I56').value = df_resultado_final_precipitacion.columns[:-1].to_list()
sheet_2.range('J55').value = "Total del periodo"
# Escribir los valores correspondientes en cada celda desde C57 a I58
sheet_2.range('C57').options(expand='table').value = df_resultado_final_precipitacion.iloc[:, :-1].values
sheet_2.range('J57').value = df_resultado_final_precipitacion.iloc[0, -1]
sheet_2.range('J58').value = df_resultado_final_precipitacion.iloc[1, -1]

# ALARMAS DATA
NAME_1 = ESTACIONES[0]["ESTACION"]
NAME_2 = ESTACIONES[1]["ESTACION"]
sheet_2.range('L52').value = NAME_1
sheet_2.range('L53').value = NAME_2

sheet_2.range('L56').value = NAME_1
sheet_2.range('L57').value = NAME_2

sheet_2.range('L59').value = f"Para las estaciones {NAME_1} y {NAME_2} no se registró excedencias sobre el límite establecido de la Resolución 2254 de 2017 (MADS)."

sheet_3.activate()

# AÑADIR MAPA
ruta_relativa_mapa = 'src/utils/metereologia/rosaContaminacion/mapa_rosa_contaminacion.png'
ruta_absoluta_mapa = os.path.join(directorio_actual, ruta_relativa_mapa)
alto_img_mapa = 680
ancho_img_mapa = 1340
sheet_3.api.Application.Run("InsertPicture", ruta_absoluta_mapa, "B5", ancho_img_mapa, alto_img_mapa)

# AÑADIR BARRA DE COLORES
ruta_relativa_barra_colores = 'src/utils/metereologia/rosaContaminacion/barra.png'
ruta_absoluta_barra_colores = os.path.join(directorio_actual, ruta_relativa_barra_colores)
alto_barra_colores = 200  # Ajusta el tamaño según sea necesario
ancho_barra_colores = 100  # Ajusta el tamaño según sea necesario
sheet_3.api.Application.Run("InsertPicture", ruta_absoluta_barra_colores, "B5", ancho_barra_colores, alto_barra_colores)

sheet_3.api.Application.Run("InsertPicture", ruta_absoluta_brujula, "C5", ancho_brujula, alto_brujula)
# AÑADIR TEXTO
sheet_3.range('B50').value = texto_rosa_contaminacion(ESTACIONES)


##pasar todo a una carpeta


import shutil
# Obtener la fecha y hora actual en el formato aaaammddHHMMSS
fecha_hora_actual = datetime.now().strftime('%Y%m%d%H%M%S')

# Crear la ruta de la carpeta de destino
carpeta_destino = os.path.join('reportes', fecha_hora_actual)
carpeta_resources = os.path.join(carpeta_destino, 'resources')

# Crear las carpetas de destino
os.makedirs(carpeta_resources, exist_ok=True)
wb.save(carpeta_destino+'/reporte_generado.xlsm')

# Lista de carpetas a mover
carpetas_a_mover = [
    'src/utils/metereologia/graficosHighcharts',
    'src/utils/metereologia/mapa',
    'src/utils/metereologia/rosaContaminacion',
    'src/utils/metereologia/windy',
    'comprimidos',
    'datos'
]

# Lista de archivos a excluir
archivos_excluir = [
    'graficosHighcharts.py',
    'mapa.py',
    'rosaContaminacion.py',
    'script.R',
    'windy.py',
    '.gitkeep'
]

def mover_archivo_fuente_a_destino(archivo_fuente, archivo_destino):
    ruta_destino = os.path.dirname(archivo_destino)
    if not os.path.exists(ruta_destino):
        os.makedirs(ruta_destino)
    shutil.move(archivo_fuente, archivo_destino)

# Mover archivos y carpetas
for carpeta in carpetas_a_mover:
    if os.path.exists(carpeta):
        for root, dirs, files in os.walk(carpeta):
            for file in files:
                archivo_completo = os.path.join(root, file)
                archivo_relativo = os.path.relpath(archivo_completo, carpeta)
                archivo_destino = os.path.join(carpeta_resources, archivo_relativo)
                # Excluir archivos específicos
                if not any(archivo_completo.endswith(excluir) for excluir in archivos_excluir):
                    mover_archivo_fuente_a_destino(archivo_completo, archivo_destino)

            # Eliminar carpetas vacías
            if not os.listdir(root):
                os.rmdir(root)

print(f"Todos los archivos se han movido a la carpeta {carpeta_destino}.")
