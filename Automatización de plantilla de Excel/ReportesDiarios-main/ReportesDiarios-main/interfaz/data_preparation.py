import subprocess
from tkinter import messagebox

class DataPreparation:
    def __init__(self, interfaz):
        self.interfaz = interfaz

    def run_preparar_datos(self):
        self.interfaz.run_script_in_thread(self._run_preparar_datos)

    def _run_preparar_datos(self):
        self.interfaz.status_label.configure(text="Preparando datos...")
        result = subprocess.run(["python3", "preparar_datos.py"], capture_output=True, text=True)
        if result.returncode == 0:
            self.interfaz.status_label.configure(text="Datos preparados correctamente.")
            messagebox.showinfo("Éxito", "Datos preparados correctamente.")
            self.interfaz.run_revisar_variables()
        else:
            self.interfaz.status_label.configure(text="Error al preparar los datos.")
            messagebox.showerror("Error", f"Error al preparar los datos: {result.stderr}")

    def run_revisar_variables(self):
        self.interfaz.run_script_in_thread(self._run_revisar_variables)

    def _run_revisar_variables(self):
        result = subprocess.run(["python3", "revisar_variables.py"], capture_output=True, text=True)
        if result.returncode == 0:
            self.interfaz.handle_variable_check()
        else:
            self.interfaz.status_label.configure(text="Error al revisar las variables.")
            messagebox.showerror("Error", f"Error al revisar las variables: {result.stderr}")
