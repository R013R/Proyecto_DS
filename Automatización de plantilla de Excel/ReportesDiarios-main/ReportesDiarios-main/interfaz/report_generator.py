import subprocess
from tkinter import messagebox

class ReportGenerator:
    def __init__(self, interfaz):
        self.interfaz = interfaz

    def run_main(self):
        self.interfaz.run_script_in_thread(self._run_main)

    def _run_main(self):
        self.interfaz.status_label.configure(text="Generando reporte...")
        result = subprocess.run(["python3", "main.py"], capture_output=True, text=True)
        if result.returncode == 0:
            self.interfaz.status_label.configure(text="Reporte generado correctamente.")
            messagebox.showinfo("Éxito", "Reporte generado correctamente.")
        else:
            self.interfaz.status_label.configure(text="Error al generar el reporte.")
            messagebox.showerror("Error", f"Error al generar el reporte: {result.stderr}")
