import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame,
    QPushButton, QLabel, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QComboBox, QTextEdit
)

class DevolucionesVista(QWidget):
    """Módulo de Devoluciones con la estética de Palma."""
    
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent)
        self.conexion = conexion
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(20)

        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 10)

        lbl_titulo = QLabel("DEVOLUCIONES")
        lbl_titulo.setFont(QFont("Montserrat", 22, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #1B4314;")
        
        lbl_subtitulo = QLabel("Gestione las devoluciones de productos y reembolsos.")
        lbl_subtitulo.setFont(QFont("Montserrat", 11, QFont.Weight.Medium))
        lbl_subtitulo.setStyleSheet("color: #64748B;")
        
        titulos_layout = QVBoxLayout()
        titulos_layout.addWidget(lbl_titulo)
        titulos_layout.addWidget(lbl_subtitulo)
        
        header_layout.addLayout(titulos_layout)
        header_layout.addStretch()
        layout_principal.addWidget(header_frame)

        tarjeta_principal = QFrame()
        tarjeta_principal.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 25px;
                border: 1px solid #E2E8F0;
            }
        """)
        
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(20)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 15))
        tarjeta_principal.setGraphicsEffect(sombra)

        layout_tarjeta = QVBoxLayout(tarjeta_principal)
        layout_tarjeta.setContentsMargins(30, 30, 30, 30)
        layout_tarjeta.setSpacing(20)

        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(15)

        self.txt_buscador = QLineEdit()
        self.txt_buscador.setPlaceholderText("Buscar devolución por número o cliente...")
        self.txt_buscador.setFixedHeight(46)
        self.txt_buscador.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAFC;
                color: #1B4314;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                padding-left: 20px;
                font-family: 'Montserrat';
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #008F39;
                background-color: #FFFFFF;
            }
        """)
        self.txt_buscador.textChanged.connect(self.filtrar_tabla)

        self.cmb_estado = QComboBox()
        self.cmb_estado.addItems(["Todos", "Pendiente", "Aprobada", "Rechazada"])
        self.cmb_estado.setFixedHeight(46)
        self.cmb_estado.setFixedWidth(150)
        self.cmb_estado.setStyleSheet("""
            QComboBox {
                background-color: #F8FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                padding: 0 15px;
                font-family: 'Montserrat';
                font-size: 13px;
                color: #1B4314;
            }
            QComboBox:focus {
                border: 2px solid #008F39;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.cmb_estado.currentTextChanged.connect(self.filtrar_tabla)

        self.btn_nueva = QPushButton("+ NUEVA DEVOLUCIÓN")
        self.btn_nueva.setFixedHeight(46)
        self.btn_nueva.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nueva.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 900;
                padding: 0 25px;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
        """)
        self.btn_nueva.clicked.connect(self.simular_nueva_devolucion)

        filtros_layout.addWidget(self.txt_buscador, 1)
        filtros_layout.addWidget(self.cmb_estado)
        filtros_layout.addWidget(self.btn_nueva)
        layout_tarjeta.addLayout(filtros_layout)

        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels([
            "N° Devolución", "Cliente", "Fecha", "Productos", "Estado", "Acciones"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setShowGrid(False)
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                font-family: 'Montserrat';
                font-size: 13px;
                color: #1B4314;
            }
            QHeaderView::section {
                background-color: #E2E8F0;
                color: #64748B;
                font-weight: bold;
                font-size: 12px;
                border: none;
                padding: 12px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E2E8F0;
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #ECFDF5;
                color: #008F39;
            }
        """)
        self.tabla.setColumnWidth(5, 150)
        
        layout_tarjeta.addWidget(self.tabla)
        layout_principal.addWidget(tarjeta_principal)

    def cargar_datos(self):
        self.tabla.setRowCount(0)
        
        # Datos de prueba (mock) porque la tabla devoluciones no existe
        datos = [
            ("DEV-001", "Supermercado El Éxito", "2026-06-21", "3 unidades", "Pendiente", "Ver"),
            ("DEV-002", "Distribuidora La 14", "2026-06-20", "1 caja", "Aprobada", "Ver"),
            ("DEV-003", "Almacenes Tía", "2026-06-19", "5 unidades", "Rechazada", "Ver"),
            ("DEV-004", "D1 S.A.S.", "2026-06-18", "2 unidades", "Pendiente", "Ver"),
        ]

        self.llenar_tabla(datos)

    def llenar_tabla(self, datos):
        self.tabla.setRowCount(len(datos))
        for fila_idx, row_data in enumerate(datos):
            for col_idx, valor in enumerate(row_data):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col_idx == 4:
                    if valor == "Pendiente":
                        item.setForeground(QColor("#EAB308"))
                    elif valor == "Aprobada":
                        item.setForeground(QColor("#008F39"))
                    elif valor == "Rechazada":
                        item.setForeground(QColor("#DC2626"))
                self.tabla.setItem(fila_idx, col_idx, item)

    def filtrar_tabla(self, texto=None):
        texto_busqueda = self.txt_buscador.text().lower() if texto is None else texto.lower()
        estado_filtro = self.cmb_estado.currentText()
        
        for fila in range(self.tabla.rowCount()):
            mostrar = True
            if texto_busqueda:
                coincide = False
                for col in range(self.tabla.columnCount() - 1):
                    item = self.tabla.item(fila, col)
                    if item and texto_busqueda in item.text().lower():
                        coincide = True
                        break
                mostrar = mostrar and coincide
            if estado_filtro != "Todos":
                item_estado = self.tabla.item(fila, 4)
                if item_estado and item_estado.text() != estado_filtro:
                    mostrar = False
            self.tabla.setRowHidden(fila, not mostrar)

    def simular_nueva_devolucion(self):
        QMessageBox.information(
            self, 
            "Nueva Devolución", 
            "Se abrirá el formulario para crear una nueva devolución.\n\n"
            "Funcionalidad en desarrollo."
        )