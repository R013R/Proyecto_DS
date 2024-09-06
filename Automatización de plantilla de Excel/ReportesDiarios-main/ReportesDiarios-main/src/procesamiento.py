import zipfile
import os
import pandas as pd
import json

def leer_configuracion(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)

def extraer_archivos(path_comprimidos):
    zip_files = [f for f in os.listdir(path_comprimidos) if f.endswith('.zip')]
    print("Archivos .zip encontrados:", zip_files)

    for zip_file in zip_files:
        with zipfile.ZipFile(os.path.join(path_comprimidos, zip_file), 'r') as zip_ref:
            # Crear directorio para extraer los archivos en comprimidos
            extract_dir = os.path.join(path_comprimidos, zip_file.replace('.zip', ''))
            os.makedirs(extract_dir, exist_ok=True)
            zip_ref.extractall(extract_dir)
            print(f"Archivos extraídos en: {extract_dir}")

def agrupar_archivos_por_serial(path_comprimidos):
    serial_files = {}
    for zip_dir in os.listdir(path_comprimidos):
        dir_path = os.path.join(path_comprimidos, zip_dir)
        if os.path.isdir(dir_path):
            for file in os.listdir(dir_path):
                if '_por hora_' in file:
                    parts = file.split('_')
                    estacion_info = parts[0]
                    serial = estacion_info.split()[-1]
                    nombre_estacion = ' '.join(estacion_info.split()[:-1])
                    print(f"Archivo por hora encontrado: {file}, Serial: {serial}, Estación: {nombre_estacion}")

                    if serial not in serial_files:
                        serial_files[serial] = {"nombre_estacion": nombre_estacion}

                    if zip_dir.endswith("CA"):
                        if "CA" not in serial_files[serial]:
                            serial_files[serial]["CA"] = []
                        serial_files[serial]["CA"].append(os.path.join(dir_path, file))
                        print(f"Archivo CA añadido para {serial}: {file}")
                    elif zip_dir.endswith("MET"):
                        if "MET" not in serial_files[serial]:
                            serial_files[serial]["MET"] = []
                        serial_files[serial]["MET"].append(os.path.join(dir_path, file))
                        print(f"Archivo MET añadido para {serial}: {file}")

    print("Archivos agrupados por serial:", serial_files)
    return serial_files

def combinar_archivos(ca_file, met_file, variables_info):
    print(f"Combinando archivos: {ca_file} y {met_file}")
    df_ca = pd.read_csv(ca_file, delimiter=';', decimal=',', skiprows=1)
    df_ca.columns = df_ca.columns.str.strip()
    df_ca['Fecha'] = pd.to_datetime(df_ca['Fecha'])

    df_met = pd.read_csv(met_file, delimiter=';', decimal=',', skiprows=1)
    df_met.columns = df_met.columns.str.strip()
    df_met['Fecha'] = pd.to_datetime(df_met['Fecha'])

    # Convertir los nombres de las columnas y las claves de variables_info a minúsculas
    df_ca.columns = df_ca.columns.str.lower()
    df_met.columns = df_met.columns.str.lower()

    # Convertir las claves de variables_info a minúsculas
    variables_info_lower = {key.lower(): value for key, value in variables_info.items()}

    # Combinar los dos DataFrames en uno solo
    df_combined = pd.merge(df_ca, df_met, on='fecha', how='outer')
    print(f"Archivos combinados: {df_combined.head()}")

    # Reemplazar nombres de columnas por los índices de variables usando las claves en minúsculas
    column_map = {name: variables_info_lower[name] for name in df_combined.columns if name in variables_info_lower}
    df_combined.rename(columns=column_map, inplace=True)

    # Reordenar las columnas según el orden especificado, omitiendo las que no están presentes
    column_order = ["fecha", "33", "31", "317", "318", "42", "34", "29", "30"]
    present_columns = [col for col in column_order if col in df_combined.columns]
    df_combined = df_combined[present_columns]

    # Convertir las fechas al formato requerido y renombrar la columna a "fecha"
    df_combined['fecha'] = df_combined['fecha'].dt.strftime('%Y-%m-%d %H:%M')

    return df_combined


def guardar_datos(serial, df_combined, path_datos, serial_info_df):
    # Guardar el DataFrame resultante en un archivo CSV
    output_csv_path = os.path.join(path_datos, f"{serial}.csv")
    df_combined.to_csv(output_csv_path, index=False)
    print(f"Datos guardados en: {output_csv_path}")

    # Guardar el archivo serial_info.csv específico para cada estación
    serial_info_path = os.path.join(path_datos, f"{serial}_info.csv")
    serial_info_df.to_csv(serial_info_path, index=False)
    print(f"Info guardada en: {serial_info_path}")

def procesar_seriales(serial_files, variables_info, path_datos, estaciones_cargadas, serial_info_df):
    estaciones_extraidas = {}
    fecha_inicio = None
    fecha_final = None

    for serial, files in serial_files.items():
        if "CA" in files and "MET" in files:
            ca_files = files["CA"]
            met_files = files["MET"]
            for ca_file in ca_files:
                for met_file in met_files:
                    df_combined = combinar_archivos(ca_file, met_file, variables_info)
                    guardar_datos(serial, df_combined, path_datos, serial_info_df)
                    
                    # Calcular fechas de inicio y final
                    if fecha_inicio is None or df_combined['fecha'].min() < fecha_inicio:
                        fecha_inicio = df_combined['fecha'].min()
                    if fecha_final is None or df_combined['fecha'].max() > fecha_final:
                        fecha_final = df_combined['fecha'].max()

            # Actualizar información de la estación
            estaciones_extraidas[serial] = {
                "ESTACION": files["nombre_estacion"],
                "LATITUD": estaciones_cargadas.get(serial, {}).get("LATITUD", 0),
                "LONGITUD": estaciones_cargadas.get(serial, {}).get("LONGITUD", 0),
                "SERIAL": serial
                
            }
            print(f"Estación extraída: {estaciones_extraidas[serial]}")
        else:
            print(f"Faltan archivos CA o MET para el serial {serial}")

    return estaciones_extraidas, fecha_inicio, fecha_final

def guardar_resultado(estaciones_extraidas, path_datos, path_comprimidos, fecha_inicio, fecha_final,R_PATH):
    resultado = {
        "ESTACIONES": list(estaciones_extraidas.values()),
        "FECHA_INICIO": fecha_inicio,
        "FECHA_FINAL": fecha_final,
        "PATH_DATOS": path_datos,
        "PATH_COMPRIMIDOS": path_comprimidos,
        "R_PATH": R_PATH
    }

    # Guardar el diccionario resultante
    output_path = os.path.join(path_datos, "resultado.json")
    with open(output_path, 'w') as outfile:
        json.dump(resultado, outfile, indent=4)

    print("Resultado final guardado en resultado.json")
    print(json.dumps(resultado, indent=4))
