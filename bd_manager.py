import mysql.connector

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="tu_contraseña",
            database="palma_db"
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None