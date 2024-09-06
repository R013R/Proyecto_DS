import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import json
import shutil
import os
import threading

class ReportAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatización de Reportes")
        self.root.geometry("800x600")

        # Configurar el tema de CustomTkinter
        ctk.set_appearance_mode("Dark")  # Opciones: "System" (automático), "Dark", "Light"
        ctk.set_default_color_theme("dark-blue")  # Temas: "blue", "green", "dark-blue"

        # Título de la aplicación
        self.title_label = ctk.CTkLabel(root, text="Sistema de Automatización de Reportes", font=("Helvetica", 20, "bold"))
        self.title_label.pack(pady=20)

        # Botón para reiniciar la aplicación
        self.reset_button = ctk.CTkButton(root, text="Empezar de Nuevo", command=self.reset_app, width=150)
        self.reset_button.place(x=20, y=20)

        # Paso 1: Seleccionar archivos
        self.step1_label = ctk.CTkLabel(root, text="Paso 1: Seleccionar archivos .zip (nombres deben terminar en MET y CA)", font=("Helvetica", 14))
        self.step1_label.pack(pady=10)

        self.select_button = ctk.CTkButton(root, text="Seleccionar Archivos", command=self.select_files, width=250, height=40)
        self.select_button.pack(pady=5)

        # Paso 2: Preparar datos
        self.step2_label = ctk.CTkLabel(root, text="Preparar Datos", font=("Helvetica", 14))
        self.step2_label.pack(pady=10)
        self.step2_label.pack_forget()

        self.run_button = ctk.CTkButton(root, text="Ejecutar Preparar Datos", command=self.run_preparar_datos, state=ctk.DISABLED, width=250, height=40)
        self.run_button.pack(pady=5)
        self.run_button.pack_forget()

        # Paso 3: Editar resultado.json
        self.step3_label = ctk.CTkLabel(root, text="Paso 2: Editar resultado.json (max 2 estaciones)", font=("Helvetica", 14))
        self.step3_label.pack(pady=10)
        self.step3_label.pack_forget()

        self.edit_button = ctk.CTkButton(root, text="Editar resultado.json", command=self.edit_json, state=ctk.DISABLED, width=250, height=40)
        self.edit_button.pack(pady=5)
        self.edit_button.pack_forget()

        # Paso 4: Generar Reporte
        self.step4_label = ctk.CTkLabel(root, text="Paso 3: Generar Reporte", font=("Helvetica", 14))
        self.step4_label.pack(pady=10)
        self.step4_label.pack_forget()

        self.save_button = ctk.CTkButton(root, text="Generar Reporte", command=self.run_main, state=ctk.DISABLED, width=250, height=40)
        self.save_button.pack(pady=5)
        self.save_button.pack_forget()

        self.status_label = ctk.CTkLabel(root, text="", font=("Helvetica", 12), fg_color="transparent")
        self.status_label.pack(pady=10)

        self.files = []
        self.loader_label = None

    def show_loader(self):
        if not self.loader_label:
            self.loader_label = ctk.CTkLabel(self.root, text="Cargando...", font=("Helvetica", 16, "bold"), text_color="blue")
            self.loader_label.pack(pady=10)
        self.disable_interface()

    def hide_loader(self):
        if self.loader_label:
            self.loader_label.destroy()
            self.loader_label = None
        self.enable_interface()

    def disable_interface(self):
        self.select_button.configure(state=ctk.DISABLED)
        self.run_button.configure(state=ctk.DISABLED)
        self.edit_button.configure(state=ctk.DISABLED)
        self.save_button.configure(state=ctk.DISABLED)
        self.reset_button.configure(state=ctk.DISABLED)

    def enable_interface(self):
        self.reset_button.configure(state=ctk.NORMAL)
        if self.files:
            self.run_button.configure(state=ctk.NORMAL)
        if os.path.exists('./datos/resultado.json'):
            self.edit_button.configure(state=ctk.NORMAL)
        if self.edit_button.cget('state') != ctk.DISABLED:
            self.save_button.configure(state=ctk.NORMAL)

    def run_script_in_thread(self, func):
        self.show_loader()
        thread = threading.Thread(target=self.run_script_and_hide_loader, args=(func,))
        thread.start()

    def run_script_and_hide_loader(self, func):
        try:
            func()
        finally:
            self.root.after(100, self.hide_loader)

    def select_files(self):
        self.files = filedialog.askopenfilenames(filetypes=[("Zip files", "*.zip")])
        if len(self.files) == 2:
            filenames = [os.path.basename(file) for file in self.files]
            met_file = any(filename.endswith("MET.zip") for filename in filenames)
            ca_file = any(filename.endswith("CA.zip") for filename in filenames)
            
            if met_file and ca_file:
                for file in self.files:
                    shutil.copy(file, 'comprimidos/')
                messagebox.showinfo("Éxito", "Archivos seleccionados y copiados a la carpeta 'comprimidos'.")
                self.select_button.configure(state=ctk.DISABLED)
                self.run_preparar_datos()
            else:
                messagebox.showerror("Error", "Debe seleccionar un archivo que termine en 'MET.zip' y otro que termine en 'CA.zip'.")
        else:
            messagebox.showerror("Error", "Debe seleccionar exactamente 2 archivos .zip.")

    def run_preparar_datos(self):
        self.run_script_in_thread(self._run_preparar_datos)

    def _run_preparar_datos(self):
        self.status_label.configure(text="Preparando datos...")
        result = subprocess.run(["python3", "preparar_datos.py"], capture_output=True, text=True)
        if result.returncode == 0:
            self.status_label.configure(text="Datos preparados correctamente.")
            messagebox.showinfo("Éxito", "Datos preparados correctamente.")
            self.run_revisar_variables()  # Ejecutar la revisión de variables después de preparar los datos
        else:
            self.status_label.configure(text="Error al preparar los datos.")
            messagebox.showerror("Error", f"Error al preparar los datos: {result.stderr}")

    def run_revisar_variables(self):
        self.run_script_in_thread(self._run_revisar_variables)

    def _run_revisar_variables(self):
        result = subprocess.run(["python3", "revisar_variables.py"], capture_output=True, text=True)
        if result.returncode == 0:
            with open('./datos/resultado_variables.json', 'r', encoding='utf-8') as file:
                resultado_variables = json.load(file)
            
            variables_no_encontradas = {}
            variable_names = {
                "317": "PM10 (μg/m³)",
                "318": "PM2.5 (μg/m³)",
                "29": "Presión Atmosférica (mmHg)",
                "30": "Temperatura Ambiente (Celsius)",
                "31": "Velocidad del Viento (m/s)",
                "33": "Dirección del Viento (°)",
                "34": "Humedad Relativa (%)",
                "42": "Precipitación (mm)"
            }

            for archivo, variables in resultado_variables.items():
                for variable, encontrada in variables.items():
                    if not encontrada:
                        var_name = variable_names.get(variable, variable)
                        if archivo not in variables_no_encontradas:
                            variables_no_encontradas[archivo] = []
                        variables_no_encontradas[archivo].append(var_name)
            
            if variables_no_encontradas:
                missing_variables_text = "\n".join([f"Archivo {archivo}: {', '.join(vars)}" for archivo, vars in variables_no_encontradas.items()])
                messagebox.showerror("Error", f"Las siguientes variables no se encontraron en los archivos:\n\n{missing_variables_text}")
                self.edit_json('variables_info.json')
                self.reset_app()
            else:
                self.status_label.configure(text="Todas las variables fueron encontradas. Puede continuar.")
                self.step3_label.pack()
                self.edit_button.pack()
                self.edit_button.configure(state=ctk.NORMAL)
        else:
            self.status_label.configure(text="Error al revisar las variables.")
            messagebox.showerror("Error", f"Error al revisar las variables: {result.stderr}")

    def edit_json(self, json_file='resultado.json'):
        if json_file == 'variables_info.json':
            json_file_path = json_file
        else:
            json_file_path = os.path.join('./datos', json_file)

        if not os.path.exists(json_file_path):
            messagebox.showerror("Error", f"El archivo {json_file_path} no existe.")
            return

        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        self.edit_window = ctk.CTkToplevel(self.root)
        self.edit_window.title(f"Editar {json_file}")
        self.edit_window.geometry("800x600")

        self.text_area = ctk.CTkTextbox(self.edit_window, wrap="word", font=("Helvetica", 10))
        self.text_area.pack(expand=1, fill='both', padx=10, pady=10)
        
        self.text_area.insert("1.0", json.dumps(data, indent=4, ensure_ascii=False))

        self.save_edit_button = ctk.CTkButton(self.edit_window, text="Guardar Cambios", command=lambda: self.save_json_changes(json_file_path), width=200, height=40)
        self.save_edit_button.pack(pady=10)

    def save_json_changes(self, json_file_path):
        data = self.text_area.get("1.0", "end").strip()
        try:
            json_data = json.loads(data)
            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)
            # Guardar también como configuracion.json si se guarda resultado.json
            if json_file_path.endswith('resultado.json'):
                with open('./configuracion.json', 'w', encoding='utf-8') as config_file:
                    json.dump(json_data, config_file, indent=4, ensure_ascii=False)
            self.status_label.configure(text=f"Cambios guardados en {json_file_path}.")
            messagebox.showinfo("Éxito", f"Cambios guardados en {json_file_path}.")
            self.edit_window.destroy()
            
            # Reiniciar solo si se está editando variables_info.json
            if "variables_info.json" in json_file_path:
                self.reset_app()
            else:
                # Continuar con el flujo normal si no es variables_info.json
                self.step4_label.pack()
                self.save_button.pack()
                self.save_button.configure(state=ctk.NORMAL)
                
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Formato JSON inválido. Por favor, revise el contenido.")

    def run_main(self):
        self.run_script_in_thread(self._run_main)

    def _run_main(self):
        self.status_label.configure(text="Generando reporte...")
        result = subprocess.run(["python3", "main.py"], capture_output=True, text=True)
        if result.returncode == 0:
            self.status_label.configure(text="Reporte generado correctamente.")
            messagebox.showinfo("Éxito", "Reporte generado correctamente.")
        else:
            self.status_label.configure(text="Error al generar el reporte.")
            messagebox.showerror("Error", f"Error al generar el reporte: {result.stderr}")

    def reset_app(self):
        for folder in ['comprimidos', 'datos']:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if filename != ".gitkeep":
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Error al borrar {file_path}. Razón: {e}')
        
        self.select_button.configure(state=ctk.NORMAL)
        self.step1_label.pack()
        self.step2_label.pack_forget()
        self.run_button.pack_forget()
        self.step3_label.pack_forget()
        self.edit_button.pack_forget()
        self.step4_label.pack_forget()
        self.save_button.pack_forget()
        self.status_label.configure(text="")
        messagebox.showinfo("Reinicio", "La aplicación se ha reiniciado.")

if __name__ == "__main__":
    root = ctk.CTk()
    app = ReportAutomationApp(root)
    root.mainloop()
