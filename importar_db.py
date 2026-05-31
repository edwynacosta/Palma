import os
import pymysql
from dotenv import load_dotenv

# Cargamos entorno en caso de ejecutar este script por separado
load_dotenv()

def importar_script_sql(ruta_sql):
    # Conexión directa temporal para la importación
    try:
        conexion = pymysql.connect(
            host=os.getenv("DB_HOST", "mysql-1d0abef0-palmasoftware.l.aivencloud.com"),
            port=int(os.getenv("DB_PORT", 24083)),
            user=os.getenv("DB_USER", "avnadmin"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "defaultdb"),
            ssl={'ssl_mode': 'REQUIRED'}
        )
        
        print("[*] Leyendo archivo SQL local...")
        with open(ruta_sql, 'r', encoding='utf-8') as archivo:
            # Separamos las consultas por punto y coma para ejecutarlas una a una
            consultas_sql = archivo.read().split(';')
        
        with conexion.cursor() as cursor:
            print("[*] Subiendo estructuras y datos a Aiven...")
            for consulta in consultas_sql:
                # Limpiamos espacios en blanco o líneas vacías
                consulta_limpia = consulta.strip()
                if consulta_limpia:
                    cursor.execute(consulta_limpia)
            
            conexion.commit()
        print("[+] ¡Importación completada con éxito en Aiven!")
        
    except Exception as e:
        print(f"[-] Error durante la importación: {e}")
    finally:
        if 'conexion' in locals() and conexion.open:
            conexion.close()

# Si ejecutas este archivo directamente, correrá la importación
if __name__ == "__main__":
    ruta = os.path.join(os.path.dirname(__file__), "palma_db.sql")
    importar_script_sql(ruta)