library(openair)
library(ggplot2)
library(readr)

# Capturar argumentos de la línea de comandos
args <- commandArgs(trailingOnly = TRUE)
base_name <- args[1]
csv_file <- paste0(base_name, ".csv")
png_file <- paste0(base_name, ".png")

# Leer datos
dataset <- read_delim(csv_file, 
                        escape_double = FALSE, 
                        col_types = cols(date = col_datetime(format = "%d/%m/%Y %H:%M")), 
                        trim_ws = TRUE)

# Guardar gráfico
png(png_file, width = 1024, height = 1024, res = 200, bg = "transparent")
polarPlot(dataset, pollutant = "PM25", units = "ug/m3", limits = c(0, 75), cex = 1.5, statistic = 'nwr')
dev.off()
