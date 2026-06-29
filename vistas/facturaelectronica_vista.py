import os
import traceback
from datetime import datetime
from PySide6.QtCore import Qt, QDate, QPoint
from PySide6.QtGui import QFont, QColor, QPainter, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame,
    QPushButton, QLabel, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QComboBox, QDateEdit, QStackedWidget, QFormLayout,
    QButtonGroup, QScrollArea
)


# ================================================================
# DIÁLOGO PARA DETALLE DE FACTURA ELECTRÓNICA (ESTILO FINANZAS)
# ================================================================
class DialogoDetalleFacturaElectronica(QDialog):
    def __init__(self, id_factura_electronica, conexion, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.id_factura_electronica = id_factura_electronica
        self.conexion = conexion

        self._crear_interfaz()
        self._cargar_datos()

    def _crear_interfaz(self):
        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(820, 680)
        self.card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 28px;
                border: 2px solid #D1E2D9;
            }
        """)
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(40)
        sombra.setColor(QColor(0, 0, 0, 50))
        sombra.setOffset(0, 10)
        self.card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(40, 32, 40, 32)
        layout_card.setSpacing(16)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return font

        # === ENCABEZADO ===
        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("DETALLE DE FACTURA ELECTRÓNICA")
        lbl_titulo.setFont(_f(18, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent; border: none;")

        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(36, 36)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setFont(_f(12, QFont.Weight.Bold))
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #F4F7F5; border: none;
                border-radius: 18px; color: #708077;
            }
            QPushButton:hover { background-color: #FDF2F2; color: #DC2626; }
        """)
        btn_cerrar.clicked.connect(self.reject)

        layout_header.addWidget(lbl_titulo)
        layout_header.addStretch()
        layout_header.addWidget(btn_cerrar)
        layout_card.addLayout(layout_header)

        # === INFO FRAME (Nº, fecha, tipo y cliente) ===
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: #F8FAF9;
                border-radius: 14px;
                border: 1px solid #D1E2D9;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(4)

        # Primera línea: Nº, fecha, tipo
        self.lbl_info = QLabel()
        self.lbl_info.setFont(_f(11, QFont.Weight.Medium))
        self.lbl_info.setStyleSheet("color: #1F2937; background: transparent;")
        info_layout.addWidget(self.lbl_info)

        # Segunda línea: Cliente, documento, email, ciudad
        self.lbl_cliente = QLabel()
        self.lbl_cliente.setFont(_f(10, QFont.Weight.Medium))
        self.lbl_cliente.setStyleSheet("color: #6B7280; background: transparent;")
        self.lbl_cliente.setWordWrap(True)
        info_layout.addWidget(self.lbl_cliente)
        layout_card.addWidget(info_frame)

        # === TABLA DE PRODUCTOS ===
        lbl_productos = QLabel("PRODUCTOS DE LA FACTURA")
        lbl_productos.setFont(_f(11, QFont.Weight.Black))
        lbl_productos.setStyleSheet("color: #17813D; background: transparent;")
        layout_card.addWidget(lbl_productos)

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit.", "Subtotal"])
        self.tabla_productos.setShowGrid(False)
        self.tabla_productos.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_productos.verticalHeader().setVisible(False)
        self.tabla_productos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_productos.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D1E2D9;
                border-radius: 12px;
                background: transparent;
                font-family: 'Montserrat';
                font-size: 11px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #F0F2F0;
                padding: 8px 12px;
                color: #1F2937;
            }
            QTableWidget::item:selected {
                background: #E8F5EE;
                color: #17813D;
            }
            QHeaderView::section {
                background: #F1F5F9;
                color: #64748B;
                font-weight: 800;
                font-size: 10px;
                border: none;
                padding: 10px 12px;
                font-family: 'Montserrat';
            }
            QTableWidget QTableCornerButton::section {
                background: transparent;
                border: none;
            }
        """)
        header = self.tabla_productos.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_productos.setColumnWidth(0, 280)
        self.tabla_productos.setColumnWidth(1, 100)
        self.tabla_productos.setColumnWidth(2, 130)
        self.tabla_productos.setColumnWidth(3, 130)
        layout_card.addWidget(self.tabla_productos)

        # === TOTAL, ESTADO Y CUFE ===
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background: #EDF7F1;
                border-radius: 12px;
                border: 2px dashed #A9DDBC;
                padding: 8px;
            }
        """)
        total_layout = QVBoxLayout(total_frame)
        total_layout.setContentsMargins(20, 12, 20, 12)
        total_layout.setSpacing(2)

        # Línea superior: total y estado
        total_estado_layout = QHBoxLayout()
        self.lbl_total = QLabel()
        self.lbl_total.setFont(_f(16, QFont.Weight.Black))
        self.lbl_total.setStyleSheet("color: #17813D; background: transparent;")
        self.lbl_estado = QLabel()
        self.lbl_estado.setFont(_f(12, QFont.Weight.Medium))
        total_estado_layout.addWidget(self.lbl_total)
        total_estado_layout.addStretch()
        total_estado_layout.addWidget(self.lbl_estado)
        total_layout.addLayout(total_estado_layout)

        # Línea inferior: CUFE
        self.lbl_cufe = QLabel()
        self.lbl_cufe.setFont(_f(10, QFont.Weight.Medium))
        self.lbl_cufe.setStyleSheet("color: #6B7280; background: transparent;")
        self.lbl_cufe.setWordWrap(True)
        total_layout.addWidget(self.lbl_cufe)

        layout_card.addWidget(total_frame)

        # === BOTÓN CERRAR ===
        btn_cerrar_dialog = QPushButton("CERRAR")
        btn_cerrar_dialog.setFixedHeight(50)
        btn_cerrar_dialog.setFont(_f(13, QFont.Weight.Black))
        btn_cerrar_dialog.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar_dialog.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 16px;
                letter-spacing: 0.5px;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 900;
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        btn_cerrar_dialog.clicked.connect(self.accept)
        layout_card.addWidget(btn_cerrar_dialog)

        layout_fondo.addWidget(self.card)

    def _cargar_datos(self):
        if not self.conexion:
            return
        try:
            cursor = self.conexion.cursor()
            # Obtener datos de la factura electrónica
            query = """
                SELECT fe.prefijo, fe.consecutivo, c.nombre_cliente, c.documento_identidad,
                       c.email, c.ciudad, fe.fecha_emision, fe.total, fe.estado, fe.cufe,
                       fe.id_factura_base
                FROM factura_electronica fe
                LEFT JOIN clientes c ON fe.id_cliente = c.id_cliente
                WHERE fe.id_factura_electronica = %s
            """
            cursor.execute(query, (self.id_factura_electronica,))
            row = cursor.fetchone()
            if not row:
                return

            if isinstance(row, dict):
                prefijo = row.get('prefijo', 'FAC')
                consecutivo = row.get('consecutivo', 0)
                cliente = row.get('nombre_cliente') or 'Sin cliente'
                documento = row.get('documento_identidad') or 'N/D'
                email = row.get('email') or 'N/D'
                ciudad = row.get('ciudad') or 'N/D'
                fecha = row.get('fecha_emision')
                total = row.get('total') or 0
                estado = row.get('estado') or 'Generada'
                cufe = row.get('cufe') or 'Sin CUFE'
                id_factura_base = row.get('id_factura_base')
            else:
                prefijo = row[0] or 'FAC'
                consecutivo = row[1] or 0
                cliente = row[2] or 'Sin cliente'
                documento = row[3] or 'N/D'
                email = row[4] or 'N/D'
                ciudad = row[5] or 'N/D'
                fecha = row[6]
                total = row[7] or 0
                estado = row[8] or 'Generada'
                cufe = row[9] or 'Sin CUFE'
                id_factura_base = row[10]

            numero = f"{prefijo}-{str(consecutivo).zfill(8)}"
            fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if fecha else 'N/D'

            # Llenar info_frame
            self.lbl_info.setText(
                f"<b>Factura N°:</b> {numero} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Fecha:</b> {fecha_str} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Tipo:</b> ELECTRÓNICA"
            )
            self.lbl_cliente.setText(
                f"<b>Cliente:</b> {cliente} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Documento:</b> {documento} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Email:</b> {email} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Ciudad:</b> {ciudad}"
            )

            # Total y estado
            self.lbl_total.setText(f"TOTAL DE LA FACTURA: ${int(total):,}")
            self.lbl_estado.setText(f"Estado: {estado}")
            if estado == "Pagada":
                self.lbl_estado.setStyleSheet("color: #008F39; font-weight: bold; background: transparent;")
            elif estado == "Pendiente":
                self.lbl_estado.setStyleSheet("color: #EAB308; font-weight: bold; background: transparent;")
            elif estado == "Anulada":
                self.lbl_estado.setStyleSheet("color: #DC2626; font-weight: bold; background: transparent;")
            else:
                self.lbl_estado.setStyleSheet("color: #64748B; font-weight: medium; background: transparent;")

            self.lbl_cufe.setText(f"CUFE: {cufe}")

            # Cargar productos de la factura base
            if id_factura_base:
                query_detalle = """
                    SELECT p.nombre_producto, df.cantidad_detfac, df.precio_unitario_detfac, df.subtotal_detfac
                    FROM detalle_factura df
                    JOIN productos p ON df.id_producto = p.id_producto
                    WHERE df.id_factura = %s
                """
                cursor.execute(query_detalle, (id_factura_base,))
                detalles = cursor.fetchall()

                self.tabla_productos.setRowCount(len(detalles))
                for fila, det in enumerate(detalles):
                    if isinstance(det, dict):
                        nombre = det.get('nombre_producto') or 'Producto'
                        cantidad = det.get('cantidad_detfac') or 0
                        precio = det.get('precio_unitario_detfac') or 0
                        subtotal = det.get('subtotal_detfac') or 0
                    else:
                        nombre = det[0] or 'Producto'
                        cantidad = det[1] or 0
                        precio = det[2] or 0
                        subtotal = det[3] or 0
                    self.tabla_productos.setItem(fila, 0, QTableWidgetItem(nombre))
                    self.tabla_productos.setItem(fila, 1, QTableWidgetItem(str(cantidad)))
                    self.tabla_productos.setItem(fila, 2, QTableWidgetItem(f"${int(precio):,}"))
                    self.tabla_productos.setItem(fila, 3, QTableWidgetItem(f"${int(subtotal):,}"))
                    self.tabla_productos.setRowHeight(fila, 40)
            else:
                self.tabla_productos.setRowCount(0)
                # Mensaje de sin productos
                self.tabla_productos.setRowCount(1)
                item = QTableWidgetItem("No hay productos asociados a esta factura electrónica")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_productos.setSpan(0, 0, 1, 4)
                self.tabla_productos.setItem(0, 0, item)

            cursor.close()

        except Exception as e:
            print(f"Error cargando detalle: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo cargar el detalle de la factura:\n{str(e)}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(40, 55, 45, 95)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def showEvent(self, event):
        super().showEvent(event)
        parent_window = self.window()
        if parent_window:
            self.setGeometry(parent_window.geometry())
        else:
            screen = self.screen().geometry()
            self.setGeometry(screen)


# ================================================================
# DIÁLOGO PARA NUEVA FACTURA ELECTRÓNICA
# ================================================================
class DialogoNuevaFacturaElectronica(QDialog):
    def __init__(self, conexion=None, empleado_id=None, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.conexion = conexion
        try:
            self.empleado_id = int(empleado_id) if empleado_id is not None else 1
        except:
            self.empleado_id = 1
        self.resultado = None
        self.factura_seleccionada_id = None
        self.datos_facturas = []
        self.filtro_tipo = "todos"

        self._crear_interfaz()
        self._cargar_facturas_recientes()

    def _crear_interfaz(self):
        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(950, 780)
        self.card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 28px;
                border: 2px solid #D1E2D9;
            }
        """)
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(40)
        sombra.setColor(QColor(0, 0, 0, 50))
        sombra.setOffset(0, 10)
        self.card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(40, 40, 40, 40)
        layout_card.setSpacing(24)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return font

        # Encabezado
        layout_header = QHBoxLayout()

        self.btn_volver = QPushButton("‹")
        self.btn_volver.setFixedSize(36, 36)
        self.btn_volver.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_volver.setFont(_f(18, QFont.Weight.Bold))
        self.btn_volver.setStyleSheet("""
            QPushButton {
                background-color: #F4F7F5; border: none;
                border-radius: 18px; color: #708077;
            }
            QPushButton:hover { background-color: #E8F5EE; color: #17813D; }
        """)
        self.btn_volver.clicked.connect(self._volver_a_lista)
        self.btn_volver.setVisible(False)

        lbl_titulo = QLabel("NUEVA FACTURA ELECTRÓNICA")
        lbl_titulo.setFont(_f(20, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent; border: none;")

        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(36, 36)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setFont(_f(12, QFont.Weight.Bold))
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #F4F7F5; border: none;
                border-radius: 18px; color: #708077;
            }
            QPushButton:hover { background-color: #FDF2F2; color: #DC2626; }
        """)
        btn_cerrar.clicked.connect(self.reject)

        layout_header.addWidget(self.btn_volver)
        layout_header.addWidget(lbl_titulo)
        layout_header.addStretch()
        layout_header.addWidget(btn_cerrar)
        layout_card.addLayout(layout_header)

        # Stack principal
        self.stack_principal = QStackedWidget()
        self.stack_principal.setStyleSheet("QStackedWidget { background: transparent; border: none; }")

        # ---- Widget LISTA ----
        widget_lista = QWidget()
        layout_lista = QVBoxLayout(widget_lista)
        layout_lista.setContentsMargins(0, 0, 0, 0)
        layout_lista.setSpacing(15)

        lbl_instruccion = QLabel("Selecciona una factura para generar su factura electrónica")
        lbl_instruccion.setFont(_f(14, QFont.Weight.Medium))
        lbl_instruccion.setStyleSheet("color: #708077; background: transparent;")
        layout_lista.addWidget(lbl_instruccion)

        # Filtros de lista
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(10)
        self.btn_filtro_todos = QPushButton("TODOS")
        self.btn_filtro_empresa = QPushButton("EMPRESA")
        self.btn_filtro_cliente = QPushButton("CLIENTE")
        for btn in (self.btn_filtro_todos, self.btn_filtro_empresa, self.btn_filtro_cliente):
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAFC;
                    color: #1B4314;
                    border: 2px solid #E2E8F0;
                    border-radius: 6px;
                    font-family: 'Montserrat';
                    font-size: 11px;
                    font-weight: bold;
                    padding: 0 15px;
                }
                QPushButton:hover { background-color: #E2E8F0; }
                QPushButton:checked {
                    background-color: #008F39;
                    color: #FFFFFF;
                    border: 2px solid #008F39;
                }
            """)
            btn.setCheckable(True)
        self.btn_filtro_todos.setChecked(True)
        self.btn_filtro_todos.clicked.connect(lambda: self._filtrar_lista("todos"))
        self.btn_filtro_empresa.clicked.connect(lambda: self._filtrar_lista("empresa"))
        self.btn_filtro_cliente.clicked.connect(lambda: self._filtrar_lista("cliente"))

        self.grupo_filtro_lista = QButtonGroup(self)
        self.grupo_filtro_lista.addButton(self.btn_filtro_todos)
        self.grupo_filtro_lista.addButton(self.btn_filtro_empresa)
        self.grupo_filtro_lista.addButton(self.btn_filtro_cliente)

        filtros_layout.addWidget(self.btn_filtro_todos)
        filtros_layout.addWidget(self.btn_filtro_empresa)
        filtros_layout.addWidget(self.btn_filtro_cliente)
        filtros_layout.addStretch()
        layout_lista.addLayout(filtros_layout)

        self.tabla_facturas = QTableWidget(0, 5)
        self.tabla_facturas.setHorizontalHeaderLabels(["N° Factura", "Cliente", "Fecha", "Total", "Acción"])
        self.tabla_facturas.setShowGrid(False)
        self.tabla_facturas.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_facturas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_facturas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_facturas.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla_facturas.verticalHeader().setVisible(False)
        self.tabla_facturas.verticalHeader().setDefaultSectionSize(45)
        self.tabla_facturas.setStyleSheet("""
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
        """)
        header = self.tabla_facturas.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_facturas.setColumnWidth(0, 120)
        self.tabla_facturas.setColumnWidth(1, 280)
        self.tabla_facturas.setColumnWidth(2, 130)
        self.tabla_facturas.setColumnWidth(3, 130)
        self.tabla_facturas.setColumnWidth(4, 120)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

        layout_lista.addWidget(self.tabla_facturas)

        btn_cancelar_lista = QPushButton("CANCELAR")
        btn_cancelar_lista.setFont(_f(12, QFont.Weight.Bold))
        btn_cancelar_lista.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar_lista.setStyleSheet("QPushButton { background: transparent; color: #9CA3AF; border: none; } QPushButton:hover { color: #DC2626; }")
        btn_cancelar_lista.clicked.connect(self.reject)
        layout_lista.addWidget(btn_cancelar_lista, alignment=Qt.AlignmentFlag.AlignRight)

        self.stack_principal.addWidget(widget_lista)

        # ---- Widget FORMULARIO ----
        widget_formulario = QWidget()
        layout_formulario = QVBoxLayout(widget_formulario)
        layout_formulario.setContentsMargins(0, 0, 0, 0)
        layout_formulario.setSpacing(20)

        lbl_tipo = QLabel("SELECCIONA EL TIPO DE DESTINATARIO")
        lbl_tipo.setFont(_f(12, QFont.Weight.Bold))
        lbl_tipo.setStyleSheet("color: #708077; background: transparent;")
        layout_formulario.addWidget(lbl_tipo)

        widget_botones_tipo = QFrame()
        widget_botones_tipo.setStyleSheet("QFrame { background: transparent; border: none; }")
        layout_botones_tipo = QHBoxLayout(widget_botones_tipo)
        layout_botones_tipo.setContentsMargins(0, 0, 0, 0)
        layout_botones_tipo.setSpacing(0)

        self.btn_empresa = QPushButton("EMPRESA")
        self.btn_cliente = QPushButton("CLIENTE")
        self.btn_empresa.setFixedHeight(44)
        self.btn_cliente.setFixedHeight(44)
        self.btn_empresa.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cliente.setCursor(Qt.CursorShape.PointingHandCursor)

        style_on = """
            QPushButton {
                background-color: transparent;
                color: #17813D;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 900;
                border: none;
                border-bottom: 3px solid #17813D;
                padding: 0 30px;
                height: 44px;
            }
        """
        style_off = """
            QPushButton {
                background-color: transparent;
                color: #9CA3AF;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 800;
                border: none;
                border-bottom: 3px solid transparent;
                padding: 0 24px;
                height: 44px;
            }
            QPushButton:hover {
                color: #17813D;
            }
        """
        self.btn_empresa.setStyleSheet(style_on)
        self.btn_cliente.setStyleSheet(style_off)

        self.btn_empresa.clicked.connect(lambda: self._cambiar_tipo("empresa"))
        self.btn_cliente.clicked.connect(lambda: self._cambiar_tipo("cliente"))

        layout_botones_tipo.addWidget(self.btn_empresa)
        layout_botones_tipo.addWidget(self.btn_cliente)
        layout_botones_tipo.addStretch()
        layout_formulario.addWidget(widget_botones_tipo)

        self.stack_campos = QStackedWidget()
        self.stack_campos.setStyleSheet("QStackedWidget { background: transparent; border: none; }")

        estilo_input = """
            QLineEdit, QComboBox {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 0 16px;
                color: #1F2937;
                font-family: 'Montserrat';
                font-size: 14px;
                height: 46px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #17813D;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
            }
        """

        # --- EMPRESA ---
        widget_empresa = QWidget()
        form_empresa = QFormLayout(widget_empresa)
        form_empresa.setSpacing(14)
        form_empresa.setContentsMargins(0, 10, 0, 0)

        self.txt_razon_social = QLineEdit()
        self.txt_razon_social.setPlaceholderText("Razón social")
        self.txt_razon_social.setStyleSheet(estilo_input)

        self.txt_nit = QLineEdit()
        self.txt_nit.setPlaceholderText("NIT")
        self.txt_nit.setStyleSheet(estilo_input)

        self.txt_regimen = QLineEdit()
        self.txt_regimen.setPlaceholderText("Régimen contable")
        self.txt_regimen.setStyleSheet(estilo_input)

        self.txt_direccion_emp = QLineEdit()
        self.txt_direccion_emp.setPlaceholderText("Dirección")
        self.txt_direccion_emp.setStyleSheet(estilo_input)

        self.txt_ciudad_emp = QLineEdit()
        self.txt_ciudad_emp.setPlaceholderText("Ciudad")
        self.txt_ciudad_emp.setStyleSheet(estilo_input)

        self.txt_resolucion = QLineEdit()
        self.txt_resolucion.setPlaceholderText("Resolución de facturación")
        self.txt_resolucion.setStyleSheet(estilo_input)

        form_empresa.addRow("Razón social:", self.txt_razon_social)
        form_empresa.addRow("NIT:", self.txt_nit)
        form_empresa.addRow("Régimen contable:", self.txt_regimen)
        form_empresa.addRow("Dirección:", self.txt_direccion_emp)
        form_empresa.addRow("Ciudad:", self.txt_ciudad_emp)
        form_empresa.addRow("Resolución:", self.txt_resolucion)

        # --- CLIENTE ---
        widget_cliente = QWidget()
        form_cliente = QFormLayout(widget_cliente)
        form_cliente.setSpacing(14)
        form_cliente.setContentsMargins(0, 10, 0, 0)

        self.txt_nombre_cli = QLineEdit()
        self.txt_nombre_cli.setPlaceholderText("Nombre o razón social")
        self.txt_nombre_cli.setStyleSheet(estilo_input)

        self.cmb_tipo_id = QComboBox()
        self.cmb_tipo_id.addItems(["CC", "NIT", "CE", "OTRO"])
        self.cmb_tipo_id.setStyleSheet(estilo_input)
        self.cmb_tipo_id.setFixedHeight(46)

        self.txt_num_id = QLineEdit()
        self.txt_num_id.setPlaceholderText("Número de identificación")
        self.txt_num_id.setStyleSheet(estilo_input)

        self.txt_email_cli = QLineEdit()
        self.txt_email_cli.setPlaceholderText("Correo electrónico")
        self.txt_email_cli.setStyleSheet(estilo_input)

        self.txt_ciudad_cli = QLineEdit()
        self.txt_ciudad_cli.setPlaceholderText("Ciudad")
        self.txt_ciudad_cli.setStyleSheet(estilo_input)

        self.txt_responsabilidad = QLineEdit()
        self.txt_responsabilidad.setPlaceholderText("Responsabilidad fiscal")
        self.txt_responsabilidad.setStyleSheet(estilo_input)

        form_cliente.addRow("Nombre:", self.txt_nombre_cli)
        form_cliente.addRow("Tipo identificación:", self.cmb_tipo_id)
        form_cliente.addRow("Número identificación:", self.txt_num_id)
        form_cliente.addRow("Correo electrónico:", self.txt_email_cli)
        form_cliente.addRow("Ciudad:", self.txt_ciudad_cli)
        form_cliente.addRow("Responsabilidad fiscal:", self.txt_responsabilidad)

        self.stack_campos.addWidget(widget_empresa)
        self.stack_campos.addWidget(widget_cliente)
        layout_formulario.addWidget(self.stack_campos)

        # Botones
        layout_botones_form = QHBoxLayout()
        layout_botones_form.setSpacing(16)
        btn_cancelar_form = QPushButton("CANCELAR")
        btn_cancelar_form.setFont(_f(12, QFont.Weight.Bold))
        btn_cancelar_form.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar_form.setStyleSheet("QPushButton { background: transparent; color: #9CA3AF; border: none; } QPushButton:hover { color: #DC2626; }")
        btn_cancelar_form.clicked.connect(self.reject)

        self.btn_guardar = QPushButton("GUARDAR FACTURA")
        self.btn_guardar.setFixedHeight(56)
        self.btn_guardar.setFont(_f(14, QFont.Weight.Black))
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 16px;
                padding: 0 40px;
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        self.btn_guardar.clicked.connect(self._guardar)

        layout_botones_form.addStretch()
        layout_botones_form.addWidget(btn_cancelar_form)
        layout_botones_form.addWidget(self.btn_guardar)
        layout_formulario.addLayout(layout_botones_form)

        self.stack_principal.addWidget(widget_formulario)

        layout_card.addWidget(self.stack_principal)
        layout_fondo.addWidget(self.card)

        self._cambiar_tipo("empresa")
        self._mostrar_lista()

    # ---- Métodos de lista de facturas ----
    def _cargar_facturas_recientes(self):
        self.datos_facturas = []
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                query = """
                    SELECT f.id_factura, c.nombre_cliente, f.fecha_fac, f.total_fac,
                           c.tipo_identificacion
                    FROM facturas f
                    LEFT JOIN clientes c ON f.id_cliente = c.id_cliente
                    ORDER BY f.fecha_fac DESC
                    LIMIT 20
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    if isinstance(row, dict):
                        self.datos_facturas.append((
                            row.get('id_factura'),
                            row.get('nombre_cliente') or 'Sin cliente',
                            row.get('fecha_fac').strftime("%Y-%m-%d") if hasattr(row.get('fecha_fac'), 'strftime') else str(row.get('fecha_fac')),
                            row.get('total_fac') or 0,
                            row.get('tipo_identificacion') or 'CC'
                        ))
                    else:
                        self.datos_facturas.append((
                            row[0],
                            row[1] or 'Sin cliente',
                            row[2].strftime("%Y-%m-%d") if hasattr(row[2], 'strftime') else str(row[2]),
                            row[3] or 0,
                            row[4] or 'CC'
                        ))
                cursor.close()
            except Exception as e:
                print(f"Error cargando facturas: {e}")
                self.datos_facturas = []
        else:
            self.datos_facturas = [
                (7, "Ricardo Esteban Pinto", "2024-04-08", 19800, "CC"),
                (6, "Camila Andrea Ospina", "2024-04-05", 27400, "CC"),
                (5, "Pedro Antonio Vargas", "2024-04-02", 34500, "CC"),
                (4, "Luisa Valentina Torres", "2024-03-20", 22700, "CC"),
                (3, "Juan Pablo Martínez", "2024-03-18", 41700, "CC"),
                (2, "María Fernanda López", "2024-03-16", 18500, "CC"),
                (1, "Carlos Andrés Gómez", "2024-03-15", 26200, "CC"),
            ]
        self._actualizar_tabla_facturas()

    def _actualizar_tabla_facturas(self):
        if self.filtro_tipo == "empresa":
            datos_filtrados = [f for f in self.datos_facturas if f[4] and f[4].upper() == 'NIT']
        elif self.filtro_tipo == "cliente":
            datos_filtrados = [f for f in self.datos_facturas if not f[4] or f[4].upper() != 'NIT']
        else:
            datos_filtrados = self.datos_facturas

        self.tabla_facturas.setRowCount(len(datos_filtrados))
        for fila, factura in enumerate(datos_filtrados):
            id_factura, cliente, fecha, total, _ = factura
            self.tabla_facturas.setItem(fila, 0, QTableWidgetItem(f"FAC-{id_factura:03d}"))
            self.tabla_facturas.setItem(fila, 1, QTableWidgetItem(cliente))
            self.tabla_facturas.setItem(fila, 2, QTableWidgetItem(fecha))
            self.tabla_facturas.setItem(fila, 3, QTableWidgetItem(f"${int(total):,}"))
            btn_crear = QPushButton("CREAR")
            btn_crear.setFixedSize(70, 30)
            btn_crear.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_crear.setStyleSheet("""
                QPushButton {
                    background-color: #008F39;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    font-family: 'Montserrat';
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #1B4314; }
            """)
            btn_crear.clicked.connect(lambda checked, fid=id_factura: self._mostrar_formulario(fid))
            self.tabla_facturas.setCellWidget(fila, 4, btn_crear)
            self.tabla_facturas.setRowHeight(fila, 45)

    def _filtrar_lista(self, tipo):
        self.filtro_tipo = tipo
        self._actualizar_tabla_facturas()

    # ---- Navegación ----
    def _mostrar_lista(self):
        self.stack_principal.setCurrentIndex(0)
        self.btn_volver.setVisible(False)
        self._actualizar_tabla_facturas()

    def _mostrar_formulario(self, factura_id):
        self.factura_seleccionada_id = factura_id
        self.stack_principal.setCurrentIndex(1)
        self.btn_volver.setVisible(True)
        self._cargar_datos_cliente(factura_id)

    def _cargar_datos_cliente(self, factura_id):
        if not self.conexion:
            return
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT id_cliente FROM facturas WHERE id_factura = %s", (factura_id,))
            row = cursor.fetchone()
            if not row:
                return
            if isinstance(row, dict):
                id_cliente = row.get('id_cliente')
            else:
                id_cliente = row[0]
            if not id_cliente:
                return

            cursor.execute("""
                SELECT nombre_cliente, documento_identidad, tipo_identificacion,
                       email, ciudad, responsabilidad_fiscal
                FROM clientes WHERE id_cliente = %s
            """, (id_cliente,))
            row_cli = cursor.fetchone()
            if not row_cli:
                return

            if isinstance(row_cli, dict):
                nombre = row_cli.get('nombre_cliente') or ''
                documento = row_cli.get('documento_identidad') or ''
                tipo_id = row_cli.get('tipo_identificacion') or 'CC'
                email = row_cli.get('email') or ''
                ciudad = row_cli.get('ciudad') or ''
                responsabilidad = row_cli.get('responsabilidad_fiscal') or ''
            else:
                nombre = row_cli[0] or ''
                documento = row_cli[1] or ''
                tipo_id = row_cli[2] or 'CC'
                email = row_cli[3] or ''
                ciudad = row_cli[4] or ''
                responsabilidad = row_cli[5] or ''

            if self.stack_campos.currentIndex() == 0:
                self.txt_razon_social.setText(nombre)
                self.txt_nit.setText(documento)
                self.txt_ciudad_emp.setText(ciudad)
                self.txt_regimen.clear()
                self.txt_direccion_emp.clear()
                self.txt_resolucion.clear()
            else:
                self.txt_nombre_cli.setText(nombre)
                self.txt_num_id.setText(documento)
                idx = self.cmb_tipo_id.findText(tipo_id)
                if idx >= 0:
                    self.cmb_tipo_id.setCurrentIndex(idx)
                else:
                    self.cmb_tipo_id.setCurrentIndex(0)
                self.txt_email_cli.setText(email)
                self.txt_ciudad_cli.setText(ciudad)
                self.txt_responsabilidad.setText(responsabilidad)

            cursor.close()
        except Exception as e:
            print(f"Error cargando datos del cliente: {e}")

    def _volver_a_lista(self):
        self._mostrar_lista()

    def _cambiar_tipo(self, tipo):
        style_on = """
            QPushButton {
                background-color: transparent;
                color: #17813D;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 900;
                border: none;
                border-bottom: 3px solid #17813D;
                padding: 0 30px;
                height: 44px;
            }
        """
        style_off = """
            QPushButton {
                background-color: transparent;
                color: #9CA3AF;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 800;
                border: none;
                border-bottom: 3px solid transparent;
                padding: 0 24px;
                height: 44px;
            }
            QPushButton:hover {
                color: #17813D;
            }
        """
        if tipo == "empresa":
            self.btn_empresa.setStyleSheet(style_on)
            self.btn_cliente.setStyleSheet(style_off)
            self.stack_campos.setCurrentIndex(0)
        else:
            self.btn_empresa.setStyleSheet(style_off)
            self.btn_cliente.setStyleSheet(style_on)
            self.stack_campos.setCurrentIndex(1)

        if self.factura_seleccionada_id:
            self._cargar_datos_cliente(self.factura_seleccionada_id)

    # ---- Guardar factura electrónica ----
    def _guardar(self):
        if not self.conexion:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return

        if not self.factura_seleccionada_id:
            QMessageBox.warning(self, "Atención", "No se ha seleccionado ninguna factura base.")
            return

        try:
            cursor = self.conexion.cursor()
            if self.stack_campos.currentIndex() == 0:
                nombre = self.txt_razon_social.text().strip()
                documento = self.txt_nit.text().strip()
                tipo_id = "NIT"
                email = None
                ciudad = self.txt_ciudad_emp.text().strip()
                responsabilidad = self.txt_regimen.text().strip()
                direccion = self.txt_direccion_emp.text().strip()
            else:
                nombre = self.txt_nombre_cli.text().strip()
                documento = self.txt_num_id.text().strip()
                tipo_id = self.cmb_tipo_id.currentText().strip()
                email = self.txt_email_cli.text().strip()
                ciudad = self.txt_ciudad_cli.text().strip()
                responsabilidad = self.txt_responsabilidad.text().strip()
                direccion = None

            if not nombre or not documento:
                QMessageBox.warning(self, "Atención", "Debes ingresar nombre y número de identificación del receptor.")
                return

            cursor.execute("SELECT id_cliente FROM clientes WHERE documento_identidad = %s", (documento,))
            row = cursor.fetchone()
            if row:
                if isinstance(row, dict):
                    id_cliente = row.get('id_cliente')
                else:
                    id_cliente = row[0]
                cursor.execute("""
                    UPDATE clientes 
                    SET nombre_cliente = %s, tipo_identificacion = %s, email = %s, ciudad = %s, 
                        responsabilidad_fiscal = %s, direccion = %s
                    WHERE id_cliente = %s
                """, (nombre, tipo_id, email, ciudad, responsabilidad, direccion, id_cliente))
            else:
                cursor.execute("""
                    INSERT INTO clientes 
                    (nombre_cliente, documento_identidad, tipo_identificacion, email, ciudad, responsabilidad_fiscal, direccion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nombre, documento, tipo_id, email, ciudad, responsabilidad, direccion))
                id_cliente = cursor.lastrowid
            self.conexion.commit()

            cursor.execute("SELECT total_fac FROM facturas WHERE id_factura = %s", (self.factura_seleccionada_id,))
            row = cursor.fetchone()
            if row:
                if isinstance(row, dict):
                    total_base = row.get('total_fac', 0)
                else:
                    total_base = row[0]
            else:
                total_base = 0

            cursor.execute("SELECT IFNULL(MAX(consecutivo), 0) + 1 FROM factura_electronica")
            row = cursor.fetchone()
            if row:
                if isinstance(row, dict):
                    consecutivo = row.get('IFNULL(MAX(consecutivo), 0) + 1', 1)
                else:
                    consecutivo = row[0]
            else:
                consecutivo = 1

            prefijo = "FAC"
            empleado_id = int(self.empleado_id) if self.empleado_id is not None else 1

            sql = """
                INSERT INTO factura_electronica 
                (id_cliente, id_empleado, id_factura_base, prefijo, consecutivo, fecha_emision, total, subtotal, iva, estado)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s, %s, 'Generada')
            """
            params = (id_cliente, empleado_id, self.factura_seleccionada_id, prefijo, consecutivo, total_base, total_base, 0)
            cursor.execute(sql, params)
            id_factura_electronica = cursor.lastrowid
            self.conexion.commit()
            cursor.close()

            QMessageBox.information(self, "Éxito", f"Factura electrónica {prefijo}-{str(consecutivo).zfill(8)} creada correctamente.")
            self.resultado = {"id": id_factura_electronica, "numero": f"{prefijo}-{str(consecutivo).zfill(8)}"}
            self.accept()

        except Exception as e:
            self.conexion.rollback()
            error_msg = f"Error al guardar factura: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(40, 55, 45, 95)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            pg = self.parent().geometry()
            self.setGeometry(self.parent().mapToGlobal(QPoint(0,0)).x(),
                             self.parent().mapToGlobal(QPoint(0,0)).y(),
                             pg.width(), pg.height())


# ================================================================
# VISTA PRINCIPAL DE FACTURA ELECTRÓNICA
# ================================================================
class FacturaElectronicaVista(QWidget):
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent)
        self.conexion = conexion
        self.filtro_tipo = "todos"
        self.datos_tabla = []
        self.empleado_id = 1
        self.filtro_fecha_activo = False
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 0)
        layout_principal.setSpacing(20)

        # Encabezado
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

        # Contenedor blanco
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

        # Filtros
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(12)

        # Botones de tipo
        self.btn_todos = QPushButton("TODOS")
        self.btn_empresa = QPushButton("EMPRESA")
        self.btn_cliente = QPushButton("CLIENTE")
        for btn in (self.btn_todos, self.btn_empresa, self.btn_cliente):
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAFC;
                    color: #1B4314;
                    border: 2px solid #E2E8F0;
                    border-radius: 8px;
                    font-family: 'Montserrat';
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0 15px;
                }
                QPushButton:hover { background-color: #E2E8F0; }
                QPushButton:checked {
                    background-color: #008F39;
                    color: #FFFFFF;
                    border: 2px solid #008F39;
                }
            """)
            btn.setCheckable(True)
        self.btn_todos.setChecked(True)
        self.btn_todos.clicked.connect(lambda: self._set_filtro_tipo("todos"))
        self.btn_empresa.clicked.connect(lambda: self._set_filtro_tipo("empresa"))
        self.btn_cliente.clicked.connect(lambda: self._set_filtro_tipo("cliente"))

        self.grupo_filtro = QButtonGroup(self)
        self.grupo_filtro.addButton(self.btn_todos)
        self.grupo_filtro.addButton(self.btn_empresa)
        self.grupo_filtro.addButton(self.btn_cliente)

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

        # Botón Fecha
        self.btn_fecha = QPushButton("📅 Fecha")
        self.btn_fecha.setFixedHeight(36)
        self.btn_fecha.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fecha.setStyleSheet("""
            QPushButton {
                background-color: #F8FAFC;
                color: #1B4314;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                font-family: 'Montserrat';
                font-size: 12px;
                font-weight: bold;
                padding: 0 15px;
            }
            QPushButton:hover { background-color: #E2E8F0; }
            QPushButton:checked {
                background-color: #008F39;
                color: #FFFFFF;
                border: 2px solid #008F39;
            }
        """)
        self.btn_fecha.setCheckable(True)
        self.btn_fecha.toggled.connect(self._toggle_fecha)

        # Widget de fechas
        self.widget_fechas = QWidget()
        self.widget_fechas.setVisible(False)
        layout_fechas = QHBoxLayout(self.widget_fechas)
        layout_fechas.setContentsMargins(0, 0, 0, 0)
        layout_fechas.setSpacing(8)

        lbl_desde = QLabel("Desde:")
        lbl_desde.setStyleSheet("color: #64748B; font-family: 'Montserrat'; font-size: 12px;")
        self.date_desde = QDateEdit()
        self.date_desde.setDate(QDate.currentDate().addDays(-30))
        self.date_desde.setCalendarPopup(True)
        self.date_desde.setFixedHeight(36)
        self.date_desde.setStyleSheet("""
            QDateEdit {
                background-color: #F8FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 10px;
                font-family: 'Montserrat';
                font-size: 13px;
            }
            QDateEdit:focus {
                border: 2px solid #008F39;
            }
        """)

        lbl_hasta = QLabel("Hasta:")
        lbl_hasta.setStyleSheet("color: #64748B; font-family: 'Montserrat'; font-size: 12px;")
        self.date_hasta = QDateEdit()
        self.date_hasta.setDate(QDate.currentDate())
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.setFixedHeight(36)
        self.date_hasta.setStyleSheet(self.date_desde.styleSheet())

        self.btn_aplicar_fecha = QPushButton("Aplicar")
        self.btn_aplicar_fecha.setFixedHeight(36)
        self.btn_aplicar_fecha.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_aplicar_fecha.setStyleSheet("""
            QPushButton {
                background-color: #008F39;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-family: 'Montserrat';
                font-size: 12px;
                font-weight: bold;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #1B4314;
            }
        """)
        self.btn_aplicar_fecha.clicked.connect(self.filtrar_tabla)

        layout_fechas.addWidget(lbl_desde)
        layout_fechas.addWidget(self.date_desde)
        layout_fechas.addWidget(lbl_hasta)
        layout_fechas.addWidget(self.date_hasta)
        layout_fechas.addWidget(self.btn_aplicar_fecha)
        layout_fechas.addStretch()

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
        self.btn_nueva.clicked.connect(self.abrir_nueva_factura)

        filtros_layout.addWidget(self.btn_todos)
        filtros_layout.addWidget(self.btn_empresa)
        filtros_layout.addWidget(self.btn_cliente)
        filtros_layout.addWidget(self.txt_buscador, 1)
        filtros_layout.addWidget(self.btn_fecha)
        filtros_layout.addWidget(self.widget_fechas)
        filtros_layout.addStretch()
        filtros_layout.addWidget(self.btn_nueva)
        layout_tarjeta.addLayout(filtros_layout)

        # Tabla
        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels([
            "N° Factura", "Cliente", "Fecha", "Total", "Estado", "Acciones"
        ])
        self.tabla.setShowGrid(False)
        self.tabla.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(45)
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
        """)
        header = self.tabla.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla.setColumnWidth(0, 120)
        self.tabla.setColumnWidth(1, 250)
        self.tabla.setColumnWidth(2, 120)
        self.tabla.setColumnWidth(3, 120)
        self.tabla.setColumnWidth(4, 100)
        self.tabla.setColumnWidth(5, 120)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)

        layout_tarjeta.addWidget(self.tabla)
        layout_principal.addWidget(tarjeta_principal)

    def _toggle_fecha(self, checked):
        self.widget_fechas.setVisible(checked)
        self.filtro_fecha_activo = checked
        self.filtrar_tabla()

    def _set_filtro_tipo(self, tipo):
        self.filtro_tipo = tipo
        self.filtrar_tabla()

    def cargar_datos(self):
        self.tabla.setRowCount(0)
        self.datos_tabla = []

        if not self.conexion:
            self.mostrar_mensaje_vacio("No hay conexión a la base de datos.")
            return

        try:
            cursor = self.conexion.cursor()
            query = """
                SELECT fe.id_factura_electronica, c.nombre_cliente, fe.fecha_emision, fe.total, fe.estado,
                       CONCAT(fe.prefijo, '-', LPAD(fe.consecutivo, 8, '0')) AS numero,
                       c.tipo_identificacion
                FROM factura_electronica fe
                LEFT JOIN clientes c ON fe.id_cliente = c.id_cliente
                ORDER BY fe.fecha_emision DESC
                LIMIT 50
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    if isinstance(row, dict):
                        tipo_id = row.get('tipo_identificacion', 'CC')
                        numero = row.get('numero', 'FAC-00000000')
                        cliente = row.get('nombre_cliente') or 'Sin cliente'
                        fecha = row.get('fecha_emision')
                        total = row.get('total') or 0
                        estado = row.get('estado') or 'Generada'
                        id_fe = row.get('id_factura_electronica')
                    else:
                        tipo_id = row[6] if row[6] else "CC"
                        numero = row[5]
                        cliente = row[1] or "Sin cliente"
                        fecha = row[2]
                        total = row[3] or 0
                        estado = row[4] or "Generada"
                        id_fe = row[0]

                    fecha_str = fecha.strftime("%Y-%m-%d") if hasattr(fecha, 'strftime') else str(fecha)
                    self.datos_tabla.append((
                        numero,
                        cliente,
                        fecha_str,
                        f"${int(total):,}",
                        estado,
                        id_fe,
                        tipo_id
                    ))
                cursor.close()
                self.llenar_tabla(self.datos_tabla)
            else:
                cursor.close()
                self.mostrar_mensaje_vacio("No hay facturas electrónicas registradas.")

        except Exception as e:
            error_msg = f"Error al cargar facturas electrónicas:\n{str(e)}"
            print(error_msg)
            traceback.print_exc()
            QMessageBox.critical(self, "Error", error_msg)
            self.mostrar_mensaje_vacio("Error al cargar los datos.")

    def mostrar_mensaje_vacio(self, mensaje):
        self.tabla.setRowCount(0)
        self.tabla.setRowCount(1)
        item = QTableWidgetItem(mensaje)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabla.setSpan(0, 0, 1, 6)
        self.tabla.setItem(0, 0, item)

    def llenar_tabla(self, datos):
        self.tabla.setRowCount(0)
        self.tabla.clearSpans()
        for fila_idx, row_data in enumerate(datos):
            self.tabla.insertRow(fila_idx)
            for col_idx in range(5):
                valor = row_data[col_idx]
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if col_idx == 3:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if col_idx == 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                    if valor == "Pagada":
                        item.setForeground(QColor("#008F39"))
                    elif valor == "Pendiente":
                        item.setForeground(QColor("#EAB308"))
                    elif valor == "Anulada":
                        item.setForeground(QColor("#DC2626"))
                self.tabla.setItem(fila_idx, col_idx, item)

            id_fe = row_data[5]
            btn_ver = QPushButton("Ver")
            btn_ver.setFixedSize(60, 28)
            btn_ver.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_ver.setStyleSheet("""
                QPushButton {
                    background-color: #008F39;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 4px;
                    font-family: 'Montserrat';
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1B4314;
                }
            """)
            btn_ver.clicked.connect(lambda checked, fid=id_fe: self.abrir_detalle(fid))
            self.tabla.setCellWidget(fila_idx, 5, btn_ver)
            self.tabla.setRowHeight(fila_idx, 45)

    def filtrar_tabla(self):
        texto_busqueda = self.txt_buscador.text().lower()
        filtro_fecha_activo = self.filtro_fecha_activo

        if filtro_fecha_activo:
            desde = self.date_desde.date().toString("yyyy-MM-dd")
            hasta = self.date_hasta.date().toString("yyyy-MM-dd")
        else:
            desde = hasta = None

        for fila in range(self.tabla.rowCount()):
            mostrar = True
            if fila >= len(self.datos_tabla):
                continue
            row_data = self.datos_tabla[fila]
            tipo = row_data[6] if len(row_data) > 6 else "CC"
            if self.filtro_tipo == "empresa" and tipo.upper() != "NIT":
                mostrar = False
            elif self.filtro_tipo == "cliente" and tipo.upper() == "NIT":
                mostrar = False

            if mostrar and texto_busqueda:
                coincide = False
                for col in range(5):
                    item = self.tabla.item(fila, col)
                    if item and texto_busqueda in item.text().lower():
                        coincide = True
                        break
                mostrar = coincide

            if mostrar and desde and hasta:
                item_fecha = self.tabla.item(fila, 2)
                if item_fecha:
                    fecha_str = item_fecha.text()
                    try:
                        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                        fecha_desde = datetime.strptime(desde, "%Y-%m-%d").date()
                        fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d").date()
                        if not (fecha_desde <= fecha_obj <= fecha_hasta):
                            mostrar = False
                    except:
                        pass

            self.tabla.setRowHidden(fila, not mostrar)

    def abrir_detalle(self, id_factura_electronica):
        dlg = DialogoDetalleFacturaElectronica(id_factura_electronica, self.conexion, self)
        dlg.exec()

    def abrir_nueva_factura(self):
        empleado_id = 1
        try:
            if hasattr(self.parent(), 'controlador'):
                ctrl = self.parent().controlador
                if hasattr(ctrl, 'usuario_actual') and ctrl.usuario_actual:
                    usuario = ctrl.usuario_actual
                    empleado_id = usuario.get('id_empleado', 1)
        except Exception as e:
            print(f"Error obteniendo empleado_id: {e}")
        dlg = DialogoNuevaFacturaElectronica(self.conexion, empleado_id, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.cargar_datos()