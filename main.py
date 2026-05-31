import sys
from dotenv import load_dotenv # Añadir esto
import os 
from PySide6.QtWidgets import QApplication, QStackedWidget
from conexion import conexion_db
from vistas.login_vista import LoginVista
from vistas.admin_vista import AdminDashboardQt

load_dotenv() # <--- ESTO ES LO MÁS IMPORTANTE. Añadir esto antes de llamar a conexion_db()


class AppControlador:
    def __init__(self, conexion):
        self.conexion = conexion
        self.stack = QStackedWidget()
        
        self.login_view = LoginVista(self)
        self.admin_view = AdminDashboardQt(self)
        
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.admin_view)
        
        self.stack.setCurrentWidget(self.login_view)
        self.stack.resize(1200, 700)
        self.stack.show()

    def cambiar_pantalla(self, nombre_pantalla):
        if nombre_pantalla == "AdminDashboard":
            self.stack.setCurrentWidget(self.admin_view)
        else:
            self.stack.setCurrentWidget(self.login_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    conexion = conexion_db()
    if conexion:
        controlador = AppControlador(conexion)
        sys.exit(app.exec())