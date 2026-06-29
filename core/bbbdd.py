import sqlite3
import os
from core.seguridad import GestorSeguridad

class RepositorioSnippets:
    def __init__(self):
        self.seguridad = GestorSeguridad()
        self.db_path = os.path.join(self.seguridad.ruta_app, "snix_boveda.db")
        self._inicializar_tablas()

    def _inicializar_tablas(self):
        with sqlite3.connect(self.db_path) as conexion:
            cursor = conexion.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash BLOB, salt BLOB)")
            cursor.execute("CREATE TABLE IF NOT EXISTS carpetas (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, color TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS snippets (id INTEGER PRIMARY KEY AUTOINCREMENT, carpeta_id INTEGER, titulo TEXT, contenido TEXT, sincronizado_cloud INTEGER DEFAULT 0, FOREIGN KEY (carpeta_id) REFERENCES carpetas(id) ON DELETE CASCADE)")
            cursor.execute("CREATE TABLE IF NOT EXISTS configuracion (clave TEXT PRIMARY KEY, valor TEXT)")
            conexion.commit()

    def obtener_config(self, clave, por_defecto=""):
        with sqlite3.connect(self.db_path) as c:
            res = c.execute("SELECT valor FROM configuracion WHERE clave = ?", (clave,)).fetchone()
            return res[0] if res else por_defecto

    def guardar_config(self, clave, valor):
        with sqlite3.connect(self.db_path) as c:
            c.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (clave, str(valor)))
            c.commit()

    def hay_usuarios_registrados(self):
        with sqlite3.connect(self.db_path) as c: 
            return c.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] > 0

    def registrar_usuario(self, user, pwd):
        h, s = self.seguridad.hashear_password(pwd)
        try:
            with sqlite3.connect(self.db_path) as c: 
                c.execute("INSERT INTO usuarios (username, password_hash, salt) VALUES (?, ?, ?)", (user, h, s))
                c.commit()
                return True
        except: return False

    def validar_login(self, user, pwd):
        with sqlite3.connect(self.db_path) as c:
            res = c.execute("SELECT password_hash, salt FROM usuarios WHERE username = ?", (user,)).fetchone()
            return self.seguridad.verificar_password(pwd, res[0], res[1]) if res else False

    def insertar_carpeta(self, nombre, color):
        with sqlite3.connect(self.db_path) as c: 
            c.execute("INSERT INTO carpetas (nombre, color) VALUES (?, ?)", (nombre, color))
            c.commit()

    def obtener_carpetas(self):
        with sqlite3.connect(self.db_path) as c: 
            return c.execute("SELECT id, nombre, color FROM carpetas").fetchall()

    def insertar_snippet(self, carpeta_id, titulo, contenido):
        cifrado = self.seguridad.cifrar_texto(contenido)
        with sqlite3.connect(self.db_path) as c:
            cur = c.execute("INSERT INTO snippets (carpeta_id, titulo, contenido, sincronizado_cloud) VALUES (?, ?, ?, 0)", (carpeta_id, titulo, cifrado))
            c.commit()
            return True, cur.lastrowid

    def obtener_por_carpeta(self, carpeta_id):
        return [(id, t, self.seguridad.descifrar_texto(c)) for id, t, c in sqlite3.connect(self.db_path).execute("SELECT id, titulo, contenido FROM snippets WHERE carpeta_id = ?", (carpeta_id,)).fetchall()]

    def eliminar_snippet(self, id):
        with sqlite3.connect(self.db_path) as c: 
            c.execute("DELETE FROM snippets WHERE id = ?", (id,))
            c.commit()
            
    def eliminar_carpeta(self, id):
        with sqlite3.connect(self.db_path) as c: 
            c.execute("DELETE FROM carpetas WHERE id = ?", (id,))
            c.commit()

    def actualizar_titulo_snippet(self, id, nuevo_titulo):
        with sqlite3.connect(self.db_path) as c: 
            c.execute("UPDATE snippets SET titulo = ? WHERE id = ?", (nuevo_titulo, id))
            c.commit()

    def actualizar_snippet(self, id, nuevo_titulo, nuevo_contenido):
        cifrado = self.seguridad.cifrar_texto(nuevo_contenido)
        with sqlite3.connect(self.db_path) as c:
            c.execute("UPDATE snippets SET titulo = ?, contenido = ? WHERE id = ?", (nuevo_titulo, cifrado, id))
            c.commit()