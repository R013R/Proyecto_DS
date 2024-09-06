import os
import shutil
from tkinter import filedialog, messagebox

class ArchivoSelector:
    def __init__(self, interfaz):
        self.interfaz = interfaz

    def select_files(self):
        self.interfaz.files = filedialog.askopenfilenames(filetypes=[("Zip files", "*.zip")])
        if len(self.interfaz.files) == 2:
            filenames = [os.path.basename(file) for file in self.interfaz.files]
            met_file = any(filename.endswith("MET.zip") for filename in filenames)
            ca_file = any(filename.endswith("CA.zip") for filename in filenames)
            
            if met_file and ca_file:
                for file in self.interfaz.files:
                    shutil.copy(file, 'comprimidos/')
                messagebox.showinfo("Éxito", "Archivos seleccionados y copiados a la carpeta 'comprimidos'.")
                self.interfaz.select_button.configure(state=self.interfaz.ctk.DISABLED)
                self.interfaz.run_preparar_datos()
            else:
                messagebox.showerror("Error", "Debe seleccionar un archivo que termine en 'MET.zip' y otro que termine en 'CA.zip'.")
        else:
            messagebox.showerror("Error", "Debe seleccionar exactamente 2 archivos .zip.")
