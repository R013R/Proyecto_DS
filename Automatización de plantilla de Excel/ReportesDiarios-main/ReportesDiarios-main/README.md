# README

## Descripción del Proyecto

Este proyecto tiene como objetivo generar reportes a partir de datos comprimidos que contienen información sobre la calidad del aire y datos meteorológicos. Los usuarios deben cargar dos carpetas comprimidas en formato `.zip` con una estructura específica. El sistema procesará estos datos y generará un archivo de configuración y un reporte en formato Excel.

## Requisitos Previos

1. **Python**: Instalar Python 3, preferiblemente la versión 3.12.
2. **R**: Instalar R y asegurarse de conocer el path de instalación.

## Instalación de Dependencias

1. Clonar este repositorio en su máquina local.
2. Navegar a la carpeta del proyecto.
3. Ejecutar los siguientes comandos para instalar las dependencias necesarias:

```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install
```

## Configuración

1. **Path de R**: Asegúrese de revisar cuál es el path de instalación de R y agréguelo en el archivo `configuracion.json`. debe usar una extructura como la siguiente: 
-`"R_PATH": "C:\\Program Files\\R\\R-4.3.3\\bin\\Rscript.exe"` usando `\\` 
-o bien tambien puede usar `"R_PATH": "C:/Program Files/R/R-4.3.3/bin/Rscript.exe"` con `/` 

## Estructura de Datos

- **Datos de Calidad del Aire**: Archivos con la estructura `AAAAMMDD_NAME_CA` deben contener:
  - PM10 (μg/m³)
  - PM2.5 (μg/m³)

- **Datos Meteorológicos**: Archivos con la estructura `AAAAMMDD_NAME_MET` deben contener:
  - Presión Atmosférica (mmHg)
  - Temperatura Ambiente (Celsius)
  - Velocidad del Viento (m/s)
  - Dirección del Viento (°)
  - Humedad Relativa (%)
  - Precipitación (mm)

## Instrucciones de Uso

1. Colocar los archivos comprimidos en la carpeta llamada `comprimidos`.
2. Ejecutar el siguiente comando para preparar los datos:

```bash
python3 preparar_datos.py
```

3. Revisar el archivo `resultado.json` generado en la carpeta `/datos`:


4. Hacer los cambios pertinentes en `resultado.json` según las necesidades específicas de las estaciones, seriales, fechas de inicio y fin.
5. Copiar el archivo de `./data/resultado.json` a `./configuracion.json`
6. Ejecutar el siguiente comando para generar el reporte:

```bash
python3 main.py
```

## Generación de Reportes

- El reporte se generará y guardará en la carpeta `reportes` usando el formato `aaaamddHHMMSS`.
- Podrá editar el archivo Excel generado a su gusto.
- Los materiales adicionales necesarios se encontrarán en la carpeta `resources`.

## Contacto

Para cualquier duda o consulta, por favor contactar al equipo de soporte a través de [kevin.naranjo@xactus.io].

## Agradecimientos

Agradecemos su interés en nuestro proyecto y esperamos que encuentre útil esta herramienta para la generación de reportes de calidad del aire y datos meteorológicos.