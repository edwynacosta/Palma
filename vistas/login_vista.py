from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect,
                             QMessageBox)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QFont, QPixmap, QColor, QFontDatabase, QPainter, QBrush

class LoginVista(QWidget):
    def __init__(self, controlador_flujo):
        super().__init__()
        self.controlador = controlador_flujo
        
        # Paleta de colores
        self.VERDE_FONDO = "#008F39"
        self.VERDE_CORPORATIVO = "#008037"
        self.VERDE_INPUT_BG = "#DCEFE3"
        self.VERDE_FOCUS = "#0D6E36"
        self.VERDE_HOVER_BOTON = "#005E28"
        self.BLANCO_CARD = "#FFFFFF"

        # Layout Principal
        layout_principal = QHBoxLayout(self)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Tarjeta Central
        self.card = QFrame()
        self.card.setFixedSize(400, 500)
        self.card.setStyleSheet(f"QFrame {{ background-color: {self.BLANCO_CARD}; border-radius: 30px; }}")
        
        # Efecto de sombra
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(30)
        sombra.setColor(QColor(0, 0, 0, 40))
        sombra.setOffset(0, 5)
        self.card.setGraphicsEffect(sombra)

        # Layout interno de la tarjeta
        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(40, 40, 40, 40)
        layout_card.setSpacing(15)

        # --- LOGO Y TÍTULO (BLOQUE DE ESTRUCTURA RÍGIDA) ---
        
        # 1. Logo
        self.lbl_logo = QLabel()
        pixmap = QPixmap("vistas/logo_palma.png")
        if not pixmap.isNull():
            # Escalado estricto
            self.lbl_logo.setPixmap(pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(self.lbl_logo, alignment=Qt.AlignmentFlag.AlignCenter)

        # 2. Título (PALMA)
        self.lbl_palma = QLabel("PALMA")
        self.lbl_palma.setFont(QFont("Montserrat", 32, QFont.Weight.Bold))
        self.lbl_palma.setStyleSheet(f"color: {self.VERDE_CORPORATIVO}; background: transparent; margin-bottom: 10px;")
        self.lbl_palma.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(self.lbl_palma, alignment=Qt.AlignmentFlag.AlignCenter)

        # 3. Inputs
        estilo_inputs = f"background-color: {self.VERDE_INPUT_BG}; color: {self.VERDE_FOCUS}; border: none; border-radius: 20px; padding: 15px; font-size: 14px;"
        
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.txt_usuario.setStyleSheet(estilo_inputs)
        layout_card.addWidget(self.txt_usuario)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setStyleSheet(estilo_inputs)
        layout_card.addWidget(self.txt_password)

        # 4. Botón
        self.btn_entrar = QPushButton("ENTRAR")
        self.btn_entrar.setFixedSize(300, 50)
        self.btn_entrar.setStyleSheet(f"QPushButton {{ background-color: {self.VERDE_CORPORATIVO}; color: white; border-radius: 20px; font-weight: bold; font-size: 16px; }} QPushButton:hover {{ background-color: {self.VERDE_HOVER_BOTON}; }}")
        self.btn_entrar.clicked.connect(self.verificar_login)
        layout_card.addWidget(self.btn_entrar, alignment=Qt.AlignmentFlag.AlignCenter)

        layout_principal.addWidget(self.card)

    # --- FORZAR FONDO VERDE ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(self.VERDE_FONDO)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def verificar_login(self):
        usuario = self.txt_usuario.text().strip()
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