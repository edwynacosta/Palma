from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect,
                             QMessageBox)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QFont, QPixmap, QColor, QPainter, QBrush

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
        
        # --- TARJETA CENTRAL AMPLIADA ---
        self.card = QFrame()
        self.card.setFixedSize(500, 650) # Tamaño aumentado para que se vea más grande
        self.card.setStyleSheet(f"QFrame {{ background-color: {self.BLANCO_CARD}; border-radius: 40px; }}")
        
        # Efecto de sombra
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(40)
        sombra.setColor(QColor(0, 0, 0, 50))
        sombra.setOffset(0, 10)
        self.card.setGraphicsEffect(sombra)

        # Layout interno de la tarjeta con más espacio
        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(60, 50, 60, 50)
        layout_card.setSpacing(25) # Espacio extra entre elementos

        # 1. Logo
        self.lbl_logo = QLabel()
        pixmap = QPixmap("vistas/logo_palma.png")
        if not pixmap.isNull():
            self.lbl_logo.setPixmap(pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(self.lbl_logo, alignment=Qt.AlignmentFlag.AlignCenter)

        # 2. Título PALMA
        self.lbl_palma = QLabel("PALMA")
        self.lbl_palma.setFont(QFont("Montserrat", 40, QFont.Weight.Bold))
        self.lbl_palma.setStyleSheet(f"color: {self.VERDE_CORPORATIVO}; background: transparent;")
        self.lbl_palma.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(self.lbl_palma, alignment=Qt.AlignmentFlag.AlignCenter)

        # 3. Inputs más grandes y legibles
        estilo_inputs = f"background-color: {self.VERDE_INPUT_BG}; color: {self.VERDE_FOCUS}; border: none; border-radius: 20px; padding: 18px; font-size: 16px;"
        
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.txt_usuario.setStyleSheet(estilo_inputs)
        layout_card.addWidget(self.txt_usuario)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setStyleSheet(estilo_inputs)
        layout_card.addWidget(self.txt_password)
        
        # Al presionar Enter en cualquiera de estos campos, se llama a verificar_login
        self.txt_usuario.returnPressed.connect(self.verificar_login)
        self.txt_password.returnPressed.connect(self.verificar_login)

        # 4. Botón más grande
        self.btn_entrar = QPushButton("ENTRAR")
        self.btn_entrar.setFixedSize(380, 60) # Botón más ancho y alto
        self.btn_entrar.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {self.VERDE_CORPORATIVO}; color: white; 
                border-radius: 25px; font-weight: bold; font-size: 18px; 
            }} 
            QPushButton:hover {{ background-color: {self.VERDE_HOVER_BOTON}; }}
        """)
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.clicked.connect(self.verificar_login)
        layout_card.addWidget(self.btn_entrar, alignment=Qt.AlignmentFlag.AlignCenter)

        layout_principal.addWidget(self.card)

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