import os
import pymysql

def conexion_db():
    try:
        # Extraemos los datos del entorno (.env ya fue cargado en main.py)
        conexion = pymysql.connect(
            host=os.getenv("DB_HOST", "mysql-1d0abef0-palmasoftware.l.aivencloud.com"),
            port=int(os.getenv("DB_PORT", 24083)),
            user=os.getenv("DB_USER", "avnadmin"),
            password=os.getenv("DB_PASSWORD"),  # Tu contraseña de Aiven
            database=os.getenv("DB_NAME", "defaultdb"),
            ssl={'ssl_mode': 'REQUIRED'}, # CLAVE: Requerido por Aiven
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor # Te devuelve las consultas como diccionarios
        )
        return conexion
    except pymysql.MySQLError as e:
        print(f"[-] Error de conexión a Aiven: {e}")
        return None