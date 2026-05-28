import pymysql
import os  # 👈 ¡Corregido! Aquí está la importación que causaba el NameError

# ==============================================================================
# 1. CREDENCIALES DE TU SERVICIO MYSQL EN AIVEN
# ==============================================================================
HOST_AIVEN = 'mysql-1d0abef0-palmasoftware.l.aivencloud.com'  
PUERTO_AIVEN = 24083                               
USUARIO_AIVEN = 'avnadmin'
PASSWORD_AIVEN = 'AVNS_zsnkr3NzJBC4GGAMW3A'  # ⚠️ Pon aquí tu contraseña de Aiven
DB_NAME = 'defaultdb'                       

# ==============================================================================
# 2. CONFIGURACIÓN DEL ARCHIVO .SQL LOCAL
# ==============================================================================
# 💡 Coloca aquí el nombre exacto de tu archivo .sql que está en la carpeta Palma
ARCHIVO_SQL = 'palma_db.sql' 

def importar_archivo_sql():
    # Validamos la existencia física del archivo .sql antes de abrir la red
    if not os.path.exists(ARCHIVO_SQL):
        print(f"❌ Error: No se encontró el archivo '{ARCHIVO_SQL}' en la carpeta.")
        print("💡 Copia tu archivo .sql dentro de la carpeta 'Palma' y verifica su nombre.")
        return

    conexion = None
    try:
        print(f"📡 Conectando a Aiven MySQL...")
        conexion = pymysql.connect(
            host=HOST_AIVEN,
            port=PUERTO_AIVEN,
            user=USUARIO_AIVEN,
            password=PASSWORD_AIVEN,
            database=DB_NAME,
            ssl={'ssl_mode': 'REQUIRED'},
            connect_timeout=45,  # Extendemos tiempos para evitar timeouts de red
            read_timeout=120,    
            write_timeout=120,   
            autocommit=False     # Control manual de la transacción
        )
        
        cursor = conexion.cursor()
        print("🔒 ¡Enlace SSL establecido con éxito!")

        print(f"📖 Leyendo '{ARCHIVO_SQL}'...")
        with open(ARCHIVO_SQL, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Separamos el script completo por instrucciones individuales mediante el punto y coma (;)
        instrucciones = contenido.split(';')
        
        print("🚀 Enviando sentencias secuencialmente a la nube...")
        contador_ejecutadas = 0

        for instruccion in instrucciones:
            sql = instruccion.strip()
            
            # Saltamos líneas vacías o comentarios del motor de bases de datos
            if not sql or sql.startswith('--') or sql.startswith('/*') or sql.startswith('#'):
                continue
            
            # Filtro para ignorar comandos que intenten cambiar de base de datos fuera de defaultdb
            sql_upper = sql.upper()
            if sql_upper.startswith('CREATE DATABASE') or sql_upper.startswith('USE '):
                continue

            try:
                cursor.execute(sql)
                contador_ejecutadas += 1
            except pymysql.MySQLError as error_sentencia:
                print(f"⚠️ Nota en instrucción {contador_ejecutadas + 1}: {error_sentencia}")
                # Si es un error menor (ej. borrar una tabla que no existía), continuamos

        # Confirmamos la transacción completa en el almacenamiento en la nube
        print("\n💾 Confirmando y guardando datos en la nube (Commit)...")
        conexion.commit()
        print(f"🎉 ¡Importación completada! Se procesaron {contador_ejecutadas} sentencias SQL.")

    except Exception as e:
        print(f"\n❌ Error crítico durante la importación: {e}")
        if conexion:
            conexion.rollback()
            print("🔄 Rollback: Se restauró el estado anterior por seguridad.")
    finally:
        if conexion:
            cursor.close()
            conexion.close()
            print("🔌 Conexión cerrada de forma segura.")

if __name__ == "__main__":
    importar_archivo_sql()