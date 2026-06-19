import os
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QColor
from PySide6.QtWidgets import (
    QWidget, QDialog, QLabel, QLineEdit, QComboBox, 
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, 
    QGraphicsDropShadowEffect, QFrame
)

class NuevoUsuarioDialog(QDialog):
    """Ventana emergente modal para agregar un nuevo usuario según la base de datos."""
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent)
        self.conexion = conexion
        
        # Tamaño exacto y deshabilitar bordes de forma compatible
        self.setFixedSize(460, 580)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        self.init_ui()
        self.cargar_datos_iniciales()

    def init_ui(self):
        # Contenedor con bordes redondeados y fondo limpio blanco
        self.contenedor = QFrame(self)
        self.contenedor.setGeometry(10, 10, 440, 560)
        self.contenedor.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 24px;
            }
        """)
        
        # Efecto de sombra corregido con QColor directo para evitar fallos de tipo
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(5)
        sombra.setColor(QColor(0, 0, 0, 160))
        self.contenedor.setGraphicsEffect(sombra)

        # Layout Principal
        layout = QVBoxLayout(self.contenedor)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(14)

        # TÍTULO DEL MODAL (Grosor ExtraBold/Black seguro)
        lbl_titulo = QLabel("NUEVO USUARIO", self.contenedor)
        lbl_titulo.setFont(QFont("Montserrat", 22, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #008F39; border: none;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)
        layout.addSpacing(5)

        # Hoja de estilos compartida para entradas de texto y comboboxes
        estilo_campos = """
            QLineEdit, QComboBox {
                background-color: #F8FAFC;
                color: #1B4314;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                padding: 10px 14px;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 600;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #008F39;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 15px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #008F39;
                margin-right: 10px;
            }
        """

        # CAMPO 1: SELECCIONAR EMPLEADO (id_empleado)
        lbl_empleado = QLabel("VINCULAR EMPLEADO", self.contenedor)
        lbl_empleado.setFont(QFont("Montserrat", 11, QFont.Bold))
        lbl_empleado.setStyleSheet("color: #1B4314; border: none;")
        layout.addWidget(lbl_empleado)
        
        self.combo_empleado = QComboBox(self.contenedor)
        self.combo_empleado.setStyleSheet(estilo_campos)
        layout.addWidget(self.combo_empleado)

        # CAMPO 2: USERNAME (username_log)
        lbl_username = QLabel("NOMBRE DE USUARIO", self.contenedor)
        lbl_username.setFont(QFont("Montserrat", 11, QFont.Bold))
        lbl_username.setStyleSheet("color: #1B4314; border: none;")
        layout.addWidget(lbl_username)
        
        self.txt_username = QLineEdit(self.contenedor)
        self.txt_username.setPlaceholderText("Ej: nicolas.herran")
        self.txt_username.setStyleSheet(estilo_campos)
        layout.addWidget(self.txt_username)

        # CAMPO 3: CONTRASEÑA (contrasena_log)
        lbl_password = QLabel("CONTRASEÑA DE ACCESO", self.contenedor)
        lbl_password.setFont(QFont("Montserrat", 11, QFont.Bold))
        lbl_password.setStyleSheet("color: #1B4314; border: none;")
        layout.addWidget(lbl_password)
        
        self.txt_password = QLineEdit(self.contenedor)
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("••••••••••••")
        self.txt_password.setStyleSheet(estilo_campos)
        layout.addWidget(self.txt_password)

        # CAMPO 4: ASIGNAR ROL (id_rol)
        lbl_rol = QLabel("ROL DE SISTEMA", self.contenedor)
        lbl_rol.setFont(QFont("Montserrat", 11, QFont.Bold))
        lbl_rol.setStyleSheet("color: #1B4314; border: none;")
        layout.addWidget(lbl_rol)
        
        self.combo_rol = QComboBox(self.contenedor)
        self.combo_rol.setStyleSheet(estilo_campos)
        layout.addWidget(self.combo_rol)

        layout.addSpacing(15)

        # BOTONES DE ACCIÓN (CANCELAR / GUARDAR)
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(15)

        self.btn_cancelar = QPushButton("CANCELAR", self.contenedor)
        self.btn_cancelar.setFont(QFont("Montserrat", 12, QFont.Bold))
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)
        self.btn_cancelar.setFixedHeight(45)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #64748B;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #334155;
            }
        """)

        self.btn_guardar = QPushButton("GUARDAR", self.contenedor)
        self.btn_guardar.setFont(QFont("Montserrat", 12, QFont.Bold))
        self.btn_guardar.setCursor(Qt.PointingHandCursor)
        self.btn_guardar.setFixedHeight(45)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #008F39;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #1B4314;
            }
        """)

        layout_botones.addWidget(self.btn_cancelar)
        layout_botones.addWidget(self.btn_guardar)
        layout.addLayout(layout_botones)

        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_guardar.clicked.connect(self.guardar_registro)

    def cargar_datos_iniciales(self):
        """Puebla los campos desde la base de datos."""
        if not self.conexion:
            self.combo_rol.addItem("Administrador", 1)
            self.combo_rol.addItem("Cajero", 2)
            self.combo_empleado.addItem("Nicolás Eduardo Herrán Daza", 1)
            return

        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT id_rol, descripcion_rol FROM rol")
            for id_rol, desc in cursor.fetchall():
                self.combo_rol.addItem(str(desc).capitalize(), id_rol)

            cursor.execute("SELECT id_empleado, nombre_empleado FROM empleados")
            for id_emp, nombre in cursor.fetchall():
                self.combo_empleado.addItem(str(nombre).title(), id_emp)

            cursor.close()
        except Exception as e:
            print(f"Error cargando relaciones en el modal: {e}")

    def guardar_registro(self):
        username = self.txt_username.text().strip()
        contrasena = self.txt_password.text().strip()
        id_rol = self.combo_rol.currentData()
        id_empleado = self.combo_empleado.currentData()

        if not username or not contrasena:
            QMessageBox.warning(self, "Atención", "Por favor, complete todos los campos de texto.")
            return

        if not self.conexion:
            QMessageBox.information(self, "Prueba Realizada", f"Usuario temporal creado:\nUser: {username}")
            self.accept()
            return

        try:
            cursor = self.conexion.cursor()
            query = """
                INSERT INTO usuarios (id_rol, id_empleado, username_log, contrasena_log)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (id_rol, id_empleado, username, contrasena))
            self.conexion.commit()
            cursor.close()

            QMessageBox.information(self, "Éxito", f"El usuario '{username}' ha sido registrado correctamente.")
            self.accept()
        except Exception as e:
            self.conexion.rollback()
            QMessageBox.critical(self, "Error SQL", f"No se pudo guardar el registro.\nDetalle: {e}")


class CuentaVista(QWidget):
    """Módulo Principal de Cuenta/Perfil adaptado como QWidget."""
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent)
        self.conexion = conexion
        self.cargar_fuentes_sistema()
        self.init_ui()

    def cargar_fuentes_sistema(self):
        ruta_fuentes = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fuentes")
        for f in ["Montserrat-Regular.ttf", "Montserrat-Bold.ttf", "Montserrat-ExtraBold.ttf", "Montserrat-Black.ttf"]:
            full_path = os.path.join(ruta_fuentes, f)
            if os.path.exists(full_path):
                QFontDatabase.addApplicationFont(full_path)

    def init_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        
        tarjeta = QFrame(self)
        tarjeta.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 20px;
            }
        """)
        layout_tarjeta = QVBoxLayout(tarjeta)
        layout_tarjeta.setContentsMargins(30, 30, 30, 30)
        layout_tarjeta.setSpacing(20)

        lbl_seccion = QLabel("GESTIÓN DE CUENTAS DE USUARIO", tarjeta)
        lbl_seccion.setFont(QFont("Montserrat", 18, QFont.Bold))
        lbl_seccion.setStyleSheet("color: #1B4314; border: none;")
        layout_tarjeta.addWidget(lbl_seccion)

        lbl_desc = QLabel("Administra las credenciales de ingreso y los privilegios de los empleados del sistema Palma.", tarjeta)
        lbl_desc.setFont(QFont("Montserrat", 11, QFont.Medium))
        lbl_desc.setStyleSheet("color: #64748B; border: none;")
        lbl_desc.setWordWrap(True)
        layout_tarjeta.addWidget(lbl_desc)
        
        layout_tarjeta.addSpacing(10)

        self.btn_nuevo_usuario = QPushButton("NUEVO USUARIO", tarjeta)
        self.btn_nuevo_usuario.setFont(QFont("Montserrat", 12, QFont.Bold))
        self.btn_nuevo_usuario.setCursor(Qt.PointingHandCursor)
        self.btn_nuevo_usuario.setFixedHeight(50)
        self.btn_nuevo_usuario.setStyleSheet("""
            QPushButton {
                background-color: #008F39;
                color: #FFFFFF;
                border: none;
                border-radius: 15px;
                padding-left: 20px;
                padding-right: 20px;
            }
            QPushButton:hover {
                background-color: #1B4314;
            }
        """)
        
        self.btn_nuevo_usuario.clicked.connect(self.abrir_popup_nuevo_usuario)
        layout_tarjeta.addWidget(self.btn_nuevo_usuario, alignment=Qt.AlignLeft)
        
        layout_principal.addWidget(tarjeta)
        layout_principal.addStretch()

    def abrir_popup_nuevo_usuario(self):
        modal = NuevoUsuarioDialog(conexion=self.conexion, parent=self)
        modal.exec()


# ALIAS DE COMPATIBILIDAD: Mapea CuentaDialog a CuentaVista para evitar fallos de importación externos
CuentaDialog = CuentaVista 


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ventana_test = CuentaVista()
    ventana_test.setWindowTitle("Módulo de Cuenta - Palma")
    ventana_test.resize(800, 600)
    ventana_test.show()
    sys.exit(app.exec())