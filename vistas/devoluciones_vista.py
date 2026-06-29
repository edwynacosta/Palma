import os
import traceback
from datetime import datetime
from PySide6.QtCore import Qt, QDate, QPoint, QStringListModel
from PySide6.QtGui import QFont, QColor, QPainter, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame,
    QPushButton, QLabel, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QComboBox, QDateEdit, QStackedWidget, QFormLayout,
    QButtonGroup, QScrollArea, QCheckBox, QSpinBox, QTextEdit,
    QCompleter
)


# ================================================================
# DIÁLOGO PARA DETALLE DE DEVOLUCIÓN (ESTILO FINANZAS)
# ================================================================
class DialogoDetalleDevolucion(QDialog):
    def __init__(self, id_devolucion, conexion, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.id_devolucion = id_devolucion
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

        # Encabezado
        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("DETALLE DE DEVOLUCIÓN")
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

        # Info Frame
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

        self.lbl_info = QLabel()
        self.lbl_info.setFont(_f(11, QFont.Weight.Medium))
        self.lbl_info.setStyleSheet("color: #1F2937; background: transparent;")
        info_layout.addWidget(self.lbl_info)

        self.lbl_cliente = QLabel()
        self.lbl_cliente.setFont(_f(10, QFont.Weight.Medium))
        self.lbl_cliente.setStyleSheet("color: #6B7280; background: transparent;")
        self.lbl_cliente.setWordWrap(True)
        info_layout.addWidget(self.lbl_cliente)

        self.lbl_motivo = QLabel()
        self.lbl_motivo.setFont(_f(10, QFont.Weight.Medium))
        self.lbl_motivo.setStyleSheet("color: #6B7280; background: transparent;")
        self.lbl_motivo.setWordWrap(True)
        info_layout.addWidget(self.lbl_motivo)

        layout_card.addWidget(info_frame)

        # Tabla de productos devueltos
        lbl_productos = QLabel("PRODUCTOS DEVUELTOS")
        lbl_productos.setFont(_f(11, QFont.Weight.Black))
        lbl_productos.setStyleSheet("color: #17813D; background: transparent;")
        layout_card.addWidget(lbl_productos)

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(6)
        self.tabla_productos.setHorizontalHeaderLabels(["Producto", "Cantidad", "Peso (g)", "Precio Unit.", "Subtotal", "Estado"])
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
        self.tabla_productos.setColumnWidth(0, 200)
        self.tabla_productos.setColumnWidth(1, 80)
        self.tabla_productos.setColumnWidth(2, 80)
        self.tabla_productos.setColumnWidth(3, 120)
        self.tabla_productos.setColumnWidth(4, 120)
        self.tabla_productos.setColumnWidth(5, 100)
        layout_card.addWidget(self.tabla_productos)

        # Total y estado
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

        layout_card.addWidget(total_frame)

        # Botón cerrar
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
            query = """
                SELECT d.id_devolucion, d.tipo_devolucion, d.fecha_devolucion,
                       c.nombre_cliente, c.documento_identidad, c.email, c.ciudad,
                       d.motivo, d.estado, d.monto_total,
                       CASE WHEN d.id_factura IS NOT NULL THEN 'VENTA' ELSE 'COMPRA' END AS tipo
                FROM devoluciones d
                LEFT JOIN facturas f ON d.id_factura = f.id_factura
                LEFT JOIN clientes c ON f.id_cliente = c.id_cliente
                WHERE d.id_devolucion = %s
            """
            cursor.execute(query, (self.id_devolucion,))
            row = cursor.fetchone()
            if not row:
                return

            if isinstance(row, dict):
                id_dev = row.get('id_devolucion')
                tipo_dev = row.get('tipo_devolucion')
                fecha = row.get('fecha_devolucion')
                cliente = row.get('nombre_cliente') or 'Sin cliente'
                documento = row.get('documento_identidad') or 'N/D'
                email = row.get('email') or 'N/D'
                ciudad = row.get('ciudad') or 'N/D'
                motivo = row.get('motivo') or 'Sin motivo'
                estado = row.get('estado') or 'Pendiente'
                total = row.get('monto_total') or 0
                tipo = row.get('tipo') or 'VENTA'
            else:
                id_dev = row[0]
                tipo_dev = row[1]
                fecha = row[2]
                cliente = row[3] or 'Sin cliente'
                documento = row[4] or 'N/D'
                email = row[5] or 'N/D'
                ciudad = row[6] or 'N/D'
                motivo = row[7] or 'Sin motivo'
                estado = row[8] or 'Pendiente'
                total = row[9] or 0
                tipo = row[10] or 'VENTA'

            fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if fecha else 'N/D'

            self.lbl_info.setText(
                f"<b>Devolución N°:</b> {id_dev} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Fecha:</b> {fecha_str} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Tipo:</b> {tipo_dev.upper()}"
            )
            self.lbl_cliente.setText(
                f"<b>Cliente:</b> {cliente} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Documento:</b> {documento} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Email:</b> {email} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Ciudad:</b> {ciudad}"
            )
            self.lbl_motivo.setText(f"<b>Motivo:</b> {motivo}")

            self.lbl_total.setText(f"TOTAL REEMBOLSADO: ${int(total):,}")
            self.lbl_estado.setText(f"Estado: {estado}")
            if estado == "Aprobada":
                self.lbl_estado.setStyleSheet("color: #008F39; font-weight: bold; background: transparent;")
            elif estado == "Pendiente":
                self.lbl_estado.setStyleSheet("color: #EAB308; font-weight: bold; background: transparent;")
            elif estado == "Rechazada":
                self.lbl_estado.setStyleSheet("color: #DC2626; font-weight: bold; background: transparent;")
            else:
                self.lbl_estado.setStyleSheet("color: #64748B; font-weight: medium; background: transparent;")

            # Cargar productos devueltos (incluyendo peso si existe)
            query_det = """
                SELECT p.nombre_producto, dd.cantidad, dd.peso, dd.precio_unitario, dd.subtotal
                FROM detalle_devolucion dd
                JOIN productos p ON dd.id_producto = p.id_producto
                WHERE dd.id_devolucion = %s
            """
            cursor.execute(query_det, (self.id_devolucion,))
            detalles = cursor.fetchall()
            self.tabla_productos.setRowCount(len(detalles))
            for fila, det in enumerate(detalles):
                if isinstance(det, dict):
                    nombre = det.get('nombre_producto') or 'Producto'
                    cantidad = det.get('cantidad') or 0
                    peso = det.get('peso') or 0
                    precio = det.get('precio_unitario') or 0
                    subtotal = det.get('subtotal') or 0
                else:
                    nombre = det[0] or 'Producto'
                    cantidad = det[1] or 0
                    peso = det[2] or 0
                    precio = det[3] or 0
                    subtotal = det[4] or 0
                self.tabla_productos.setItem(fila, 0, QTableWidgetItem(nombre))
                self.tabla_productos.setItem(fila, 1, QTableWidgetItem(str(cantidad)))
                self.tabla_productos.setItem(fila, 2, QTableWidgetItem(str(peso) if peso else "-"))
                self.tabla_productos.setItem(fila, 3, QTableWidgetItem(f"${int(precio):,}"))
                self.tabla_productos.setItem(fila, 4, QTableWidgetItem(f"${int(subtotal):,}"))
                self.tabla_productos.setItem(fila, 5, QTableWidgetItem('N/A'))
                self.tabla_productos.setRowHeight(fila, 40)

            cursor.close()

        except Exception as e:
            print(f"Error cargando detalle devolución: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo cargar el detalle de la devolución:\n{str(e)}")

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
# DIÁLOGO PARA NUEVA DEVOLUCIÓN (CON DEVOLUCIÓN RÁPIDA)
# ================================================================
class DialogoNuevaDevolucion(QDialog):
    def __init__(self, conexion=None, empleado_id=None, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.conexion = conexion
        self.empleado_id = empleado_id or 1
        self.resultado = None

        self.factura_seleccionada_id = None
        self.datos_facturas = []
        self.filtro_tipo = "todos"
        self.detalles_factura = []  # productos de la factura seleccionada
        self.modo_rapido = False    # si es devolución rápida sin factura

        self._crear_interfaz()
        self._cargar_facturas_recientes()

    def _crear_interfaz(self):
        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(1050, 800)
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

        lbl_titulo = QLabel("NUEVA DEVOLUCIÓN")
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

        # Stack principal (lista / formulario)
        self.stack_principal = QStackedWidget()
        self.stack_principal.setStyleSheet("QStackedWidget { background: transparent; border: none; }")

        # ---- Widget LISTA de facturas ----
        widget_lista = QWidget()
        layout_lista = QVBoxLayout(widget_lista)
        layout_lista.setContentsMargins(0, 0, 0, 0)
        layout_lista.setSpacing(15)

        lbl_instruccion = QLabel("Selecciona una factura para realizar la devolución o usa Devolución Rápida")
        lbl_instruccion.setFont(_f(14, QFont.Weight.Medium))
        lbl_instruccion.setStyleSheet("color: #708077; background: transparent;")
        layout_lista.addWidget(lbl_instruccion)

        # Filtros
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

        # Botones de acción en la lista
        layout_botones_lista = QHBoxLayout()
        layout_botones_lista.setSpacing(16)

        btn_rapida = QPushButton("⚡ DEVOLUCIÓN RÁPIDA")
        btn_rapida.setFixedHeight(46)
        btn_rapida.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_rapida.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 900;
                padding: 0 25px;
            }
            QPushButton:hover { background-color: #D97706; }
        """)
        btn_rapida.clicked.connect(self._iniciar_devolucion_rapida)

        btn_cancelar_lista = QPushButton("CANCELAR")
        btn_cancelar_lista.setFont(_f(12, QFont.Weight.Bold))
        btn_cancelar_lista.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar_lista.setStyleSheet("QPushButton { background: transparent; color: #9CA3AF; border: none; } QPushButton:hover { color: #DC2626; }")
        btn_cancelar_lista.clicked.connect(self.reject)

        layout_botones_lista.addWidget(btn_rapida)
        layout_botones_lista.addStretch()
        layout_botones_lista.addWidget(btn_cancelar_lista)
        layout_lista.addLayout(layout_botones_lista)

        self.stack_principal.addWidget(widget_lista)

        # ---- Widget FORMULARIO (productos a devolver) ----
        widget_formulario = QWidget()
        layout_formulario = QVBoxLayout(widget_formulario)
        layout_formulario.setContentsMargins(0, 0, 0, 0)
        layout_formulario.setSpacing(20)

        # Cliente (opcional)
        lbl_cliente = QLabel("CLIENTE (OPCIONAL)")
        lbl_cliente.setFont(_f(12, QFont.Weight.Black))
        lbl_cliente.setStyleSheet("color: #708077;")
        layout_formulario.addWidget(lbl_cliente)

        self.txt_cliente = QLineEdit()
        self.txt_cliente.setPlaceholderText("Nombre del cliente (autocompletado, opcional)")
        self.txt_cliente.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 0 16px;
                color: #1F2937;
                font-family: 'Montserrat';
                font-size: 14px;
                height: 46px;
            }
            QLineEdit:focus {
                border: 2px solid #17813D;
                background-color: #FFFFFF;
            }
        """)
        layout_formulario.addWidget(self.txt_cliente)

        # Motivo de devolución
        lbl_motivo = QLabel("MOTIVO DE LA DEVOLUCIÓN")
        lbl_motivo.setFont(_f(12, QFont.Weight.Black))
        lbl_motivo.setStyleSheet("color: #708077;")
        layout_formulario.addWidget(lbl_motivo)

        self.txt_motivo = QTextEdit()
        self.txt_motivo.setPlaceholderText("Describe el motivo de la devolución...")
        self.txt_motivo.setFixedHeight(60)
        self.txt_motivo.setStyleSheet("""
            QTextEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 8px 16px;
                color: #1F2937;
                font-family: 'Montserrat';
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #17813D;
                background-color: #FFFFFF;
            }
        """)
        layout_formulario.addWidget(self.txt_motivo)

        # Tabla de productos a devolver
        lbl_productos = QLabel("PRODUCTOS A DEVOLVER")
        lbl_productos.setFont(_f(12, QFont.Weight.Black))
        lbl_productos.setStyleSheet("color: #708077;")
        layout_formulario.addWidget(lbl_productos)

        # Botón para agregar producto (en modo rápido)
        self.btn_agregar_producto = QPushButton("+ AGREGAR PRODUCTO")
        self.btn_agregar_producto.setFixedHeight(40)
        self.btn_agregar_producto.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agregar_producto.setStyleSheet("""
            QPushButton {
                background-color: #008F39;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-family: 'Montserrat';
                font-size: 12px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #1B4314; }
        """)
        self.btn_agregar_producto.clicked.connect(self._mostrar_dialogo_seleccion_producto)
        layout_formulario.addWidget(self.btn_agregar_producto)

        # Tabla con columnas: Seleccionar, Producto, Cantidad (Und), Peso (g), Precio Unit., Estado, Subtotal
        self.tabla_productos_devolver = QTableWidget(0, 7)
        self.tabla_productos_devolver.setHorizontalHeaderLabels(
            ["Seleccionar", "Producto", "Cantidad (Und)", "Peso (g)", "Precio Unit.", "Estado", "Subtotal"]
        )
        self.tabla_productos_devolver.setShowGrid(False)
        self.tabla_productos_devolver.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_productos_devolver.verticalHeader().setVisible(False)
        self.tabla_productos_devolver.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_productos_devolver.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla_productos_devolver.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D1E2D9;
                border-radius: 12px;
                background: transparent;
                font-family: 'Montserrat';
                font-size: 12px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #F0F2F0;
                padding: 6px 8px;
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
                padding: 8px;
                font-family: 'Montserrat';
            }
        """)
        header_prod = self.tabla_productos_devolver.horizontalHeader()
        header_prod.setStretchLastSection(True)
        header_prod.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_productos_devolver.setColumnWidth(0, 70)
        self.tabla_productos_devolver.setColumnWidth(1, 180)
        self.tabla_productos_devolver.setColumnWidth(2, 100)
        self.tabla_productos_devolver.setColumnWidth(3, 100)
        self.tabla_productos_devolver.setColumnWidth(4, 120)
        self.tabla_productos_devolver.setColumnWidth(5, 120)
        self.tabla_productos_devolver.setColumnWidth(6, 120)
        layout_formulario.addWidget(self.tabla_productos_devolver)

        # Total a reembolsar
        total_reembolso_layout = QHBoxLayout()
        lbl_reembolso = QLabel("TOTAL A REEMBOLSAR:")
        lbl_reembolso.setFont(_f(14, QFont.Weight.Bold))
        lbl_reembolso.setStyleSheet("color: #17813D;")
        self.lbl_total_reembolso = QLabel("$0")
        self.lbl_total_reembolso.setFont(_f(18, QFont.Weight.Black))
        self.lbl_total_reembolso.setStyleSheet("color: #17813D;")
        total_reembolso_layout.addWidget(lbl_reembolso)
        total_reembolso_layout.addStretch()
        total_reembolso_layout.addWidget(self.lbl_total_reembolso)
        layout_formulario.addLayout(total_reembolso_layout)

        # Botones
        layout_botones_form = QHBoxLayout()
        layout_botones_form.setSpacing(16)
        btn_cancelar_form = QPushButton("CANCELAR")
        btn_cancelar_form.setFont(_f(12, QFont.Weight.Bold))
        btn_cancelar_form.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar_form.setStyleSheet("QPushButton { background: transparent; color: #9CA3AF; border: none; } QPushButton:hover { color: #DC2626; }")
        btn_cancelar_form.clicked.connect(self.reject)

        self.btn_guardar = QPushButton("GUARDAR DEVOLUCIÓN")
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

        self._mostrar_lista()

        # Cargar nombres de clientes para autocompletado
        self._cargar_clientes_autocompletado()

    def _cargar_clientes_autocompletado(self):
        if not self.conexion:
            return
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT nombre_cliente FROM clientes ORDER BY nombre_cliente LIMIT 100")
            rows = cursor.fetchall()
            nombres = [row[0] for row in rows if row[0]]
            modelo = QStringListModel(nombres)
            completer = QCompleter(modelo, self)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.txt_cliente.setCompleter(completer)
            cursor.close()
        except Exception as e:
            print(f"Error cargando clientes para autocompletado: {e}")

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
            btn_seleccionar = QPushButton("SELECCIONAR")
            btn_seleccionar.setFixedSize(90, 30)
            btn_seleccionar.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_seleccionar.setStyleSheet("""
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
            btn_seleccionar.clicked.connect(lambda checked, fid=id_factura: self._mostrar_formulario(fid))
            self.tabla_facturas.setCellWidget(fila, 4, btn_seleccionar)
            self.tabla_facturas.setRowHeight(fila, 45)

    def _filtrar_lista(self, tipo):
        self.filtro_tipo = tipo
        self._actualizar_tabla_facturas()

    # ---- Navegación entre lista y formulario ----
    def _mostrar_lista(self):
        self.stack_principal.setCurrentIndex(0)
        self.btn_volver.setVisible(False)
        self._actualizar_tabla_facturas()

    def _mostrar_formulario(self, factura_id):
        self.modo_rapido = False
        self.factura_seleccionada_id = factura_id
        self.stack_principal.setCurrentIndex(1)
        self.btn_volver.setVisible(True)
        self._cargar_datos_factura(factura_id)
        self.btn_agregar_producto.setVisible(False)

    def _iniciar_devolucion_rapida(self):
        self.modo_rapido = True
        self.factura_seleccionada_id = None
        self.stack_principal.setCurrentIndex(1)
        self.btn_volver.setVisible(True)
        self.btn_agregar_producto.setVisible(True)
        self._limpiar_formulario_rapido()

    def _volver_a_lista(self):
        self._mostrar_lista()

    def _limpiar_formulario_rapido(self):
        self.txt_cliente.clear()
        self.txt_motivo.clear()
        self.tabla_productos_devolver.setRowCount(0)
        self.lbl_total_reembolso.setText("$0")
        self.factura_seleccionada_id = None
        self.detalles_factura = []

    # ---- Carga de datos de la factura seleccionada ----
    def _cargar_datos_factura(self, factura_id):
        if not self.conexion:
            return
        try:
            cursor = self.conexion.cursor()
            # Obtener cliente de la factura
            cursor.execute("""
                SELECT c.nombre_cliente, c.documento_identidad, c.email, c.ciudad,
                       c.id_cliente
                FROM facturas f
                LEFT JOIN clientes c ON f.id_cliente = c.id_cliente
                WHERE f.id_factura = %s
            """, (factura_id,))
            row = cursor.fetchone()
            if row:
                if isinstance(row, dict):
                    nombre = row.get('nombre_cliente') or ''
                    doc = row.get('documento_identidad') or ''
                    email = row.get('email') or ''
                    ciudad = row.get('ciudad') or ''
                else:
                    nombre = row[0] or ''
                    doc = row[1] or ''
                    email = row[2] or ''
                    ciudad = row[3] or ''
                self.txt_cliente.setText(f"{nombre} - {doc} - {email} - {ciudad}")
            else:
                self.txt_cliente.setText("Cliente no encontrado")

            # Obtener productos de la factura
            query_detalle = """
                SELECT p.id_producto, p.nombre_producto, df.cantidad_detfac, df.precio_unitario_detfac,
                       (df.cantidad_detfac * df.precio_unitario_detfac) AS subtotal
                FROM detalle_factura df
                JOIN productos p ON df.id_producto = p.id_producto
                WHERE df.id_factura = %s
            """
            cursor.execute(query_detalle, (factura_id,))
            detalles = cursor.fetchall()
            self.detalles_factura = []
            self.tabla_productos_devolver.setRowCount(0)
            for fila, det in enumerate(detalles):
                if isinstance(det, dict):
                    id_prod = det.get('id_producto')
                    nombre = det.get('nombre_producto') or 'Producto'
                    cantidad = det.get('cantidad_detfac') or 0
                    precio = det.get('precio_unitario_detfac') or 0
                else:
                    id_prod = det[0]
                    nombre = det[1] or 'Producto'
                    cantidad = det[2] or 0
                    precio = det[3] or 0
                self.detalles_factura.append({
                    'id_producto': id_prod,
                    'nombre': nombre,
                    'cantidad_original': cantidad,
                    'precio_unitario': precio
                })
                self._agregar_fila_producto(id_prod, nombre, precio, cantidad)

            cursor.close()
            self._calcular_reembolso()

        except Exception as e:
            print(f"Error cargando datos de factura: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos de la factura:\n{str(e)}")

    def _agregar_fila_producto(self, id_prod, nombre, precio, cantidad_max=9999):
        fila = self.tabla_productos_devolver.rowCount()
        self.tabla_productos_devolver.insertRow(fila)

        # Checkbox
        chk = QCheckBox()
        chk.setChecked(False)
        chk.stateChanged.connect(self._calcular_reembolso)
        self.tabla_productos_devolver.setCellWidget(fila, 0, chk)

        # Nombre producto
        self.tabla_productos_devolver.setItem(fila, 1, QTableWidgetItem(nombre))

        # Cantidad (Und)
        spin_cant = QSpinBox()
        spin_cant.setRange(0, int(cantidad_max))
        spin_cant.setValue(0)
        spin_cant.valueChanged.connect(self._calcular_reembolso)
        self.tabla_productos_devolver.setCellWidget(fila, 2, spin_cant)

        # Peso (g)
        spin_peso = QSpinBox()
        spin_peso.setRange(0, 99999)
        spin_peso.setValue(0)
        spin_peso.setSuffix(" g")
        spin_peso.valueChanged.connect(self._calcular_reembolso)
        self.tabla_productos_devolver.setCellWidget(fila, 3, spin_peso)

        # Precio unitario
        item_precio = QTableWidgetItem(f"${int(precio):,}")
        item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_productos_devolver.setItem(fila, 4, item_precio)

        # Estado del producto
        cmb_estado = QComboBox()
        cmb_estado.addItems(["Disponible", "Vencido", "Dañado"])
        cmb_estado.setStyleSheet("""
            QComboBox {
                background-color: #F8FAF9;
                border: 1px solid #D1E2D9;
                border-radius: 6px;
                padding: 2px 8px;
                font-family: 'Montserrat';
                font-size: 11px;
            }
        """)
        self.tabla_productos_devolver.setCellWidget(fila, 5, cmb_estado)

        # Subtotal
        item_subtotal = QTableWidgetItem("$0")
        item_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_productos_devolver.setItem(fila, 6, item_subtotal)

        self.tabla_productos_devolver.setRowHeight(fila, 45)

        # Conectar lógica de exclusión mutua entre cantidad y peso
        spin_cant.valueChanged.connect(lambda v, s=spin_peso: s.setValue(0) if v > 0 else None)
        spin_peso.valueChanged.connect(lambda v, s=spin_cant: s.setValue(0) if v > 0 else None)

    # ---- Diálogo de selección de producto con autocompletado ----
    def _mostrar_dialogo_seleccion_producto(self):
        dlg = QDialog(self, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dlg.setModal(True)
        dlg.setFixedSize(500, 220)

        layout_fondo = QVBoxLayout(dlg)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("MainCard")
        card.setFixedSize(460, 200)
        card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 20px;
                border: 2px solid #D1E2D9;
            }
        """)
        sombra = QGraphicsDropShadowEffect(card)
        sombra.setBlurRadius(30)
        sombra.setColor(QColor(0, 0, 0, 50))
        sombra.setOffset(0, 8)
        card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(card)
        layout_card.setContentsMargins(30, 30, 30, 30)
        layout_card.setSpacing(15)

        lbl = QLabel("SELECCIONAR PRODUCTO")
        lbl.setFont(QFont("Montserrat", 14, QFont.Weight.Black))
        lbl.setStyleSheet("color: #17813D;")

        txt_producto = QLineEdit()
        txt_producto.setPlaceholderText("Escribe el nombre del producto...")
        txt_producto.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 0 16px;
                font-family: 'Montserrat';
                font-size: 14px;
                height: 44px;
            }
            QLineEdit:focus {
                border: 2px solid #17813D;
                background-color: #FFFFFF;
            }
        """)

        # Autocompletado de productos con filtrado
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("SELECT nombre_producto, id_producto, precio_venta_prod FROM productos WHERE id_estado = 1")
                rows = cursor.fetchall()
                self.productos_busqueda = []
                nombres_productos = []
                for row in rows:
                    if isinstance(row, dict):
                        nombre = row.get('nombre_producto')
                        id_prod = row.get('id_producto')
                        precio = row.get('precio_venta_prod')
                    else:
                        nombre = row[0]
                        id_prod = row[1]
                        precio = row[2]
                    self.productos_busqueda.append((nombre, id_prod, precio))
                    nombres_productos.append(nombre)
                cursor.close()
                modelo = QStringListModel(nombres_productos)
                completer = QCompleter(modelo, self)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                completer.setFilterMode(Qt.MatchFlag.MatchContains)
                txt_producto.setCompleter(completer)
            except:
                pass

        def confirmar():
            texto = txt_producto.text().strip()
            if not texto:
                QMessageBox.warning(dlg, "Atención", "Ingresa un nombre de producto.")
                return
            # Buscar el producto seleccionado (por coincidencia exacta o por el primer que coincida)
            encontrado = None
            for nombre, id_prod, precio in self.productos_busqueda:
                if nombre.lower() == texto.lower():
                    encontrado = (id_prod, nombre, precio)
                    break
            if not encontrado:
                # Si no hay coincidencia exacta, buscar por contiene (tomar el primero)
                for nombre, id_prod, precio in self.productos_busqueda:
                    if texto.lower() in nombre.lower():
                        encontrado = (id_prod, nombre, precio)
                        break
            if not encontrado:
                QMessageBox.warning(dlg, "Atención", "Producto no encontrado.")
                return
            # Agregar a la tabla
            self._agregar_fila_producto(encontrado[0], encontrado[1], encontrado[2])
            dlg.accept()

        # Permitir Enter para confirmar
        txt_producto.returnPressed.connect(confirmar)

        btn_seleccionar = QPushButton("SELECCIONAR")
        btn_seleccionar.setFixedHeight(40)
        btn_seleccionar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_seleccionar.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        btn_seleccionar.clicked.connect(confirmar)

        btn_cancelar = QPushButton("CANCELAR")
        btn_cancelar.setFixedHeight(40)
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setStyleSheet("QPushButton { background: transparent; color: #9CA3AF; border: none; } QPushButton:hover { color: #DC2626; }")
        btn_cancelar.clicked.connect(dlg.reject)

        layout_card.addWidget(lbl)
        layout_card.addWidget(txt_producto)
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        layout_botones.addWidget(btn_cancelar)
        layout_botones.addWidget(btn_seleccionar)
        layout_card.addLayout(layout_botones)

        layout_fondo.addWidget(card)
        dlg.exec()

    def _calcular_reembolso(self):
        total = 0
        for fila in range(self.tabla_productos_devolver.rowCount()):
            chk = self.tabla_productos_devolver.cellWidget(fila, 0)
            spin_cant = self.tabla_productos_devolver.cellWidget(fila, 2)
            spin_peso = self.tabla_productos_devolver.cellWidget(fila, 3)
            if chk and chk.isChecked() and (spin_cant or spin_peso):
                cant = spin_cant.value() if spin_cant else 0
                peso = spin_peso.value() if spin_peso else 0
                precio_item = self.tabla_productos_devolver.item(fila, 4)
                if precio_item:
                    precio_text = precio_item.text().replace('$', '').replace(',', '')
                    try:
                        precio = int(precio_text)
                    except:
                        precio = 0
                    subtotal = (cant * precio) + (peso / 1000.0 * precio)
                    item_subtotal = self.tabla_productos_devolver.item(fila, 6)
                    if item_subtotal:
                        item_subtotal.setText(f"${int(subtotal):,}")
                    total += subtotal
                else:
                    item_subtotal = self.tabla_productos_devolver.item(fila, 6)
                    if item_subtotal:
                        item_subtotal.setText("$0")
            else:
                item_subtotal = self.tabla_productos_devolver.item(fila, 6)
                if item_subtotal:
                    item_subtotal.setText("$0")
        self.lbl_total_reembolso.setText(f"${int(total):,}")

    # ---- Guardar devolución ----
    def _guardar(self):
        if not self.conexion:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return

        # Verificar que al menos un producto esté seleccionado con cantidad > 0 o peso > 0
        productos_a_devolver = []
        for fila in range(self.tabla_productos_devolver.rowCount()):
            chk = self.tabla_productos_devolver.cellWidget(fila, 0)
            spin_cant = self.tabla_productos_devolver.cellWidget(fila, 2)
            spin_peso = self.tabla_productos_devolver.cellWidget(fila, 3)
            if chk and chk.isChecked():
                cant = spin_cant.value() if spin_cant else 0
                peso = spin_peso.value() if spin_peso else 0
                if cant == 0 and peso == 0:
                    continue
                id_prod = self.detalles_factura[fila]['id_producto'] if fila < len(self.detalles_factura) else 0
                precio = self.detalles_factura[fila]['precio_unitario'] if fila < len(self.detalles_factura) else 0
                estado_combo = self.tabla_productos_devolver.cellWidget(fila, 5)
                estado = estado_combo.currentText() if estado_combo else "Disponible"
                productos_a_devolver.append({
                    'id_producto': id_prod,
                    'cantidad': cant,
                    'peso': peso,
                    'precio_unitario': precio,
                    'estado': estado
                })

        if not productos_a_devolver:
            QMessageBox.warning(self, "Atención", "Selecciona al menos un producto con cantidad o peso mayor a cero.")
            return

        motivo = self.txt_motivo.toPlainText().strip()
        if not motivo:
            QMessageBox.warning(self, "Atención", "Debes escribir un motivo para la devolución.")
            return

        # Calcular total a reembolsar
        monto_total = 0
        for p in productos_a_devolver:
            subtotal = (p['cantidad'] * p['precio_unitario']) + (p['peso'] / 1000.0 * p['precio_unitario'])
            monto_total += subtotal

        # Verificar cliente (opcional)
        nombre_cliente = self.txt_cliente.text().strip()
        id_cliente = None
        if nombre_cliente:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("SELECT id_cliente FROM clientes WHERE nombre_cliente LIKE %s", (f"%{nombre_cliente}%",))
                row = cursor.fetchone()
                if row:
                    id_cliente = row[0]
                else:
                    cursor.execute("INSERT INTO clientes (nombre_cliente, documento_identidad) VALUES (%s, %s)",
                                   (nombre_cliente, 'N/D'))
                    id_cliente = cursor.lastrowid
                    self.conexion.commit()
                cursor.close()
            except Exception as e:
                print(f"Error al buscar/crear cliente: {e}")

        try:
            cursor = self.conexion.cursor()
            id_factura = self.factura_seleccionada_id if not self.modo_rapido else None
            sql_cab = """
                INSERT INTO devoluciones
                (tipo_devolucion, id_factura, id_empleado, fecha_devolucion, motivo, estado, monto_total)
                VALUES ('venta', %s, %s, NOW(), %s, 'Pendiente', %s)
            """
            cursor.execute(sql_cab, (id_factura, self.empleado_id, motivo, int(monto_total)))
            id_devolucion = cursor.lastrowid

            for prod in productos_a_devolver:
                subtotal = (prod['cantidad'] * prod['precio_unitario']) + (prod['peso'] / 1000.0 * prod['precio_unitario'])
                sql_det = """
                    INSERT INTO detalle_devolucion
                    (id_devolucion, id_producto, cantidad, peso, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_det, (id_devolucion, prod['id_producto'], prod['cantidad'],
                                         prod['peso'], prod['precio_unitario'], int(subtotal)))

            self.conexion.commit()
            cursor.close()
            QMessageBox.information(self, "Éxito", f"Devolución N° {id_devolucion} creada correctamente.")
            self.resultado = {"id": id_devolucion}
            self.accept()

        except Exception as e:
            self.conexion.rollback()
            error_msg = f"Error al guardar devolución: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
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
# VISTA PRINCIPAL DE DEVOLUCIONES
# ================================================================
class DevolucionesVista(QWidget):
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent)
        self.conexion = conexion
        self.filtro_tipo = "todos"
        self.filtro_fecha_activo = False
        self.datos_tabla = []
        self.empleado_id = 1
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

        lbl_titulo = QLabel("DEVOLUCIONES")
        lbl_titulo.setFont(QFont("Montserrat", 22, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent;")

        lbl_subtitulo = QLabel("Gestione las devoluciones de productos y reembolsos.")
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

        # Widget de fechas personalizadas
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

        # Botón nueva devolución
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
        self.btn_nueva.clicked.connect(self.abrir_nueva_devolucion)

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
            "N° Devolución", "Cliente", "Fecha", "Productos", "Estado", "Acciones"
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
        self.tabla.setColumnWidth(0, 130)
        self.tabla.setColumnWidth(1, 280)
        self.tabla.setColumnWidth(2, 130)
        self.tabla.setColumnWidth(3, 200)
        self.tabla.setColumnWidth(4, 120)
        self.tabla.setColumnWidth(5, 100)
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
                SELECT d.id_devolucion, c.nombre_cliente, d.fecha_devolucion, d.estado, d.monto_total,
                       (SELECT COUNT(*) FROM detalle_devolucion WHERE id_devolucion = d.id_devolucion) AS num_productos,
                       c.tipo_identificacion
                FROM devoluciones d
                LEFT JOIN facturas f ON d.id_factura = f.id_factura
                LEFT JOIN clientes c ON f.id_cliente = c.id_cliente
                ORDER BY d.fecha_devolucion DESC
                LIMIT 50
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    if isinstance(row, dict):
                        id_dev = row.get('id_devolucion')
                        cliente = row.get('nombre_cliente') or 'Sin cliente'
                        fecha = row.get('fecha_devolucion')
                        estado = row.get('estado') or 'Pendiente'
                        total = row.get('monto_total') or 0
                        num_prods = row.get('num_productos') or 0
                        tipo_id = row.get('tipo_identificacion') or 'CC'
                    else:
                        id_dev = row[0]
                        cliente = row[1] or 'Sin cliente'
                        fecha = row[2]
                        estado = row[3] or 'Pendiente'
                        total = row[4] or 0
                        num_prods = row[5] or 0
                        tipo_id = row[6] if len(row) > 6 else 'CC'

                    fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if hasattr(fecha, 'strftime') else str(fecha)
                    self.datos_tabla.append((
                        id_dev,
                        cliente,
                        fecha_str,
                        f"{num_prods} productos",
                        estado,
                        id_dev,
                        tipo_id
                    ))
                cursor.close()
                self.llenar_tabla(self.datos_tabla)
            else:
                cursor.close()
                self.mostrar_mensaje_vacio("No hay devoluciones registradas.")
        except Exception as e:
            error_msg = f"Error cargando devoluciones: {str(e)}"
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
                if col_idx == 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                    if valor == "Aprobada":
                        item.setForeground(QColor("#008F39"))
                    elif valor == "Pendiente":
                        item.setForeground(QColor("#EAB308"))
                    elif valor == "Rechazada":
                        item.setForeground(QColor("#DC2626"))
                self.tabla.setItem(fila_idx, col_idx, item)

            id_dev = row_data[5]
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
            btn_ver.clicked.connect(lambda checked, fid=id_dev: self.abrir_detalle(fid))
            self.tabla.setCellWidget(fila_idx, 5, btn_ver)
            self.tabla.setRowHeight(fila_idx, 45)

    def filtrar_tabla(self):
        texto_busqueda = self.txt_buscador.text().lower()
        filtro_fecha_activo = self.filtro_fecha_activo
        filtro_tipo = self.filtro_tipo

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

            if filtro_tipo == "empresa" and tipo.upper() != "NIT":
                mostrar = False
            elif filtro_tipo == "cliente" and tipo.upper() == "NIT":
                mostrar = False

            if mostrar and texto_busqueda:
                coincide = False
                for col in range(4):
                    item = self.tabla.item(fila, col)
                    if item and texto_busqueda in item.text().lower():
                        coincide = True
                        break
                mostrar = coincide

            if mostrar and desde and hasta:
                item_fecha = self.tabla.item(fila, 2)
                if item_fecha:
                    fecha_str = item_fecha.text().split()[0]
                    try:
                        dia, mes, anio = map(int, fecha_str.split('/'))
                        fecha_obj = QDate(anio, mes, dia)
                        fecha_desde = QDate.fromString(desde, "yyyy-MM-dd")
                        fecha_hasta = QDate.fromString(hasta, "yyyy-MM-dd")
                        if not (fecha_desde <= fecha_obj <= fecha_hasta):
                            mostrar = False
                    except:
                        pass

            self.tabla.setRowHidden(fila, not mostrar)

    def abrir_detalle(self, id_devolucion):
        dlg = DialogoDetalleDevolucion(id_devolucion, self.conexion, self)
        dlg.exec()

    def abrir_nueva_devolucion(self):
        empleado_id = 1
        try:
            if hasattr(self.parent(), 'controlador'):
                ctrl = self.parent().controlador
                if hasattr(ctrl, 'usuario_actual') and ctrl.usuario_actual:
                    usuario = ctrl.usuario_actual
                    empleado_id = usuario.get('id_empleado', 1)
        except Exception as e:
            print(f"Error obteniendo empleado_id: {e}")
        dlg = DialogoNuevaDevolucion(self.conexion, empleado_id, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.cargar_datos()