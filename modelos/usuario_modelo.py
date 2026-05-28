# modelos/usuario_modelo.py
from conexion import obtener_conexion

class UsuarioModelo:
    def __init__(self):
        pass

    def verificar_credenciales(self, usuario, contrasena):
        """
        Consulta las credenciales usando las columnas reales de tu clúster en Aiven.
        """
        conexion = obtener_conexion()
        if not conexion:
            return None
            
        try:
            with conexion.cursor() as cursor:
                # 👇 CAMBIO CLAVE: Usamos las columnas reales indexadas en tu panel de Aiven
                # Cambié 'email' por 'username_log' y 'rol' por 'id_rol' o la columna de texto de tu rol
                sql = "SELECT id_rol FROM usuarios WHERE username_log = %s AND password = %s"
                cursor.execute(sql, (usuario, contrasena))
                resultado = cursor.fetchone()
                
                if resultado:
                    # Retorna el rol encontrado (ej: si id_rol es un número o texto, lo procesa el controlador)
                    return str(resultado[0])
                return None
        except Exception as e:
            print(f"❌ Error en la consulta de credenciales: {e}")
            return None
        finally:
            conexion.close()