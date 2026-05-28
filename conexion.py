import os
import pymysql
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Obtener las credenciales de manera segura desde el entorno
HOST_AIVEN = os.getenv("AIVEN_HOST")
# Convertimos el puerto a entero (int) y usamos 3306 como respaldo por defecto
PUERTO_AIVEN = int(os.getenv("AIVEN_PORT", 3306))
USUARIO_AIVEN = os.getenv("AIVEN_USER")
PASSWORD_AIVEN = os.getenv("AIVEN_PASSWORD")
DB_NAME = os.getenv("AIVEN_DB_NAME")

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