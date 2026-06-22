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
        # Layout principal
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(20)

        # ══════════════════════════════════════════════════════════════════════════════
        # 1. ENCABEZADO SUPERIOR
        # ══════════════════════════════════════════════════════════════════════════════
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 10)

        lbl_titulo = QLabel("FACTURA ELECTRÓNICA")
        lbl_titulo.setFont(QFont("Montserrat", 22, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #1B4314;")
        
        lbl_subtitulo = QLabel("Gestione sus facturas electrónicas de manera rápida y segura.")
        lbl_subtitulo.setFont(QFont("Montserrat", 11, QFont.Weight.Medium))
        lbl_subtitulo.setStyleSheet("color: #64748B;")
        
        titulos_layout = QVBoxLayout()
        titulos_layout.addWidget(lbl_titulo)
        titulos_layout.addWidget(lbl_subtitulo)
        
        header_layout.addLayout(titulos_layout)
        header_layout.addStretch()
        layout_principal.addWidget(header_frame)

        # ══════════════════════════════════════════════════════════════════════════════
        # 2. CONTENEDOR PRINCIPAL BLANCO (ESTILO TARJETA)
        # ══════════════════════════════════════════════════════════════════════════════
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

        # --- Filtros y búsqueda ---
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(15)

        # Buscador
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

        # Filtro de estado
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

        # Botón Nueva Factura
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

        # --- Tabla de Facturas ---
        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels([
            "N° Factura", "Cliente", "Fecha", "Total", "Estado", "Acciones"
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
        """Carga datos de facturas."""
        self.tabla.setRowCount(0)
        
        # Datos de prueba
        datos = [
            ("FAC-001", "Supermercado El Éxito", "2026-06-21", "$1,250,000", "Pagada", "Ver | PDF"),
            ("FAC-002", "Distribuidora La 14", "2026-06-20", "$850,000", "Pendiente", "Ver | PDF"),
            ("FAC-003", "Almacenes Tía", "2026-06-19", "$2,100,000", "Pagada", "Ver | PDF"),
            ("FAC-004", "D1 S.A.S.", "2026-06-18", "$320,000", "Anulada", "Ver | PDF"),
            ("FAC-005", "Oxxo Colombia", "2026-06-17", "$1,500,000", "Pagada", "Ver | PDF"),
        ]

        # Si hay base de datos, intentar cargar datos reales
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("""
                    SELECT id_factura, cliente, fecha, total, estado 
                    FROM facturas 
                    ORDER BY fecha DESC 
                    LIMIT 20
                """)
                resultados = cursor.fetchall()
                if resultados:
                    datos = []
                    for row in resultados:
                        datos.append((
                            f"FAC-{row[0]}",
                            row[1],
                            row[2].strftime("%Y-%m-%d") if hasattr(row[2], 'strftime') else str(row[2]),
                            f"${int(row[3]):,}",
                            row[4],
                            "Ver | PDF"
                        ))
                cursor.close()
            except Exception as e:
                print(f"Error cargando facturas: {e}")

        # Llenar la tabla
        for fila_idx, row_data in enumerate(datos):
            self.tabla.insertRow(fila_idx)
            for col_idx, valor in enumerate(row_data):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Colores para el estado
                if col_idx == 4:
                    if valor == "Pagada":
                        item.setForeground(QColor("#008F39"))
                    elif valor == "Pendiente":
                        item.setForeground(QColor("#EAB308"))
                    elif valor == "Anulada":
                        item.setForeground(QColor("#DC2626"))
                self.tabla.setItem(fila_idx, col_idx, item)

    def filtrar_tabla(self, texto=None):
        """Filtra la tabla por texto y estado."""
        texto_busqueda = self.txt_buscador.text().lower() if texto is None else texto.lower()
        estado_filtro = self.cmb_estado.currentText()
        
        for fila in range(self.tabla.rowCount()):
            mostrar = True
            
            # Filtro por texto
            if texto_busqueda:
                coincide = False
                for col in range(self.tabla.columnCount() - 1):  # Excluir columna de acciones
                    item = self.tabla.item(fila, col)
                    if item and texto_busqueda in item.text().lower():
                        coincide = True
                        break
                mostrar = mostrar and coincide
            
            # Filtro por estado
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