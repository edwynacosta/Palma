import pymysql

# ==============================================================================
# CONFIGURACIÓN DE CREDENCIALES DE AIVEN
# ==============================================================================
HOST_AIVEN = 'mysql-1d0abef0-palmasoftware.l.aivencloud.com'  
PUERTO_AIVEN = 24083  # Cambia por el número de puerto que te asigne Aiven
USUARIO_AIVEN = 'avnadmin'
PASSWORD_AIVEN = 'AVNS_zsnkr3NzJBC4GGAMW3A'       
DB_NAME = 'defaultdb'  # En Aiven siempre trabajamos sobre la base por defecto

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