from bd_manager import obtener_conexion
import mysql.connector

class UsuarioModelo:
    def verificar_credenciales(self, usuario, password):
        """
        Consulta la base de datos en XAMPP para validar al usuario.
        Retorna un diccionario con los datos del usuario si coincide, o None si falla.
        """
        conexion = obtener_conexion()
        if not conexion:
            return None  # Si la base de datos está apagada, falla la validación
            
        cursor = conexion.cursor(dictionary=True) # dictionary=True nos devuelve el registro como un dict de Python
        user_lower = usuario.lower()
        
        try:
            # Consulta SQL parametrizada por seguridad (evita Inyección SQL)
            query = "SELECT username, password, rol, nombre FROM usuarios WHERE username = %s"
            cursor.execute(query, (user_lower,))
            resultado = cursor.fetchone()
            
            # Si el usuario existe y la contraseña coincide
            if resultado and resultado["password"] == password:
                # Retornamos los datos tal cual los espera nuestro controlador
                return {
                    "nombre": resultado["nombre"],
                    "rol": resultado["rol"]
                }
                
        except mysql.connector.Error as err:
            print(f"Error en la consulta SQL: {err}")
            
        finally:
            # Buenas prácticas: Cerramos los canales de comunicación siempre
            cursor.close()
            conexion.close()
            
        return None