import sys
import os
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from conexion import conexion_db
from vistas.login_vista import LoginVista
from vistas.admin_vista import AdminDashboardQt
from vistas.inventario_vista import InventarioVista
from vistas.proveedores_vista import ProveedoresVista

load_dotenv()

class MainWindow(QMainWindow):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        self.setWindowTitle("PALMA")
        
        # Icono
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
        
        # Inicialización de vistas
        self.login_view = LoginVista(self)
        self.admin_view = AdminDashboardQt(self, datos_usuario={})
        self.inventario_view = InventarioVista(self, self.conexion)
        self.proveedores_view = ProveedoresVista(self, self.conexion)
        
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.admin_view)
        self.stack.addWidget(self.inventario_view)
        self.stack.addWidget(self.proveedores_view)
        
        self.stack.setCurrentWidget(self.login_view)
        self.showMaximized()

    def cambiar_pantalla(self, nombre_pantalla, datos_usuario=None):
        if nombre_pantalla == "AdminDashboard":
            if datos_usuario:
                self.admin_view.datos_usuario = datos_usuario
            if hasattr(self.admin_view, 'actualizar_interfaz_usuario'):
                self.admin_view.actualizar_interfaz_usuario()
            self.stack.setCurrentWidget(self.admin_view)
        elif nombre_pantalla == "Inventario":
            if hasattr(self.inventario_view, "cargar_productos"):
                self.inventario_view.cargar_productos()
            self.stack.setCurrentWidget(self.inventario_view)
        elif nombre_pantalla == "Proveedores":
            if hasattr(self.proveedores_view, "cargar_proveedores"):
                self.proveedores_view.cargar_proveedores()
            self.stack.setCurrentWidget(self.proveedores_view)
        else:
            self.stack.setCurrentWidget(self.login_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    conexion = conexion_db()
    if conexion:
        ventana_principal = MainWindow(conexion)
        sys.exit(app.exec())
    else:
        sys.exit(1)
