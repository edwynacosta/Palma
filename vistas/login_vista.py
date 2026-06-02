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

        # --- SOLUCIÓN PARA RUTAS DE FUENTES ---
        # Detecta la localización del archivo actual para armar una ruta absoluta confiable
        ruta_vistas = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz = os.path.dirname(ruta_vistas)
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")

        # Carga de fuentes locales apuntando a la carpeta correcta del proyecto
        QFontDatabase.addApplicationFont(os.path.join(carpeta_fuentes, "Montserrat-Bold.ttf"))
        QFontDatabase.addApplicationFont(os.path.join(carpeta_fuentes, "Montserrat-Regular.ttf"))
        QFontDatabase.addApplicationFont(os.path.join(carpeta_fuentes, "Montserrat-Medium.ttf"))
        
        # --- DEFINICIÓN DE FUENTES NATIVAS SUAVIZADAS ---
        self.fuente_titulo = QFont("Montserrat", 32, QFont.Weight.Bold)
        
        self.fuente_inputs = QFont("Montserrat")
        self.fuente_inputs.setPixelSize(15)
        self.fuente_inputs.setWeight(QFont.Weight.Normal)
        
        # Configuración especial para el botón: Elimina el 'hinting' de Windows que deforma y rompe las letras
        self.fuente_boton = QFont("Montserrat")
        self.fuente_boton.setPixelSize(15)  # Coincide con tu diseño original pero estabiliza los bordes
        self.fuente_boton.setBold(True)
        self.fuente_boton.setHintingPreference(QFont.HintingPreference.PreferNoHinting) # <--- CLAVE DEL SUAVIZADO
        
        self.fuente_links = QFont("Montserrat", 8, QFont.Weight.Medium)

        # Paleta
        self.VERDE_FONDO       = "#008F39"
        self.VERDE_CORPORATIVO = "#008037"
        self.VERDE_INPUT_BG    = "#DCEFE3"
        self.VERDE_FOCUS       = "#0D6E36"
        self.VERDE_HOVER_BOTON = "#005E28"
        self.VERDE_BOTON       = "#1B4314"
        self.BLANCO_CARD       = "#FFFFFF"

        # Layout principal: centra la tarjeta
        layout_principal = QHBoxLayout(self)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # TARJETA (tamaño original)
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

        # 1. Logo — Un poco más grande para mejor presencia visual (cambiado a 180x180)
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

        # 2. Título — Configurado mediante .setFont() nativo
        self.lbl_palma = QLabel("PALMA")
        self.lbl_palma.setFont(self.fuente_titulo)
        self.lbl_palma.setStyleSheet(
            f"color: {self.VERDE_CORPORATIVO}; background: transparent;"
        )
        self.lbl_palma.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(self.lbl_palma, alignment=Qt.AlignmentFlag.AlignCenter)

        layout_card.addSpacing(30)

        # 3. Inputs (Se remueven las propiedades font del CSS para evitar que Qt rompa el renderizado)
        estilo_input = f"""
            QLineEdit {{
                background-color: {self.VERDE_INPUT_BG};
                color: {self.VERDE_FOCUS};
                border: 2px solid transparent;
                border-radius: 20px;
                padding: 0px 22px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.VERDE_CORPORATIVO};
            }}
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

        # 4. Fila inferior: botón ENTRAR + links a la derecha
        fila_inferior = QHBoxLayout()
        fila_inferior.setSpacing(0)
        fila_inferior.setContentsMargins(0, 0, 0, 0)

        # Botón ENTRAR con la fuente nativa de alta definición aplicada externamente al CSS
        self.btn_entrar = QPushButton("ENTRAR")
        self.btn_entrar.setFixedSize(152, 54)
        self.btn_entrar.setFont(self.fuente_boton)  # <--- Aplica el máximo suavizado vectorial
        self.btn_entrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.VERDE_BOTON};
                color: white;
                border-radius: 22px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.VERDE_HOVER_BOTON};
            }}
        """)
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.clicked.connect(self.verificar_login)

        estilo_link = f"""
            QLabel {{
                color: {self.VERDE_FOCUS};
                background: transparent;
            }}
        """
        lbl_forgot_user = QLabel("¿Olvidaste el usuario?")
        lbl_forgot_pass = QLabel("¿Olvidaste la contraseña?")
        lbl_ayuda       = QLabel("Ayuda")

        for lbl in [lbl_forgot_user, lbl_forgot_pass, lbl_ayuda]:
            lbl.setFont(self.fuente_links)
            lbl.setStyleSheet(estilo_link)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)

        links_layout = QVBoxLayout()
        links_layout.setSpacing(1)
        links_layout.setContentsMargins(0, 0, 0, 0)
        links_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        links_layout.addWidget(lbl_forgot_user)
        links_layout.addWidget(lbl_forgot_pass)
        links_layout.addWidget(lbl_ayuda)

        fila_inferior.addWidget(self.btn_entrar, alignment=Qt.AlignmentFlag.AlignVCenter)
        fila_inferior.addStretch()
        fila_inferior.addLayout(links_layout)

        layout_card.addLayout(fila_inferior)

        layout_card.addStretch(2)

        layout_principal.addWidget(self.card)

    # FONDO VERDE
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(self.VERDE_FONDO)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    # Limpiar campos — llamar desde el controlador al volver al login
    def limpiar_campos(self):
        self.txt_usuario.clear()
        self.txt_password.clear()
        self.txt_usuario.setFocus()

    def showEvent(self, event):
        """Se dispara cada vez que esta pantalla se hace visible."""
        self.limpiar_campos()
        super().showEvent(event)

    # LÓGICA DE LOGIN
    def verificar_login(self):
        usuario  = self.txt_usuario.text().strip()
        password = self.txt_password.text().strip()
        try:
            with self.controlador.conexion.cursor() as cursor:
                sql = "SELECT id_usuario, username_log FROM usuarios WHERE username_log = %s AND contrasena_log = %s;"
                cursor.execute(sql, (usuario, password))
                if cursor.fetchone():
                    self.controlador.cambiar_pantalla("AdminDashboard")
                else:
                    QMessageBox.warning(self, "Acceso", "Usuario o contraseña incorrectos.")
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"Error de conexión: {e}")