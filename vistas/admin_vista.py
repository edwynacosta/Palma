# vistas/admin_vista.py
import sys
from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve, QTimer
from PySide6.QtGui import QFont
from datetime import datetime

class TarjetaModulo(QPushButton):
    """Botón personalizado en Qt con animaciones dinámicas de elevación"""
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setFont(QFont("Montserrat", 16, QFont.Weight.Bold))
        self.setMinimumSize(220, 220)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Estilos base de las tarjetas (Blanco, texto verde)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #008037;
                border-radius: 35px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1B4314;
                color: #FFFFFF;
            }
        """)
        
        # Framework de animación para el efecto flotante
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setEndValue(QPoint(self.x(), self.y() - 8))
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setEndValue(QPoint(self.x(), self.y() + 8))
        self.anim.start()
        super().leaveEvent(event)


class AdminDashboardQt(QWidget):
    # CORREGIDO: Ahora acepta controlador_flujo para evitar el TypeError
    def __init__(self, controlador_flujo=None):
        super().__init__()
        self.controlador = controlador_flujo
        self.setStyleSheet("background-color: #008F39;") # Verde plano corporativo

        # --- DISEÑO VERTICAL PRINCIPAL ---
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(60, 30, 60, 40)

        # ==============================================================================
        # 1. BARRA SUPERIOR (NAV BAR DERECHA)
        # ==============================================================================
        nav_layout = QHBoxLayout()
        
        btn_admin = QPushButton("Ver Admin")
        btn_cajero = QPushButton("Ver Cajero")
        btn_logout = QPushButton("Cerrar Sesión")
        
        # Cursores
        btn_admin.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cajero.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Conectar acción de cerrar sesión
        if self.controlador:
            btn_logout.clicked.connect(lambda: self.controlador.cambiar_pantalla("LoginFrame"))

        # Hojas de estilo exactas
        style_nav = """
            QPushButton {
                background-color: #FFFFFF; 
                color: #008037; 
                font-family: 'Montserrat';
                font-size: 11px;
                font-weight: bold; 
                border-radius: 6px; 
                padding: 6px 15px;
            }
            QPushButton:hover {
                background-color: #D6EFE2;
            }
        """
        style_logout = """
            QPushButton {
                background-color: #DC3545; 
                color: white; 
                font-family: 'Montserrat';
                font-size: 11px;
                font-weight: bold; 
                border-radius: 6px; 
                padding: 6px 15px;
            }
            QPushButton:hover {
                background-color: #BD2130;
            }
        """
        btn_admin.setStyleSheet(style_nav)
        btn_cajero.setStyleSheet(style_nav)
        btn_logout.setStyleSheet(style_logout)
        
        nav_layout.addStretch()
        nav_layout.addWidget(btn_admin)
        nav_layout.addWidget(btn_cajero)
        nav_layout.addWidget(btn_logout)
        layout_principal.addLayout(nav_layout)

        # ==============================================================================
        # 2. CUADRÍCULA DE MÓDULOS (GRID CALCADO)
        # ==============================================================================
        grid_layout = QGridLayout()
        grid_layout.setSpacing(30)
        grid_layout.setContentsMargins(40, 20, 40, 20)

        self.mod_ventas = TarjetaModulo("VENTAS")
        # Forzar estado activo inicial para VENTAS (Verde oliva oscuro asentado)
        self.mod_ventas.setStyleSheet("background-color: #1B4314; color: white; border-radius: 35px; border: none;")
        
        self.mod_inventarios = TarjetaModulo("INVENTARIOS")
        self.mod_finanzas = TarjetaModulo("FINANZAS")
        self.mod_personal = TarjetaModulo("PERSONAL")
        
        self.mod_cuenta = TarjetaModulo("CUENTA")
        self.mod_cuenta.setMinimumHeight(470) 

        # Posicionamiento en la matriz
        grid_layout.addWidget(self.mod_ventas, 0, 0)
        grid_layout.addWidget(self.mod_inventarios, 0, 1)
        grid_layout.addWidget(self.mod_finanzas, 1, 0)
        grid_layout.addWidget(self.mod_personal, 1, 1)
        grid_layout.addWidget(self.mod_cuenta, 0, 2, 2, 1)

        layout_principal.addLayout(grid_layout)
        layout_principal.addStretch()

        # ==============================================================================
        # 3. FOOTER (INFO DE USUARIO + RELOJ DINÁMICO)
        # ==============================================================================
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(40, 0, 40, 0)
        
        # Bloque Usuario
        self.lbl_user = QLabel("Nicolás Herrán\nAdministrador")
        self.lbl_user.setFont(QFont("Montserrat", 14))
        self.lbl_user.setStyleSheet("color: white; font-weight: bold; line-height: 120%;")
        
        # Bloque Reloj
        self.lbl_time = QLabel()
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.lbl_time.setStyleSheet("color: white; font-family: 'Montserrat'; font-weight: bold;")
        
        footer_layout.addWidget(self.lbl_user)
        footer_layout.addStretch()
        footer_layout.addWidget(self.lbl_time)
        layout_principal.addLayout(footer_layout)

        # Iniciar el temporizador del reloj
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_tiempo)
        self.timer.start(1000)
        self.actualizar_tiempo()

    def actualizar_tiempo(self):
        """Mantiene actualizado el reloj inferior con el formato de la interfaz."""
        ahora = datetime.now()
        string_hora = ahora.strftime("%H:%M")
        
        dias = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        
        string_fecha = f"{dias[ahora.weekday()]} {ahora.day} {meses[ahora.month - 1]}, {ahora.year}"
        
        # Formateo usando hojas de estilo internas para mantener tamaños diferentes
        self.lbl_time.setText(f"<span style='font-size: 42px;'>{string_hora}</span><br><span style='font-size: 11px;'>{string_fecha}</span>")