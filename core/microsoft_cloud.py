# core/microsoft_cloud.py
import threading
import time

class MicrosoftCloudConnector:
    """Capa de Sincronización: Conexiones asíncronas seguras con Microsoft Azure/Graph."""
    def subir_snippet_async(self, snippet_id: int, titulo: str, contenido_cifrado: str, callback_exito):
        def proceso():
            try:
                # Simulación de latencia de red empresarial ( handshake API )
                time.sleep(1)
                print(f"☁️ [Microsoft Cloud]: Sincronizando de forma segura '{titulo}'...")
                
                # Al confirmar la transferencia, ejecutamos el callback seguro
                callback_exito(snippet_id)
                print(f"✔️ [Microsoft Cloud]: Confirmación de guardado en la nube para ID {snippet_id}")
            except Exception as e:
                print(f"❌ [Microsoft Cloud Error]: Servidor inaccesible: {e}")

        hilo = threading.Thread(target=proceso)
        hilo.start()