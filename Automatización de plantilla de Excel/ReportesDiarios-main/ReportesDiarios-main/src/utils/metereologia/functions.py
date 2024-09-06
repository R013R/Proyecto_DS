import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from PIL import Image

def load_csv(path,indice_columnas="fecha"):
  df=pd.read_csv(path,index_col=indice_columnas)
  df.set_index(pd.to_datetime(df.index, dayfirst=False),inplace=True)
  for column in df.columns:
    df.rename(columns = {column:int(float(column))}, inplace = True)
  return df

def load_data(path,ESTACIONES,FECHA_INICIO,FECHA_FINAL):
    for ESTACION in ESTACIONES:
        df_datos = load_csv(f"{path}/{ESTACION["SERIAL"]}.csv",indice_columnas="fecha")
        df_info = pd.read_csv(f"{path}/{ESTACION["SERIAL"]}_info.csv")

        df_datos=df_datos.loc[:,df_info["VARIABLE"].to_list()]
        for column in df_datos.columns:
            CAL_SPAN=df_info[df_info["VARIABLE"]==column]["CAL_SPAN"].iloc[0]
            NOMBRE=df_info[df_info["VARIABLE"]==column]["NOMBRE"].iloc[0]
            df_datos[column]=df_datos[column]*CAL_SPAN
            df_datos.rename(columns = {column:NOMBRE}, inplace = True)
            df_datos=df_datos.loc[FECHA_INICIO:FECHA_FINAL]
        ESTACION["DF_DATOS"]=df_datos
    return ESTACIONES

def escala_precipitacion():
    data = {
        'Escasa': {'Precipitacion diaria': '0-5'},
        'Ligera': {'Precipitacion diaria': '6-10'},
        'Moderada': {'Precipitacion diaria': '11-20'},
        'Fuerte': {'Precipitacion diaria': '21-50'},
        'Muy fuerte': {'Precipitacion diaria': '51-70'},
        'Intensa': {'Precipitacion diaria': '>70'}
    }
    # Convertir el diccionario de diccionarios en un DataFrame
    df_precipitacion = pd.DataFrame.from_dict(data, orient='index').reset_index()
    df_precipitacion.columns = ['Denominacion', 'Precipitacion diaria']
    return df_precipitacion

def escala_vientos(ESTACIONES):
    df_viento = pd.DataFrame([
        ["Calma", "0 - 0.2"],
        ["Aire Ligero", "0.3 - 1.6"],
        ["Brisa Ligera", "1.6 - 3.4"],
        ["Brisa Suave", "3.4 - 5.5"],
        ["Brisa Moderada", "5.5 - 8"],
        ["Brisa Fresca", "8 - 10.9"],
        ["Brisa Fuerte", "10.9 - 13.9"],
        ["Viento Casi temporal", "13.9 - 16.9"],
        ["Viento Temporal", "17 - 20.5"],
        ["Viento Temporal Fuerte", "20.6 - 24.1"],
        ["Tormenta", "24.2 - 28.3"],
        ["Tormenta Violenta", "28.4 - 32.6"],
        ["Huracán", ">32.7"]
    ], columns=['Descripcion', 'Rango de Velocidad'])
    # Contar valores en cada rango
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
        (32.7, float('inf'))  # Para representar ">32.7" usamos infinito como límite superior
    ]
    for ESTACION in ESTACIONES:
        df_datos=ESTACION["DF_DATOS"]
        conteos = []
        total_valores = len(df_datos["VELOCIDAD VIENTO"])
        for limite_inferior, limite_superior in rangos:
            # Contar cuántos valores caen dentro de este rango
            conteo = df_datos["VELOCIDAD VIENTO"].apply(lambda x: limite_inferior <= x <= limite_superior).sum()
            conteos.append(conteo)
        # Calcular el porcentaje para cada clase
        porcentajes = [str(round((conteo / total_valores) * 100,1))+"%" for conteo in conteos]
        # Añadir los porcentajes al DataFrame df_viento como una nueva columna
        df_viento['Porcentaje '+ESTACION["ESTACION"]] = porcentajes
        # Encontrar el índice de la fila con el mayor porcentaje
        indice_maximo = df_viento['Porcentaje '+ESTACION["ESTACION"]].idxmax()
        descripcion_maxima_viento = df_viento.loc[indice_maximo, "Descripcion"]
        ESTACION["descripcion_maxima_viento"]=descripcion_maxima_viento
    return df_viento








def direccion_a_punto_cardinal(df_datos):
    direcciones_radianes = np.radians(df_datos['DIRECCION VIENTO'])
    # Calcular los componentes de seno y coseno
    senos = np.sin(direcciones_radianes)
    cosenos = np.cos(direcciones_radianes)
    # Calcular la media de los componentes de seno y coseno
    media_senos = np.mean(senos)
    media_cosenos = np.mean(cosenos)
    # Calcular la dirección media del viento en radianes
    angulo_medio_radianes = np.arctan2(media_senos, media_cosenos)
    # Convertir el ángulo medio de vuelta a grados
    direccion_media_grados = np.degrees(angulo_medio_radianes) % 360
    # Si el resultado es negativo, ajustarlo para que esté en el rango [0, 360)
    if direccion_media_grados < 0:
        direccion_media_grados += 360
    # Definir los sectores para cada punto cardinal
    sectores = [(0, 'N'), (22.5, 'NNE'), (45, 'NE'), (67.5, 'ENE'),
                (90, 'E'), (112.5, 'ESE'), (135, 'SE'), (157.5, 'SSE'),
                (180, 'S'), (202.5, 'SSW'), (225, 'SW'), (247.5, 'WSW'),
                (270, 'W'), (292.5, 'WNW'), (315, 'NW'), (337.5, 'NNW'), (360, 'N')]
    # Encontrar el sector al que pertenece la dirección dada
    for limite_superior, punto_cardinal in sectores:
        if direccion_media_grados <= limite_superior:
            return punto_cardinal
        


def tabla_promedio_metereologia(ESTACIONES):
    data={'variable': ["Hum. (%)", "Rain. (mm)", "Bar. (mmHg)", "Temp (°C)", "W. Speed. (m/s)", "Max. W.S (m/s)", "Wind Dir"]}
    for ESTACION in ESTACIONES:
        df_datos = ESTACION["DF_DATOS"]
        # Calcular los valores solicitados
        HUMEDAD = df_datos["HUMEDAD RELATIVA"].mean()
        LLUVIA = df_datos["PRECIPITACION"].sum()
        PRESION = df_datos["PRESION ATMOSFERICA"].mean()
        TEMPERATURA = df_datos["TEMPERATURA AMBIENTE"].mean()
        W_SPEED = ESTACION["descripcion_maxima_viento"]
        MAX_W_S = df_datos["VELOCIDAD VIENTO"].max()
        W_DIR = direccion_a_punto_cardinal(df_datos)
        # Crear un diccionario con los valores calculados
        data[ESTACION["ESTACION"]] = [HUMEDAD, LLUVIA, PRESION, TEMPERATURA, W_SPEED, MAX_W_S, W_DIR]
        
    # Crear DataFrame con los datos de las estaciones
    df_estacion = pd.DataFrame(data)
        
    return df_estacion

def hourly_wind_speed_all_stations(ESTACIONES):
    dfs_hourly = {}

    for ESTACION in ESTACIONES:
        df_datos = pd.DataFrame(ESTACION['DF_DATOS']["VELOCIDAD VIENTO"])
        # Resamplear los datos para obtener el promedio de la velocidad del viento por hora
        df_resampled = df_datos.resample('H').mean()
        # Agrupar por hora del día y obtener el promedio de las velocidades para cada hora
        df_hourly = df_resampled.groupby(df_resampled.index.hour)['VELOCIDAD VIENTO'].mean().reindex(range(24), fill_value=0)
        dfs_hourly[ESTACION['ESTACION']] = df_hourly

    return dfs_hourly

def hourly_precipitation_all_stations(ESTACIONES):
    dfs_hourly={}
    
    for ESTACION in ESTACIONES:
        df_datos = pd.DataFrame(ESTACION['DF_DATOS']["PRECIPITACION"])
        # Resamplear los datos para sumar la precipitación por hora
        df_resampled = df_datos.resample('h').sum()
        # Agrupar por hora del día y sumar las precipitaciones para cada hora
        df_hourly = df_resampled.groupby(df_resampled.index.hour)['PRECIPITACION'].sum().reindex(range(24), fill_value=0)
        dfs_hourly[ESTACION['ESTACION']] = df_hourly
    return dfs_hourly

def plot_hourly_precipitation_all_stations(ESTACIONES):
    fig, ax = plt.subplots(figsize=(15, 2))
    cell_text = []
    row_labels = []
    max_precipitation = 0
    
    for ESTACION in ESTACIONES:
        nombre_estacion = ESTACION['ESTACION']
        df_datos = pd.DataFrame(ESTACION['DF_DATOS']["PRECIPITACION"])
        
        # Resamplear los datos para sumar la precipitación por hora
        df_resampled = df_datos.resample('H').sum()

        # Agrupar por hora del día y sumar las precipitaciones para cada hora
        df_hourly = df_resampled.groupby(df_resampled.index.hour)['PRECIPITACION'].sum().reindex(range(24), fill_value=0)
        
        # Actualizar el máximo de precipitación para ajustar los límites del eje Y
        max_precipitation = max(max_precipitation, df_hourly.max())

        # Graficar la línea para la estación actual
        ax.plot(df_hourly.index, df_hourly, marker='o', linestyle='-', linewidth=1, label=nombre_estacion)
        ax.fill_between(df_hourly.index, df_hourly, alpha=0.4)
        # Preparar los datos de la estación para la tabla
        cell_text.append(df_hourly.round(2).astype(str).tolist())
        row_labels.append(nombre_estacion)

    # Configurar las etiquetas y títulos del gráfico
    ax.set_title('Precipitación Acumulada Horaria por Estación')
    ax.set_ylabel('Precipitación (mm)')
    ax.set_xticks([])
    ax.set_ylim(0, max_precipitation + (0.1 * max_precipitation))
    ax.legend(loc='upper right')
    ax.grid()
    
    # Agregar la tabla con los datos de precipitación de todas las estaciones
    colLabels = ['{:02d}h'.format(h) for h in range(24)]
    the_table = plt.table(cellText=cell_text, 
                          rowLabels=row_labels, 
                          colLabels=colLabels,
                          loc='bottom', 
                          cellLoc='center',
                          rowLoc='center',
                          bbox=[0, -0.3, 1, 0.3])

    the_table.auto_set_font_size(False)
    the_table.set_fontsize(10)
    the_table.scale(1, 2.5)
    
    ax.set_xlim(-0.5, 23.5)
    plt.subplots_adjust(left=0.2, bottom=0.2)
    plt.show()



def poner_brujula_mapa(path_mapa="mapa_pg_1.png",path_brujula="../../image/brujula.jpg",brujula_size=(150,150)):
    main_image = Image.open(path_mapa)
    compass_image = Image.open(path_brujula)
    # Cambiar el tamaño de la imagen de la brújula en px
    compass_resized = compass_image.resize(brujula_size)
    # Calcular la posición donde se colocará la brújula en la esquina superior derecha
    x_position = main_image.width - compass_resized.width
    y_position = 0  # Esquina superior
    # Sobreponer la imagen de la brújula en la imagen principal
    main_image.paste(compass_resized, (x_position, y_position))
    # cortar la imagen para que no se vea el zoom en el lado izquierdo ni el texto inferior
    left = 100
    top = 0
    right = main_image.width
    bottom = main_image.height - 100
    main_image = main_image.crop((left, top, right, bottom))
    main_image.save(path_mapa)


def direccion_a_cuadrante(direccion):
    if 0 <= direccion < 90:
        return 'primer'
    elif 90 <= direccion < 180:
        return 'segundo'
    elif 180 <= direccion < 270:
        return 'tercer'
    else:
        return 'cuarto'

def get_texto_viento(FECHA_INICIO, FECHA_FINAL, ESTACIONES):
    TEXTO_VIENTO = f"Durante el periodo analizado, "

    for i, estacion in enumerate(ESTACIONES):
        NOMBRE_ESTACION = estacion["ESTACION"]
        df_datos = estacion["DF_DATOS"]

        # Convertir direcciones del viento a cuadrantes y nombres
        cuadrantes = df_datos["DIRECCION VIENTO"].apply(direccion_a_cuadrante)
        cuadrante_predominante = cuadrantes.mode()[0]
        cuadrante_minoritaria = cuadrantes.value_counts().idxmin()
        direccion_predominante = df_datos["DIRECCION VIENTO"].mode()[0]
        direccion_minoritaria = df_datos["DIRECCION VIENTO"].value_counts().idxmin()

        # Convertir dirección numérica a nombre
        direccion_predominante_nombre = direccion_a_nombre(direccion_predominante)
        direccion_minoritaria_nombre = direccion_a_nombre(direccion_minoritaria)

        velocidad_mayor = df_datos["VELOCIDAD VIENTO"].max()
        menor_precipitacion_horaria = df_datos["PRECIPITACION"].min()
        volumen_precipitacion = df_datos["PRECIPITACION"].max()
        precipitacion_acum = df_datos["PRECIPITACION"].sum()

        # Clasificar la precipitación acumulada según la escala
        clasificacion_precipitacion = clasificar_precipitacion(precipitacion_acum)

        if i == 0:
            TEXTO_ESTACION = (
                f"la dirección predominante del viento, corresponde a vectores provenientes principalmente del {cuadrante_predominante} cuadrante "
                f"desde el ({direccion_predominante_nombre}) y en menor frecuencia del ({direccion_minoritaria_nombre}), "
                f"con velocidades de {velocidad_mayor:.1f} m/s para la estación {NOMBRE_ESTACION}. "
            )
        else:
            TEXTO_ESTACION = (
                f"Por otro lado, en la estación {NOMBRE_ESTACION} predominaron vientos desde el {cuadrante_predominante} cuadrante, principalmente desde el ({direccion_predominante_nombre}) "
                f"y en menor frecuencia del ({direccion_minoritaria_nombre}), con velocidades de hasta {velocidad_mayor:.1f} m/s. "
            )
        
        TEXTO_VIENTO += TEXTO_ESTACION

        # Agregar información sobre la precipitación
        TEXTO_VIENTO += (
            f"En la estación {NOMBRE_ESTACION}, se registró un volumen máximo de precipitación de {volumen_precipitacion:.1f} mm "
            f"y un acumulado de {precipitacion_acum:.1f} mm. Según la escala de precipitación, "
            f"esto se clasifica como '{clasificacion_precipitacion}'. "
        )
    
    return TEXTO_VIENTO

def clasificar_precipitacion(precipitacion_acum):
    """Clasifica la precipitación acumulada según la escala proporcionada."""
    if precipitacion_acum <= 5:
        return 'Escasa'
    elif 6 <= precipitacion_acum <= 10:
        return 'Ligera'
    elif 11 <= precipitacion_acum <= 20:
        return 'Moderada'
    elif 21 <= precipitacion_acum <= 50:
        return 'Fuerte'
    elif 51 <= precipitacion_acum <= 70:
        return 'Muy fuerte'
    else:
        return 'Intensa'

def direccion_a_nombre(direccion):
    """Convierte una dirección numérica en grados a su nombre cardinal correspondiente."""
    sectores = [
        (0, 'N'), (22.5, 'NNE'), (45, 'NE'), (67.5, 'ENE'),
        (90, 'E'), (112.5, 'ESE'), (135, 'SE'), (157.5, 'SSE'),
        (180, 'S'), (202.5, 'SSW'), (225, 'SW'), (247.5, 'WSW'),
        (270, 'O'), (292.5, 'WNW'), (315, 'NW'), (337.5, 'NNW'), (360, 'N')
    ]
    for limite_superior, nombre in sectores:
        if direccion <= limite_superior:
            return nombre
    return 'Desconocido'


def texto_rosa_contaminacion(ESTACIONES):
    texto_resumen = "Durante el periodo analizado y de acuerdo con las rosas de contaminación, "
    for ESTACION in ESTACIONES:
        df_datos = ESTACION['DF_DATOS']
        nombre_estacion = ESTACION['ESTACION']
        
        # Ajustar las direcciones para que el norte esté alineado con 90 grados, restando 90 grados
        df_datos['DIRECCION VIENTO AJUSTADA'] = (df_datos['DIRECCION VIENTO'] - 90) % 360

        # Crear un DataFrame para analizar los cuadrantes
        cuadrantes = {
            'primero': {'data': df_datos[(df_datos['DIRECCION VIENTO AJUSTADA'] >= 0) & (df_datos['DIRECCION VIENTO AJUSTADA'] < 90)]},
            'segundo': {'data': df_datos[(df_datos['DIRECCION VIENTO AJUSTADA'] >= 90) & (df_datos['DIRECCION VIENTO AJUSTADA'] < 180)]},
            'tercer': {'data': df_datos[(df_datos['DIRECCION VIENTO AJUSTADA'] >= 180) & (df_datos['DIRECCION VIENTO AJUSTADA'] < 270)]},
            'cuarto': {'data': df_datos[(df_datos['DIRECCION VIENTO AJUSTADA'] >= 270) & (df_datos['DIRECCION VIENTO AJUSTADA'] < 360)]}
        }

        # Calcular la velocidad promedio del viento y PM10 para cada cuadrante
        for key, value in cuadrantes.items():
            value['velocidad_media'] = value['data']['VELOCIDAD VIENTO'].mean()
            value['pm10_media'] = value['data']['PM10'].mean()

        # Encontrar los cuadrantes más impactados por PM10
        cuadrantes_significativos = sorted(cuadrantes.items(), key=lambda x: (x[1]['pm10_media'], x[1]['velocidad_media']), reverse=True)[:2]

        # Generar el texto resumen con los cuadrantes más impactados
        texto_resumen += f"para la estación de {nombre_estacion}, "
        for cuadrante, data in cuadrantes_significativos:
            texto_resumen += f"los mayores aportes se observan provenientes de los vectores que conforman el {cuadrante} cuadrante, "
            texto_resumen += f"con una velocidad promedio del viento de {data['velocidad_media']:.1f} m/s y niveles de concentración de PM10 de {data['pm10_media']:.0f} µg/mᵌ. "

    return texto_resumen

def clasificar_hora(hora):
    if 0 <= hora < 6:
        return "madrugada"
    elif 12 <= hora < 18:
        return "tarde"
    elif 18 <= hora < 24:
        return "noche"
    else:
        return "mañana"  # Desde las 06:00 hasta las 12:00

def generar_texto_particulado(ESTACIONES):
    TEXTO_PARTICULADO="Durante el periodo analizado. "
    for ESTACION in ESTACIONES:
        df = ESTACION["DF_DATOS"].resample('h').agg({
        'PM10': 'mean',  # Media para PM10
        'PM25': 'mean',
        'PRECIPITACION': 'sum'  # Suma para Precipitación
        })
        df['Parte_del_dia'] = df.index.hour.map(clasificar_hora)
        # Encontrar el máximo de PM10
        max_pm10 = df['PM10'].max()
        max_pm10_time = df[df['PM10'] == max_pm10]

        # Extraer la información del momento en que ocurrió el máximo
        max_hora = max_pm10_time.index.hour[0]
        max_fecha = max_pm10_time.index.date[0]
        parte_del_dia = max_pm10_time['Parte_del_dia'].iloc[0]

        # Formatear la fecha
        max_fecha_str = max_fecha.strftime('%d de %B')
        TEXTO_PARTICULADO+=f"La concentración horaria en la estación de {ESTACION["ESTACION"]}, presentó valores de PM10 que oscilaron entre {ESTACION["DF_DATOS"]["PM10"].min()} y {ESTACION["DF_DATOS"]["PM10"].max()} μg /m³ "
        TEXTO_PARTICULADO+=f"y de PM2.5 entre {ESTACION["DF_DATOS"]["PM25"].min()} y {ESTACION["DF_DATOS"]["PM25"].max()} μg /m³. "
        TEXTO_PARTICULADO+=f"Se observa que las mayores concentraciones se registran en la {parte_del_dia}, cuyo valor más alto de PM10 se obtuvo durante las {max_hora}:00h del {max_fecha_str}, con un valor de {max_pm10} μg/m³. "
        TEXTO_PARTICULADO+=f"En cuanto la precipitación, se registró un volumen acumulado de {ESTACION["DF_DATOS"]["PRECIPITACION"].sum()} mm en la estación. \n" 
    return TEXTO_PARTICULADO


def graficas_highchart(ESTACIONES, RESAMPLE_TIME="H", POLLUTION="PM10", variable="PRECIPITACION"):
    df1 = ESTACIONES[0]["DF_DATOS"]
    df2 = ESTACIONES[1]["DF_DATOS"]

    # Asegurarse de que los índices son DateTimeIndex
    if not isinstance(df1.index, pd.DatetimeIndex):
        df1.index = pd.to_datetime(df1.index)
    if not isinstance(df2.index, pd.DatetimeIndex):
        df2.index = pd.to_datetime(df2.index)

    name1 = f"{ESTACIONES[0]['ESTACION']} - {ESTACIONES[0]['SERIAL']}"
    name2 = f"{ESTACIONES[1]['ESTACION']} - {ESTACIONES[1]['SERIAL']}"

    # Cambiar la agregación dependiendo de la variable
    agg_method = 'mean' if variable == "VELOCIDAD VIENTO" else 'sum'
    
    df1_resampled = df1.resample(RESAMPLE_TIME).agg({
        'PM10': 'mean',
        'PM25': 'mean',
        variable: agg_method
    })
    df2_resampled = df2.resample(RESAMPLE_TIME).agg({
        'PM10': 'mean',
        'PM25': 'mean',
        variable: agg_method
    })

    data1_pollutant = json.dumps(list(df1_resampled[POLLUTION].fillna(0)))
    data2_pollutant = json.dumps(list(df2_resampled[POLLUTION].fillna(0)))
    data1_variable = json.dumps(list(df1_resampled[variable].fillna(0)))
    data2_variable = json.dumps(list(df2_resampled[variable].fillna(0)))

    POLLUTION_NAME = "PM10" if POLLUTION == "PM10" else "PM2.5"
    VARIABLE_NAME = "VELOCIDAD VIENTO" if variable == "VELOCIDAD VIENTO" else "PRECIPITACIÓN"
    VARIABLE_SHORT_NAME = "WS" if variable == "VELOCIDAD VIENTO" else "prec"
    RESAMPLE_NAME = "HORA" if RESAMPLE_TIME.lower() == "h" else "DIA"
    
    title = f'{POLLUTION_NAME} & {VARIABLE_NAME} POR {RESAMPLE_NAME}'
    
    # Formateo personalizado para fechas en el eje X
    def format_date(date):
        if RESAMPLE_NAME == "DIA":
            return date.strftime('%d %b')
        elif date.hour == 0:  # Es medianoche, mostrar la fecha
            return date.strftime('%d %b')
        elif date.hour == 12:  # Es mediodía, mostrar '12:00'
            return '12:00'
        else:
            return ''  # Dejar vacío para no mostrar otras horas

    x_categories = [format_date(date) for date in df1_resampled.index]

    # Establecer el tickInterval y el formateador de etiquetas para manejar los horarios
    if RESAMPLE_NAME == "HORA":
        tick_interval = 24  # Mostrar etiquetas cada 24 horas (corresponde a la medianoche)
    else:
        tick_interval = 1  # Para el caso diario, mostrar cada día

    x_categories_json = json.dumps(x_categories)

    # Decidir el tipo de gráfico para la variable
    series_type = 'line' if variable == "VELOCIDAD VIENTO" else 'areaspline'

    # Agregar una línea horizontal si RESAMPLE_NAME es "DIA"
    additional_series = ""
    if RESAMPLE_NAME == "DIA":
        additional_series = f""",
            {{
                name: 'Límite [75]',
                type: 'line',
                data: [{','.join(['75' for _ in range(len(df1_resampled.index))])}],
                color: 'red',
                dashStyle: 'Dash',
                marker: {{
                    enabled: false
                }},
                enableMouseTracking: false
            }}
        """

    # Establecer colores dependiendo de la variable
    if variable == "VELOCIDAD VIENTO":
        variable_color_1 = '#8B4513'  # Tonalidad de café para la primera estación
        variable_color_2 = '#CE7857'  # Tonalidad de café más clara para la segunda estación
    else:
        variable_color_1 = '#69B5FF'  # Azul claro para la primera estación
        variable_color_2 = '#CDE2FF'  # Azul más claro para la segunda estación

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Highcharts in Python</title>
        <script src="https://code.highcharts.com/highcharts.js"></script>
        <script src="https://code.highcharts.com/modules/exporting.js"></script>
        <script src="https://code.highcharts.com/modules/export-data.js"></script>
    </head>
    <body>
        <div id="container" style="width:800px; height:400px;"></div>
        <script>
            Highcharts.chart('container', {{
                chart: {{
                    zoomType: 'xy'
                }},
                title: {{
                    text: '{title}',
                    align: 'center'
                }},
                xAxis: {{
                    categories: {x_categories_json},
                    tickInterval: {tick_interval},
                    labels: {{
                        formatter: function () {{
                            return this.value ? this.value : '';
                        }},
                        rotation: 0  // Labels en horizontal
                    }}
                }},
                yAxis: [{{
                    title: {{
                        text: '{POLLUTION_NAME} (μg/m³)'
                    }}
                }}, {{
                    title: {{
                        text: '{VARIABLE_NAME} ({VARIABLE_SHORT_NAME})'
                    }},
                    opposite: true
                }}],
                series: [
                    {{
                        name: '{name1}',
                        type: 'column',
                        data: {data1_pollutant},
                        color: '#FA9A67',
                        pointPadding: 0.1,
                        groupPadding: 0.1,
                    }},
                    {{
                        name: '{name1} ({VARIABLE_SHORT_NAME})',
                        type: '{series_type}',
                        yAxis: 1,
                        data: {data1_variable},
                        color: '{variable_color_1}',
                        marker: {{
                            enabled: true
                        }},
                    }},
                    {{
                        name: '{name2}',
                        type: 'column',
                        data: {data2_pollutant},
                        color: '#86CE2C',
                        pointPadding: 0.1,
                        groupPadding: 0.1,
                    }},
                    {{
                        name: '{name2} ({VARIABLE_SHORT_NAME})',
                        type: '{series_type}',
                        yAxis: 1,
                        data: {data2_variable},
                        color: '{variable_color_2}',
                        marker: {{
                            enabled: true
                        }},
                    }}
                    {additional_series}
                ]
            }});
        </script>
    </body>
    </html>
    """

    # El nombre del archivo HTML varía si es PRECIPITACIÓN o VELOCIDAD VIENTO
    prefix = "WS_" if variable == "VELOCIDAD VIENTO" else ""
    filename = f"{prefix}{POLLUTION}_{RESAMPLE_NAME}.html"

    with open(filename, "w", encoding='utf-8') as file:
        file.write(html_content)

