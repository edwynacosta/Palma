import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from dotenv import load_dotenv

load_dotenv()

try:
    from conexion import conexion_db
except ImportError as e:
    print(f"[-] Error crítico: No se encontró el archivo 'conexion.py' o falló la importación: {e}")
    sys.exit(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    print("[*] Conectando con el clúster de Aiven...")
    conexion = conexion_db()
    
    if conexion:
        print("[+] ¡Base de datos de Aiven vinculada con éxito al sistema Palma!")
        
        try:
            # ---------------------------------------------------------
            # IMPORTANTE: Aquí es donde debes importar e instanciar 
            # la clase de tu ventana de Login o Interfaz Principal.
            # Por ejemplo:
            #
            # from vistas.login import LoginVentana
            # ventana = LoginVentana(conexion)
            # ventana.show()
            # ---------------------------------------------------------
            
            # Mensaje informativo en consola mientras integras tus interfaces
            print("[*] Ejecutando el bucle principal de PySide6...")
            
            # Este método mantiene la ventana abierta y escuchando los clics del usuario
            sys.exit(app.exec())
            
        except Exception as error_vista:
            print(f"[-] Error al inicializar la interfaz gráfica: {error_vista}")
            sys.exit(1)
            
    else:
        # Si la función devolvió None, le mostramos un aviso visual al usuario
        print("[-] Error: No se pudo iniciar el sistema de inventarios.")
        
        # Creamos un cuadro de diálogo nativo de PySide6 para alertar del problema
        alerta = QMessageBox()
        alerta.setIcon(QMessageBox.Critical)
        alerta.setWindowTitle("Error de Conexión")
        alerta.setText("No se pudo conectar con el servidor de Base de Datos en la nube.")
        alerta.setInformativeText(
            "Por favor, verifica que tu archivo '.env' tenga las credenciales correctas "
            "y que cuentes con acceso estable a internet."
        )
        alerta.exec()
        
        # Cerramos de forma segura
        sys.exit(1)