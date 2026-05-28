import sys
import os
from PySide6.QtWidgets import QApplication, QStackedWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from modelos.usuario_modelo import UsuarioModelo
from vistas.login_vista import LoginVista

class PalmaApp(QStackedWidget):
    def __init__(self, modelo):
        super().__init__()
        self.modelo = modelo  # Guardamos el modelo conectado a la nube
        
        # 1. Configuración de la ventana principal
        self.setWindowTitle("PALMA")
        
        # Cargar el icono oficial de la palmera (.ico)
        ruta_icono = os.path.join("vistas", "logo_palma.ico")
        if os.path.exists(ruta_icono):
            self.setWindowIcon(QIcon(ruta_icono))
        
        # 2. Iniciar inmediatamente en pantalla completa nativa
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        # 3. Inicializamos la vista del Login pasándole este Stack como navegador
        self.vista_login = LoginVista(self)

        # 4. Agregamos el widget al stack de pantallas (Índice 0)
        self.addWidget(self.vista_login)
        self.setCurrentIndex(0)

    def cambiar_pantalla(self, nombre_pantalla):
        """Navegación nativa de PySide6 para alternar interfaces"""
        if nombre_pantalla == "AdminDashboard":
            # self.setCurrentIndex(1) # Descomentar cuando agregues tu panel administrativo
            print("Acceso correcto. Redireccionando al Dashboard...")
        elif nombre_pantalla == "LoginFrame":
            self.setCurrentIndex(0)

    def keyPressEvent(self, event):
        """Atajo de teclado: ESC para alternar el tamaño o salir de la app"""
        if event.key() == Qt.Key.Key_Escape:
            if self.windowState() == Qt.WindowState.WindowFullScreen:
                self.setWindowState(Qt.WindowState.WindowNoState)  # Ventana normal
            else:
                self.close()  # Cierra si ya estaba minimizada
        super().keyPressEvent(event)

if __name__ == "__main__":
    # Inicialización obligatoria del motor de eventos gráficos de Qt
    app = QApplication(sys.argv)
    
    print("🚀 Iniciando sistema PALMA...")
    
    # 1. Instanciamos el modelo de datos (Se conecta automáticamente a Aiven con SSL)
    modelo_sistema = UsuarioModelo()
    
    # 2. Encendemos la interfaz gráfica pasándole el modelo ya conectado
    sistema = PalmaApp(modelo_sistema)
    sistema.show()
    
    # Cierre limpio del hilo de ejecución de Python al cerrar la ventana
    sys.exit(app.exec())