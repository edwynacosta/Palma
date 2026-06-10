import os
import pymysql

def conexion_db():
    try:
        conexion = pymysql.connect(
            host=os.getenv("DB_HOST", "mysql-1d0abef0-palmasoftware.l.aivencloud.com"),
            port=int(os.getenv("DB_PORT", 24083)),
            user=os.getenv("DB_USER", "avnadmin"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "defaultdb"),
            ssl={'ssl_mode': 'REQUIRED'},
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conexion
    except Exception as e:
        # Limpiar el mensaje de error
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error en conexion_db: {error_msg}")
        return None

def obtener_conexion():
    return conexion_db()