import os

class UIComponents:
    def __init__(self, interfaz):
        self.interfaz = interfaz

    def show_loader(self):
        if not self.interfaz.loader_label:
            self.interfaz.loader_label = self.interfaz.ctk.CTkLabel(self.interfaz.root, text="Cargando...", font=("Helvetica", 16, "bold"), text_color="blue")
            self.interfaz.loader_label.pack(pady=10)
        self.disable_interface()

    def hide_loader(self):
        if self.interfaz.loader_label:
            self.interfaz.loader_label.destroy()
            self.interfaz.loader_label = None
        self.enable_interface()

    def disable_interface(self):
        self.interfaz.select_button.configure(state=self.interfaz.ctk.DISABLED)
        self.interfaz.run_button.configure(state=self.interfaz.ctk.DISABLED)
        self.interfaz.edit_button.configure(state=self.interfaz.ctk.DISABLED)
        self.interfaz.save_button.configure(state=self.interfaz.ctk.DISABLED)
        self.interfaz.reset_button.configure(state=self.interfaz.ctk.DISABLED)

    def enable_interface(self):
        self.interfaz.reset_button.configure(state=self.interfaz.ctk.NORMAL)
        if self.interfaz.files:
            self.interfaz.run_button.configure(state=self.interfaz.ctk.NORMAL)
        if os.path.exists('./datos/resultado.json'):
            self.interfaz.edit_button.configure(state=self.interfaz.ctk.NORMAL)
        if self.interfaz.edit_button.cget('state') != self.interfaz.ctk.DISABLED:
            self.interfaz.save_button.configure(state=self.interfaz.ctk.NORMAL)

    def run_script_in_thread(self, func):
        self.show_loader()
        thread = threading.Thread(target=self.run_script_and_hide_loader, args=(func,))
        thread.start()

    def run_script_and_hide_loader(self, func):
        try:
            func()
        finally:
            self.interfaz.root.after(100, self.hide_loader)
