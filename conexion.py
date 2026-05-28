import pymysql
import os
from dotenv import load_dotenv
# ... tus otras importaciones (como mysql.connector, psycopg2, etc.)

# Cargar las variables del archivo .env
load_dotenv()

# Obtener las credenciales de manera segura
DB_PASSWORD = os.getenv("AIVEN_PASSWORD")
DB_HOST = os.getenv("AIVEN_HOST")
DB_USER = os.getenv("AIVEN_USER")

def obtener_conexion():
    """
    Establece una conexión segura SSL compatible con las restricciones de Aiven.
    """
    print(f"📡 Intentando abrir socket hacia: {HOST_AIVEN}:{PUERTO_AIVEN}...")
    try:
        conexion = pymysql.connect(
            host=HOST_AIVEN,
            port=PUERTO_AIVEN,
            user=USUARIO_AIVEN,
            password=PASSWORD_AIVEN,
            database=DB_NAME,
            # 👇 FORZAMOS EL MODO SSL REQUERIDO PARA EVITAR EL CORTE DE AIVEN
            ssl={'ssl_mode': 'REQUIRED'}, 
            connect_timeout=30,   # Más tiempo para el saludo inicial
            read_timeout=60,      # Evita que muera durante queries
            write_timeout=60,
            autocommit=True  
        )
        print("✅ Enlace de red establecido de forma segura con SSL.")
        return conexion
    except pymysql.MySQLError as e:
        print(f"❌ Error crítico de conexión: {e}")
        return None