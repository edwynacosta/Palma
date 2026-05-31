import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, 
                                QPushButton, QLabel, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QParallelAnimationGroup
from PySide6.QtGui import QFont, QFontDatabase, QColor

class TarjetaModulo(QPushButton):
    """Botón con tamaño fijo ampliado, sombras sutiles y animación de elevación física"""
    def __init__(self, texto, alto_personalizado=None, parent=None):
        super().__init__(texto, parent)
        
        if os.path.exists("Montserrat-Bold.ttf"):
            QFontDatabase.addApplicationFont("Montserrat-Bold.ttf")
            
        self.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if alto_personalizado:
            self.setFixedSize(290, alto_personalizado)
        else:
            self.setFixedSize(290, 290)
        
        self.estilo_reposo = """
            QPushButton {
                background-color: #FFFFFF;
                color: #008037;
                border-radius: 35px;
                border: none;
            }
        """
        self.estilo_hover = """
            QPushButton {
                background-color: #1B4314;
                color: #FFFFFF;
                border-radius: 35px;
                border: none;
            }
        """
        self.setStyleSheet(self.estilo_reposo)
        
        self.sombra = QGraphicsDropShadowEffect(self)
        self.sombra.setBlurRadius(15)
        self.sombra.setXOffset(0)
        self.sombra.setYOffset(4)
        self.sombra.setColor(QColor(0, 0, 0, 35)) 
        self.setGraphicsEffect(self.sombra)
        
        self.anim_grupo = QParallelAnimationGroup(self)
        
        self.anim_pos = QPropertyAnimation(self, b"pos")
        self.anim_pos.setDuration(150)
        self.anim_pos.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.anim_sombra = QPropertyAnimation(self.sombra, b"yOffset")
        self.anim_sombra.setDuration(150)
        self.anim_sombra.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.anim_grupo.addAnimation(self.anim_pos)
        self.anim_grupo.addAnimation(self.anim_sombra)
        
        self.pos_original = None

    def enterEvent(self, event):
        self.setStyleSheet(self.estilo_hover)
        if self.pos_original is None:
            self.pos_original = self.pos()
            
        self.anim_grupo.stop()
        self.anim_pos.setStartValue(self.pos())
        self.anim_pos.setEndValue(QPoint(self.pos_original.x(), self.pos_original.y() - 6))
        self.anim_sombra.setEndValue(10)
        self.sombra.setBlurRadius(22)
        self.anim_grupo.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.estilo_reposo)
        if self.pos_original is not None:
            self.anim_grupo.stop()
            self.anim_pos.setStartValue(self.pos())
            self.anim_pos.setEndValue(self.pos_original)
            self.anim_sombra.setEndValue(4)
            self.sombra.setBlurRadius(15)
            self.anim_grupo.start()
        super().leaveEvent(event)


class AdminDashboardQt(QWidget):
    def __init__(self, controlador_flujo=None, datos_usuario=None):
        super().__init__()
        self.controlador = controlador_flujo # Aquí guardas el controlador que viene del main
        self.datos_usuario = datos_usuario
        # ... resto de tu código de interfaz ...
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("ContenedorPrincipal")
        self.setStyleSheet("QWidget#ContenedorPrincipal { background-color: #008037; }")

        if os.path.exists("Montserrat-Regular.ttf"):
            QFontDatabase.addApplicationFont("Montserrat-Regular.ttf")

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(50, 40, 50, 40)

        # ==============================================================================
        # BARRA SUPERIOR
        # ==============================================================================
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(12)
        
        btn_admin = QPushButton("Ver Admin")
        btn_cajero = QPushButton("Ver Cajero")
        btn_logout = QPushButton("Cerrar Sesión")
        
        for btn in [btn_admin, btn_cajero, btn_logout]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if self.controlador:
            btn_logout.clicked.connect(lambda: self.controlador.cambiar_pantalla("LoginFrame"))

        style_nav = """
            QPushButton {
                background-color: #FFFFFF; color: #008037; font-family: 'Montserrat';
                font-size: 11px; font-weight: bold; border-radius: 8px; 
                padding: 7px 16px; border: none;
            }
            QPushButton:hover { background-color: #1B4314; color: #FFFFFF; }
        """
        style_logout = """
            QPushButton {
                background-color: #DC3545; color: white; font-family: 'Montserrat';
                font-size: 11px; font-weight: bold; border-radius: 8px; 
                padding: 7px 16px; border: none;
            }
            QPushButton:hover { background-color: #BD2130; }
        """
        btn_admin.setStyleSheet(style_nav)
        btn_cajero.setStyleSheet(style_nav)
        btn_logout.setStyleSheet(style_logout)
        
        nav_layout.addStretch()
        nav_layout.addWidget(btn_admin)
        nav_layout.addWidget(btn_cajero)
        nav_layout.addWidget(btn_logout)
        layout_principal.addLayout(nav_layout)
        
        layout_principal.addStretch()

        # ==============================================================================
        # CUADRÍCULA COMPACTA
        # ==============================================================================
        contenedor_grid = QWidget()
        grid_layout = QGridLayout(contenedor_grid)
        grid_layout.setSpacing(35) 
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        self.mod_ventas = TarjetaModulo("VENTAS")
        self.mod_inventarios = TarjetaModulo("INVENTARIOS")
        self.mod_finanzas = TarjetaModulo("FINANZAS")
        self.mod_personal = TarjetaModulo("PERSONAL")
        self.mod_cuenta = TarjetaModulo("CUENTA", alto_personalizado=615)

        grid_layout.addWidget(self.mod_ventas, 0, 0)          
        grid_layout.addWidget(self.mod_finanzas, 1, 0)        
        grid_layout.addWidget(self.mod_inventarios, 0, 1)     
        grid_layout.addWidget(self.mod_personal, 1, 1)        
        grid_layout.addWidget(self.mod_cuenta, 0, 2, 2, 1)    

        layout_centrado_horizontal = QHBoxLayout()
        layout_centrado_horizontal.addStretch()
        layout_centrado_horizontal.addWidget(contenedor_grid)
        layout_centrado_horizontal.addStretch()

        layout_principal.addLayout(layout_centrado_horizontal)
        
        layout_principal.addStretch()

        # ==============================================================================
        # FOOTER (CORREGIDO: ALINEACIÓN TOTAL A LA IZQUIERDA ABAJO)
        # ==============================================================================
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(10, 0, 10, 0)
        
        self.lbl_user = QLabel()
        self.lbl_user.setFont(QFont("Montserrat", 16, QFont.Weight.Bold))
        # Se agrega alineación estricta al extremo inferior izquierdo
        self.lbl_user.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.lbl_user.setStyleSheet("color: white; line-height: 120%;")
        
        self.lbl_time = QLabel()
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.lbl_time.setStyleSheet("color: white; font-family: 'Montserrat'; font-weight: bold;")
        
        footer_layout.addWidget(self.lbl_user)
        footer_layout.addStretch() # Este stretch empuja el reloj a la derecha y mantiene al usuario a la izquierda
        footer_layout.addWidget(self.lbl_time)
        layout_principal.addLayout(footer_layout)

        self.actualizar_interfaz_usuario()

        # Reloj
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_tiempo)
        self.timer.start(1000)
        self.actualizar_tiempo()

    # ==============================================================================
    # MECANISMO DE DETECCIÓN DE USUARIO
    # ==============================================================================
    def establecer_usuario(self, nombre, rol):
        if nombre and rol:
            # Usamos formato HTML sutil para diferenciar visualmente el Rol del Nombre
            self.lbl_user.setText(f"<span style='font-size: 20px;'>{str(nombre).title()}</span><br>"
                                  f"<span style='font-size: 14px; font-weight: normal; opacity: 0.8;'>{str(rol).capitalize()}</span>")

    def actualizar_interfaz_usuario(self):
        nombre_final = "Nicolás Herrán"
        rol_final = "Administrador"
        
        if isinstance(self.datos_usuario, dict) and self.datos_usuario:
            nombre_final = self.datos_usuario.get("nombre", nombre_final)
            rol_final = self.datos_usuario.get("rol", rol_final)
            
        nombre_final = str(nombre_final).strip().title()
        rol_final = str(rol_final).strip().capitalize()
        
        # Mismo formato visual limpio usando HTML básico soportado por QLabel
        self.lbl_user.setText(f"<span style='font-size: 20px;'>{nombre_final}</span><br>"
                              f"<span style='font-size: 14px; font-weight: 500; color: #E0E0E0;'>{rol_final}</span>")

    def showEvent(self, event):
        self.actualizar_interfaz_usuario()
        super().showEvent(event)

    def actualizar_tiempo(self):
        ahora = datetime.now()
        string_hora = ahora.strftime("%H:%M")
        dias = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        string_fecha = f"{dias[ahora.weekday()]} {ahora.day} {meses[ahora.month - 1]}, {ahora.year}"
        self.lbl_time.setText(f"<span style='font-size: 46px; font-weight: 900;'>{string_hora}</span><br><span style='font-size: 13px; letter-spacing: 1px;'>{string_fecha}</span>")


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    usuario_detectado = {"nombre": "nicolás herrán", "rol": "administrador"}
    
    ventana = AdminDashboardQt(datos_usuario=usuario_detectado)
    ventana.resize(1280, 800)
    ventana.show()
    sys.exit(app.exec())