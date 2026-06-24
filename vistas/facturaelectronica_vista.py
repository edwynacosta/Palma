import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame,
    QPushButton, QLabel, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QSpinBox, QComboBox, QDateEdit
)
from PySide6.QtCore import QDate

class FacturaElectronicaVista(QWidget):
    """Módulo de Factura Electrónica con la estética de Palma."""
    
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent)
        self.conexion = conexion
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 0, 20, 0)
        layout_principal.setSpacing(20)

        # ENCABEZADO SUPERIOR
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 0, 0, 10)

        lbl_titulo = QLabel("FACTURA ELECTRÓNICA")
        lbl_titulo.setFont(QFont("Montserrat", 22, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent;")
        
        lbl_subtitulo = QLabel("Gestione sus facturas electrónicas de manera rápida y segura.")
        lbl_subtitulo.setFont(QFont("Montserrat", 11, QFont.Weight.Medium))
        lbl_subtitulo.setStyleSheet("color: #64748B; background: transparent;")
        
        titulos_layout = QVBoxLayout()
        titulos_layout.setSpacing(2)
        titulos_layout.addWidget(lbl_titulo)
        titulos_layout.addWidget(lbl_subtitulo)
        
        header_layout.addLayout(titulos_layout)
        header_layout.addStretch()
        layout_principal.addWidget(header_frame)

        # CONTENEDOR PRINCIPAL BLANCO
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

        # Filtros y búsqueda
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(15)

        self.txt_buscador = QLineEdit()
        self.txt_buscador.setPlaceholderText("Buscar factura por número o cliente...")
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
        self.cmb_estado.addItems(["Todos", "Pagada", "Pendiente", "Anulada"])
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

        self.btn_nueva = QPushButton("+ NUEVA FACTURA")
        self.btn_nueva.setFixedHeight(46)
        self.btn_nueva.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nueva.setStyleSheet("""
            QPushButton {
                background-color: #008F39;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 900;
                padding: 0 25px;
            }
            QPushButton:hover {
                background-color: #1B4314;
            }
        """)
        self.btn_nueva.clicked.connect(self.simular_nueva_factura)

        filtros_layout.addWidget(self.txt_buscador, 1)
        filtros_layout.addWidget(self.cmb_estado)
        filtros_layout.addWidget(self.btn_nueva)
        layout_tarjeta.addLayout(filtros_layout)

        # TABLA DE FACTURAS (CORREGIDA)
        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels([
            "N° Factura", "Cliente", "Fecha", "Total", "Estado", "Acciones"
        ])
        
        # Configuración de la tabla sin bordes
        self.tabla.setShowGrid(False)
        self.tabla.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Tamaño fijo de filas
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(45)
        self.tabla.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        # Estilo de la tabla
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                outline: none;
                font-family: 'Montserrat';
                font-size: 13px;
                color: #1B4314;
                gridline-color: transparent;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E2E8F0;
                padding: 8px 12px;
                background: transparent;
            }
            QTableWidget::item:selected {
                background-color: #ECFDF5;
                color: #008F39;
            }
            QTableWidget::item:hover {
                background-color: #F8FAFC;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                color: #64748B;
                font-weight: 800;
                font-size: 12px;
                border: none;
                padding: 12px 8px;
                font-family: 'Montserrat';
            }
            QTableWidget QTableCornerButton::section {
                background: transparent;
                border: none;
            }
        """)
        
        # Configuración de columnas con tamaños fijos
        header = self.tabla.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Anchos fijos para cada columna
        self.tabla.setColumnWidth(0, 120)   # N° Factura
        self.tabla.setColumnWidth(1, 280)   # Cliente
        self.tabla.setColumnWidth(2, 130)   # Fecha
        self.tabla.setColumnWidth(3, 130)   # Total
        self.tabla.setColumnWidth(4, 120)   # Estado
        self.tabla.setColumnWidth(5, 120)   # Acciones
        
        # Las columnas 1 (Cliente) y 5 (Acciones) pueden estirarse si es necesario
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        
        layout_tarjeta.addWidget(self.tabla)
        layout_principal.addWidget(tarjeta_principal)

    def cargar_datos(self):
        self.tabla.setRowCount(0)
        datos_mock = [
            ("FAC-001", "Supermercado El Éxito", "2026-06-21", "$1,250,000", "Pagada", "Ver | PDF"),
            ("FAC-002", "Distribuidora La 14", "2026-06-20", "$850,000", "Pendiente", "Ver | PDF"),
            ("FAC-003", "Almacenes Tía", "2026-06-19", "$2,100,000", "Pagada", "Ver | PDF"),
            ("FAC-004", "D1 S.A.S.", "2026-06-18", "$320,000", "Anulada", "Ver | PDF"),
            ("FAC-005", "Oxxo Colombia", "2026-06-17", "$1,500,000", "Pagada", "Ver | PDF"),
        ]

        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                query = """
                    SELECT f.id_factura, c.nombre_cliente, f.fecha_fac, f.total_fac,
                           CASE WHEN f.total_fac > 0 THEN 'Pagada' ELSE 'Pendiente' END AS estado
                    FROM facturas f
                    LEFT JOIN clientes c ON f.id_cliente = c.id_cliente
                    ORDER BY f.fecha_fac DESC
                    LIMIT 20
                """
                cursor.execute(query)
                resultados = cursor.fetchall()
                if resultados:
                    datos = []
                    for row in resultados:
                        datos.append((
                            f"FAC-{row[0]}",
                            row[1] or "Cliente genérico",
                            row[2].strftime("%Y-%m-%d") if hasattr(row[2], 'strftime') else str(row[2]),
                            f"${int(row[3]):,}" if row[3] else "$0",
                            row[4],
                            "Ver | PDF"
                        ))
                    self.llenar_tabla(datos)
                    cursor.close()
                    return
                cursor.close()
            except Exception as e:
                print(f"Error cargando facturas: {e}")
        
        self.llenar_tabla(datos_mock)

    def llenar_tabla(self, datos):
        self.tabla.setRowCount(len(datos))
        for fila_idx, row_data in enumerate(datos):
            for col_idx, valor in enumerate(row_data):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                # Alinear el total a la derecha
                if col_idx == 3:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                # Alinear el estado al centro
                if col_idx == 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                    if valor == "Pagada":
                        item.setForeground(QColor("#008F39"))
                    elif valor == "Pendiente":
                        item.setForeground(QColor("#EAB308"))
                    elif valor == "Anulada":
                        item.setForeground(QColor("#DC2626"))
                self.tabla.setItem(fila_idx, col_idx, item)
        
        # Ajustar altura de las filas
        for fila in range(self.tabla.rowCount()):
            self.tabla.setRowHeight(fila, 45)

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

    def simular_nueva_factura(self):
        QMessageBox.information(
            self, 
            "Nueva Factura", 
            "Se abrirá el formulario para crear una nueva factura electrónica.\n\n"
            "Funcionalidad en desarrollo."
        )