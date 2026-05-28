import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def conexion_db():
    try:
        conexion = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl_disabled=False # Habilita SSL automáticamente para Aiven
        )
        print("¡Conexión segura establecida con PyMySQL en Aiven!")
        return conexion
    except pymysql.MySQLError as error:
        print(f"Error: {error}")
        return None