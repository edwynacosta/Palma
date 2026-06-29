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
# DIÁLOGO PARA DETALLE DE RECIBO (EDITABLE)
# ================================================================
class DialogoDetalleRecibo(QDialog):
    def __init__(self, id_fac_compra, conexion, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.id_fac_compra = id_fac_compra
        self.conexion = conexion
        self.estado_actual = None  # se llena al cargar
        self.productos_detalle = []  # lista de dicts con los datos del detalle

        self._crear_interfaz()
        self._cargar_datos()

    def _crear_interfaz(self):
        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(950, 700)
        self.card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 28px;
                border: 1px solid #D1E2D9;
            }
        """)
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(20)
        sombra.setColor(QColor(0, 0, 0, 20))
        sombra.setOffset(0, 5)
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
        lbl_titulo = QLabel("DETALLE DE RECIBO")
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

        self.lbl_proveedor = QLabel()
        self.lbl_proveedor.setFont(_f(10, QFont.Weight.Medium))
        self.lbl_proveedor.setStyleSheet("color: #6B7280; background: transparent;")
        self.lbl_proveedor.setWordWrap(True)
        info_layout.addWidget(self.lbl_proveedor)

        layout_card.addWidget(info_frame)

        # Tabla de productos (editable)
        lbl_productos = QLabel("PRODUCTOS RECIBIDOS")
        lbl_productos.setFont(_f(11, QFont.Weight.Black))
        lbl_productos.setStyleSheet("color: #17813D; background: transparent;")
        layout_card.addWidget(lbl_productos)

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(6)
        self.tabla_productos.setHorizontalHeaderLabels(["Producto", "Cantidad", "Peso (g)", "Precio Unit.", "Subtotal", "Acción"])
        self.tabla_productos.setShowGrid(False)
        self.tabla_productos.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_productos.verticalHeader().setVisible(False)
        self.tabla_productos.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.EditKeyPressed)
        self.tabla_productos.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D1E2D9;
                border-radius: 12px;
                background: transparent;
                font-family: 'Montserrat';
                font-size: 13px;
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
            QTableWidget::item:editable {
                background-color: #FDFDFD;
            }
            QHeaderView::section {
                background: #F1F5F9;
                color: #64748B;
                font-weight: 800;
                font-size: 11px;
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
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_productos.setColumnWidth(0, 200)
        self.tabla_productos.setColumnWidth(1, 80)
        self.tabla_productos.setColumnWidth(2, 100)
        self.tabla_productos.setColumnWidth(3, 120)
        self.tabla_productos.setColumnWidth(4, 130)
        self.tabla_productos.setColumnWidth(5, 80)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)

        # Conectar señal para recalcular al editar
        self.tabla_productos.cellChanged.connect(self._on_cell_changed)

        layout_card.addWidget(self.tabla_productos)

        # Total
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background: #EDF7F1;
                border-radius: 12px;
                border: 2px dashed #A9DDBC;
                padding: 8px;
            }
        """)
        total_layout = QHBoxLayout(total_frame)
        total_layout.setContentsMargins(20, 12, 20, 12)
        self.lbl_total = QLabel()
        self.lbl_total.setFont(_f(16, QFont.Weight.Black))
        self.lbl_total.setStyleSheet("color: #17813D; background: transparent;")
        total_layout.addWidget(self.lbl_total, alignment=Qt.AlignmentFlag.AlignCenter)

        layout_card.addWidget(total_frame)

        # Botones: RECIBIR y ACEPTAR
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(16)

        self.btn_recibir = QPushButton("RECIBIR")
        self.btn_recibir.setFixedHeight(50)
        self.btn_recibir.setFont(_f(13, QFont.Weight.Black))
        self.btn_recibir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recibir.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: #FFFFFF;
                border: none;
                border-radius: 16px;
                letter-spacing: 0.5px;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 900;
                padding: 0 30px;
            }
            QPushButton:hover { background-color: #D97706; }
            QPushButton:disabled { background-color: #D1D5DB; color: #9CA3AF; }
        """)
        self.btn_recibir.clicked.connect(self._marcar_recibido)

        btn_aceptar = QPushButton("ACEPTAR")
        btn_aceptar.setFixedHeight(50)
        btn_aceptar.setFont(_f(13, QFont.Weight.Black))
        btn_aceptar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 16px;
                letter-spacing: 0.5px;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 900;
                padding: 0 30px;
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        btn_aceptar.clicked.connect(self.accept)

        layout_botones.addStretch()
        layout_botones.addWidget(self.btn_recibir)
        layout_botones.addWidget(btn_aceptar)
        layout_card.addLayout(layout_botones)

        layout_fondo.addWidget(self.card)

    def _cargar_datos(self):
        if not self.conexion:
            return
        try:
            cursor = self.conexion.cursor()
            # Cabecera
            query = """
                SELECT fc.id_fac_compra, fc.numero_fac_compra, fc.fecha_fac_compra,
                       p.nombre_empresa, p.nit, p.telefono_principal, p.email,
                       fc.valor_fac_compra, fc.estado
                FROM factura_compra fc
                LEFT JOIN proveedores p ON fc.id_proveedor = p.id_proveedor
                WHERE fc.id_fac_compra = %s
            """
            cursor.execute(query, (self.id_fac_compra,))
            row = cursor.fetchone()
            if not row:
                return

            if isinstance(row, dict):
                id_fac = row.get('id_fac_compra')
                numero = row.get('numero_fac_compra') or 'N/D'
                fecha = row.get('fecha_fac_compra')
                proveedor = row.get('nombre_empresa') or 'Sin proveedor'
                nit = row.get('nit') or 'N/D'
                telefono = row.get('telefono_principal') or 'N/D'
                email = row.get('email') or 'N/D'
                total = row.get('valor_fac_compra') or 0
                estado = row.get('estado') or 'pendiente'
            else:
                id_fac = row[0]
                numero = row[1] or 'N/D'
                fecha = row[2]
                proveedor = row[3] or 'Sin proveedor'
                nit = row[4] or 'N/D'
                telefono = row[5] or 'N/D'
                email = row[6] or 'N/D'
                total = row[7] or 0
                estado = row[8] if len(row) > 8 else 'pendiente'

            self.estado_actual = estado
            fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if fecha else 'N/D'

            self.lbl_info.setText(
                f"<b>Recibo N°:</b> {numero} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Fecha:</b> {fecha_str} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>ID:</b> {id_fac} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Estado:</b> {estado.upper()}"
            )
            self.lbl_proveedor.setText(
                f"<b>Proveedor:</b> {proveedor} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>NIT:</b> {nit} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Teléfono:</b> {telefono} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Email:</b> {email}"
            )

            # Si ya está recibido, deshabilitar botón Recibir
            if estado.upper() == 'RECIBIDO':
                self.btn_recibir.setEnabled(False)
                self.btn_recibir.setToolTip("Este pedido ya fue recibido")

            # Detalle
            query_det = """
                SELECT df.id_detalle_compra, p.nombre_producto, df.cantidad, df.peso_gramos,
                       df.precio_unitario, df.subtotal
                FROM detalle_factura_compra df
                JOIN productos p ON df.id_producto = p.id_producto
                WHERE df.id_fac_compra = %s
            """
            cursor.execute(query_det, (self.id_fac_compra,))
            detalles = cursor.fetchall()
            self.productos_detalle = []
            self.tabla_productos.setRowCount(0)

            for fila, det in enumerate(detalles):
                if isinstance(det, dict):
                    id_det = det.get('id_detalle_compra')
                    nombre = det.get('nombre_producto') or 'Producto'
                    cantidad = det.get('cantidad') or 0
                    peso = det.get('peso_gramos') or 0
                    precio = det.get('precio_unitario') or 0
                    subtotal = det.get('subtotal') or 0
                else:
                    id_det = det[0]
                    nombre = det[1] or 'Producto'
                    cantidad = det[2] or 0
                    peso = det[3] or 0
                    precio = det[4] or 0
                    subtotal = det[5] or 0

                self._agregar_fila_detalle(id_det, nombre, cantidad, peso, precio, subtotal)

            self._actualizar_total()

            cursor.close()

        except Exception as e:
            print(f"Error cargando detalle: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo cargar el detalle del recibo:\n{str(e)}")

    def _agregar_fila_detalle(self, id_det, nombre, cantidad, peso, precio, subtotal):
        fila = self.tabla_productos.rowCount()
        self.tabla_productos.insertRow(fila)

        # Producto (no editable)
        item_producto = QTableWidgetItem(nombre)
        item_producto.setFlags(item_producto.flags() & ~Qt.ItemIsEditable)
        self.tabla_productos.setItem(fila, 0, item_producto)

        # Cantidad (editable)
        item_cant = QTableWidgetItem(str(cantidad))
        self.tabla_productos.setItem(fila, 1, item_cant)

        # Peso (editable)
        item_peso = QTableWidgetItem(f"{peso:.2f}")
        self.tabla_productos.setItem(fila, 2, item_peso)

        # Precio Unit. (no editable)
        item_precio = QTableWidgetItem(f"${int(precio):,}")
        item_precio.setFlags(item_precio.flags() & ~Qt.ItemIsEditable)
        self.tabla_productos.setItem(fila, 3, item_precio)

        # Subtotal (no editable, se recalcula)
        item_subtotal = QTableWidgetItem(f"${int(subtotal):,}")
        item_subtotal.setFlags(item_subtotal.flags() & ~Qt.ItemIsEditable)
        self.tabla_productos.setItem(fila, 4, item_subtotal)

        # Botón eliminar (acción)
        btn_eliminar = QPushButton("✕")
        btn_eliminar.setFixedSize(28, 28)
        btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #FEE2E2;
                border: none;
                border-radius: 14px;
                color: #DC2626;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: #FFFFFF;
            }
        """)
        btn_eliminar.clicked.connect(lambda: self._eliminar_fila(fila, id_det))
        self.tabla_productos.setCellWidget(fila, 5, btn_eliminar)

        self.tabla_productos.setRowHeight(fila, 40)

        # Guardar en lista interna
        self.productos_detalle.append({
            'id_detalle': id_det,
            'id_producto': None,  # no lo usamos para edición
            'nombre': nombre,
            'cantidad': cantidad,
            'peso': peso,
            'precio_unitario': precio,
            'subtotal': subtotal
        })

    def _on_cell_changed(self, row, column):
        if column not in (1, 2):
            return
        if row >= len(self.productos_detalle):
            return

        item_cant = self.tabla_productos.item(row, 1)
        item_peso = self.tabla_productos.item(row, 2)
        if not item_cant or not item_peso:
            return

        try:
            cantidad = float(item_cant.text()) if item_cant.text() else 0
            peso = float(item_peso.text()) if item_peso.text() else 0
        except ValueError:
            return

        precio = self.productos_detalle[row]['precio_unitario']
        subtotal = cantidad * precio

        self.tabla_productos.item(row, 4).setText(f"${int(subtotal):,}")

        self.productos_detalle[row]['cantidad'] = cantidad
        self.productos_detalle[row]['peso'] = peso
        self.productos_detalle[row]['subtotal'] = subtotal

        self._actualizar_total()

    def _eliminar_fila(self, fila, id_detalle):
        # Confirmar eliminación
        if QMessageBox.question(self, "Eliminar", "¿Desea eliminar este producto del recibo?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No:
            return
        # Eliminar de la base de datos
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("DELETE FROM detalle_factura_compra WHERE id_detalle_compra = %s", (id_detalle,))
                self.conexion.commit()
                cursor.close()
            except Exception as e:
                self.conexion.rollback()
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto:\n{str(e)}")
                return
        # Eliminar de la lista y la tabla
        if fila < len(self.productos_detalle):
            self.productos_detalle.pop(fila)
        self.tabla_productos.removeRow(fila)
        self._actualizar_total()

    def _actualizar_total(self):
        total = sum(p['subtotal'] for p in self.productos_detalle)
        self.lbl_total.setText(f"TOTAL DE LA COMPRA: ${int(total):,}")

    def _marcar_recibido(self):
        if not self.conexion:
            return
        if self.estado_actual.upper() == 'RECIBIDO':
            QMessageBox.information(self, "Info", "Este pedido ya está recibido.")
            return

        # Preguntar confirmación
        if QMessageBox.question(self, "Confirmar", "¿Desea marcar este pedido como RECIBIDO?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No:
            return

        try:
            cursor = self.conexion.cursor()
            cursor.execute("UPDATE factura_compra SET estado = 'RECIBIDO' WHERE id_fac_compra = %s", (self.id_fac_compra,))
            self.conexion.commit()
            cursor.close()
            self.estado_actual = 'RECIBIDO'
            self.btn_recibir.setEnabled(False)
            self.btn_recibir.setToolTip("Este pedido ya fue recibido")
            # Actualizar información en el label
            self.lbl_info.setText(self.lbl_info.text().replace("PENDIENTE", "RECIBIDO"))
            QMessageBox.information(self, "Éxito", "Pedido marcado como RECIBIDO correctamente.")
            # Emitir señal para refrescar la vista principal (opcional)
        except Exception as e:
            self.conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el estado:\n{str(e)}")

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
# DIÁLOGO PARA SELECCIONAR PRODUCTO (con autocompletado)
# ================================================================
class DialogoSeleccionProducto(QDialog):
    def __init__(self, productos_db, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.productos_db = productos_db if productos_db else []
        self.producto_seleccionado = None
        self._crear_interfaz()

    def _crear_interfaz(self):
        self.setFixedSize(420, 160)
        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(380, 130)
        self.card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #D1E2D9;
            }
        """)
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(15)
        sombra.setColor(QColor(0, 0, 0, 25))
        sombra.setOffset(0, 4)
        self.card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(20, 16, 20, 16)
        layout_card.setSpacing(10)

        lbl = QLabel("SELECCIONAR PRODUCTO")
        lbl.setFont(QFont("Montserrat", 12, QFont.Weight.Black))
        lbl.setStyleSheet("color: #17813D;")

        self.txt_producto = QLineEdit()
        self.txt_producto.setPlaceholderText("Escribe el nombre del producto...")
        self.txt_producto.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 8px;
                padding: 0 12px;
                font-family: 'Montserrat';
                font-size: 13px;
                height: 34px;
            }
            QLineEdit:focus {
                border: 2px solid #17813D;
                background-color: #FFFFFF;
            }
        """)

        # AUTOOMPLETADO: usar los nombres de productos
        if self.productos_db:
            nombres = []
            for p in self.productos_db:
                if isinstance(p, dict):
                    nombres.append(p.get('nombre_producto', ''))
                else:
                    nombres.append(p[1])
            modelo = QStringListModel(nombres)
            completer = QCompleter(modelo, self)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.txt_producto.setCompleter(completer)

        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(10)

        btn_cancelar = QPushButton("CANCELAR")
        btn_cancelar.setFixedHeight(32)
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #9CA3AF;
                border: none;
                font-family: 'Montserrat';
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { color: #DC2626; }
        """)
        btn_cancelar.clicked.connect(self.reject)

        btn_seleccionar = QPushButton("SELECCIONAR")
        btn_seleccionar.setFixedHeight(32)
        btn_seleccionar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_seleccionar.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        btn_seleccionar.clicked.connect(self._confirmar)

        layout_botones.addStretch()
        layout_botones.addWidget(btn_cancelar)
        layout_botones.addWidget(btn_seleccionar)

        layout_card.addWidget(lbl)
        layout_card.addWidget(self.txt_producto)
        layout_card.addLayout(layout_botones)

        layout_fondo.addWidget(self.card)

    def _confirmar(self):
        texto = self.txt_producto.text().strip()
        if not texto:
            QMessageBox.warning(self, "Atención", "Ingresa un nombre de producto.")
            return
        encontrado = None
        for p in self.productos_db:
            nombre = p[1] if not isinstance(p, dict) else p.get('nombre_producto', '')
            if nombre.lower() == texto.lower():
                encontrado = p
                break
        if not encontrado:
            for p in self.productos_db:
                nombre = p[1] if not isinstance(p, dict) else p.get('nombre_producto', '')
                if texto.lower() in nombre.lower():
                    encontrado = p
                    break
        if not encontrado:
            QMessageBox.warning(self, "Atención", "Producto no encontrado.")
            return
        self.producto_seleccionado = encontrado
        self.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(40, 55, 45, 95)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def showEvent(self, event):
        super().showEvent(event)
        screen = self.screen().geometry()
        self.setGeometry(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
            self.width(), self.height()
        )


# ================================================================
# DIÁLOGO PARA NUEVO RECIBO (con tabla editable)
# ================================================================
class DialogoNuevoRecibo(QDialog):
    def __init__(self, conexion=None, empleado_id=None, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.conexion = conexion
        self.empleado_id = empleado_id or 1
        self.resultado = None

        self.productos_agregados = []
        self.proveedores = []
        self.productos_db = []

        self._crear_interfaz()
        self._cargar_datos_iniciales()

    def _cargar_datos_iniciales(self):
        if not self.conexion:
            return
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT id_proveedor, nombre_empresa, nit FROM proveedores")
            rows_prov = cursor.fetchall()
            self.proveedores = []
            for row in rows_prov:
                if isinstance(row, dict):
                    self.proveedores.append((row['id_proveedor'], row['nombre_empresa'], row.get('nit')))
                else:
                    self.proveedores.append(row)

            cursor.execute("SELECT id_producto, nombre_producto, precio_venta_prod FROM productos WHERE id_estado = 1")
            rows_prod = cursor.fetchall()
            self.productos_db = []
            for row in rows_prod:
                if isinstance(row, dict):
                    self.productos_db.append((row['id_producto'], row['nombre_producto'], row['precio_venta_prod']))
                else:
                    self.productos_db.append(row)

            cursor.close()
            self._cargar_autocompletados()
        except Exception as e:
            print(f"Error cargando datos iniciales: {e}")
            traceback.print_exc()
            self.proveedores = []
            self.productos_db = []
            QMessageBox.warning(self, "Error de carga", f"No se pudieron cargar los datos:\n{str(e)}")

    def _cargar_autocompletados(self):
        if self.proveedores:
            nombres_prov = []
            for p in self.proveedores:
                if isinstance(p, dict):
                    nombres_prov.append(p.get('nombre_empresa', ''))
                else:
                    nombres_prov.append(p[1])
            modelo_prov = QStringListModel(nombres_prov)
            completer_prov = QCompleter(modelo_prov, self)
            completer_prov.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer_prov.setFilterMode(Qt.MatchFlag.MatchContains)
            self.txt_proveedor.setCompleter(completer_prov)

    def _crear_interfaz(self):
        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(1100, 820)
        self.card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 28px;
                border: 1px solid #D1E2D9;
            }
        """)
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(20)
        sombra.setColor(QColor(0, 0, 0, 20))
        sombra.setOffset(0, 5)
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
        lbl_titulo = QLabel("NUEVO RECIBO DE PROVEEDOR")
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

        layout_header.addWidget(lbl_titulo)
        layout_header.addStretch()
        layout_header.addWidget(btn_cerrar)
        layout_card.addLayout(layout_header)

        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        estilo_input = """
            QLineEdit, QComboBox, QDateEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 0 16px;
                color: #1F2937;
                font-family: 'Montserrat';
                font-size: 14px;
                height: 44px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #17813D;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
            }
        """

        self.txt_numero = QLineEdit()
        self.txt_numero.setPlaceholderText("Número de factura")
        self.txt_numero.setStyleSheet(estilo_input)

        self.txt_proveedor = QLineEdit()
        self.txt_proveedor.setPlaceholderText("Nombre del proveedor (autocompletado)")
        self.txt_proveedor.setStyleSheet(estilo_input)

        self.date_fecha = QDateEdit()
        self.date_fecha.setDate(QDate.currentDate())
        self.date_fecha.setCalendarPopup(True)
        self.date_fecha.setStyleSheet(estilo_input)

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
        self.btn_agregar_producto.clicked.connect(self._agregar_producto)

        form_layout.addRow("Número de factura:", self.txt_numero)
        form_layout.addRow("Proveedor:", self.txt_proveedor)
        form_layout.addRow("Fecha:", self.date_fecha)
        form_layout.addRow("", self.btn_agregar_producto)

        layout_card.addLayout(form_layout)

        # Tabla de productos
        lbl_productos = QLabel("PRODUCTOS A RECIBIR")
        lbl_productos.setFont(_f(12, QFont.Weight.Black))
        lbl_productos.setStyleSheet("color: #708077;")
        layout_card.addWidget(lbl_productos)

        self.tabla_productos = QTableWidget(0, 6)
        self.tabla_productos.setHorizontalHeaderLabels(["Producto", "Cantidad", "Peso (g)", "Precio Unit.", "Subtotal", "Acción"])
        self.tabla_productos.setShowGrid(False)
        self.tabla_productos.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_productos.verticalHeader().setVisible(False)
        self.tabla_productos.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.EditKeyPressed)
        self.tabla_productos.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D1E2D9;
                border-radius: 12px;
                background: transparent;
                font-family: 'Montserrat';
                font-size: 14px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #F0F2F0;
                padding: 8px 10px;
                color: #1F2937;
            }
            QTableWidget::item:selected {
                background: #E8F5EE;
                color: #17813D;
            }
            QTableWidget::item:editable {
                background-color: #FDFDFD;
            }
            QHeaderView::section {
                background: #F1F5F9;
                color: #64748B;
                font-weight: 800;
                font-size: 11px;
                border: none;
                padding: 8px 10px;
                font-family: 'Montserrat';
            }
        """)
        header = self.tabla_productos.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_productos.setColumnWidth(0, 250)
        self.tabla_productos.setColumnWidth(1, 80)
        self.tabla_productos.setColumnWidth(2, 100)
        self.tabla_productos.setColumnWidth(3, 120)
        self.tabla_productos.setColumnWidth(4, 130)
        self.tabla_productos.setColumnWidth(5, 80)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)

        self.tabla_productos.cellChanged.connect(self._on_cell_changed_nuevo)

        layout_card.addWidget(self.tabla_productos)

        # Total
        total_layout = QHBoxLayout()
        lbl_total_text = QLabel("TOTAL:")
        lbl_total_text.setFont(_f(14, QFont.Weight.Bold))
        lbl_total_text.setStyleSheet("color: #17813D;")
        self.lbl_total = QLabel("$0")
        self.lbl_total.setFont(_f(18, QFont.Weight.Black))
        self.lbl_total.setStyleSheet("color: #17813D;")
        total_layout.addWidget(lbl_total_text)
        total_layout.addWidget(self.lbl_total)
        total_layout.addStretch()
        layout_card.addLayout(total_layout)

        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(16)
        btn_cancelar = QPushButton("CANCELAR")
        btn_cancelar.setFont(_f(12, QFont.Weight.Bold))
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setStyleSheet("QPushButton { background: transparent; color: #9CA3AF; border: none; } QPushButton:hover { color: #DC2626; }")
        btn_cancelar.clicked.connect(self.reject)

        self.btn_guardar = QPushButton("GUARDAR RECIBO")
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

        layout_botones.addStretch()
        layout_botones.addWidget(btn_cancelar)
        layout_botones.addWidget(self.btn_guardar)
        layout_card.addLayout(layout_botones)

        layout_fondo.addWidget(self.card)

    def _agregar_producto(self):
        if not self.productos_db:
            QMessageBox.warning(self, "Sin productos", "No hay productos disponibles en el inventario.")
            return
        dlg = DialogoSeleccionProducto(self.productos_db, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            producto = dlg.producto_seleccionado
            if producto:
                if isinstance(producto, dict):
                    id_prod = producto['id_producto']
                    nombre = producto['nombre_producto']
                    precio = producto['precio_venta_prod']
                else:
                    id_prod, nombre, precio = producto
                cantidad = 1
                peso = 0.0
                subtotal = cantidad * float(precio)
                self._agregar_fila_producto(id_prod, nombre, precio, cantidad, peso, subtotal)

    def _agregar_fila_producto(self, id_prod, nombre, precio, cantidad, peso, subtotal):
        fila = self.tabla_productos.rowCount()
        self.tabla_productos.insertRow(fila)

        item_producto = QTableWidgetItem(nombre)
        item_producto.setFlags(item_producto.flags() & ~Qt.ItemIsEditable)
        self.tabla_productos.setItem(fila, 0, item_producto)

        item_cant = QTableWidgetItem(str(cantidad))
        self.tabla_productos.setItem(fila, 1, item_cant)

        item_peso = QTableWidgetItem(f"{peso:.2f}")
        self.tabla_productos.setItem(fila, 2, item_peso)

        item_precio = QTableWidgetItem(f"${int(precio):,}")
        item_precio.setFlags(item_precio.flags() & ~Qt.ItemIsEditable)
        self.tabla_productos.setItem(fila, 3, item_precio)

        item_subtotal = QTableWidgetItem(f"${int(subtotal):,}")
        item_subtotal.setFlags(item_subtotal.flags() & ~Qt.ItemIsEditable)
        self.tabla_productos.setItem(fila, 4, item_subtotal)

        btn_eliminar = QPushButton("✕")
        btn_eliminar.setFixedSize(28, 28)
        btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #FEE2E2;
                border: none;
                border-radius: 14px;
                color: #DC2626;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: #FFFFFF;
            }
        """)
        btn_eliminar.clicked.connect(lambda: self._eliminar_fila_nuevo(fila))
        self.tabla_productos.setCellWidget(fila, 5, btn_eliminar)

        self.tabla_productos.setRowHeight(fila, 40)

        self.productos_agregados.append({
            'id_producto': id_prod,
            'cantidad': cantidad,
            'peso': peso,
            'precio_unitario': precio,
            'subtotal': subtotal
        })
        self._actualizar_total_nuevo()

    def _on_cell_changed_nuevo(self, row, column):
        if column not in (1, 2):
            return
        if row >= len(self.productos_agregados):
            return

        item_cant = self.tabla_productos.item(row, 1)
        item_peso = self.tabla_productos.item(row, 2)
        if not item_cant or not item_peso:
            return

        try:
            cantidad = float(item_cant.text()) if item_cant.text() else 0
            peso = float(item_peso.text()) if item_peso.text() else 0
        except ValueError:
            return

        precio = self.productos_agregados[row]['precio_unitario']
        subtotal = cantidad * precio

        self.tabla_productos.item(row, 4).setText(f"${int(subtotal):,}")

        self.productos_agregados[row]['cantidad'] = cantidad
        self.productos_agregados[row]['peso'] = peso
        self.productos_agregados[row]['subtotal'] = subtotal

        self._actualizar_total_nuevo()

    def _eliminar_fila_nuevo(self, fila):
        if fila < len(self.productos_agregados):
            self.productos_agregados.pop(fila)
        self.tabla_productos.removeRow(fila)
        self._actualizar_total_nuevo()

    def _actualizar_total_nuevo(self):
        total = sum(p['subtotal'] for p in self.productos_agregados)
        self.lbl_total.setText(f"${int(total):,}")

    def _guardar(self):
        if not self.conexion:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return

        if not self.productos_agregados:
            QMessageBox.warning(self, "Atención", "Debes agregar al menos un producto.")
            return

        numero = self.txt_numero.text().strip()
        if not numero:
            QMessageBox.warning(self, "Atención", "Ingresa el número de factura.")
            return

        nombre_prov = self.txt_proveedor.text().strip()
        if not nombre_prov:
            QMessageBox.warning(self, "Atención", "Ingresa el nombre del proveedor.")
            return

        id_proveedor = None
        for p in self.proveedores:
            if isinstance(p, dict):
                if p.get('nombre_empresa', '').lower() == nombre_prov.lower():
                    id_proveedor = p['id_proveedor']
                    break
            else:
                if p[1].lower() == nombre_prov.lower():
                    id_proveedor = p[0]
                    break

        if not id_proveedor:
            respuesta = QMessageBox.question(
                self, "Proveedor no encontrado",
                f"El proveedor '{nombre_prov}' no existe. ¿Deseas crearlo?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.Yes:
                try:
                    cursor = self.conexion.cursor()
                    cursor.execute("INSERT INTO proveedores (nombre_empresa) VALUES (%s)", (nombre_prov,))
                    id_proveedor = cursor.lastrowid
                    self.conexion.commit()
                    cursor.close()
                    self.proveedores.append((id_proveedor, nombre_prov, None))
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo crear el proveedor: {str(e)}")
                    return
            else:
                return

        fecha = self.date_fecha.date().toPython()
        total = sum(p['subtotal'] for p in self.productos_agregados)

        try:
            cursor = self.conexion.cursor()
            sql_cab = """
                INSERT INTO factura_compra
                (numero_fac_compra, id_proveedor, id_empleado, fecha_fac_compra, valor_fac_compra, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_cab, (numero, id_proveedor, self.empleado_id, fecha, total, 'PENDIENTE'))
            id_fac_compra = cursor.lastrowid

            for prod in self.productos_agregados:
                sql_det = """
                    INSERT INTO detalle_factura_compra
                    (id_fac_compra, id_producto, cantidad, peso_gramos, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_det, (id_fac_compra, prod['id_producto'], prod['cantidad'],
                                         prod['peso'], prod['precio_unitario'], prod['subtotal']))

            self.conexion.commit()
            cursor.close()
            QMessageBox.information(self, "Éxito", f"Pedido N° {numero} creado correctamente (estado: PENDIENTE).")
            self.resultado = {"id": id_fac_compra, "numero": numero}
            self.accept()

        except Exception as e:
            self.conexion.rollback()
            error_msg = f"Error al guardar recibo: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
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
# VISTA PRINCIPAL RECIBO DE PROVEEDORES
# ================================================================
class ReciboProveedoresVista(QWidget):
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent)
        self.conexion = conexion
        self.filtro_estado = "todos"  # 'todos', 'pendiente', 'recibido'
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

        titulos_layout = QVBoxLayout()
        titulos_layout.setSpacing(2)
        lbl_titulo = QLabel("RECEPCIÓN DE PROVEEDORES")
        lbl_titulo.setFont(QFont("Montserrat", 22, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent;")

        lbl_subtitulo = QLabel("Gestione las entradas de mercancía y el inventario.")
        lbl_subtitulo.setFont(QFont("Montserrat", 11, QFont.Weight.Medium))
        lbl_subtitulo.setStyleSheet("color: #64748B; background: transparent;")

        titulos_layout.addWidget(lbl_titulo)
        titulos_layout.addWidget(lbl_subtitulo)

        header_layout.addLayout(titulos_layout)
        header_layout.addStretch()

        self.btn_nuevo = QPushButton("+ NUEVO PEDIDO")
        self.btn_nuevo.setFixedHeight(46)
        self.btn_nuevo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #008F39;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                font-family: 'Montserrat';
                font-size: 14px;
                font-weight: 900;
                padding: 0 30px;
            }
            QPushButton:hover {
                background-color: #1B4314;
            }
        """)
        self.btn_nuevo.clicked.connect(self.abrir_nuevo_recibo)
        header_layout.addWidget(self.btn_nuevo)

        layout_principal.addWidget(header_frame)

        # Tarjeta principal
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

        # Botones de filtro de estado
        self.btn_todos = QPushButton("TODOS")
        self.btn_recibidos = QPushButton("RECIBIDOS")
        self.btn_pendientes = QPushButton("PENDIENTES")

        for btn in (self.btn_todos, self.btn_recibidos, self.btn_pendientes):
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAFC;
                    color: #1B4314;
                    border: 2px solid #E2E8F0;
                    border-radius: 8px;
                    font-family: 'Montserrat';
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0 18px;
                }
                QPushButton:hover {
                    background-color: #E2E8F0;
                }
                QPushButton:checked {
                    background-color: #008F39;
                    color: #FFFFFF;
                    border: 2px solid #008F39;
                }
            """)

        self.grupo_estado = QButtonGroup(self)
        self.grupo_estado.addButton(self.btn_todos)
        self.grupo_estado.addButton(self.btn_recibidos)
        self.grupo_estado.addButton(self.btn_pendientes)
        self.btn_todos.setChecked(True)
        self.grupo_estado.buttonClicked.connect(self._cambiar_filtro_estado)

        filtros_layout.addWidget(self.btn_todos)
        filtros_layout.addWidget(self.btn_recibidos)
        filtros_layout.addWidget(self.btn_pendientes)

        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.VLine)
        separador.setFrameShadow(QFrame.Shadow.Sunken)
        separador.setStyleSheet("background-color: #D1D5DB; max-width: 2px;")
        filtros_layout.addWidget(separador)

        # Botón fecha
        self.btn_fecha = QPushButton("📅 Fecha")
        self.btn_fecha.setFixedHeight(36)
        self.btn_fecha.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fecha.setCheckable(True)
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
        self.btn_fecha.toggled.connect(self._toggle_fecha)

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

        filtros_layout.addWidget(self.btn_fecha)
        filtros_layout.addWidget(self.widget_fechas)

        # Buscador
        self.txt_buscador = QLineEdit()
        self.txt_buscador.setPlaceholderText("Buscar por número o proveedor...")
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

        filtros_layout.addWidget(self.txt_buscador, 1)

        layout_tarjeta.addLayout(filtros_layout)

        # Tabla principal
        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels([
            "N° Pedido", "Proveedor", "Fecha", "Total", "Estado", "Acciones"
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
        self.tabla.setColumnWidth(3, 130)
        self.tabla.setColumnWidth(4, 130)  # ANCHO AMPLIADO para que no se corte "RECIBIDO" o "PENDIENTE"
        self.tabla.setColumnWidth(5, 180)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)

        layout_tarjeta.addWidget(self.tabla)
        layout_principal.addWidget(tarjeta_principal)

    def _cambiar_filtro_estado(self, button):
        if button == self.btn_todos:
            self.filtro_estado = "todos"
        elif button == self.btn_recibidos:
            self.filtro_estado = "recibido"
        elif button == self.btn_pendientes:
            self.filtro_estado = "pendiente"
        self.filtrar_tabla()

    def _toggle_fecha(self, checked):
        self.widget_fechas.setVisible(checked)
        self.filtro_fecha_activo = checked
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
                SELECT fc.id_fac_compra, fc.numero_fac_compra, p.nombre_empresa,
                       fc.fecha_fac_compra, fc.valor_fac_compra, fc.estado
                FROM factura_compra fc
                LEFT JOIN proveedores p ON fc.id_proveedor = p.id_proveedor
                ORDER BY fc.fecha_fac_compra DESC
                LIMIT 50
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    if isinstance(row, dict):
                        id_fac = row.get('id_fac_compra')
                        numero = row.get('numero_fac_compra') or 'N/A'
                        proveedor = row.get('nombre_empresa') or 'Sin proveedor'
                        fecha = row.get('fecha_fac_compra')
                        total = row.get('valor_fac_compra') or 0
                        estado = row.get('estado') or 'pendiente'
                    else:
                        id_fac = row[0]
                        numero = row[1] or 'N/A'
                        proveedor = row[2] or 'Sin proveedor'
                        fecha = row[3]
                        total = row[4] or 0
                        estado = row[5] if len(row) > 5 else 'pendiente'

                    fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if hasattr(fecha, 'strftime') else str(fecha)
                    self.datos_tabla.append((
                        numero,
                        proveedor,
                        fecha_str,
                        f"${int(total):,}",
                        estado,
                        id_fac
                    ))
                cursor.close()
                self.llenar_tabla(self.datos_tabla)
            else:
                cursor.close()
                self.mostrar_mensaje_vacio("No hay pedidos registrados.")
        except Exception as e:
            error_msg = f"Error cargando recibos: {str(e)}"
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
            for col_idx in range(4):
                valor = row_data[col_idx]
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.tabla.setItem(fila_idx, col_idx, item)

            estado = row_data[4]
            estado_texto = estado.upper()
            item_estado = QTableWidgetItem(estado_texto)
            item_estado.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if estado == 'recibido':
                item_estado.setBackground(QColor("#D1FAE5"))
                item_estado.setForeground(QColor("#065F46"))
            else:
                item_estado.setBackground(QColor("#FEF3C7"))
                item_estado.setForeground(QColor("#92400E"))
            self.tabla.setItem(fila_idx, 4, item_estado)

            id_fac = row_data[5]
            contenedor = QWidget()
            layout_acciones = QHBoxLayout(contenedor)
            layout_acciones.setContentsMargins(0, 0, 0, 0)
            layout_acciones.setSpacing(4)

            btn_ver = QPushButton("Ver")
            btn_ver.setFixedSize(50, 28)
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
            btn_ver.clicked.connect(lambda checked, fid=id_fac: self.abrir_detalle(fid))
            layout_acciones.addWidget(btn_ver)

            if estado == 'pendiente':
                btn_recibir = QPushButton("Recibir")
                btn_recibir.setFixedSize(60, 28)
                btn_recibir.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_recibir.setStyleSheet("""
                    QPushButton {
                        background-color: #F59E0B;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 4px;
                        font-family: 'Montserrat';
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #D97706;
                    }
                """)
                btn_recibir.clicked.connect(lambda checked, fid=id_fac: self.marcar_recibido(fid))
                layout_acciones.addWidget(btn_recibir)

            layout_acciones.addStretch()
            self.tabla.setCellWidget(fila_idx, 5, contenedor)
            self.tabla.setRowHeight(fila_idx, 45)

    def marcar_recibido(self, id_fac):
        if not self.conexion:
            return
        try:
            cursor = self.conexion.cursor()
            cursor.execute("UPDATE factura_compra SET estado = 'RECIBIDO' WHERE id_fac_compra = %s", (id_fac,))
            self.conexion.commit()
            cursor.close()
            QMessageBox.information(self, "Éxito", "Pedido marcado como RECIBIDO.")
            self.cargar_datos()
        except Exception as e:
            self.conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el estado:\n{str(e)}")

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
            estado_fila = row_data[4]

            # Filtro por estado
            if self.filtro_estado != "todos":
                if estado_fila != self.filtro_estado:
                    mostrar = False

            # Filtro por texto
            if mostrar and texto_busqueda:
                coincide = False
                for col in range(3):
                    item = self.tabla.item(fila, col)
                    if item and texto_busqueda in item.text().lower():
                        coincide = True
                        break
                mostrar = coincide

            # Filtro por fecha
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

    def abrir_detalle(self, id_fac_compra):
        dlg = DialogoDetalleRecibo(id_fac_compra, self.conexion, self)
        dlg.exec()

    def abrir_nuevo_recibo(self):
        empleado_id = 1
        try:
            if hasattr(self.parent(), 'controlador'):
                ctrl = self.parent().controlador
                if hasattr(ctrl, 'usuario_actual') and ctrl.usuario_actual:
                    usuario = ctrl.usuario_actual
                    empleado_id = usuario.get('id_empleado', 1)
        except Exception as e:
            print(f"Error obteniendo empleado_id: {e}")
        dlg = DialogoNuevoRecibo(self.conexion, empleado_id, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.cargar_datos()