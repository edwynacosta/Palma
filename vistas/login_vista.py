# vistas/login_vista.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QColor, QPainter

class LoginVista(QWidget):
    def __init__(self, controlador_flujo):
        super().__init__()
        self.controlador = controlador_flujo
        
        # Activar el dibujado de estilos nativo en Windows
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Paleta de Colores Exacta
        self.VERDE_FONDO = "#008F39"
        self.VERDE_CORPORATIVO = "#008037"
        self.VERDE_INPUT_BG = "#DCEFE3"
        self.VERDE_FOCUS = "#0D6E36"
        self.VERDE_HOVER_BOTON = "#005E28"
        self.BLANCO_CARD = "#FFFFFF"

        self.setStyleSheet(f"background-color: {self.VERDE_FONDO};")

        layout_principal = QHBoxLayout(self)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # --- TARJETA CENTRAL ---
        self.card = QFrame()
        self.card.setFixedSize(420, 600)
        self.card.setStyleSheet(f"QFrame {{ background-color: {self.BLANCO_CARD}; border-radius: 40px; }}")
        
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(35)
        sombra.setColor(QColor(0, 0, 0, 45))
        sombra.setOffset(0, 10)
        self.card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(45, 45, 45, 45)
        layout_card.setSpacing(15)

        # --- LOGO Y TÍTULO ---
        self.lbl_logo = QLabel()
        pixmap = QPixmap("vistas/logo_palma.png")
        if not pixmap.isNull():
            self.lbl_logo.setPixmap(pixmap.scaled(130, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.lbl_logo.setText("🌴")
            self.lbl_logo.setStyleSheet("font-size: 70px; background: transparent;")
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(self.lbl_logo)

        # Título "PALMA" con tipografía limpia y pesada
        self.lbl_palma = QLabel("PALMA")
        fuente_palma = QFont("Segoe UI", 36, QFont.Weight.Bold)
        fuente_palma.setStyleStrategy(QFont.StyleStrategy.PreferAntialias) # Fuerza suavizado de bordes
        self.lbl_palma.setFont(fuente_palma)
        self.lbl_palma.setStyleSheet(f"color: {self.VERDE_CORPORATIVO}; background: transparent; margin-bottom: 10px;")
        self.lbl_palma.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(self.lbl_palma)

        # --- INPUTS ESTILIZADOS ---
        estilo_inputs = f"""
            QLineEdit {{
                background-color: {self.VERDE_INPUT_BG};
                color: {self.VERDE_FOCUS};
                border: 2px solid {self.VERDE_INPUT_BG};
                border-radius: 25px;
                padding-left: 20px;
                font-family: 'Segoe UI';
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.VERDE_FOCUS};
            }}
        """

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.txt_usuario.setFixedSize(330, 50)
        self.txt_usuario.setStyleSheet(estilo_inputs)
        self.txt_usuario.returnPressed.connect(self.verificar_login)
        layout_card.addWidget(self.txt_usuario, 0, Qt.AlignmentFlag.AlignCenter)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setFixedSize(330, 50)
        self.txt_password.setStyleSheet(estilo_inputs)
        self.txt_password.returnPressed.connect(self.verificar_login)
        layout_card.addWidget(self.txt_password, 0, Qt.AlignmentFlag.AlignCenter)

        layout_card.addSpacing(15)

        # --- SECCIÓN BOTÓN Y LINKS ---
        layout_inferior = QHBoxLayout()
        layout_inferior.setSpacing(15)
        
        # 1. BOTÓN ENTRAR CON RENDERIZADO CRISTALINO (Solución a tu problema visual)
        self.btn_entrar = QPushButton("ENTRAR")
        self.btn_entrar.setFixedSize(145, 50)
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Configuramos la fuente usando Segoe UI / Arial con estrategia de Antialiasing explícita
        fuente_boton = QFont("Segoe UI", 14, QFont.Weight.DemiBold)
        fuente_boton.setStyleStrategy(QFont.StyleStrategy.PreferAntialias) 
        fuente_boton.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.5) # Separa ligeramente las letras para mayor nitidez
        self.btn_entrar.setFont(fuente_boton)
        
        self.btn_entrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.VERDE_CORPORATIVO};
                color: white;
                border-radius: 18px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.VERDE_HOVER_BOTON};
            }}
        """)
        self.btn_entrar.clicked.connect(self.verificar_login)
        layout_inferior.addWidget(self.btn_entrar)

        # 3. Contenedor de links compactos
        layout_links = QVBoxLayout()
        layout_links.setSpacing(3)
        layout_links.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Configuración de fuente limpia para los textos pequeños
        fuente_links = QFont("Segoe UI", 9, QFont.Weight.Bold)
        fuente_links.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        
        estilo_links = f"""
            QLabel {{
                color: {self.VERDE_FOCUS}; 
                background: transparent;
                margin: 0px;
                padding: 0px;
            }}
        """
        
        lbl_olvido_u = QLabel("¿Olvidaste el usuario?")
        lbl_olvido_c = QLabel("¿Olvidaste la contraseña?")
        lbl_ayuda = QLabel("Ayuda")
        
        for lbl in [lbl_olvido_u, lbl_olvido_c, lbl_ayuda]:
            lbl.setFont(fuente_links)
            lbl.setStyleSheet(estilo_links)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout_links.addWidget(lbl)
            
        layout_inferior.addLayout(layout_links)
        layout_card.addLayout(layout_inferior)

        layout_principal.addWidget(self.card)

    def mousePressEvent(self, event):
        focused_widget = self.focusWidget()
        if isinstance(focused_widget, QLineEdit):
            focused_widget.clearFocus()
        super().mousePressEvent(event)

    def verificar_login(self):
        self.controlador.cambiar_pantalla("AdminDashboard")