# modelos/usuario_modelo.py
from conexion import obtener_conexion  # <-- Conexión a la nube de Aiven

class UsuarioModelo:
    def __init__(self):
        # Al instanciar el modelo, podemos probar si la red hacia Aiven responde
        self.probar_conexion_nube()

    def probar_conexion_nube(self):
        conexion = obtener_conexion()
        if conexion:
            conexion.close()
            print("📡 [Modelo] Prueba de conexión exitosa con el clúster de Aiven.")
        else:
            print("⚠️ [Modelo] No se pudo establecer contacto con la base de datos remota.")

    def verificar_usuario(self, usuario, contrasena):
        """Método de ejemplo para validar credenciales en la nube"""
        conexion = obtener_conexion()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                # Ajusta la consulta según el nombre exacto de tu tabla y columnas
                sql = "SELECT * FROM usuarios WHERE email = %s AND password = %s"
                cursor.execute(sql, (usuario, contrasena))
                resultado = cursor.fetchone()
                return resultado is not None
        except Exception as e:
            print(f"Error al consultar usuario: {e}")
            return False
        finally:
            conexion.close()