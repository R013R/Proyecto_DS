import os
import json
from tkinter import messagebox

class JsonEditor:
    def __init__(self, interfaz):
        self.interfaz = interfaz

    def edit_json(self, json_file='resultado.json'):
        json_file_path = self.get_json_file_path(json_file)

        if not os.path.exists(json_file_path):
            messagebox.showerror("Error", f"El archivo {json_file_path} no existe.")
            return

        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        self.interfaz.edit_window = self.interfaz.ctk.CTkToplevel(self.interfaz.root)
        self.interfaz.edit_window.title(f"Editar {json_file}")
        self.interfaz.edit_window.geometry("800x600")

        self.interfaz.text_area = self.interfaz.ctk.CTkTextbox(self.interfaz.edit_window, wrap="word", font=("Helvetica", 10))
        self.interfaz.text_area.pack(expand=1, fill='both', padx=10, pady=10)
        
        self.interfaz.text_area.insert("1.0", json.dumps(data, indent=4, ensure_ascii=False))

        self.interfaz.save_edit_button = self.interfaz.ctk.CTkButton(
            self.interfaz.edit_window, 
            text="Guardar Cambios", 
            command=lambda: self.save_json_changes(json_file_path, json_file), 
            width=200, 
            height=40
        )
        self.interfaz.save_edit_button.pack(pady=10)

    def get_json_file_path(self, json_file):
        if json_file == 'variables_info.json':
            return json_file
        return os.path.join('./datos', json_file)

    def save_json_changes(self, json_file_path, json_file):
        data = self.interfaz.text_area.get("1.0", "end").strip()
        try:
            json_data = json.loads(data)
            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)
            self.interfaz.status_label.configure(text=f"Cambios guardados en {json_file_path}.")
            messagebox.showinfo("Éxito", f"Cambios guardados en {json_file_path}.")
            self.interfaz.edit_window.destroy()
            
            # Solo reiniciar si se está editando `variables_info.json`
            if json_file == 'variables_info.json':
                self.interfaz.reset_app()
            else:
                # Continuar con el flujo normal si se está editando otro archivo
                self.interfaz.step4_label.pack()
                self.interfaz.save_button.pack()
                self.interfaz.save_button.configure(state=self.interfaz.ctk.NORMAL)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Formato JSON inválido. Por favor, revise el contenido.")
