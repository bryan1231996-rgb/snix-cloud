import customtkinter as ctk
from tkinter import filedialog
from core import RepositorioSnippets, GestorSeguridad, MicrosoftCloudConnector

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- DICCIONARIO MULTILINGÜE ---
IDIOMAS = {
    "Español": {
        "title": "SniX Cloud - Bóveda Empresarial",
        "sections": "📁 Secciones / Temas",
        "new_folder": "+ Nueva Carpeta",
        "settings": "⚙️ Configuración / Cloud",
        "del_folder": "🗑️ Eliminar Carpeta Activa",
        "search": "🔍 Filtrar scripts en tiempo real...",
        "add_script": "+ Añadir Script",
        "del_mode": "🗑️ Modo Selección Crítica",
        "exit_del_mode": "✔️ Salir del Modo Crítico",
        "empty_folder": "Selecciona una carpeta a la izquierda",
        "save_prefs": "Guardar Preferencias",
        "restart_msg": "✅ Reinicia la app para aplicar el idioma."
    },
    "English": {
        "title": "SniX Cloud - Enterprise Vault",
        "sections": "📁 Sections / Themes",
        "new_folder": "+ New Folder",
        "settings": "⚙️ Settings / Cloud Sync",
        "del_folder": "🗑️ Delete Active Folder",
        "search": "🔍 Filter scripts in real-time...",
        "add_script": "+ Add Script",
        "del_mode": "🗑️ Critical Selection Mode",
        "exit_del_mode": "✔️ Exit Critical Mode",
        "empty_folder": "Select a folder on the left to begin",
        "save_prefs": "Save Preferences",
        "restart_msg": "✅ Restart the app to apply changes."
    }
}

COLORES_DISPONIBLES = [("#1F538D", "Azul"), ("#A12B2B", "Rojo"), ("#2E7D32", "Verde"), ("#E65100", "Naranja"), ("#6A1B9A", "Morado"), ("#37474F", "Gris")]

# ==========================================
# 1. PANTALLA PRINCIPAL (BÓVEDA)
# ==========================================
class SniXCloudApp(ctk.CTkToplevel):
    def __init__(self, db_instance, master=None):
        super().__init__(master)
        self.db = db_instance
        self.carpeta_seleccionada_id = None
        self.nombre_carpeta_activa = "Ninguna"
        self.modo_eliminacion = False

        idioma_guardado = self.db.obtener_config("idioma", "Español")
        self.t = IDIOMAS.get(idioma_guardado, IDIOMAS["Español"])

        self.title(self.t["title"])
        self.geometry("1050x750")
        self.minsize(800, 600)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        self._construir_ui()
        self.cargar_carpetas_en_ui()

    def cerrar_aplicacion(self):
        if self.master: self.master.destroy()
        self.destroy()

    def _construir_ui(self):
        self.frame_izq = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.frame_izq.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.frame_izq, text=self.t["sections"], font=("Segoe UI", 16, "bold")).pack(pady=15, padx=10)

        self.scroll_carpetas = ctk.CTkScrollableFrame(self.frame_izq, fg_color="transparent")
        self.scroll_carpetas.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.btn_nueva_c = ctk.CTkButton(self.frame_izq, text=self.t["new_folder"], command=self.abrir_ventana_carpeta, fg_color="#34495E")
        self.btn_nueva_c.pack(pady=5, padx=15, fill="x")
        
        self.btn_settings = ctk.CTkButton(self.frame_izq, text=self.t["settings"], fg_color="transparent", border_width=1, command=self.abrir_settings)
        self.btn_settings.pack(pady=5, padx=15, fill="x")

        self.btn_eliminar_c = ctk.CTkButton(self.frame_izq, text=self.t["del_folder"], fg_color="#7B2424", command=self.eliminar_carpeta_activa)

        self.frame_der = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_der.grid(row=0, column=1, sticky="nsew", padx=25, pady=20)
        self.frame_der.grid_rowconfigure(3, weight=1)
        self.frame_der.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.frame_der, text="⚡ SniX Cloud Vault", font=("Segoe UI", 24, "bold")).grid(row=0, column=0, sticky="w")
        self.lbl_estado_carpeta = ctk.CTkLabel(self.frame_der, text=self.t["empty_folder"], text_color="gray")
        self.lbl_estado_carpeta.grid(row=1, column=0, sticky="w", pady=(0, 15))

        self.search_entry = ctk.CTkEntry(self.frame_der, placeholder_text=self.t["search"], height=35)
        self.search_entry.grid(row=2, column=0, sticky="ew", pady=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.actualizar_vista_lista())

        self.lista_scroll = ctk.CTkScrollableFrame(self.frame_der)
        self.lista_scroll.grid(row=3, column=0, sticky="nsew", pady=10)

        self.actions_bar = ctk.CTkFrame(self.frame_der, fg_color="transparent")
        self.actions_bar.grid(row=4, column=0, sticky="ew", pady=5)

        self.btn_nuevo_snippet = ctk.CTkButton(self.actions_bar, text=self.t["add_script"], state="disabled", command=self.abrir_ventana_nuevo)
        self.btn_nuevo_snippet.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_modo_borrar = ctk.CTkButton(self.actions_bar, text=self.t["del_mode"], fg_color="#A12B2B", state="disabled", command=self.alternar_modo_eliminacion)
        self.btn_modo_borrar.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def cargar_carpetas_en_ui(self):
        for widget in self.scroll_carpetas.winfo_children(): widget.destroy()
        self.btn_eliminar_c.pack_forget()
        for id_c, nombre, color in self.db.obtener_carpetas():
            ctk.CTkButton(self.scroll_carpetas, text=f"📁 {nombre}", fg_color=color, anchor="w",
                          command=lambda idx=id_c, nom=nombre: self.seleccionar_carpeta(idx, nom)).pack(fill="x", pady=4, padx=5)

    def seleccionar_carpeta(self, id_carpeta, nombre_carpeta):
        self.carpeta_seleccionada_id = id_carpeta
        self.lbl_estado_carpeta.configure(text=f"📂 {nombre_carpeta}", text_color="#1F538D", font=("Arial", 14, "bold"))
        self.btn_nuevo_snippet.configure(state="normal")
        self.btn_modo_borrar.configure(state="normal")
        self.btn_eliminar_c.pack(side="bottom", pady=15, padx=15, fill="x")
        self.modo_eliminacion = False
        self.btn_modo_borrar.configure(text=self.t["del_mode"], fg_color="#A12B2B")
        self.actualizar_vista_lista()

    def eliminar_carpeta_activa(self):
        if self.carpeta_seleccionada_id:
            self.db.eliminar_carpeta(self.carpeta_seleccionada_id)
            self.carpeta_seleccionada_id = None
            self.lbl_estado_carpeta.configure(text=self.t["empty_folder"], text_color="gray")
            self.btn_nuevo_snippet.configure(state="disabled")
            self.btn_modo_borrar.configure(state="disabled")
            self.actualizar_vista_lista()
            self.cargar_carpetas_en_ui()

    def abrir_ventana_carpeta(self):
        vent = ctk.CTkToplevel(self); vent.geometry("360x260"); vent.attributes("-topmost", True)
        entry_nom = ctk.CTkEntry(vent, width=250, placeholder_text="Nombre..."); entry_nom.pack(pady=20)
        combo_color = ctk.CTkComboBox(vent, values=[c[1] for c in COLORES_DISPONIBLES], state="readonly")
        combo_color.set("Azul")
        combo_color.pack(pady=10)
        def guardar():
            if entry_nom.get().strip():
                col_sel = next(c[0] for c in COLORES_DISPONIBLES if c[1] == combo_color.get())
                self.db.insertar_carpeta(entry_nom.get(), col_sel)
                self.cargar_carpetas_en_ui(); vent.destroy()
        ctk.CTkButton(vent, text="Crear", command=guardar).pack(pady=10)

    def alternar_modo_eliminacion(self):
        self.modo_eliminacion = not self.modo_eliminacion
        self.btn_modo_borrar.configure(text=self.t["exit_del_mode"] if self.modo_eliminacion else self.t["del_mode"],
                                       fg_color="#2E7D32" if self.modo_eliminacion else "#A12B2B")
        self.actualizar_vista_lista()

    def actualizar_vista_lista(self):
        for widget in self.lista_scroll.winfo_children(): widget.destroy()
        if not self.carpeta_seleccionada_id: return
        texto_busqueda = self.search_entry.get().lower().strip()
        snippets = self.db.obtener_por_carpeta(self.carpeta_seleccionada_id)
        if texto_busqueda: snippets = [s for s in snippets if texto_busqueda in s[1].lower() or texto_busqueda in s[2].lower()]

        for item in snippets:
            id_sp, titulo_sp, contenido_sp = item
            card = ctk.CTkFrame(self.lista_scroll, fg_color="#3D2424" if self.modo_eliminacion else "#2B2B2B", corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)
            
            # --- AQUÍ ESTÁ LA MAGIA: EL TÍTULO AHORA ES UN BOTÓN ---
            btn_abrir = ctk.CTkButton(card, text=f"📄 {titulo_sp}", fg_color="transparent", hover_color="#3D5C75", 
                                      font=("Arial", 14, "bold"), anchor="w",
                                      command=lambda idx=id_sp, tit=titulo_sp, cont=contenido_sp: self.abrir_visualizador(idx, tit, cont))
            btn_abrir.pack(side="left", fill="both", expand=True, padx=12, pady=8)
            
            actions_frame = ctk.CTkFrame(card, fg_color="transparent")
            actions_frame.pack(side="right", fill="y", padx=8)

            if not self.modo_eliminacion:
                ctk.CTkButton(actions_frame, text="📋", width=35, height=28, command=lambda code=contenido_sp: self.copiar_al_portapapeles(code)).pack(side="left", padx=2)
            else:
                ctk.CTkButton(actions_frame, text="💥", width=35, height=28, fg_color="#D32F2F", command=lambda idx=id_sp: self.ejecutar_borrado(idx)).pack(side="right", padx=2)

    # --- NUEVA FUNCIÓN PARA VER Y EDITAR NOTAS ---
    def abrir_visualizador(self, id_snippet, titulo_actual, contenido_actual):
        vent = ctk.CTkToplevel(self)
        vent.title(f"Visualizando: {titulo_actual}")
        vent.geometry("650x550")
        vent.attributes("-topmost", True)
        
        # Grid para que la caja de texto se expanda al maximizar
        vent.grid_columnconfigure(0, weight=1)
        vent.grid_rowconfigure(1, weight=1)

        entry_tit = ctk.CTkEntry(vent, font=("Arial", 16, "bold"))
        entry_tit.insert(0, titulo_actual)
        entry_tit.grid(row=0, column=0, padx=20, pady=15, sticky="ew")

        txt_cod = ctk.CTkTextbox(vent, font=("Consolas", 13))
        txt_cod.insert("1.0", contenido_actual)
        txt_cod.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        def guardar_cambios():
            nuevo_tit = entry_tit.get().strip()
            nuevo_cont = txt_cod.get("1.0", "end-1c")
            if nuevo_tit:
                # Llama a la nueva función que agregamos en bbbdd.py
                self.db.actualizar_snippet(id_snippet, nuevo_tit, nuevo_cont)
                self.actualizar_vista_lista()
                vent.destroy()

        ctk.CTkButton(vent, text="💾 Guardar Cambios", font=("Arial", 14, "bold"), height=40, command=guardar_cambios).grid(row=2, column=0, pady=15)

    def ejecutar_borrado(self, id_snippet):
        self.db.eliminar_snippet(id_snippet)
        self.actualizar_vista_lista()

    def copiar_al_portapapeles(self, texto):
        self.clipboard_clear(); self.clipboard_append(texto); self.update()

    def abrir_ventana_nuevo(self):
        vent = ctk.CTkToplevel(self); vent.geometry("600x520"); vent.attributes("-topmost", True)
        vent.grid_columnconfigure(0, weight=1); vent.grid_rowconfigure(2, weight=1)
        entry_t = ctk.CTkEntry(vent, placeholder_text="Título..."); entry_t.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        txt_cod = ctk.CTkTextbox(vent); txt_cod.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        def guardar_proceso():
            if entry_t.get().strip() and self.carpeta_seleccionada_id:
                exito, nuevo_id = self.db.insertar_snippet(self.carpeta_seleccionada_id, entry_t.get(), txt_cod.get("1.0", "end-1c"))
                if exito: self.actualizar_vista_lista(); vent.destroy()
        ctk.CTkButton(vent, text="🔒 Guardar Nuevo", height=38, command=guardar_proceso).grid(row=3, column=0, pady=15, padx=20, sticky="ew")

    # --- CONFIGURACIÓN Y MULTILENGUAJE ---
    def abrir_settings(self):
        vent = ctk.CTkToplevel(self)
        vent.title(self.t["settings"])
        vent.geometry("520x620")
        vent.attributes("-topmost", True)

        tabview = ctk.CTkTabview(vent, width=480, height=520)
        tabview.pack(padx=20, pady=10, fill="both", expand=True)
        tab_cloud = tabview.add("Cloud Sync")
        tab_settings = tabview.add("App Settings")

        ctk.CTkLabel(tab_cloud, text="Sincronización Multinube", font=("Segoe UI", 16, "bold")).pack(pady=15)
        ctk.CTkComboBox(tab_cloud, values=["OneDrive", "iCloud", "Azure Entra ID"]).pack(pady=5, padx=30, fill="x")
        ctk.CTkEntry(tab_cloud, placeholder_text="Tenant ID").pack(pady=8, padx=30, fill="x")
        ctk.CTkButton(tab_cloud, text="🔗 Autorizar", fg_color="#2E7D32").pack(pady=20, padx=30, fill="x")

        ctk.CTkLabel(tab_settings, text="Preferencias", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        ctk.CTkLabel(tab_settings, text="Idioma / Language:", anchor="w").pack(fill="x", padx=30)
        combo_idioma = ctk.CTkComboBox(tab_settings, values=list(IDIOMAS.keys()), state="readonly")
        combo_idioma.set(self.db.obtener_config("idioma", "Español"))
        combo_idioma.pack(pady=5, padx=30, fill="x")

        ctk.CTkLabel(tab_settings, text="Directorio Local:", anchor="w").pack(fill="x", padx=30, pady=(10,0))
        frame_explorador = ctk.CTkFrame(tab_settings, fg_color="transparent")
        frame_explorador.pack(fill="x", padx=30, pady=5)
        entry_path = ctk.CTkEntry(frame_explorador)
        entry_path.insert(0, self.db.obtener_config("ruta_local", ""))
        entry_path.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(frame_explorador, text="...", width=40, command=lambda: entry_path.insert(0, filedialog.askdirectory()) if filedialog.askdirectory() else None).pack(side="right")

        switch_autosave = ctk.CTkSwitch(tab_settings, text="Habilitar Auto-Save")
        switch_autosave.pack(pady=15, padx=35, anchor="w")
        if self.db.obtener_config("autosave") == "1": switch_autosave.select()

        lbl_msg = ctk.CTkLabel(vent, text="", text_color="green")
        lbl_msg.pack()

        def ejecutar_guardado():
            self.db.guardar_config("idioma", combo_idioma.get())
            self.db.guardar_config("ruta_local", entry_path.get())
            self.db.guardar_config("autosave", "1" if switch_autosave.get() else "0")
            lbl_msg.configure(text=self.t["restart_msg"])
            vent.after(1500, vent.destroy)

        ctk.CTkButton(vent, text=self.t["save_prefs"], height=35, command=ejecutar_guardado).pack(pady=10)

# ==========================================
# 2. PANTALLA DE LOGIN
# ==========================================
class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = RepositorioSnippets()
        self.title("SniX Gateway")
        self.geometry("340x360")
        
        self.frame = ctk.CTkFrame(self, corner_radius=15)
        self.frame.pack(pady=30, padx=25, fill="both", expand=True)
        self.lbl_titulo = ctk.CTkLabel(self.frame, text="🔒 Acceso", font=("Arial", 18, "bold"))
        self.lbl_titulo.pack(pady=(25, 15))
        
        self.entry_user = ctk.CTkEntry(self.frame, placeholder_text="Usuario", width=240)
        self.entry_user.pack(pady=10)
        self.entry_pass = ctk.CTkEntry(self.frame, placeholder_text="Clave", show="*", width=240)
        self.entry_pass.pack(pady=10)
        self.lbl_error = ctk.CTkLabel(self.frame, text="", text_color="red")
        self.lbl_error.pack()
        
        if not self.db.hay_usuarios_registrados():
            ctk.CTkButton(self.frame, text="Registrar", command=self.registrar).pack(pady=20)
        else:
            ctk.CTkButton(self.frame, text="Autenticar", command=self.login).pack(pady=20)

    def login(self):
        if self.db.validar_login(self.entry_user.get().strip(), self.entry_pass.get().strip()):
            self.withdraw()
            app_boveda = SniXCloudApp(self.db, self)
            app_boveda.grab_set()
        else: 
            self.lbl_error.configure(text="Credenciales inválidas")

    def registrar(self):
        if self.db.registrar_usuario(self.entry_user.get().strip(), self.entry_pass.get().strip()):
            self.destroy()
            LoginApp().mainloop()
        else: 
            self.lbl_error.configure(text="Error de registro")

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()