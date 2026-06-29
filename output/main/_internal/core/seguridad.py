import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class GestorSeguridad:
    def __init__(self, frase_maestra: str = "SniX_Cloud_Enterprise_2026"):
        self.ruta_app = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local")), "SniXCloud")
        os.makedirs(self.ruta_app, exist_ok=True)
        self.clave = self._derivar_clave_local(frase_maestra)
        self.fernet = Fernet(self.clave)

    def _derivar_clave_local(self, frase: str) -> bytes:
        archivo_sal = os.path.join(self.ruta_app, ".inst_salt")
        if os.path.exists(archivo_sal):
            with open(archivo_sal, "rb") as f:
                sal = f.read()
        else:
            sal = os.urandom(16)
            with open(archivo_sal, "wb") as f:
                f.write(sal)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=sal,
            iterations=100000
        )
        return base64.urlsafe_b64encode(kdf.derive(frase.encode()))

    def cifrar_texto(self, texto_plano: str) -> str:
        if not texto_plano.strip(): return ""
        return self.fernet.encrypt(texto_plano.encode()).decode()

    def descifrar_texto(self, texto_cifrado: str) -> str:
        if not texto_cifrado.strip(): return ""
        try:
            return self.fernet.decrypt(texto_cifrado.encode()).decode()
        except Exception:
            return "❌ [Error: Datos corruptos]"

    # --- NUEVAS FUNCIONES PARA CONTRASEÑAS ---
    def hashear_password(self, password: str, salt: bytes = None) -> tuple:
        """Crea un hash seguro de la contraseña."""
        if salt is None:
            salt = os.urandom(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return hash_obj, salt

    def verificar_password(self, password_intento: str, hash_guardado: bytes, salt: bytes) -> bool:
        """Verifica si la contraseña ingresada coincide con el hash guardado."""
        hash_intento, _ = self.hashear_password(password_intento, salt)
        return hash_intento == hash_guardado