import os
import sys
from datetime import datetime

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QTimer, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QLabel, QPushButton, QWidget
from vistas.cuenta_vista import CuentaDialog
from vistas.inventario_vista import InventarioVista


class BotonAnimado(QPushButton):
    """Tarjeta-boton blanca con elevacion sutil al pasar el cursor."""

    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.pos_original = None
        self.radio = 39

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.anim_pos = QPropertyAnimation(self, b"pos", self)
        self.anim_pos.setDuration(150)
        self.anim_pos.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.actualizar_estilo()

    def actualizar_estilo(self, hover=False):
        fondo = "#1B4314" if hover else "#FFFFFF"
        color = "#FFFFFF" if hover else "#008F39"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {fondo};
                color: {color};
                border: none;
                border-radius: {self.radio}px;
                font-family: 'Montserrat';
                font-weight: 900;
            }}
        """)

    def enterEvent(self, event):
        self.actualizar_estilo(hover=True)

        if self.pos_original is None:
            self.pos_original = self.pos()

        self.raise_()
        self.anim_pos.stop()
        self.anim_pos.setStartValue(self.pos())
        self.anim_pos.setEndValue(QPoint(self.pos_original.x(), self.pos_original.y() - 8))
        self.anim_pos.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        self.actualizar_estilo(hover=False)

        if self.pos_original is not None:
            self.anim_pos.stop()
            self.anim_pos.setStartValue(self.pos())
            self.anim_pos.setEndValue(self.pos_original)
            self.anim_pos.start()

        super().leaveEvent(event)

    def fijar_geometria(self, x, y, ancho, alto, radio, font_size):
        self.pos_original = QPoint(x, y)
        self.radio = radio
        self.setGeometry(x, y, ancho, alto)
        self.setFont(QFont("Montserrat", font_size, QFont.Weight.Black))
        self.actualizar_estilo()


class AdminDashboardQt(QWidget):
    def __init__(self, controlador_flujo=None, datos_usuario=None):
        super().__init__()

        self.controlador = controlador_flujo
        self.datos_usuario = datos_usuario or {}
        self.VERDE_FONDO = "#008F39"

        self.cargar_fuentes()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("ContenedorAdmin")
        self.setStyleSheet(
            f"QWidget#ContenedorAdmin {{ background-color: {self.VERDE_FONDO}; }}"
        )

        self.btn_admin = QPushButton("Ver Admin", self)
        self.btn_cajero = QPushButton("Ver Cajero", self)
        self.btn_logout = QPushButton("Cerrar Sesión", self)

        for boton in [self.btn_admin, self.btn_cajero, self.btn_logout]:
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            boton.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.btn_admin.clicked.connect(self.ver_admin)
        self.btn_cajero.clicked.connect(self.ver_cajero)
        self.btn_logout.clicked.connect(self.cerrar_sesion)

        self.aplicar_estilo_nav()

        self.mod_ventas = BotonAnimado("VENTAS", self)
        self.mod_inventarios = BotonAnimado("INVENTARIOS", self)
        self.mod_finanzas = BotonAnimado("FINANZAS", self)
        self.mod_cuenta = BotonAnimado("CUENTA", self)

        self.mod_ventas.clicked.connect(self.abrir_modulo_caja)
        self.mod_cuenta.clicked.connect(self.abrir_cuenta)

        self.lbl_avatar = QLabel("", self)
        self.lbl_avatar.setStyleSheet("""
            QLabel {
                background-color: #E9EEF2;
                border: none;
                border-radius: 32px;
            }
        """)

        self.lbl_user = QLabel(self)
        self.lbl_user.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background: transparent;
                font-family: 'Montserrat';
            }
        """)

        self.lbl_time = QLabel(self)
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.lbl_time.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background: transparent;
                font-family: 'Montserrat';
            }
        """)

        self.actualizar_interfaz_usuario()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_tiempo)
        self.timer.start(1000)
        self.actualizar_tiempo()

    def cargar_fuentes(self):
        ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")

        for archivo in [
            "Montserrat-Regular.ttf",
            "Montserrat-Medium.ttf",
            "Montserrat-Bold.ttf",
            "Montserrat-ExtraBold.ttf",
            "Montserrat-Black.ttf",
        ]:
            ruta = os.path.join(carpeta_fuentes, archivo)

            if os.path.exists(ruta):
                QFontDatabase.addApplicationFont(ruta)

    def aplicar_estilo_nav(self):
        estilo_nav = """
            QPushButton {
                background-color: #FFFFFF;
                color: #008F39;
                border: none;
                border-radius: 9px;
                font-family: 'Montserrat';
                font-size: 9px;
                font-weight: 900;
            }
            QPushButton:hover {
                background-color: #1B4314;
                color: #FFFFFF;
            }
        """

        estilo_logout = """
            QPushButton {
                background-color: #FFFFFF;
                color: #FF0000;
                border: none;
                border-radius: 9px;
                font-family: 'Montserrat';
                font-size: 9px;
                font-weight: 900;
            }
            QPushButton:hover {
                background-color: #FF0000;
                color: #FFFFFF;
            }
        """

        self.btn_admin.setStyleSheet(estilo_nav)
        self.btn_cajero.setStyleSheet(estilo_nav)
        self.btn_logout.setStyleSheet(estilo_logout)

    def escala(self):
        return min(self.width() / 1904, self.height() / 943)

    def sx(self, valor):
        return round(valor * self.escala())

    def resizeEvent(self, event):
        self.reacomodar_interfaz()
        super().resizeEvent(event)

    def reacomodar_interfaz(self):
        ancho_card = self.sx(368)
        alto_card = self.sx(320)
        ancho_cuenta = self.sx(369)
        alto_cuenta = self.sx(665)
        gap = self.sx(24)

        total_ancho = ancho_card * 2 + ancho_cuenta + gap * 2
        x_inicio = (self.width() - total_ancho) // 2

        y_inicio = self.sx(85)
        y_abajo = y_inicio + alto_card + gap

        btn_w = self.sx(96)
        btn_h = self.sx(31)
        btn_gap = self.sx(12)
        logout_w = self.sx(109)

        nav_total = btn_w * 2 + logout_w + btn_gap * 2
        nav_x = self.width() - self.sx(30) - nav_total
        nav_y = self.sx(27)

        self.btn_admin.setGeometry(nav_x, nav_y, btn_w, btn_h)
        self.btn_cajero.setGeometry(nav_x + btn_w + btn_gap, nav_y, btn_w, btn_h)
        self.btn_logout.setGeometry(nav_x + (btn_w + btn_gap) * 2, nav_y, logout_w, btn_h)

        radio = self.sx(39)
        font_card = max(14, self.sx(24))

        self.mod_ventas.fijar_geometria(
            x_inicio,
            y_inicio,
            ancho_card * 2 + gap,
            alto_card,
            radio,
            max(16, self.sx(26)),
        )

        self.mod_finanzas.fijar_geometria(
            x_inicio,
            y_abajo,
            ancho_card,
            alto_card,
            radio,
            font_card,
        )

        self.mod_inventarios.fijar_geometria(
            x_inicio + ancho_card + gap,
            y_abajo,
            ancho_card,
            alto_card,
            radio,
            max(13, self.sx(22)),
        )

        self.mod_cuenta.fijar_geometria(
            x_inicio + (ancho_card + gap) * 2,
            y_inicio,
            ancho_cuenta,
            alto_cuenta,
            radio,
            font_card,
        )

        avatar = self.sx(64)

        self.lbl_avatar.setGeometry(
            self.sx(310),
            self.height() - self.sx(112),
            avatar,
            avatar,
        )

        self.lbl_avatar.setStyleSheet(f"""
            QLabel {{
                background-color: #E9EEF2;
                border: none;
                border-radius: {avatar // 2}px;
            }}
        """)

        self.lbl_user.setGeometry(
            self.sx(390),
            self.height() - self.sx(112),
            self.sx(420),
            self.sx(76),
        )

        self.lbl_time.setGeometry(
            self.width() - self.sx(575),
            self.height() - self.sx(137),
            self.sx(300),
            self.sx(96),
        )

        self.actualizar_interfaz_usuario()
        self.actualizar_tiempo()

    def abrir_modulo_caja(self):
        if self.controlador:
            self.controlador.cambiar_pantalla(
                "Caja",
                datos_usuario=self.datos_usuario
            )

    def abrir_cuenta(self):
        conexion = getattr(self.controlador, "conexion", None)
        dlg = CuentaDialog(conexion, self.datos_usuario, self)
        dlg.exec()

    def ver_admin(self):
        if self.controlador:
            self.controlador.cambiar_pantalla(
                "AdminDashboard",
                datos_usuario=self.datos_usuario
            )

    def ver_cajero(self):
        if self.controlador:
            self.controlador.cambiar_pantalla(
                "CajeroDashboard",
                datos_usuario=self.datos_usuario
            )

    def cerrar_sesion(self):
        if self.controlador:
            self.controlador.cambiar_pantalla("Login")

    def establecer_usuario(self, nombre, rol):
        self.datos_usuario = {
            "nombre": nombre,
            "rol": rol
        }
        self.actualizar_interfaz_usuario()

    def actualizar_interfaz_usuario(self):
        nombre_final = "Nicolás Herrán"
        rol_final = "Administrador"

        if isinstance(self.datos_usuario, dict) and self.datos_usuario:
            nombre_final = self.datos_usuario.get(
                "username_log",
                self.datos_usuario.get("nombre", nombre_final)
            )

            rol_final = self.datos_usuario.get("rol", rol_final)

        nombre_final = str(nombre_final).strip().title()
        rol_final = str(rol_final).strip().capitalize()

        s = self.escala() if self.width() and self.height() else 1

        nombre_px = max(15, round(24 * s))
        rol_px = max(10, round(15 * s))

        self.lbl_user.setText(
            f"<span style='font-size:{nombre_px}px; font-weight:900;'>{nombre_final}</span><br>"
            f"<span style='font-size:{rol_px}px; font-weight:500;'>{rol_final}</span>"
        )

    def showEvent(self, event):
        self.actualizar_interfaz_usuario()
        self.reacomodar_interfaz()
        super().showEvent(event)

    def actualizar_tiempo(self):
        ahora = datetime.now()

        dias = [
            "LUNES", "MARTES", "MIERCOLES", "JUEVES",
            "VIERNES", "SABADO", "DOMINGO"
        ]

        meses = [
            "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
            "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
        ]

        s = self.escala() if self.width() and self.height() else 1

        hora_px = max(34, round(58 * s))
        fecha_px = max(10, round(15 * s))

        string_hora = ahora.strftime("%H:%M")
        string_fecha = (
            f"{dias[ahora.weekday()]} "
            f"{ahora.day} {meses[ahora.month - 1]}, {ahora.year}"
        )

        self.lbl_time.setText(
            f"<span style='font-size:{hora_px}px; font-weight:900;'>{string_hora}</span><br>"
            f"<span style='font-size:{fecha_px}px; font-weight:900;'>{string_fecha}</span>"
        )


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    usuario_detectado = {
        "nombre": "nicolás herrán",
        "rol": "administrador",
    }

    ventana = AdminDashboardQt(datos_usuario=usuario_detectado)
    ventana.resize(1904, 943)
    ventana.show()

    sys.exit(app.exec())