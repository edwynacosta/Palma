import mysql.connector

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",      # Servidor local de XAMPP
            user="root",           # Usuario por defecto de XAMPP
            password="",           # IMPORTANTE: En XAMPP la contraseña va VACÍA (sin espacios, solo comillas)
            database="palma_db"    # Asegúrate de que este nombre coincida con tu phpMyAdmin
        )
        if conexion.is_connected():
            print("🚀 ¡Conexión exitosa a XAMPP MySQL!")
            return conexion
    except mysql.connector.Error as err:
        print(f"❌ Error de conexión: {err}")
        return None

def cerrar_conexion(conexion, cursor=None):
    """Cierra de forma segura el cursor y la conexión."""
    try:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
            print("🔌 Conexión cerrada correctamente.")
    except mysql.connector.Error as err:
        print(f"⚠️ Error al cerrar la conexión: {err}")