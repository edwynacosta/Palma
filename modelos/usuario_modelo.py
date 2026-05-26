# modelos/usuario_modelo.py
from bd_manager import obtener_conexion
import mysql.connector

class UsuarioModelo:
    def verificar_credenciales(self, usuario, password):
        conexion = obtener_conexion()
        if not conexion:
            return None
            
        cursor = conexion.cursor(dictionary=True)
        user_lower = usuario.lower()
        
        try:
            # Traemos las columnas reales de tu XAMPP: username_log y contrasena_log
            query = "SELECT username_log, contrasena_log, id_rol FROM usuarios WHERE username_log = %s"
            cursor.execute(query, (user_lower,))
            resultado = cursor.fetchone()
            
            if resultado:
                # REPARACIÓN: Usamos 'contrasena_log' para evitar el KeyError
                if resultado["contrasena_log"] == password:
                    return {
                        "nombre": resultado["username_log"],
                        "rol": str(resultado["id_rol"])
                    }
                else:
                    print("Contraseña incorrecta.")
            else:
                print("El usuario no existe.")
                
        except mysql.connector.Error as err:
            print(f"Error de SQL: {err}")
        finally:
            cursor.close()
            conexion.close()
            
        return None