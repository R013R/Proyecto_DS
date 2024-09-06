from src import procesamiento
import pandas as pd

# Ruta del archivo de configuración
config_path = "configuracion.json"

# Leer configuración
config = procesamiento.leer_configuracion(config_path)

# Estaciones cargadas desde configuración
estaciones_cargadas = {estacion["SERIAL"]: estacion for estacion in config["ESTACIONES"]}
print("Estaciones cargadas desde configuración:", estaciones_cargadas)
import json
variables_info_path = "variables_info.json"
with open(variables_info_path, 'r', encoding='utf-8') as file:
    variables_info = json.load(file)
# Información de las variables (serial_info)
# variables_info = {
#     "PM10 (μg/m³)": "317",
#     "PM2.5 (μg/m³)": "318",
#     "Presión Atmosférica (mmHg)": "29",
#     "Temperatura Ambiente (Celsius)": "30",
#     "Velocidad del Viento (m/s)": "31",
#     "Dirección del Viento (°)": "33",
#     "Humedad Relativa (%)": "34",
#     "Precipitación (mm)": "42"
# }

# Serial info dataframe
serial_info_df = pd.DataFrame([
    {"VARIABLE": "317", "NOMBRE": "PM10", "CLASE": "PARTICULADO", "CAL_SPAN": 1, "UNIDAD": "", "RANGO_INFERIOR": 0, "RANGO_SUPERIOR": 1000, "RESAMPLE_FUNTION": "mean"},
    {"VARIABLE": "318", "NOMBRE": "PM25", "CLASE": "PARTICULADO", "CAL_SPAN": 1, "UNIDAD": "", "RANGO_INFERIOR": 0, "RANGO_SUPERIOR": 1000, "RESAMPLE_FUNTION": "mean"},
    {"VARIABLE": "29", "NOMBRE": "PRESION ATMOSFERICA", "CLASE": "METEREOLOGIA", "CAL_SPAN": 1, "UNIDAD": "mmHg", "RANGO_INFERIOR": 0, "RANGO_SUPERIOR": 1000, "RESAMPLE_FUNTION": "mean"},
    {"VARIABLE": "30", "NOMBRE": "TEMPERATURA AMBIENTE", "CLASE": "METEREOLOGIA", "CAL_SPAN": 1, "UNIDAD": "°C", "RANGO_INFERIOR": -100, "RANGO_SUPERIOR": 100, "RESAMPLE_FUNTION": "mean"},
    {"VARIABLE": "31", "NOMBRE": "VELOCIDAD VIENTO", "CLASE": "METEREOLOGIA", "CAL_SPAN": 1, "UNIDAD": "m/s", "RANGO_INFERIOR": 0, "RANGO_SUPERIOR": 100, "RESAMPLE_FUNTION": "mean"},
    {"VARIABLE": "33", "NOMBRE": "DIRECCION VIENTO", "CLASE": "METEREOLOGIA", "CAL_SPAN": 1, "UNIDAD": "°", "RANGO_INFERIOR": 0, "RANGO_SUPERIOR": 360, "RESAMPLE_FUNTION": "mean"},
    {"VARIABLE": "34", "NOMBRE": "HUMEDAD RELATIVA", "CLASE": "METEREOLOGIA", "CAL_SPAN": 1, "UNIDAD": "%", "RANGO_INFERIOR": 0, "RANGO_SUPERIOR": 120, "RESAMPLE_FUNTION": "mean"},
    {"VARIABLE": "42", "NOMBRE": "PRECIPITACION", "CLASE": "METEREOLOGIA", "CAL_SPAN": 1, "UNIDAD": "mm", "RANGO_INFERIOR": 0, "RANGO_SUPERIOR": 100, "RESAMPLE_FUNTION": "sum"}
])

# Extraer archivos
procesamiento.extraer_archivos(config["PATH_COMPRIMIDOS"])

# Agrupar archivos por serial
serial_files = procesamiento.agrupar_archivos_por_serial(config["PATH_COMPRIMIDOS"])
R_PATH = config["R_PATH"]
# Procesar seriales y combinar datos
estaciones_extraidas, fecha_inicio, fecha_final = procesamiento.procesar_seriales(serial_files, variables_info, config["PATH_DATOS"], estaciones_cargadas, serial_info_df)

# Guardar resultado final
procesamiento.guardar_resultado(estaciones_extraidas, config["PATH_DATOS"], config["PATH_COMPRIMIDOS"], fecha_inicio, fecha_final,R_PATH)
