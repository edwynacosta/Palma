import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
                             QFrame, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QAction

# Definimos los colores y estilos globales para replicar el diseño
STYLE_SHEET = """
QMainWindow {
    background-color: #F8F9FA;
}
QWidget {
    font-family: 'Segoe UI', sans-serif;
    color: #333333;
}
QFrame {
    border: none;
}
QLabel {
    color: #6c757d;
}

/* Panel Izquierdo */
#SidebarPanel {
    background-color: transparent;
    padding-right: 20px;
}
#RefundTotalLabel {
    color: #FFFFFF;
    font-size: 32px;
    font-weight: bold;
}
#RefundTextLabel {
    color: #FFFFFF;
    font-size: 14px;
}
#SidebarRefundBox {
    background-color: #B22222;
    border-radius: 12px;
    padding: 20px;
}
#IdInvoiceLine {
    background-color: #FFFFFF;
    border: 1px solid #D3D3D3;
    border-radius: 6px;
    padding: 8px;
    color: #333333;
    font-size: 14px;
}
#ChangeBoxLabel {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: bold;
}
#ChangeTextLabel {
    color: #FFFFFF;
    font-size: 14px;
}
#SidebarChangeBox {
    background-color: #F5E0E0;
    border-radius: 12px;
    padding: 20px;
}
#ChangeBoxLabel {
    color: #B22222;
}
#ChangeTextLabel {
    color: #B22222;
}
#ReembolsarButton {
    background-color: #B22222;
    color: #FFFFFF;
    border-radius: 12px;
    padding: 15px;
    font-size: 16px;
    font-weight: bold;
    text-transform: uppercase;
}
#ReembolsarButton:hover {
    background-color: #a01f1f;
}

/* Panel Principal Derecho */
#MainContentPanel {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E0E0E0;
    padding: 20px;
}
#ReturnsTitleLabel {
    color: #B22222;
    font-size: 28px;
    font-weight: bold;
}
#OperationIdLabel {
    color: #6c757d;
    font-size: 12px;
}
#TableHeaderLabel {
    font-size: 12px;
    font-weight: bold;
    color: #a3aab0;
}
#TableCellLabel {
    font-size: 14px;
    color: #333333;
}
QSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #D3D3D3;
    border-radius: 6px;
    padding: 6px;
    font-size: 14px;
}
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #D3D3D3;
    border-radius: 6px;
    padding: 6px;
    font-size: 14px;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #D3D3D3;
}
#WarningLabel {
    color: #FF6F61;
    font-size: 20px;
}
#ObservationsEdit {
    background-color: #FFFFFF;
    border: 1px solid #D3D3D3;
    border-radius: 6px;
    padding: 10px;
    color: #333333;
    font-size: 14px;
}
#SecondaryActionButton {
    background-color: #FFFFFF;
    color: #a3aab0;
    border: 1px solid #D3D3D3;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 13px;
    text-transform: uppercase;
    font-weight: normal;
}
#SecondaryActionButton:hover {
    background-color: #F8F9FA;
    color: #333333;
    border: 1px solid #333333;
}

/* Banner Superior */
#TopBarFrame {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E0E0E0;
    padding: 5px;
}
#CajaTitleLabel {
    color: #12551e;
    font-size: 12px;
    font-weight: bold;
}
#NavButton {
    background-color: transparent;
    border: none;
    padding: 10px 15px;
    font-size: 11px;
    text-transform: uppercase;
    color: #a3aab0;
}
#NavButton:hover {
    color: #333333;
}
#NavButtonActive {
    background-color: #f1faf2;
    border-radius: 8px;
    color: #1a7126;
    font-weight: bold;
}
#UserProfileFrame {
    background-color: transparent;
}
#UserProfileNameLabel {
    color: #6c757d;
    font-size: 12px;
}
#CloseButton {
    background-color: transparent;
    border: none;
    color: #a3aab0;
    font-size: 16px;
}
#CloseButton:hover {
    color: #B22222;
}
"""

class DevolucionesWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema de Caja - Devoluciones")
        self.setMinimumSize(QSize(1100, 700))
        self.setStyleSheet(STYLE_SHEET)

        # Widget central y diseño principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Banner Superior
        self.top_bar_frame = QFrame()
        self.top_bar_frame.setObjectName("TopBarFrame")
        top_bar_layout = QHBoxLayout(self.top_bar_frame)
        top_bar_layout.setContentsMargins(15, 5, 15, 5)

        caja_label = QLabel("CAJA")
        caja_label.setObjectName("CajaTitleLabel")
        top_bar_layout.addWidget(caja_label)
        top_bar_layout.addStretch()

        # Botones de Navegación
        nav_buttons_frame = QFrame()
        nav_layout = QHBoxLayout(nav_buttons_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(5)
        
        btn_caja = QPushButton("CAJA")
        btn_caja.setObjectName("NavButton")
        
        btn_factura = QPushButton("FACTURA ELECTRÓNICA")
        btn_factura.setObjectName("NavButton")
        
        btn_devoluciones = QPushButton("DEVOLUCIONES")
        btn_devoluciones.setObjectName("NavButtonActive") # Activa
        
        btn_recibo = QPushButton("RECIBO PROVEEDORES")
        btn_recibo.setObjectName("NavButton")

        nav_layout.addWidget(btn_caja)
        nav_layout.addWidget(btn_factura)
        nav_layout.addWidget(btn_devoluciones)
        nav_layout.addWidget(btn_recibo)
        
        top_bar_layout.addWidget(nav_buttons_frame)
        top_bar_layout.addStretch()

        # Perfil de Usuario
        user_frame = QFrame()
        user_frame.setObjectName("UserProfileFrame")
        user_layout = QHBoxLayout(user_frame)