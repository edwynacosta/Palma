import os
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame,
    QPushButton, QLabel, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

class ReciboProveedoresVista(QWidget):
    """Módulo de Recibo de Proveedores convertido a PySide6 con la estética de Palma."""
    
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent)
        self.conexion = conexion
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 0, 20, 0)
        layout_principal.setSpacing(20)

        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 0, 0, 10)

        lbl_titulo = QLabel("RECEPCIÓN DE PROVEEDORES")
        lbl_titulo.setFont(QFont("Montserrat", 22, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent;")
        
        lbl_subtitulo = QLabel("Gestione las entradas de mercancía y el inventario.")
        lbl_subtitulo.setFont(QFont("Montserrat", 11, QFont.Weight.Medium))
        lbl_subtitulo.setStyleSheet("color: #64748B; background: transparent;")
        
        titulos_layout = QVBoxLayout()
        titulos_layout.setSpacing(2)
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

        buscador_layout = QHBoxLayout()
        
        self.txt_buscador = QLineEdit()
        self.txt_buscador.setPlaceholderText("Buscar proveedor o producto...")
        self.txt_buscador.setFixedHeight(50)
        self.txt_buscador.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAFC;
                color: #1B4314;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                padding-left: 20px;
                font-family: 'Montserrat';
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #008F39;
                background-color: #FFFFFF;
            }
        """)
        self.txt_buscador.textChanged.connect(self.filtrar_tabla)

        self.btn_registrar = QPushButton("REGISTRAR ENTRADA")
        self.btn_registrar.setFixedHeight(50)
        self.btn_registrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_registrar.setStyleSheet("""
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
        self.btn_registrar.clicked.connect(self.simular_registro)

        buscador_layout.addWidget(self.txt_buscador)
        buscador_layout.addWidget(self.btn_registrar)
        layout_tarjeta.addLayout(buscador_layout)

        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Proveedor", "Producto Suministrado", "Última Entrega", "Estado"])
        
        self.tabla.setShowGrid(False)
        self.tabla.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(45)
        self.tabla.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
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
        
        header = self.tabla.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.tabla.setColumnWidth(0, 100)
        self.tabla.setColumnWidth(1, 280)
        self.tabla.setColumnWidth(2, 280)
        self.tabla.setColumnWidth(3, 150)
        self.tabla.setColumnWidth(4, 120)
        
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        
        layout_tarjeta.addWidget(self.tabla)
        layout_principal.addWidget(tarjeta_principal)

    def cargar_datos(self):
        self.tabla.setRowCount(0)
        datos_mock = [
            ("PRV-001", "DistriHortalizas La Granja", "Tomate, Cebolla, Papa", "2026-06-20", "Activo"),
            ("PRV-002", "Frutas del Valle SAS", "Manzana, Pera, Uva", "2026-06-18", "Activo"),
            ("PRV-003", "Empaques y Plásticos Bogotá", "Bolsas, Bandejas", "2026-06-05", "Pendiente"),
        ]

        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                query = """
                    SELECT id_proveedor, nombre_empresa, ciudad, telefono_principal, nit
                    FROM proveedores
                    LIMIT 20
                """
                cursor.execute(query)
                resultados = cursor.fetchall()
                if resultados:
                    datos = []
                    for row in resultados:
                        productos = "Varios"
                        fecha = "2026-06-22"
                        estado = "Activo" if row[4] else "Pendiente"
                        datos.append((
                            f"PRV-{row[0]}",
                            row[1],
                            productos,
                            fecha,
                            estado
                        ))
                    self.llenar_tabla(datos)
                    cursor.close()
                    return
                cursor.close()
            except Exception as e:
                print(f"No se pudo cargar desde MySQL, usando mock. Error: {e}")

        self.llenar_tabla(datos_mock)

    def llenar_tabla(self, datos):
        self.tabla.setRowCount(len(datos))
        for fila_idx, row_data in enumerate(datos):
            for col_idx, valor in enumerate(row_data):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.tabla.setItem(fila_idx, col_idx, item)
        
        for fila in range(self.tabla.rowCount()):
            self.tabla.setRowHeight(fila, 45)

    def filtrar_tabla(self, texto):
        texto = texto.lower()
        for fila in range(self.tabla.rowCount()):
            coincide = False
            for col in range(self.tabla.columnCount()):
                item = self.tabla.item(fila, col)
                if item and texto in item.text().lower():
                    coincide = True
                    break
            self.tabla.setRowHidden(fila, not coincide)

    def simular_registro(self):
        QMessageBox.information(self, "Módulo en Construcción", "La interfaz de registro de entrada de inventario se abrirá aquí.")