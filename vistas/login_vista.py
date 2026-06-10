import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect,
                               QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QColor, QPainter, QBrush, QFontDatabase


class LoginVista(QWidget):
    def __init__(self, controlador_flujo):
        super().__init__()
        self.controlador = controlador_flujo

        # Rutas absolutas de fuentes
        ruta_vistas     = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz       = os.path.dirname(ruta_vistas)
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")

        for f in ("Montserrat-Bold.ttf", "Montserrat-Regular.ttf", "Montserrat-Medium.ttf"):
            ruta_f = os.path.join(carpeta_fuentes, f)
            if os.path.exists(ruta_f):
                QFontDatabase.addApplicationFont(ruta_f)

        # Fuentes nativas
        self.fuente_titulo = QFont("Montserrat", 32, QFont.Weight.Bold)

        self.fuente_inputs = QFont("Montserrat")
        self.fuente_inputs.setPixelSize(15)
        self.fuente_inputs.setWeight(QFont.Weight.Normal)

        self.fuente_boton = QFont("Montserrat")
        self.fuente_boton.setPixelSize(15)
        self.fuente_boton.setBold(True)
        self.fuente_boton.setHintingPreference(QFont.HintingPreference.PreferNoHinting)

        self.fuente_links = QFont("Montserrat", 8, QFont.Weight.Medium)

        # Paleta
        self.VERDE_FONDO       = "#008F39"
        self.VERDE_CORPORATIVO = "#008037"
        self.VERDE_INPUT_BG    = "#DCEFE3"
        self.VERDE_FOCUS       = "#0D6E36"
        self.VERDE_HOVER_BOTON = "#005E28"
        self.VERDE_BOTON       = "#1B4314"
        self.BLANCO_CARD       = "#FFFFFF"

        layout_principal = QHBoxLayout(self)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tarjeta
        self.card = QFrame()
        self.card.setFixedSize(500, 650)
        self.card.setStyleSheet(
            f"QFrame {{ background-color: {self.BLANCO_CARD}; border-radius: 40px; }}"
        )
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(40)
        sombra.setColor(QColor(0, 0, 0, 50))
        sombra.setOffset(0, 10)
        self.card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(55, 0, 55, 0)
        layout_card.setSpacing(0)
        layout_card.addStretch(2)

        # Logo
        self.lbl_logo = QLabel()
        ruta_logo = os.path.join(ruta_vistas, "logo_palma.png")
        pixmap = QPixmap(ruta_logo)
        if not pixmap.isNull():
            self.lbl_logo.setPixmap(
                pixmap.scaled(180, 180,
                              Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(self.lbl_logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_card.addSpacing(6)

        # Título
        self.lbl_palma = QLabel("PALMA")
        self.lbl_palma.setFont(self.fuente_titulo)
        self.lbl_palma.setStyleSheet(f"color: {self.VERDE_CORPORATIVO}; background: transparent;")
        self.lbl_palma.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(self.lbl_palma, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_card.addSpacing(30)

        # Inputs
        estilo_input = f"""
            QLineEdit {{
                background-color: {self.VERDE_INPUT_BG};
                color: {self.VERDE_FOCUS};
                border: 2px solid transparent;
                border-radius: 20px;
                padding: 0px 22px;
            }}
            QLineEdit:focus {{ border: 2px solid {self.VERDE_CORPORATIVO}; }}
        """

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.txt_usuario.setFixedHeight(54)
        self.txt_usuario.setFont(self.fuente_inputs)
        self.txt_usuario.setStyleSheet(estilo_input)
        layout_card.addWidget(self.txt_usuario)
        layout_card.addSpacing(16)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setFixedHeight(54)
        self.txt_password.setFont(self.fuente_inputs)
        self.txt_password.setStyleSheet(estilo_input)
        layout_card.addWidget(self.txt_password)

        self.txt_usuario.returnPressed.connect(self.verificar_login)
        self.txt_password.returnPressed.connect(self.verificar_login)
        layout_card.addSpacing(28)

        # Fila inferior
        fila_inferior = QHBoxLayout()
        fila_inferior.setSpacing(0)
        fila_inferior.setContentsMargins(0, 0, 0, 0)

        self.btn_entrar = QPushButton("ENTRAR")
        self.btn_entrar.setFixedSize(152, 54)
        self.btn_entrar.setFont(self.fuente_boton)
        self.btn_entrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.VERDE_BOTON}; color: white;
                border-radius: 22px; border: none;
            }}
            QPushButton:hover {{ background-color: {self.VERDE_HOVER_BOTON}; }}
        """)
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.clicked.connect(self.verificar_login)

        estilo_link = f"QLabel {{ color: {self.VERDE_FOCUS}; background: transparent; }}"
        lbl_fu = QLabel("¿Olvidaste el usuario?")
        lbl_fp = QLabel("¿Olvidaste la contraseña?")
        lbl_ay = QLabel("Ayuda")

        for lbl in [lbl_fu, lbl_fp, lbl_ay]:
            lbl.setFont(self.fuente_links)
            lbl.setStyleSheet(estilo_link)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)

        links_layout = QVBoxLayout()
        links_layout.setSpacing(1)
        links_layout.setContentsMargins(0, 0, 0, 0)
        links_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        links_layout.addWidget(lbl_fu)
        links_layout.addWidget(lbl_fp)
        links_layout.addWidget(lbl_ay)

        fila_inferior.addWidget(self.btn_entrar, alignment=Qt.AlignmentFlag.AlignVCenter)
        fila_inferior.addStretch()
        fila_inferior.addLayout(links_layout)

        layout_card.addLayout(fila_inferior)
        layout_card.addStretch(2)
        layout_principal.addWidget(self.card)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(self.VERDE_FONDO)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def limpiar_campos(self):
        self.txt_usuario.clear()
        self.txt_password.clear()
        self.txt_usuario.setFocus()

    def showEvent(self, event):
        self.limpiar_campos()
        super().showEvent(event)

    def verificar_login(self):
        usuario  = self.txt_usuario.text().strip()
        password = self.txt_password.text().strip()
        try:
            with self.controlador.conexion.cursor() as cursor:
                # Traemos username_log (nombre real) e id_rol (1=admin, 2=cajero)
                sql = """
                    SELECT id_usuario, username_log, id_rol
                    FROM usuarios
                    WHERE username_log = %s AND contrasena_log = %s
                """
                cursor.execute(sql, (usuario, password))
                fila = cursor.fetchone()

                if fila:
                    # Compatible con cursor dict (DictCursor) y cursor tupla
                    if isinstance(fila, dict):
                        id_usuario   = fila["id_usuario"]
                        username_log = fila["username_log"]
                        id_rol       = fila["id_rol"]
                    else:
                        id_usuario, username_log, id_rol = fila

                    # Texto del rol según id_rol numérico
                    id_rol_int = int(id_rol)
                    rol_texto  = "administrador" if id_rol_int == 1 else "cajero"

                    # Diccionario limpio que viaja por toda la app
                    datos_sesion = {
                        "id_usuario"  : id_usuario,
                        "username_log": username_log,   # nombre real del usuario
                        "nombre"      : username_log,   # alias para los dashboards
                        "rol"         : rol_texto,      # "administrador" | "cajero"
                        "id_rol"      : id_rol_int,     # 1 | 2  (entero)
                    }

                    # Siempre pedimos AdminDashboard; el router redirige a cajero si id_rol==2
                    self.controlador.cambiar_pantalla("AdminDashboard", datos_usuario=datos_sesion)

                else:
                    QMessageBox.warning(self, "Acceso", "Usuario o contraseña incorrectos.")

        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"Error de conexión: {e}")
