import os
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QDoubleValidator, QFont, QFontDatabase, QIntValidator, QAction
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QMenu,
    QSizePolicy,
    QGraphicsDropShadowEffect
)

from modelos.inventario_modelo import InventarioModelo


class InventarioVista(QWidget):
    def __init__(self, controlador_flujo, conexion):
        super().__init__()
        self.controlador = controlador_flujo
        self.modelo = InventarioModelo(conexion)
        self.productos = []
        self.sugerencias_busqueda = []
        self.producto_actual = None
        self.id_inventario_actual = None
        self.filtro_rapido = "TODOS"  # TODOS, STOCK_BAJO, VENCIDOS
        self.COLOR_FONDO = "#F0F4F2"

        self.setObjectName("InventarioRoot")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._cargar_fuentes()
        self._construir_interfaz()
        self._aplicar_estilos()
        self.cargar_catalogos()
        self.cargar_sugerencias_busqueda()
        self.cargar_productos()

    def _cargar_fuentes(self):
        ruta_vistas = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz = os.path.dirname(ruta_vistas)
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")
        for fuente in ("Montserrat-Regular.ttf", "Montserrat-Bold.ttf", "Montserrat-Medium.ttf", "Montserrat-Black.ttf"):
            ruta = os.path.join(carpeta_fuentes, fuente)
            if os.path.exists(ruta):
                QFontDatabase.addApplicationFont(ruta)

    def _construir_interfaz(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(12, 13, 12, 13)
        layout_principal.setSpacing(0)

        # ── CONTENEDOR PRINCIPAL BLANCO ──
        contenedor_blanco = QFrame()
        contenedor_blanco.setObjectName("ContenedorInventario")
        contenedor_blanco.setStyleSheet("""
            QFrame#ContenedorInventario {
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

        # ── BARRA SUPERIOR ──
        navbar = QFrame()
        navbar.setObjectName("NavbarInventario")
        navbar.setFixedHeight(68)
        navbar.setStyleSheet("""
            QFrame#NavbarInventario { 
                background: #FFFFFF; border: none; border-bottom: 1px solid #EEF0F2; 
                border-top-left-radius: 18px; border-top-right-radius: 18px; 
            }
        """)
        layout_navbar = QHBoxLayout(navbar)
        layout_navbar.setContentsMargins(0, 0, 20, 0)
        layout_navbar.setSpacing(0)

        # Título a la izquierda
        titulo_layout = QHBoxLayout()
        titulo_layout.setContentsMargins(20, 0, 0, 0)
        lbl_titulo = QLabel("INVENTARIO")
        lbl_titulo.setFont(QFont("Montserrat", 20, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent;")
        titulo_layout.addWidget(lbl_titulo)

        # Botón Recargar (opcional)
        btn_recargar = QPushButton("↻")
        btn_recargar.setFixedSize(36, 36)
        btn_recargar.setFont(QFont("Montserrat", 14, QFont.Weight.Bold))
        btn_recargar.setCursor(Qt.PointingHandCursor)
        btn_recargar.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #9CA3AF;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #F1F5F9;
                color: #17813D;
            }
        """)
        btn_recargar.clicked.connect(self.cargar_productos)
        titulo_layout.addWidget(btn_recargar)

        # ── Panel de usuario ──
        layout_meta = QVBoxLayout()
        layout_meta.setSpacing(0)
        layout_meta.setContentsMargins(0, 0, 0, 0)
        layout_meta.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        self.lbl_nombre_cajero = QLabel("Usuario")
        self.lbl_nombre_cajero.setFont(QFont("Montserrat", 11, QFont.Weight.Black))
        self.lbl_nombre_cajero.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_nombre_cajero.setStyleSheet("color:#17813D; background:transparent;")

        self.lbl_rol_caja = QLabel("ROL")
        self.lbl_rol_caja.setFont(QFont("Montserrat", 8, QFont.Weight.Bold))
        self.lbl_rol_caja.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_rol_caja.setStyleSheet("color:#9CA3AF; background:transparent;")

        layout_meta.addWidget(self.lbl_nombre_cajero)
        layout_meta.addWidget(self.lbl_rol_caja)

        self.lbl_avatar = QLabel("US")
        self.lbl_avatar.setFixedSize(36, 36)
        self.lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_avatar.setFont(QFont("Montserrat", 11, QFont.Weight.Black))
        self.lbl_avatar.setStyleSheet("QLabel { background:#E9F7EF; border:1px solid #A9DDBC; border-radius:18px; color:#17813D; }")

        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.setFixedSize(105, 34)
        btn_logout.setFont(QFont("Montserrat", 8, QFont.Weight.Bold))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("QPushButton { background:#FFFFFF; color:#DC2626; border:1px solid #FECACA; border-radius:9px; } QPushButton:hover { background:#DC2626; color:#FFFFFF; border-color:#DC2626; }")
        btn_logout.clicked.connect(self.cerrar_sesion)

        btn_salir = QPushButton("✕")
        btn_salir.setFixedSize(36, 36)
        btn_salir.setFont(QFont("Montserrat", 12, QFont.Weight.Black))
        btn_salir.setCursor(Qt.PointingHandCursor)
        btn_salir.setStyleSheet("QPushButton { background:#FFFFFF; color:#9CA3AF; border:1px solid #E5E7EB; border-radius:10px; } QPushButton:hover { background:#DC2626; color:#FFFFFF; border-color:#DC2626; }")
        btn_salir.clicked.connect(self.volver_dashboard)

        layout_usuario = QHBoxLayout()
        layout_usuario.setSpacing(12)
        layout_usuario.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout_usuario.addLayout(layout_meta)
        layout_usuario.addWidget(self.lbl_avatar)
        layout_usuario.addWidget(btn_logout)
        layout_usuario.addWidget(btn_salir)

        layout_navbar.addLayout(titulo_layout)
        layout_navbar.addStretch()
        layout_navbar.addLayout(layout_usuario)
        layout_contenedor.addWidget(navbar)

        # ── CONTENIDO ──
        contenido = QWidget()
        layout_contenido = QVBoxLayout(contenido)
        layout_contenido.setContentsMargins(20, 16, 20, 16)
        layout_contenido.setSpacing(16)

        # ── FILA DE BOTONES DE FILTRO RÁPIDO ──
        botones_filtro = QHBoxLayout()
        botones_filtro.setSpacing(10)

        self.btn_todos = QPushButton("PRODUCTOS")
        self.btn_stock_bajo = QPushButton("STOCK BAJO")
        self.btn_vencidos = QPushButton("VENCIDOS")
        self.lbl_valor = QLabel("VALOR INVENTARIO: $0")

        for btn in (self.btn_todos, self.btn_stock_bajo, self.btn_vencidos):
            btn.setFixedHeight(36)
            btn.setFont(QFont("Montserrat", 10, QFont.Weight.Black))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAF9;
                    border: 2px solid #D1E2D9;
                    border-radius: 10px;
                    color: #1F2937;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #FFFFFF;
                    border: 2px solid #17813D;
                }
                QPushButton:checked {
                    background-color: #E8F5EE;
                    border: 2px solid #17813D;
                    color: #17813D;
                }
            """)
            btn.setCheckable(True)

        self.btn_todos.setChecked(True)
        self.btn_todos.clicked.connect(lambda: self.aplicar_filtro_rapido("TODOS"))
        self.btn_stock_bajo.clicked.connect(lambda: self.aplicar_filtro_rapido("STOCK_BAJO"))
        self.btn_vencidos.clicked.connect(lambda: self.aplicar_filtro_rapido("VENCIDOS"))

        self.lbl_valor.setFont(QFont("Montserrat", 10, QFont.Weight.Bold))
        self.lbl_valor.setStyleSheet("color: #17813D; background: transparent; padding: 0 10px;")

        botones_filtro.addWidget(self.btn_todos)
        botones_filtro.addWidget(self.btn_stock_bajo)
        botones_filtro.addWidget(self.btn_vencidos)
        botones_filtro.addStretch()
        botones_filtro.addWidget(self.lbl_valor)
        layout_contenido.addLayout(botones_filtro)

        # ── FILTROS (búsqueda, categoría, estado) ──
        filtros = QFrame()
        filtros.setObjectName("PanelFiltros")
        filtros.setStyleSheet("QFrame#PanelFiltros { background: #F8FAF9; border-radius: 12px; border: 1px solid #E2E8F0; }")
        filtros_layout = QHBoxLayout(filtros)
        filtros_layout.setContentsMargins(16, 8, 16, 8)
        filtros_layout.setSpacing(12)

        self.txt_busqueda = QLineEdit()
        self.txt_busqueda.setPlaceholderText("Buscar por producto, marca o proveedor")
        self.txt_busqueda.setFixedHeight(38)
        self.txt_busqueda.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #D1E2D9;
                border-radius: 10px;
                padding: 0 14px;
                font-family: 'Montserrat';
                font-size: 12px;
                color: #1F2937;
            }
            QLineEdit:focus { border: 2px solid #17813D; }
        """)
        self.txt_busqueda.returnPressed.connect(self.cargar_productos)

        self.cmb_categoria_filtro = QComboBox()
        self.cmb_categoria_filtro.setFixedHeight(38)
        self.cmb_categoria_filtro.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 2px solid #D1E2D9;
                border-radius: 10px;
                padding: 0 12px;
                font-family: 'Montserrat';
                font-size: 12px;
                color: #1F2937;
            }
            QComboBox:focus { border: 2px solid #17813D; }
        """)
        self.cmb_estado_filtro = QComboBox()
        self.cmb_estado_filtro.setFixedHeight(38)
        self.cmb_estado_filtro.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 2px solid #D1E2D9;
                border-radius: 10px;
                padding: 0 12px;
                font-family: 'Montserrat';
                font-size: 12px;
                color: #1F2937;
            }
            QComboBox:focus { border: 2px solid #17813D; }
        """)

        self.btn_buscar = QPushButton("BUSCAR")
        self.btn_buscar.setFixedHeight(38)
        self.btn_buscar.setFont(QFont("Montserrat", 10, QFont.Weight.Black))
        self.btn_buscar.setCursor(Qt.PointingHandCursor)
        self.btn_buscar.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        self.btn_buscar.clicked.connect(self.cargar_productos)

        filtros_layout.addWidget(self.txt_busqueda, 3)
        filtros_layout.addWidget(QLabel("Categoría:"))
        filtros_layout.addWidget(self.cmb_categoria_filtro)
        filtros_layout.addWidget(QLabel("Estado:"))
        filtros_layout.addWidget(self.cmb_estado_filtro)
        filtros_layout.addWidget(self.btn_buscar)

        layout_contenido.addWidget(filtros)

        # ── TABLA Y FORMULARIO ──
        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(16)

        # Tabla
        tabla_panel = QFrame()
        tabla_panel.setObjectName("PanelTabla")
        tabla_panel.setStyleSheet("QFrame#PanelTabla { background: transparent; border: none; }")
        tabla_layout = QVBoxLayout(tabla_panel)
        tabla_layout.setContentsMargins(0, 0, 0, 0)
        tabla_layout.setSpacing(8)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(10)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Producto", "Marca", "Categoría", "Estado", "Proveedor", "Precio", "Stock", "Condición", "Actualizado"]
        )
        self.tabla.setShowGrid(False)
        self.tabla.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(42)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
                outline: none;
                font-family: 'Montserrat';
                font-size: 12px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                border-bottom: 1px solid #F0F2F0;
                padding: 6px 8px;
                background: transparent;
                color: #1F2937;
            }
            QTableWidget::item:selected {
                background: #E8F5EE;
                color: #17813D;
            }
            QTableWidget::item:hover {
                background-color: #F8FAFC;
            }
            QHeaderView::section {
                background: #F1F5F9;
                color: #64748B;
                font-weight: 800;
                font-size: 10px;
                border: none;
                padding: 8px 10px;
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
        self.tabla.setColumnWidth(0, 50)
        self.tabla.setColumnWidth(1, 180)
        self.tabla.setColumnWidth(2, 100)
        self.tabla.setColumnWidth(3, 100)
        self.tabla.setColumnWidth(4, 100)
        self.tabla.setColumnWidth(5, 140)
        self.tabla.setColumnWidth(6, 90)
        self.tabla.setColumnWidth(7, 70)
        self.tabla.setColumnWidth(8, 90)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Stretch)
        self.tabla.itemSelectionChanged.connect(self.cargar_producto_seleccionado)

        tabla_layout.addWidget(self.tabla)
        cuerpo.addWidget(tabla_panel, stretch=2)

        # Formulario de detalle
        form_panel = QFrame()
        form_panel.setObjectName("PanelFormulario")
        form_panel.setStyleSheet("""
            QFrame#PanelFormulario {
                background: #F8FAF9;
                border-radius: 14px;
                border: 1px solid #E2E8F0;
            }
        """)
        form_panel.setFixedWidth(340)
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(18, 16, 18, 16)
        form_layout.setSpacing(10)

        lbl_form = QLabel("DETALLE DEL PRODUCTO")
        lbl_form.setFont(QFont("Montserrat", 12, QFont.Weight.Black))
        lbl_form.setStyleSheet("color: #17813D;")

        form_layout.addWidget(lbl_form)

        # Campos
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre del producto")
        self.txt_marca = QLineEdit()
        self.txt_marca.setPlaceholderText("Marca")
        self.txt_precio = QLineEdit()
        self.txt_precio.setPlaceholderText("Precio de venta")
        self.txt_precio.setValidator(QDoubleValidator(0.0, 999999999.0, 2, self))
        self.txt_stock = QLineEdit()
        self.txt_stock.setPlaceholderText("Stock actual")
        self.txt_stock.setValidator(QIntValidator(0, 9999999, self))
        self.txt_condicion = QLineEdit()
        self.txt_condicion.setPlaceholderText("Condición")

        self.cmb_categoria = QComboBox()
        self.cmb_estado = QComboBox()
        self.cmb_proveedor = QComboBox()

        for etiqueta, widget in (
            ("Producto", self.txt_nombre),
            ("Marca", self.txt_marca),
            ("Categoría", self.cmb_categoria),
            ("Estado", self.cmb_estado),
            ("Proveedor", self.cmb_proveedor),
            ("Precio", self.txt_precio),
            ("Stock", self.txt_stock),
            ("Condición", self.txt_condicion),
        ):
            lbl = QLabel(etiqueta)
            lbl.setFont(QFont("Montserrat", 9, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #64748B;")
            form_layout.addWidget(lbl)
            form_layout.addWidget(widget)

        form_layout.addStretch()

        acciones = QHBoxLayout()
        acciones.setSpacing(8)
        self.btn_nuevo = QPushButton("NUEVO")
        self.btn_nuevo.setFixedHeight(36)
        self.btn_nuevo.setFont(QFont("Montserrat", 10, QFont.Weight.Black))
        self.btn_nuevo.setCursor(Qt.PointingHandCursor)
        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background: #FFFFFF;
                color: #17813D;
                border: 2px solid #A9DDBC;
                border-radius: 10px;
            }
            QPushButton:hover { background: #E9F7EF; }
        """)
        self.btn_nuevo.clicked.connect(self.limpiar_formulario)

        self.btn_guardar = QPushButton("GUARDAR")
        self.btn_guardar.setFixedHeight(36)
        self.btn_guardar.setFont(QFont("Montserrat", 10, QFont.Weight.Black))
        self.btn_guardar.setCursor(Qt.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover { background: #228E49; }
        """)
        self.btn_guardar.clicked.connect(self.guardar_producto)

        acciones.addWidget(self.btn_nuevo)
        acciones.addWidget(self.btn_guardar)
        form_layout.addLayout(acciones)

        cuerpo.addWidget(form_panel)
        layout_contenido.addLayout(cuerpo, stretch=1)

        layout_contenedor.addWidget(contenido, 1)
        layout_principal.addWidget(contenedor_blanco)

        self.cmb_categoria_filtro.currentIndexChanged.connect(self.cargar_productos)
        self.cmb_estado_filtro.currentIndexChanged.connect(self.cargar_productos)

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget#InventarioRoot {
                background-color: #F0F4F2;
                font-family: 'Montserrat';
            }
            QLineEdit, QComboBox {
                background-color: #FFFFFF;
                border: 2px solid #D1E2D9;
                border-radius: 10px;
                padding: 0 12px;
                font-family: 'Montserrat';
                font-size: 12px;
                color: #1F2937;
                height: 36px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #17813D;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(self.COLOR_FONDO)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    # ========== MÉTODOS DE USUARIO ==========
    def actualizar_usuario(self, nombre, rol):
        nombre_display = str(nombre).strip().title()
        rol_display = str(rol).strip().upper()
        self.lbl_nombre_cajero.setText(nombre_display)
        self.lbl_rol_caja.setText(rol_display)
        iniciales = "".join([n[0] for n in nombre_display.split()[:2]]).upper()
        self.lbl_avatar.setText(iniciales)

    def cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Salir", "¿Estás seguro de que deseas cerrar la sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.controlador.cambiar_pantalla("Login")

    def volver_dashboard(self):
        self.controlador.cambiar_pantalla("AdminDashboard")

    def showEvent(self, event):
        if hasattr(self.controlador, "usuario_actual") and self.controlador.usuario_actual:
            datos = self.controlador.usuario_actual
            self.actualizar_usuario(datos.get("nombre", "Usuario"), datos.get("rol", "cajero"))
        super().showEvent(event)

    # ========== FUNCIONES DE INVENTARIO ==========
    def cargar_catalogos(self):
        try:
            catalogos = self.modelo.obtener_catalogos()
        except Exception as error:
            QMessageBox.critical(self, "Inventario", f"No se pudieron cargar los catálogos: {error}")
            return

        self._llenar_combo(self.cmb_categoria, catalogos["categorias"], "id_categoria", "nombre_categoria")
        self._llenar_combo(self.cmb_estado, catalogos["estados"], "id_estado", "nombre_estado")
        self._llenar_combo(self.cmb_proveedor, catalogos["proveedores"], "id_proveedor", "nombre_empresa")

        self._llenar_combo(
            self.cmb_categoria_filtro,
            catalogos["categorias"],
            "id_categoria",
            "nombre_categoria",
            texto_inicial="Todas",
        )
        self._llenar_combo(
            self.cmb_estado_filtro,
            catalogos["estados"],
            "id_estado",
            "nombre_estado",
            texto_inicial="Todos",
        )

    def _llenar_combo(self, combo, datos, llave_id, llave_texto, texto_inicial=None):
        combo.blockSignals(True)
        combo.clear()
        if texto_inicial is not None:
            combo.addItem(texto_inicial, None)
        for item in datos:
            combo.addItem(str(item.get(llave_texto, "")), item.get(llave_id))
        combo.blockSignals(False)

    def cargar_sugerencias_busqueda(self):
        try:
            self.sugerencias_busqueda = self.modelo.obtener_sugerencias_busqueda()
        except Exception:
            self.sugerencias_busqueda = []

    def cargar_productos(self):
        if hasattr(self, "lista_sugerencias"):
            self.lista_sugerencias.hide()
        texto = self.txt_busqueda.text() if hasattr(self, "txt_busqueda") else ""
        id_categoria = self.cmb_categoria_filtro.currentData() if hasattr(self, "cmb_categoria_filtro") else None
        id_estado = self.cmb_estado_filtro.currentData() if hasattr(self, "cmb_estado_filtro") else None

        try:
            self.productos = self.modelo.listar_productos(texto, id_categoria, id_estado)
        except Exception as error:
            QMessageBox.critical(self, "Inventario", f"No se pudo cargar el inventario: {error}")
            return

        self._actualizar_tabla()
        self._actualizar_resumen()

        if self.productos:
            self.tabla.selectRow(0)
        else:
            self.limpiar_formulario()

    def _actualizar_tabla(self):
        self.tabla.setRowCount(len(self.productos))
        for fila, producto in enumerate(self.productos):
            valores = [
                producto.get("id_producto"),
                producto.get("nombre_producto"),
                producto.get("marca_producto"),
                producto.get("nombre_categoria"),
                producto.get("nombre_estado"),
                producto.get("nombre_empresa"),
                self._formatear_moneda(producto.get("precio_venta_prod")),
                producto.get("stock_actual"),
                producto.get("condicion"),
                self._formatear_fecha(producto.get("timestamp_ultima_actualizacion")),
            ]
            for columna, valor in enumerate(valores):
                celda = QTableWidgetItem("" if valor is None else str(valor))
                if columna in (0, 6, 7):
                    celda.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if columna == 7 and self._a_entero(valor) <= 20:
                    celda.setForeground(QColor("#B42318"))
                    celda.setFont(QFont("Montserrat", 10, QFont.Weight.Bold))
                self.tabla.setItem(fila, columna, celda)
        self.aplicar_filtro_rapido(self.filtro_rapido, actualizar_botones=False)

    def _actualizar_resumen(self):
        total = len(self.productos)
        stock_bajo = sum(1 for item in self.productos if self._a_entero(item.get("stock_actual")) <= 20)
        vencidos = sum(1 for item in self.productos if str(item.get("condicion") or "").lower() == "vencida")
        valor = sum(
            self._a_decimal(item.get("precio_venta_prod")) * self._a_decimal(item.get("stock_actual"))
            for item in self.productos
        )

        self.lbl_valor.setText(f"VALOR INVENTARIO: ${valor:,.0f}".replace(",", "."))

    def aplicar_filtro_rapido(self, filtro, actualizar_botones=True):
        self.filtro_rapido = filtro
        if actualizar_botones:
            self.btn_todos.setChecked(filtro == "TODOS")
            self.btn_stock_bajo.setChecked(filtro == "STOCK_BAJO")
            self.btn_vencidos.setChecked(filtro == "VENCIDOS")

        for fila in range(self.tabla.rowCount()):
            mostrar = True
            if filtro == "STOCK_BAJO":
                item_stock = self.tabla.item(fila, 7)
                stock = self._a_entero(item_stock.text()) if item_stock else 0
                mostrar = stock <= 20
            elif filtro == "VENCIDOS":
                item_cond = self.tabla.item(fila, 8)
                cond = item_cond.text().lower() if item_cond else ""
                mostrar = cond == "vencida"
            self.tabla.setRowHidden(fila, not mostrar)

    def cargar_producto_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0 or fila >= len(self.productos):
            return

        producto = self.productos[fila]
        self.producto_actual = producto.get("id_producto")
        self.id_inventario_actual = producto.get("id_inventario")

        self.txt_nombre.setText(str(producto.get("nombre_producto") or ""))
        self.txt_marca.setText(str(producto.get("marca_producto") or ""))
        self.txt_precio.setText(self._numero_a_texto(producto.get("precio_venta_prod")))
        self.txt_stock.setText(str(producto.get("stock_actual") or 0))
        self.txt_condicion.setText(str(producto.get("condicion") or "Buena"))
        self._seleccionar_combo(self.cmb_categoria, producto.get("id_categoria"))
        self._seleccionar_combo(self.cmb_estado, producto.get("id_estado"))
        self._seleccionar_combo(self.cmb_proveedor, producto.get("id_proveedor"))

    def limpiar_formulario(self):
        self.producto_actual = None
        self.id_inventario_actual = None
        self.tabla.clearSelection()
        self.txt_nombre.clear()
        self.txt_marca.clear()
        self.txt_precio.clear()
        self.txt_stock.setText("0")
        self.txt_condicion.setText("Buena")
        if self.cmb_categoria.count():
            self.cmb_categoria.setCurrentIndex(0)
        if self.cmb_estado.count():
            self.cmb_estado.setCurrentIndex(0)
        if self.cmb_proveedor.count():
            self.cmb_proveedor.setCurrentIndex(0)
        self.txt_nombre.setFocus()

    def guardar_producto(self):
        datos = self._leer_formulario()
        if not datos:
            return

        try:
            self.modelo.guardar_producto(datos)
        except Exception as error:
            QMessageBox.critical(self, "Inventario", f"No se pudo guardar el producto: {error}")
            return

        QMessageBox.information(self, "Inventario", "Producto guardado correctamente.")
        self.cargar_sugerencias_busqueda()
        self.cargar_productos()

    def _leer_formulario(self):
        nombre = self.txt_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Inventario", "El nombre del producto es obligatorio.")
            return None

        id_categoria = self.cmb_categoria.currentData()
        id_estado = self.cmb_estado.currentData()
        id_proveedor = self.cmb_proveedor.currentData()
        if not id_categoria or not id_estado or not id_proveedor:
            QMessageBox.warning(self, "Inventario", "Selecciona categoría, estado y proveedor.")
            return None

        try:
            precio = float((self.txt_precio.text().strip() or "0").replace(",", "."))
            stock = int(self.txt_stock.text().strip() or 0)
        except ValueError:
            QMessageBox.warning(self, "Inventario", "Precio y stock deben ser valores numéricos.")
            return None

        if precio < 0 or stock < 0:
            QMessageBox.warning(self, "Inventario", "Precio y stock no pueden ser negativos.")
            return None

        condicion = self.txt_condicion.text().strip() or "Buena"
        return {
            "id_producto": self.producto_actual,
            "id_inventario": self.id_inventario_actual,
            "nombre_producto": nombre,
            "marca_producto": self.txt_marca.text().strip(),
            "id_categoria": id_categoria,
            "id_estado": id_estado,
            "id_proveedor": id_proveedor,
            "precio_venta_prod": precio,
            "stock_actual": stock,
            "condicion": condicion,
        }

    def _seleccionar_combo(self, combo, valor):
        indice = combo.findData(valor)
        if indice >= 0:
            combo.setCurrentIndex(indice)

    def _formatear_moneda(self, valor):
        numero = self._a_decimal(valor)
        return f"${numero:,.0f}".replace(",", ".")

    def _formatear_fecha(self, valor):
        if hasattr(valor, "strftime"):
            return valor.strftime("%d/%m/%Y %H:%M")
        return "" if valor is None else str(valor)

    def _numero_a_texto(self, valor):
        if valor is None:
            return ""
        numero = self._a_decimal(valor)
        if numero == numero.to_integral_value():
            return str(int(numero))
        return str(numero)

    def _a_entero(self, valor):
        try:
            return int(valor or 0)
        except (TypeError, ValueError):
            return 0

    def _a_decimal(self, valor):
        if isinstance(valor, Decimal):
            return valor
        try:
            return Decimal(str(valor or 0))
        except Exception:
            return Decimal("0")