from conexion import obtener_conexion

class UsuarioModelo:
    def __init__(self):
        pass

    def verificar_credenciales(self, usuario, contrasena):
        conexion = obtener_conexion()
        if not conexion:
            print("No se pudo establecer conexión con la base de datos")
            return None
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT id_usuario, username_log, id_rol
                    FROM usuarios 
                    WHERE username_log = %s AND contrasena_log = %s
                """
                cursor.execute(sql, (usuario, contrasena))
                resultado = cursor.fetchone()
                
                if resultado:
                    # Retorna el diccionario completo con los datos del usuario
                    return resultado
                return None
        except Exception as e:
            print(f"Error en la consulta de credenciales: {e}")
            return None
        finally:
            conexion.close()