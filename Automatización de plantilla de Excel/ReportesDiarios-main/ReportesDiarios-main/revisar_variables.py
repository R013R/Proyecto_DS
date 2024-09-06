import os
import json
import pandas as pd

# Cargar configuración desde configuracion.json
config_path = "configuracion.json"
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

# Ruta de la carpeta "datos"
path_datos = config["PATH_DATOS"]

# Variables que se deben buscar en los archivos CSV
variables_requeridas = ["fecha", "33", "31", "317", "318", "42", "34", "29", "30"]

# Diccionario para almacenar los resultados
resultado_variables = {}

# Buscar y revisar los archivos CSV
for filename in os.listdir(path_datos):
    if filename.endswith(".csv") and not filename.endswith("_info.csv"):
        # Cargar el archivo CSV
        file_path = os.path.join(path_datos, filename)
        df = pd.read_csv(file_path)
        
        # Verificar si cada variable requerida está en las columnas del DataFrame
        resultado = {var: (var in df.columns) for var in variables_requeridas}
        
        # Guardar el resultado para este archivo
        resultado_variables[filename] = resultado

# Guardar los resultados en un archivo JSON
output_path = os.path.join(path_datos, "resultado_variables.json")
with open(output_path, 'w', encoding='utf-8') as outfile:
    json.dump(resultado_variables, outfile, indent=4)

print(f"Revisión completa. Los resultados se han guardado en {output_path}.")
