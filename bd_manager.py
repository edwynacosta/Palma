# bd_manager.py
import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="palma_db"
        )
        if conexion.is_connected():
            print("🚀 ¡Conexión exitosa a XAMPP MySQL!") 
            return conexion
            
    except Error as err:
        # Esto te dirá el número exacto del problema en la terminal de VS Code
        print("\n❌ ¡OCURRIÓ UN ERROR DE CAPA DE DATOS!")
        print(f"Detalle técnico del error: {err}")
        print(f"Código del error de MySQL: {err.errno}\n")
        return None