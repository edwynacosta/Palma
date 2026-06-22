import os
from datetime import datetime, timedelta
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLineEdit, QComboBox, QTabWidget,
    QGraphicsDropShadowEffect, QGridLayout, QGroupBox
)

class FinanzasVista(QWidget):
    def __init__(self, controlador, conexion):
        super().__init__()
        self.controlador = controlador
        self.conexion = conexion
        self.cargar_fuentes()
        self.construir_interfaz()

    def cargar_fuentes(self):
        ruta_vistas = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz = os.path.dirname(ruta_vistas)
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")
        for f in ("Montserrat-Regular.ttf", "Montserrat-Bold.ttf",
                  "Montserrat-Medium.ttf", "Montserrat-Black.ttf"):
            ruta = os.path.join(carpeta_fuentes, f)
            if os.path.exists(ruta):
                QFontDatabase.addApplicationFont(ruta)

    def construir_interfaz(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(12, 13, 12, 13)
        layout_principal.setSpacing(0)

        contenedor_blanco = QFrame()
        contenedor_blanco.setObjectName("ContenedorFinanzas")
        contenedor_blanco.setStyleSheet("""
            QFrame#ContenedorFinanzas {
                background-color: #FFFFFF;
                border: 1px solid #C8E6D4;
                border-radius: 18px;
            }
        """)
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(22)
        sombra.setColor(QColor(23, 129, 61, 30))
        sombra.setOffset(0, 4)
        contenedor_blanco.setGraphicsEffect(sombra)

        layout_contenedor = QVBoxLayout(contenedor_blanco)
        layout_contenedor.setContentsMargins(0, 0, 0, 0)
        layout_contenedor.setSpacing(0)

        # Barra superior
        barra_superior = QFrame()
        barra_superior.setFixedHeight(68)
        barra_superior.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border: none;
                border-bottom: 1px solid #EEF0F2;
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
            }
        """)
        layout_barra = QHBoxLayout(barra_superior)
        layout_barra.setContentsMargins(20, 0, 20, 0)

        btn_volver = QPushButton("← Volver")
        btn_volver.setFont(QFont("Montserrat", 10, QFont.Weight.Bold))
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #17813D;
                border: none;
            }
            QPushButton:hover { color: #0D6E36; }
        """)
        btn_volver.clicked.connect(lambda: self.controlador.cambiar_pantalla("AdminDashboard"))

        titulo = QLabel("FINANZAS")
        titulo.setFont(QFont("Montserrat", 20, QFont.Weight.Black))
        titulo.setStyleSheet("color: #17813D; background: transparent;")

        layout_barra.addWidget(btn_volver)
        layout_barra.addStretch()
        layout_barra.addWidget(titulo)
        layout_barra.addStretch()
        layout_contenedor.addWidget(barra_superior)

        # Pestañas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
                margin-top: 5px;
            }
            QTabBar::tab {
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 900;
                color: #9CA3AF;
                background: transparent;
                padding: 10px 20px;
                border: none;
                border-bottom: 3px solid transparent;
            }
            QTabBar::tab:selected {
                color: #17813D;
                border-bottom: 3px solid #17813D;
            }
            QTabBar::tab:hover {
                color: #17813D;
            }
        """)

        self.pagina_facturas = self.crear_pagina_facturas()
        self.tabs.addTab(self.pagina_facturas, "FACTURAS")

        self.pagina_indices = self.crear_pagina_indices()
        self.tabs.addTab(self.pagina_indices, "ÍNDICES")

        layout_contenedor.addWidget(self.tabs, 1)
        layout_principal.addWidget(contenedor_blanco)

    # ===================== FACTURAS =====================
    def crear_pagina_facturas(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        filtros = QHBoxLayout()
        filtros.setSpacing(15)

        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(["VENTAS", "COMPRAS"])
        self.cmb_tipo.setFixedHeight(40)
        self.cmb_tipo.setStyleSheet("""
            QComboBox {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 0 15px;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: bold;
                color: #1F2937;
            }
            QComboBox:focus { border: 2px solid #17813D; }
        """)
        self.cmb_tipo.currentIndexChanged.connect(self.cargar_facturas)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por número, cliente o proveedor...")
        self.txt_buscar.setFixedHeight(40)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 0 16px;
                font-family: 'Montserrat';
                font-size: 13px;
            }
            QLineEdit:focus { border: 2px solid #17813D; }
        """)
        self.txt_buscar.textChanged.connect(self.filtrar_facturas)

        self.btn_ver_detalle = QPushButton("VER DETALLE")
        self.btn_ver_detalle.setFixedHeight(40)
        self.btn_ver_detalle.setFont(QFont("Montserrat", 11, QFont.Weight.Black))
        self.btn_ver_detalle.setCursor(Qt.PointingHandCursor)
        self.btn_ver_detalle.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #228E49; }
            QPushButton:disabled {
                background-color: #A9DDBC;
                color: #E8F5EE;
            }
        """)
        self.btn_ver_detalle.setEnabled(False)
        self.btn_ver_detalle.clicked.connect(self.mostrar_detalle_factura)

        filtros.addWidget(self.cmb_tipo)
        filtros.addWidget(self.txt_buscar, 1)
        filtros.addWidget(self.btn_ver_detalle)
        layout.addLayout(filtros)

        self.tabla_facturas = QTableWidget()
        self.tabla_facturas.setColumnCount(6)
        self.tabla_facturas.setHorizontalHeaderLabels([
            "N°", "Fecha", "Cliente/Proveedor", "Total", "Estado", "Tipo"
        ])
        self.tabla_facturas.verticalHeader().setVisible(False)
        self.tabla_facturas.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_facturas.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_facturas.setShowGrid(False)
        self.tabla_facturas.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
                font-family: 'Montserrat';
                font-size: 12px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #F0F2F0;
                padding: 8px 4px;
            }
            QTableWidget::item:selected {
                background: #E8F5EE;
                color: #17813D;
            }
            QHeaderView::section {
                background: transparent;
                color: #86B896;
                font-weight: 800;
                font-size: 10px;
                border: none;
                border-bottom: 1px solid #EEF0F2;
                padding: 10px 4px;
            }
        """)
        self.tabla_facturas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_facturas.setColumnWidth(0, 80)
        self.tabla_facturas.setColumnWidth(1, 120)
        self.tabla_facturas.setColumnWidth(2, 200)
        self.tabla_facturas.setColumnWidth(3, 100)
        self.tabla_facturas.setColumnWidth(4, 100)
        self.tabla_facturas.setColumnWidth(5, 80)
        self.tabla_facturas.itemSelectionChanged.connect(
            lambda: self.btn_ver_detalle.setEnabled(self.tabla_facturas.currentRow() >= 0)
        )

        layout.addWidget(self.tabla_facturas, 1)

        self.cargar_facturas()
        return widget

    def cargar_facturas(self):
        tipo = self.cmb_tipo.currentText()
        if tipo == "VENTAS":
            self.cargar_facturas_ventas()
        else:
            self.cargar_facturas_compras()

    def cargar_facturas_ventas(self):
        query = """
            SELECT f.id_factura, f.fecha_fac, c.nombre_cliente, f.total_fac,
                   CASE WHEN f.total_fac > 0 THEN 'Pagada' ELSE 'Pendiente' END AS estado
            FROM facturas f
            LEFT JOIN clientes c ON f.id_cliente = c.id_cliente
            ORDER BY f.fecha_fac DESC
        """
        datos = self.ejecutar_consulta(query)
        if datos:
            self.llenar_tabla_facturas(datos, "VENTA")
        else:
            # Mock
            mock = [
                (1, datetime.now(), "Supermercado El Éxito", 1250000, "Pagada"),
                (2, datetime.now() - timedelta(days=1), "Distribuidora La 14", 850000, "Pendiente"),
                (3, datetime.now() - timedelta(days=2), "Almacenes Tía", 2100000, "Pagada"),
            ]
            self.llenar_tabla_facturas(mock, "VENTA")

    def cargar_facturas_compras(self):
        query = """
            SELECT fc.id_fac_compra, fc.fecha_fac_compra, p.nombre_empresa,
                   fc.valor_fac_compra,
                   CASE WHEN fc.valor_fac_compra > 0 THEN 'Pagada' ELSE 'Pendiente' END AS estado
            FROM factura_compra fc
            LEFT JOIN proveedores p ON fc.id_proveedor = p.id_proveedor
            ORDER BY fc.fecha_fac_compra DESC
        """
        datos = self.ejecutar_consulta(query)
        if datos:
            self.llenar_tabla_facturas(datos, "COMPRA")
        else:
            mock = [
                (1, datetime.now(), "DistriHortalizas La Granja", 850000, "Pagada"),
                (2, datetime.now() - timedelta(days=3), "Lácteos del Valle Ltda", 640000, "Pendiente"),
            ]
            self.llenar_tabla_facturas(mock, "COMPRA")

    def ejecutar_consulta(self, query, params=None):
        """Ejecuta consulta y devuelve siempre una lista de tuplas."""
        if not self.conexion:
            return []
        try:
            cursor = self.conexion.cursor()
            cursor.execute(query, params or ())
            resultados = cursor.fetchall()
            cursor.close()
            # Normalizar: convertir cada fila a tupla si es dict
            if resultados and isinstance(resultados[0], dict):
                # Convertir todos los dict a tuplas en el orden de las columnas
                # Obtenemos los nombres de las columnas del cursor
                columnas = [desc[0] for desc in cursor.description]
                resultados = [tuple(fila.get(col) for col in columnas) for fila in resultados]
            return resultados
        except Exception as e:
            print(f"Error en consulta: {e}")
            return []

    def llenar_tabla_facturas(self, datos, tipo):
        self.tabla_facturas.setRowCount(0)
        self.datos_facturas = datos
        self.tipo_actual = tipo

        for fila, registro in enumerate(datos):
            self.tabla_facturas.insertRow(fila)
            # Ahora registro siempre es tupla: (id, fecha, cliente, total, estado)
            id_fact = registro[0]
            fecha = registro[1]
            cliente = registro[2] or "N/A"
            total = registro[3] or 0
            estado = registro[4] or "Pendiente"

            fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if hasattr(fecha, 'strftime') else str(fecha)
            total_str = f"${float(total):,.0f}" if total else "$0"

            self.tabla_facturas.setItem(fila, 0, QTableWidgetItem(str(id_fact)))
            self.tabla_facturas.setItem(fila, 1, QTableWidgetItem(fecha_str))
            self.tabla_facturas.setItem(fila, 2, QTableWidgetItem(cliente))
            self.tabla_facturas.setItem(fila, 3, QTableWidgetItem(total_str))
            self.tabla_facturas.setItem(fila, 4, QTableWidgetItem(estado))
            self.tabla_facturas.setItem(fila, 5, QTableWidgetItem(tipo))

        self.filtrar_facturas()

    def filtrar_facturas(self):
        texto = self.txt_buscar.text().strip().lower()
        for fila in range(self.tabla_facturas.rowCount()):
            coincide = False
            for col in range(5):
                item = self.tabla_facturas.item(fila, col)
                if item and texto in item.text().lower():
                    coincide = True
                    break
            self.tabla_facturas.setRowHidden(fila, not coincide)

    def mostrar_detalle_factura(self):
        fila = self.tabla_facturas.currentRow()
        if fila < 0:
            return
        id_item = self.tabla_facturas.item(fila, 0).text()
        tipo = self.tabla_facturas.item(fila, 5).text()
        if tipo == "VENTA":
            self.mostrar_detalle_venta(int(id_item))
        else:
            self.mostrar_detalle_compra(int(id_item))

    def mostrar_detalle_venta(self, id_factura):
        query_enc = """
            SELECT f.id_factura, f.fecha_fac, c.nombre_cliente, c.documento_identidad,
                   c.telefono, c.email, f.total_fac
            FROM facturas f
            LEFT JOIN clientes c ON f.id_cliente = c.id_cliente
            WHERE f.id_factura = %s
        """
        enc = self.ejecutar_consulta(query_enc, (id_factura,))
        if not enc:
            QMessageBox.warning(self, "Detalle", "No se encontró la factura.")
            return
        row = enc[0]  # tupla
        id_fact, fecha, cliente, documento, telefono, email, total = row

        query_det = """
            SELECT p.nombre_producto, df.cantidad_detfac, df.precio_unitario_detfac, df.subtotal_detfac
            FROM detalle_factura df
            JOIN productos p ON df.id_producto = p.id_producto
            WHERE df.id_factura = %s
        """
        detalles = self.ejecutar_consulta(query_det, (id_factura,))
        self.mostrar_dialogo_detalle({
            'id': id_fact,
            'fecha': fecha,
            'cliente': cliente,
            'documento': documento or "N/A",
            'telefono': telefono or "N/A",
            'email': email or "N/A",
            'total': total or 0
        }, detalles, "VENTA")

    def mostrar_detalle_compra(self, id_fac_compra):
        query_enc = """
            SELECT fc.id_fac_compra, fc.fecha_fac_compra, p.nombre_empresa,
                   p.nit, p.telefono_principal, p.email, fc.valor_fac_compra
            FROM factura_compra fc
            LEFT JOIN proveedores p ON fc.id_proveedor = p.id_proveedor
            WHERE fc.id_fac_compra = %s
        """
        enc = self.ejecutar_consulta(query_enc, (id_fac_compra,))
        if not enc:
            QMessageBox.warning(self, "Detalle", "No se encontró la factura de compra.")
            return
        row = enc[0]
        id_fact, fecha, proveedor, nit, telefono, email, total = row

        query_det = """
            SELECT prod.nombre_producto, m.cantidad_movimiento
            FROM movimientos m
            JOIN inventarios i ON m.id_inventario = i.id_inventario
            JOIN productos prod ON i.id_producto = prod.id_producto
            WHERE m.id_fac_compra = %s
        """
        detalles = self.ejecutar_consulta(query_det, (id_fac_compra,))
        self.mostrar_dialogo_detalle({
            'id': id_fact,
            'fecha': fecha,
            'cliente': proveedor,
            'documento': nit or "N/A",
            'telefono': telefono or "N/A",
            'email': email or "N/A",
            'total': total or 0
        }, detalles, "COMPRA")

    def mostrar_dialogo_detalle(self, encabezado, detalles, tipo):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Detalle de {tipo}")
        dlg.setModal(True)
        dlg.setMinimumSize(550, 400)
        dlg.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(dlg)

        info = QLabel()
        if tipo == "VENTA":
            info.setText(f"""
                <b>Factura N°:</b> {encabezado['id']}<br>
                <b>Fecha:</b> {encabezado['fecha'].strftime('%d/%m/%Y %H:%M') if hasattr(encabezado['fecha'], 'strftime') else encabezado['fecha']}<br>
                <b>Cliente:</b> {encabezado['cliente']}<br>
                <b>Documento:</b> {encabezado['documento']}<br>
                <b>Teléfono:</b> {encabezado['telefono']}<br>
                <b>Email:</b> {encabezado['email']}<br>
                <b>Total:</b> ${float(encabezado['total']):,.0f}
            """)
        else:
            info.setText(f"""
                <b>Factura Compra N°:</b> {encabezado['id']}<br>
                <b>Fecha:</b> {encabezado['fecha'].strftime('%d/%m/%Y %H:%M') if hasattr(encabezado['fecha'], 'strftime') else encabezado['fecha']}<br>
                <b>Proveedor:</b> {encabezado['cliente']}<br>
                <b>NIT:</b> {encabezado['documento']}<br>
                <b>Teléfono:</b> {encabezado['telefono']}<br>
                <b>Email:</b> {encabezado['email']}<br>
                <b>Total:</b> ${float(encabezado['total']):,.0f}
            """)
        info.setFont(QFont("Montserrat", 11))
        info.setStyleSheet("background: #F8FAF9; border-radius: 10px; padding: 15px;")
        layout.addWidget(info)

        tabla_det = QTableWidget()
        if tipo == "VENTA":
            tabla_det.setColumnCount(4)
            tabla_det.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit.", "Subtotal"])
            for fila, det in enumerate(detalles):
                # det es tupla: (nombre, cantidad, precio_unit, subtotal)
                nombre, cant, precio, subtotal = det
                tabla_det.insertRow(fila)
                tabla_det.setItem(fila, 0, QTableWidgetItem(nombre))
                tabla_det.setItem(fila, 1, QTableWidgetItem(str(cant)))
                tabla_det.setItem(fila, 2, QTableWidgetItem(f"${float(precio):,.0f}"))
                tabla_det.setItem(fila, 3, QTableWidgetItem(f"${float(subtotal):,.0f}"))
        else:
            tabla_det.setColumnCount(2)
            tabla_det.setHorizontalHeaderLabels(["Producto", "Cantidad"])
            for fila, det in enumerate(detalles):
                nombre, cant = det
                tabla_det.insertRow(fila)
                tabla_det.setItem(fila, 0, QTableWidgetItem(nombre))
                tabla_det.setItem(fila, 1, QTableWidgetItem(str(cant)))

        tabla_det.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla_det.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla_det.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D1E2D9;
                border-radius: 10px;
                font-family: 'Montserrat';
                font-size: 11px;
            }
        """)
        layout.addWidget(tabla_det)

        btn_cerrar = QPushButton("CERRAR")
        btn_cerrar.setFixedHeight(40)
        btn_cerrar.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover { background: #228E49; }
        """)
        btn_cerrar.clicked.connect(dlg.accept)
        layout.addWidget(btn_cerrar)

        dlg.exec()

    # ===================== ÍNDICES =====================
    def crear_pagina_indices(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        grid = QGridLayout()
        grid.setSpacing(20)

        top5 = self.crear_tarjeta_top5()
        grid.addWidget(top5, 0, 0)

        bottom5 = self.crear_tarjeta_bottom5()
        grid.addWidget(bottom5, 0, 1)

        ventas = self.crear_tarjeta_ventas_periodos()
        grid.addWidget(ventas, 1, 0, 1, 2)

        historico = self.crear_tarjeta_historico_mensual()
        grid.addWidget(historico, 2, 0, 1, 2)

        dias = self.crear_tarjeta_dias_semana()
        grid.addWidget(dias, 3, 0, 1, 2)

        layout.addLayout(grid)
        layout.addStretch()

        self.actualizar_indices()
        return widget

    def crear_tarjeta_top5(self):
        group = QGroupBox("TOP 5 PRODUCTOS MÁS VENDIDOS")
        group.setStyleSheet(self.estilo_grupo())
        layout = QVBoxLayout(group)
        self.tabla_top5 = QTableWidget()
        self.tabla_top5.setColumnCount(2)
        self.tabla_top5.setHorizontalHeaderLabels(["Producto", "Cantidad"])
        self.tabla_top5.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_top5.setShowGrid(False)
        self.tabla_top5.setStyleSheet(self.estilo_tabla_indice())
        self.tabla_top5.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_top5)
        return group

    def crear_tarjeta_bottom5(self):
        group = QGroupBox("5 PRODUCTOS MENOS VENDIDOS")
        group.setStyleSheet(self.estilo_grupo())
        layout = QVBoxLayout(group)
        self.tabla_bottom5 = QTableWidget()
        self.tabla_bottom5.setColumnCount(2)
        self.tabla_bottom5.setHorizontalHeaderLabels(["Producto", "Cantidad"])
        self.tabla_bottom5.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_bottom5.setShowGrid(False)
        self.tabla_bottom5.setStyleSheet(self.estilo_tabla_indice())
        self.tabla_bottom5.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_bottom5)
        return group

    def crear_tarjeta_ventas_periodos(self):
        group = QGroupBox("VENTAS POR PERÍODO")
        group.setStyleSheet(self.estilo_grupo())
        layout = QVBoxLayout(group)
        self.lbl_ventas_periodos = QLabel()
        self.lbl_ventas_periodos.setFont(QFont("Montserrat", 12))
        self.lbl_ventas_periodos.setStyleSheet("padding: 10px; background: #F8FAF9; border-radius: 10px;")
        layout.addWidget(self.lbl_ventas_periodos)

        btn_recargar = QPushButton("RECARGAR ÍNDICES")
        btn_recargar.setFont(QFont("Montserrat", 10, QFont.Weight.Bold))
        btn_recargar.setCursor(Qt.PointingHandCursor)
        btn_recargar.setStyleSheet("""
            QPushButton {
                background: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover { background: #228E49; }
        """)
        btn_recargar.clicked.connect(self.actualizar_indices)
        layout.addWidget(btn_recargar)
        return group

    def crear_tarjeta_historico_mensual(self):
        group = QGroupBox("VENTAS HISTÓRICAS POR MES")
        group.setStyleSheet(self.estilo_grupo())
        layout = QVBoxLayout(group)
        self.tabla_historico = QTableWidget()
        self.tabla_historico.setColumnCount(2)
        self.tabla_historico.setHorizontalHeaderLabels(["Mes", "Total Vendido"])
        self.tabla_historico.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_historico.setShowGrid(False)
        self.tabla_historico.setStyleSheet(self.estilo_tabla_indice())
        self.tabla_historico.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_historico)
        return group

    def crear_tarjeta_dias_semana(self):
        group = QGroupBox("VENTAS POR DÍA DE LA SEMANA")
        group.setStyleSheet(self.estilo_grupo())
        layout = QVBoxLayout(group)
        self.tabla_dias = QTableWidget()
        self.tabla_dias.setColumnCount(3)
        self.tabla_dias.setHorizontalHeaderLabels(["Día", "Total Vendido", "Promedio"])
        self.tabla_dias.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_dias.setShowGrid(False)
        self.tabla_dias.setStyleSheet(self.estilo_tabla_indice())
        self.tabla_dias.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_dias)
        return group

    def estilo_grupo(self):
        return """
            QGroupBox {
                background-color: #FFFFFF;
                border: 2px solid #D1E2D9;
                border-radius: 16px;
                margin-top: 16px;
                font-family: 'Montserrat';
                font-weight: 900;
                font-size: 13px;
                color: #17813D;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background: #FFFFFF;
            }
        """

    def estilo_tabla_indice(self):
        return """
            QTableWidget {
                background: transparent;
                border: none;
                font-family: 'Montserrat';
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px 4px;
                border-bottom: 1px solid #F0F2F0;
            }
            QTableWidget::item:selected {
                background: #E8F5EE;
                color: #17813D;
            }
            QHeaderView::section {
                background: transparent;
                color: #86B896;
                font-weight: 800;
                font-size: 10px;
                border: none;
                border-bottom: 1px solid #EEF0F2;
                padding: 8px 4px;
            }
        """

    def actualizar_indices(self):
        self.cargar_top5()
        self.cargar_bottom5()
        self.cargar_ventas_periodos()
        self.cargar_historico_mensual()
        self.cargar_dias_semana()

    def cargar_top5(self):
        query = """
            SELECT p.nombre_producto, SUM(df.cantidad_detfac) AS total
            FROM detalle_factura df
            JOIN productos p ON df.id_producto = p.id_producto
            GROUP BY p.id_producto
            ORDER BY total DESC
            LIMIT 5
        """
        datos = self.ejecutar_consulta(query)
        self.tabla_top5.setRowCount(0)
        if datos:
            for fila, (nombre, total) in enumerate(datos):
                self.tabla_top5.insertRow(fila)
                self.tabla_top5.setItem(fila, 0, QTableWidgetItem(nombre))
                self.tabla_top5.setItem(fila, 1, QTableWidgetItem(str(total)))
        else:
            mock = [("Manzana Roja", 150), ("Leche Entera", 120), ("Arroz Blanco", 90)]
            for fila, (nombre, total) in enumerate(mock):
                self.tabla_top5.insertRow(fila)
                self.tabla_top5.setItem(fila, 0, QTableWidgetItem(nombre))
                self.tabla_top5.setItem(fila, 1, QTableWidgetItem(str(total)))

    def cargar_bottom5(self):
        query = """
            SELECT p.nombre_producto, COALESCE(SUM(df.cantidad_detfac), 0) AS total
            FROM productos p
            LEFT JOIN detalle_factura df ON p.id_producto = df.id_producto
            GROUP BY p.id_producto
            ORDER BY total ASC
            LIMIT 5
        """
        datos = self.ejecutar_consulta(query)
        self.tabla_bottom5.setRowCount(0)
        if datos:
            for fila, (nombre, total) in enumerate(datos):
                self.tabla_bottom5.insertRow(fila)
                self.tabla_bottom5.setItem(fila, 0, QTableWidgetItem(nombre))
                self.tabla_bottom5.setItem(fila, 1, QTableWidgetItem(str(total)))
        else:
            mock = [("Zanahoria", 5), ("Yogur Fresa", 3), ("Shampoo", 2)]
            for fila, (nombre, total) in enumerate(mock):
                self.tabla_bottom5.insertRow(fila)
                self.tabla_bottom5.setItem(fila, 0, QTableWidgetItem(nombre))
                self.tabla_bottom5.setItem(fila, 1, QTableWidgetItem(str(total)))

    def cargar_ventas_periodos(self):
        hoy = datetime.now().date()
        semana = hoy - timedelta(days=7)
        query_sem = """
            SELECT COALESCE(SUM(total_fac), 0) FROM facturas
            WHERE fecha_fac >= %s AND fecha_fac <= %s
        """
        resultado = self.ejecutar_consulta(query_sem, (semana, hoy))
        total_sem = resultado[0][0] if resultado else 0

        mes = hoy - timedelta(days=30)
        query_mes = """
            SELECT COALESCE(SUM(total_fac), 0) FROM facturas
            WHERE fecha_fac >= %s AND fecha_fac <= %s
        """
        resultado = self.ejecutar_consulta(query_mes, (mes, hoy))
        total_mes = resultado[0][0] if resultado else 0

        anio = hoy - timedelta(days=365)
        query_anio = """
            SELECT COALESCE(SUM(total_fac), 0) FROM facturas
            WHERE fecha_fac >= %s AND fecha_fac <= %s
        """
        resultado = self.ejecutar_consulta(query_anio, (anio, hoy))
        total_anio = resultado[0][0] if resultado else 0

        self.lbl_ventas_periodos.setText(f"""
            <b>ÚLTIMA SEMANA:</b> ${total_sem:,.0f}<br>
            <b>ÚLTIMO MES:</b> ${total_mes:,.0f}<br>
            <b>ÚLTIMO AÑO:</b> ${total_anio:,.0f}
        """)

    def cargar_historico_mensual(self):
        query = """
            SELECT DATE_FORMAT(fecha_fac, '%Y-%m') AS mes, COALESCE(SUM(total_fac), 0) AS total
            FROM facturas
            GROUP BY mes
            ORDER BY mes ASC
        """
        datos = self.ejecutar_consulta(query)
        self.tabla_historico.setRowCount(0)
        if datos:
            for fila, (mes, total) in enumerate(datos):
                self.tabla_historico.insertRow(fila)
                self.tabla_historico.setItem(fila, 0, QTableWidgetItem(mes))
                self.tabla_historico.setItem(fila, 1, QTableWidgetItem(f"${total:,.0f}"))
        else:
            mock = [("2026-01", 1500000), ("2026-02", 2000000), ("2026-03", 1800000)]
            for fila, (mes, total) in enumerate(mock):
                self.tabla_historico.insertRow(fila)
                self.tabla_historico.setItem(fila, 0, QTableWidgetItem(mes))
                self.tabla_historico.setItem(fila, 1, QTableWidgetItem(f"${total:,.0f}"))

    def cargar_dias_semana(self):
        query = """
            SELECT DAYOFWEEK(fecha_fac) AS dia, COALESCE(SUM(total_fac), 0) AS total,
                   COUNT(*) AS num_facturas
            FROM facturas
            GROUP BY dia
            ORDER BY dia
        """
        datos = self.ejecutar_consulta(query)
        dias_nombres = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
        self.tabla_dias.setRowCount(0)
        if datos:
            for fila, (dia_num, total, num) in enumerate(datos):
                nombre = dias_nombres[dia_num-1] if 1 <= dia_num <= 7 else "Desconocido"
                self.tabla_dias.insertRow(fila)
                self.tabla_dias.setItem(fila, 0, QTableWidgetItem(nombre))
                self.tabla_dias.setItem(fila, 1, QTableWidgetItem(f"${total:,.0f}"))
                promedio = total / num if num > 0 else 0
                self.tabla_dias.setItem(fila, 2, QTableWidgetItem(f"${promedio:,.0f}"))
        else:
            mock = [(2, 1500000, 5), (3, 1200000, 4), (4, 800000, 3)]
            for fila, (dia_num, total, num) in enumerate(mock):
                nombre = dias_nombres[dia_num-1] if 1 <= dia_num <= 7 else "Desconocido"
                self.tabla_dias.insertRow(fila)
                self.tabla_dias.setItem(fila, 0, QTableWidgetItem(nombre))
                self.tabla_dias.setItem(fila, 1, QTableWidgetItem(f"${total:,.0f}"))
                promedio = total / num if num > 0 else 0
                self.tabla_dias.setItem(fila, 2, QTableWidgetItem(f"${promedio:,.0f}"))