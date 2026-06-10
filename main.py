import sys
import os
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon
from conexion import conexion_db

from vistas.login_vista import LoginVista
from vistas.admin_vista import AdminDashboardQt
from vistas.caja_vista import CajaVista
from vistas.cajero_vista import CajeroDashboardQt

load_dotenv()

class MainWindow(QMainWindow):
    def __init__(self, conexion):
        super().__init__()
        self.conexion     = conexion
        self.usuario_actual = None

        self.setWindowTitle("PALMA")

        ruta_icono = os.path.join("vistas", "logo_palma.ico")
        if os.path.exists(ruta_icono):
            self.setWindowIcon(QIcon(ruta_icono))

        self.setStyleSheet("QMainWindow { background-color: #008037; }")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout_central = QVBoxLayout(self.central_widget)
        layout_central.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        layout_central.addWidget(self.stack)

        self.login_view  = LoginVista(self)
        self.admin_view  = AdminDashboardQt(self, datos_usuario={})
        self.cajero_view = CajeroDashboardQt(self, datos_usuario={})
        self.caja_view   = CajaVista(self)

        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.admin_view)
        self.stack.addWidget(self.cajero_view)
        self.stack.addWidget(self.caja_view)

        self.stack.setCurrentWidget(self.login_view)
        self.showMaximized()

    def cambiar_pantalla(self, nombre_pantalla, datos_usuario=None):
        # ── Guardar sesión solo cuando vienen datos nuevos ─────────────────────
        if datos_usuario:
            self.usuario_actual = datos_usuario   # ya viene limpio desde login_vista

        datos   = self.usuario_actual or {}
        id_rol  = datos.get("id_rol")             # 1 = admin, 2 = cajero  (entero o str)
        nombre  = datos.get("username_log", "Usuario")
        rol_txt = datos.get("rol", "")

        print(f"[ROUTER] pantalla='{nombre_pantalla}' | id_rol={id_rol} | rol='{rol_txt}' | nombre='{nombre}'")

        # ── Intercepción: cajero nunca puede llegar al panel admin ─────────────
        if str(id_rol) == "2":
            if nombre_pantalla in ("AdminDashboard", "MainDashboard"):
                print("[ROUTER] Cajero → redirigido a CajeroDashboard")
                nombre_pantalla = "CajeroDashboard"

        # ── Enrutamiento ───────────────────────────────────────────────────────
        if nombre_pantalla == "AdminDashboard":
            self.admin_view.datos_usuario = datos
            self.admin_view.actualizar_interfaz_usuario()
            self.stack.setCurrentWidget(self.admin_view)

        elif nombre_pantalla == "CajeroDashboard":
            self.cajero_view.datos_usuario = datos
            self.cajero_view.actualizar_interfaz_usuario()
            self.stack.setCurrentWidget(self.cajero_view)

        elif nombre_pantalla == "Caja":
            if hasattr(self.caja_view, "lbl_nombre_cajero"):
                self.caja_view.lbl_nombre_cajero.setText(nombre.title())
            if hasattr(self.caja_view, "lbl_avatar"):
                iniciales = "".join([n[0] for n in nombre.split()[:2]]).upper()
                self.caja_view.lbl_avatar.setText(
                    f"<span style='color:#1A7C3E;font-weight:bold;font-size:12px;'>{iniciales}</span>"
                )
            self.stack.setCurrentWidget(self.caja_view)

        else:
            # Login / LoginFrame / cualquier destino desconocido
            self.usuario_actual = None
            self.stack.setCurrentWidget(self.login_view)
            print("[ROUTER] → Login")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    conexion = conexion_db()
    if conexion:
        ventana = MainWindow(conexion)
        sys.exit(app.exec())
    else:
        sys.exit(1)
