import sys
import os
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtCore import Qt
from conexion import conexion_db

from vistas.login_vista import LoginVista
from vistas.admin_vista import AdminDashboardQt
from vistas.caja_vista import CajaVista
from vistas.cajero_vista import CajeroDashboardQt
from vistas.facturaelectronica_vista import FacturaElectronicaVista
from vistas.ReciboProveedores_vista import ReciboProveedoresVista
from vistas.inventario_vista import InventarioVista
from vistas.proveedor_vista import ProveedoresVista
from vistas.finanzas_vista import FinanzasVista

load_dotenv()

class MainWindow(QMainWindow):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        self.usuario_actual = None

        self.setWindowTitle("Palma software")

        ruta_icono = os.path.join("vistas", "logo_palma.ico")
        if os.path.exists(ruta_icono):
            self.setWindowIcon(QIcon(ruta_icono))

        self.setStyleSheet("QMainWindow { background-color: #008037; }")

        # ── CONFIGURACIÓN DE VENTANA SIN BORDES ──
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout_central = QVBoxLayout(self.central_widget)
        layout_central.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        layout_central.addWidget(self.stack)

        self.login_view = LoginVista(self)
        self.admin_view = AdminDashboardQt(self, datos_usuario={})
        self.cajero_view = CajeroDashboardQt(self, datos_usuario={})
        self.caja_view = CajaVista(self)
        self.factura_view = FacturaElectronicaVista(conexion=self.conexion)
        self.inventario_view = InventarioVista(self, conexion)
        self.proveedores_view = ProveedoresVista(self, conexion)
        self.finanzas_view = FinanzasVista(self, conexion)

        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.admin_view)
        self.stack.addWidget(self.cajero_view)
        self.stack.addWidget(self.caja_view)
        self.stack.addWidget(self.factura_view)
        self.stack.addWidget(self.inventario_view)
        self.stack.addWidget(self.proveedores_view)
        self.stack.addWidget(self.finanzas_view)

        self.stack.setCurrentWidget(self.login_view)
        
        # ── APLICAR EL AJUSTE DE PANTALLA EN LUGAR DE showMaximized() ──
        self.congelar_tamano_pantalla()
        self.show()

    def congelar_tamano_pantalla(self):
        pantalla = QGuiApplication.primaryScreen()
        area_util = pantalla.availableGeometry()
        self.move(area_util.topLeft())
        self.setFixedSize(area_util.size())

    def cambiar_pantalla(self, nombre_pantalla, datos_usuario=None):
        if datos_usuario:
            self.usuario_actual = datos_usuario

        datos = self.usuario_actual or {}
        id_rol = datos.get("id_rol")
        nombre = datos.get("username_log", "Usuario")
        rol_txt = datos.get("rol", "")

        print(f"[ROUTER] pantalla='{nombre_pantalla}' | id_rol={id_rol} | rol='{rol_txt}' | nombre='{nombre}'")

        if str(id_rol) == "2":
            if nombre_pantalla in ("AdminDashboard", "MainDashboard"):
                print("[ROUTER] Cajero → redirigido a CajeroDashboard")
                nombre_pantalla = "CajeroDashboard"

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
            
        elif nombre_pantalla == "Facturacion":
            self.stack.setCurrentWidget(self.factura_view)
            
        elif nombre_pantalla == "Inventario":
            self.stack.setCurrentWidget(self.inventario_view)
 
        elif nombre_pantalla == "Proveedores":
            self.stack.setCurrentWidget(self.proveedores_view)

        elif nombre_pantalla == "Finanzas":
            self.stack.setCurrentWidget(self.finanzas_view)

        else:
            self.usuario_actual = None
            self.stack.setCurrentWidget(self.login_view)
            print("[ROUTER] → Login")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    print("Conectando a la base de datos...")
    conexion = conexion_db()
    
    if conexion:
        try:
            # Verificar conexión sin necesidad de fetchone()
            with conexion.cursor() as cursor:
                cursor.execute("SELECT 1")
                # Si llegamos aquí, la conexión es válida
            ventana = MainWindow(conexion)
            sys.exit(app.exec())
        except Exception as e:
            print(f"Error al verificar conexión: {repr(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("No se pudo conectar a la base de datos. Verifica tu archivo .env")
        sys.exit(1)