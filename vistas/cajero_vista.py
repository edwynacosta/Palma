
import os
import sys
from datetime import datetime

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QTimer, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QLabel, QPushButton, QWidget


class BotonAnimado(QPushButton):
    """Tarjeta-boton blanca con una elevacion sutil al pasar el cursor."""

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


class CajeroDashboardQt(QWidget):
    def __init__(self, controlador_flujo=None, datos_usuario=None):
        super().__init__()

        self.controlador = controlador_flujo
        self.datos_usuario = datos_usuario or {}

        self.VERDE_FONDO = "#008F39"

        self.cargar_fuentes()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("ContenedorCajero")
        self.setStyleSheet(
            f"QWidget#ContenedorCajero {{ background-color: {self.VERDE_FONDO}; }}"
        )

        self.btn_logout = QPushButton("Cerrar sesión", self)
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_logout.clicked.connect(self.cerrar_sesion)
        self.btn_logout.setStyleSheet("""
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
                background-color: #FDEEEF;
            }
        """)

        self.mod_ventas = BotonAnimado("V E N T A S", self)
        self.mod_finanzas = BotonAnimado("F I N A N Z A S", self)
        self.mod_inventarios = BotonAnimado("I N V E N T A R I O S", self)

        self.mod_ventas.clicked.connect(self.abrir_modulo_caja)
        self.mod_inventarios.clicked.connect(self.abrir_modulo_inventario)
        self.mod_finanzas.clicked.connect(self.abrir_modulo_facturacion)  # ← NUEVO

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

    def escala(self):
        return min(self.width() / 1904, self.height() / 943)

    def sx(self, valor):
        return round(valor * self.escala())

    def resizeEvent(self, event):
        self.reacomodar_interfaz()
        super().resizeEvent(event)

    def reacomodar_interfaz(self):
        ancho_ventas = self.sx(1152)
        alto_ventas = self.sx(324)

        ancho_card = self.sx(564)
        alto_card = self.sx(316)
        gap = self.sx(24)

        centro_x = self.width() // 2
        x_inicio = centro_x - (ancho_ventas // 2)

        y_ventas = self.sx(87)
        y_cards = self.sx(436)

        self.btn_logout.setGeometry(
            self.width() - self.sx(151),
            self.sx(29),
            self.sx(121),
            self.sx(31),
        )

        self.mod_ventas.fijar_geometria(
            x_inicio,
            y_ventas,
            ancho_ventas,
            alto_ventas,
            self.sx(39),
            max(16, self.sx(27)),
        )

        self.mod_finanzas.fijar_geometria(
            x_inicio,
            y_cards,
            ancho_card,
            alto_card,
            self.sx(39),
            max(13, self.sx(20)),
        )

        self.mod_inventarios.fijar_geometria(
            x_inicio + ancho_card + gap,
            y_cards,
            ancho_card,
            alto_card,
            self.sx(39),
            max(13, self.sx(20)),
        )

        avatar = self.sx(64)

        self.lbl_avatar.setGeometry(
            self.sx(310),
            self.height() - self.sx(110),
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
            self.sx(389),
            self.height() - self.sx(111),
            self.sx(390),
            self.sx(75),
        )

        self.lbl_time.setGeometry(
            self.width() - self.sx(590),
            self.height() - self.sx(139),
            self.sx(280),
            self.sx(95),
        )

        self.actualizar_interfaz_usuario()
        self.actualizar_tiempo()

    def cerrar_sesion(self):
        if self.controlador:
            self.controlador.cambiar_pantalla("Login")

    def abrir_modulo_caja(self):
        if self.controlador:
            self.controlador.cambiar_pantalla(
                "Caja",
                datos_usuario=self.datos_usuario
            )
    def abrir_modulo_inventario(self):
        if self.controlador:
            self.controlador.cambiar_pantalla(
                "Inventario",
                datos_usuario=self.datos_usuario
            )

    def abrir_modulo_facturacion(self):  # ← NUEVO
        if self.controlador:
            self.controlador.cambiar_pantalla(
                "Facturacion",
                datos_usuario=self.datos_usuario
            )

    def actualizar_interfaz_usuario(self):
        nombre_final = "Edwin Acosta"
        rol_final = "Cajero"

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
            f"{dias[ahora.weekday()]}, "
            f"{ahora.day} DE {meses[ahora.month - 1]} DE {ahora.year}"
        )

        self.lbl_time.setText(
            f"<span style='font-size:{hora_px}px; font-weight:900;'>{string_hora}</span><br>"
            f"<span style='font-size:{fecha_px}px; font-weight:900;'>{string_fecha}</span>"
        )


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    cajero_detectado = {
        "nombre": "edwin acosta",
        "rol": "cajero"
    }

    ventana = CajeroDashboardQt(datos_usuario=cajero_detectado)
    ventana.resize(1904, 943)
    ventana.show()

    sys.exit(app.exec())