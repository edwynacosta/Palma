import sys
import os
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from conexion import conexion_db

# Importación de todas las vistas del ecosistema Palma
from vistas.login_vista import LoginVista
from vistas.admin_vista import AdminDashboardQt
from vistas.caja_vista import CajaVista  # <- Nueva vista de caja insertada

load_dotenv()

class MainWindow(QMainWindow):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        self.setWindowTitle("PALMA")
        
        # Icono de la aplicación
        ruta_icono = os.path.join("vistas", "logo_palma.ico")
        if os.path.exists(ruta_icono):
            self.setWindowIcon(QIcon(ruta_icono))
            
        self.setStyleSheet("QMainWindow { background-color: #008037; }")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout_central = QVBoxLayout(self.central_widget)
        self.layout_central.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        self.layout_central.addWidget(self.stack)
        
        # Inicialización e inyección de dependencias en las vistas
        self.login_view = LoginVista(self)
        self.admin_view = AdminDashboardQt(self, datos_usuario={})
        self.caja_view = CajaVista(self)  # <- Instancia de la caja vinculada al controlador
        
        # Registro en el StackedWidget
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.admin_view)
        self.stack.addWidget(self.caja_view)  # <- Añadida al gestor de pantallas
        
        # Pantalla inicial por defecto
        self.stack.setCurrentWidget(self.login_view)
        self.showMaximized()

    def cambiar_pantalla(self, nombre_pantalla, datos_usuario=None):
        """Gestiona el enrutamiento de la aplicación y la inyección de datos de sesión."""
        if nombre_pantalla == "AdminDashboard":
            if datos_usuario:
                self.admin_view.datos_usuario = datos_usuario
            if hasattr(self.admin_view, 'actualizar_interfaz_usuario'):
                self.admin_view.actualizar_interfaz_usuario()
            self.stack.setCurrentWidget(self.admin_view)
            
        elif nombre_pantalla == "Caja":
            # Si se pasa información de usuario desde el login o dashboard, la enviamos a la caja
            if datos_usuario and hasattr(self.caja_view, 'lbl_nombre_cajero'):
                nombre = datos_usuario.get('username_log', "Edwin Acosta")
                self.caja_view.lbl_nombre_cajero.setText(nombre)
                # Forzar actualización de iniciales del avatar
                iniciales = "".join([n[0] for n in nombre.split()[:2]]).upper()
                self.caja_view.lbl_avatar.setText(
                    f"<span style='color:#1A7C3E; font-weight:bold; font-size:12px;'>{iniciales}</span>"
                )
            self.stack.setCurrentWidget(self.caja_view)
            
        else:
            # Enrutamiento de seguridad: Cualquier otra pantalla regresa al Login
            self.stack.setCurrentWidget(self.login_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    conexion = conexion_db()
    if conexion:
        ventana_principal = MainWindow(conexion)
        sys.exit(app.exec())
    else:
        sys.exit(1)