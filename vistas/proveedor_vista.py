import os
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
    QSizePolicy
)

from modelos.proveedor_modelo import ProveedorModelo


class ProveedoresVista(QWidget):
    def __init__(self, controlador_flujo, conexion):
        super().__init__()
        self.controlador = controlador_flujo
        self.modelo = ProveedorModelo(conexion)
        self.proveedores = []
        self.productos = []
        self.COLOR_FONDO = "#F0F4F2"

        self.setObjectName("ProveedoresRoot")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._cargar_fuentes()
        self._construir_interfaz()
        self._aplicar_estilos()
        self.cargar_proveedores()

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
        contenedor_blanco.setObjectName("ContenedorProveedores")
        contenedor_blanco.setStyleSheet("""
            QFrame#ContenedorProveedores {
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
        navbar.setObjectName("NavbarProveedores")
        navbar.setFixedHeight(68)
        navbar.setStyleSheet("""
            QFrame#NavbarProveedores { 
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
        lbl_titulo = QLabel("PROVEEDORES")
        lbl_titulo.setFont(QFont("Montserrat", 20, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent;")
        titulo_layout.addWidget(lbl_titulo)

        # Botón Recargar
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
        btn_recargar.clicked.connect(self.cargar_proveedores)
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

        # ── FILTRO DE BÚSQUEDA ──
        filtros = QFrame()
        filtros.setObjectName("PanelFiltros")
        filtros.setStyleSheet("QFrame#PanelFiltros { background: #F8FAF9; border-radius: 12px; border: 1px solid #E2E8F0; }")
        filtros_layout = QHBoxLayout(filtros)
        filtros_layout.setContentsMargins(16, 8, 16, 8)
        filtros_layout.setSpacing(12)

        self.txt_busqueda = QLineEdit()
        self.txt_busqueda.setPlaceholderText("Buscar proveedor por nombre, NIT, teléfono, email o ciudad")
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
        self.txt_busqueda.returnPressed.connect(self.cargar_proveedores)

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
        self.btn_buscar.clicked.connect(self.cargar_proveedores)

        filtros_layout.addWidget(self.txt_busqueda, 1)
        filtros_layout.addWidget(self.btn_buscar)
        layout_contenido.addWidget(filtros)

        # ── CUERPO: TABLA DE PROVEEDORES Y DETALLE ──
        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(16)

        # Panel izquierdo: Lista de proveedores
        panel_proveedores = QFrame()
        panel_proveedores.setObjectName("PanelProveedores")
        panel_proveedores.setStyleSheet("QFrame#PanelProveedores { background: transparent; border: none; }")
        panel_proveedores.setFixedWidth(420)
        proveedores_layout = QVBoxLayout(panel_proveedores)
        proveedores_layout.setContentsMargins(0, 0, 0, 0)
        proveedores_layout.setSpacing(8)

        lbl_proveedores = QLabel("LISTA DE PROVEEDORES")
        lbl_proveedores.setFont(QFont("Montserrat", 12, QFont.Weight.Black))
        lbl_proveedores.setStyleSheet("color: #17813D;")

        proveedores_layout.addWidget(lbl_proveedores)

        self.tabla_proveedores = QTableWidget()
        self.tabla_proveedores.setColumnCount(4)
        self.tabla_proveedores.setHorizontalHeaderLabels(["ID", "Proveedor", "Ciudad", "Productos"])
        self.tabla_proveedores.setShowGrid(False)
        self.tabla_proveedores.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_proveedores.verticalHeader().setVisible(False)
        self.tabla_proveedores.verticalHeader().setDefaultSectionSize(42)
        self.tabla_proveedores.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_proveedores.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_proveedores.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla_proveedores.setStyleSheet("""
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
        header = self.tabla_proveedores.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_proveedores.setColumnWidth(0, 50)
        self.tabla_proveedores.setColumnWidth(1, 180)
        self.tabla_proveedores.setColumnWidth(2, 100)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla_proveedores.itemSelectionChanged.connect(self.cargar_proveedor_seleccionado)

        proveedores_layout.addWidget(self.tabla_proveedores)
        cuerpo.addWidget(panel_proveedores)

        # Panel derecho: Detalle del proveedor
        panel_detalle = QFrame()
        panel_detalle.setObjectName("PanelDetalle")
        panel_detalle.setStyleSheet("""
            QFrame#PanelDetalle {
                background: #F8FAF9;
                border-radius: 14px;
                border: 1px solid #E2E8F0;
            }
        """)
        detalle_layout = QVBoxLayout(panel_detalle)
        detalle_layout.setContentsMargins(18, 16, 18, 16)
        detalle_layout.setSpacing(12)

        lbl_detalle = QLabel("CONTACTO Y PRODUCTOS")
        lbl_detalle.setFont(QFont("Montserrat", 12, QFont.Weight.Black))
        lbl_detalle.setStyleSheet("color: #17813D;")

        detalle_layout.addWidget(lbl_detalle)

        # Contacto
        contacto = QFrame()
        contacto.setObjectName("Contacto")
        contacto.setStyleSheet("QFrame#Contacto { background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; }")
        contacto_layout = QGridLayout(contacto)
        contacto_layout.setContentsMargins(14, 12, 14, 12)
        contacto_layout.setHorizontalSpacing(16)
        contacto_layout.setVerticalSpacing(6)

        self.lbl_empresa = self._crear_dato_contacto("Empresa", "-")
        self.lbl_nit = self._crear_dato_contacto("NIT", "-")
        self.lbl_telefono = self._crear_dato_contacto("Teléfono", "-")
        self.lbl_email = self._crear_dato_contacto("Email", "-")
        self.lbl_direccion = self._crear_dato_contacto("Dirección", "-")
        self.lbl_ciudad = self._crear_dato_contacto("Ciudad", "-")

        contacto_layout.addLayout(self.lbl_empresa, 0, 0)
        contacto_layout.addLayout(self.lbl_nit, 0, 1)
        contacto_layout.addLayout(self.lbl_telefono, 1, 0)
        contacto_layout.addLayout(self.lbl_email, 1, 1)
        contacto_layout.addLayout(self.lbl_direccion, 2, 0)
        contacto_layout.addLayout(self.lbl_ciudad, 2, 1)

        detalle_layout.addWidget(contacto)

        # Tabla de productos del proveedor
        lbl_productos = QLabel("PRODUCTOS SUMINISTRADOS")
        lbl_productos.setFont(QFont("Montserrat", 10, QFont.Weight.Bold))
        lbl_productos.setStyleSheet("color: #64748B;")
        detalle_layout.addWidget(lbl_productos)

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(7)
        self.tabla_productos.setHorizontalHeaderLabels(
            ["ID", "Producto", "Marca", "Categoría", "Estado", "Precio", "Stock"]
        )
        self.tabla_productos.setShowGrid(False)
        self.tabla_productos.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_productos.verticalHeader().setVisible(False)
        self.tabla_productos.verticalHeader().setDefaultSectionSize(36)
        self.tabla_productos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_productos.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
                outline: none;
                font-family: 'Montserrat';
                font-size: 11px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                border-bottom: 1px solid #F0F2F0;
                padding: 4px 6px;
                background: transparent;
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
                font-size: 9px;
                border: none;
                padding: 6px 8px;
                font-family: 'Montserrat';
            }
            QTableWidget QTableCornerButton::section {
                background: transparent;
                border: none;
            }
        """)
        header_prod = self.tabla_productos.horizontalHeader()
        header_prod.setStretchLastSection(False)
        header_prod.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_productos.setColumnWidth(0, 40)
        self.tabla_productos.setColumnWidth(1, 140)
        self.tabla_productos.setColumnWidth(2, 80)
        self.tabla_productos.setColumnWidth(3, 80)
        self.tabla_productos.setColumnWidth(4, 80)
        self.tabla_productos.setColumnWidth(5, 80)
        header_prod.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        detalle_layout.addWidget(self.tabla_productos, stretch=1)

        cuerpo.addWidget(panel_detalle, stretch=2)
        layout_contenido.addLayout(cuerpo, stretch=1)

        layout_contenedor.addWidget(contenido, 1)
        layout_principal.addWidget(contenedor_blanco)

    def _crear_dato_contacto(self, titulo, valor):
        layout = QVBoxLayout()
        layout.setSpacing(2)
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(QFont("Montserrat", 8, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #64748B;")
        lbl_valor = QLabel(valor)
        lbl_valor.setFont(QFont("Montserrat", 11, QFont.Weight.Medium))
        lbl_valor.setStyleSheet("color: #1F2937;")
        lbl_valor.setWordWrap(True)
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        layout.valor = lbl_valor
        return layout

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget#ProveedoresRoot {
                background-color: #F0F4F2;
                font-family: 'Montserrat';
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #D1E2D9;
                border-radius: 10px;
                padding: 0 12px;
                font-family: 'Montserrat';
                font-size: 12px;
                color: #1F2937;
                height: 36px;
            }
            QLineEdit:focus {
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

    # ========== FUNCIONES DE PROVEEDORES ==========
    def cargar_proveedores(self):
        try:
            self.proveedores = self.modelo.listar_proveedores(self.txt_busqueda.text())
        except Exception as error:
            QMessageBox.critical(self, "Proveedores", f"No se pudieron cargar los proveedores: {error}")
            return

        self.tabla_proveedores.setRowCount(len(self.proveedores))
        for fila, proveedor in enumerate(self.proveedores):
            valores = [
                proveedor.get("id_proveedor"),
                proveedor.get("nombre_empresa"),
                proveedor.get("ciudad"),
                proveedor.get("total_productos"),
            ]
            for columna, valor in enumerate(valores):
                celda = QTableWidgetItem("" if valor is None else str(valor))
                if columna in (0, 3):
                    celda.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_proveedores.setItem(fila, columna, celda)

        if self.proveedores:
            self.tabla_proveedores.selectRow(0)
        else:
            self._limpiar_detalle()

    def cargar_proveedor_seleccionado(self):
        fila = self.tabla_proveedores.currentRow()
        if fila < 0 or fila >= len(self.proveedores):
            return

        proveedor = self.proveedores[fila]
        self.lbl_empresa.valor.setText(str(proveedor.get("nombre_empresa") or "-"))
        self.lbl_nit.valor.setText(str(proveedor.get("nit") or "-"))
        self.lbl_telefono.valor.setText(str(proveedor.get("telefono_principal") or "-"))
        self.lbl_email.valor.setText(str(proveedor.get("email") or "-"))
        self.lbl_direccion.valor.setText(str(proveedor.get("direccion") or "-"))
        self.lbl_ciudad.valor.setText(str(proveedor.get("ciudad") or "-"))
        self.cargar_productos_proveedor(proveedor.get("id_proveedor"))

    def cargar_productos_proveedor(self, id_proveedor):
        try:
            self.productos = self.modelo.listar_productos_proveedor(id_proveedor)
        except Exception as error:
            QMessageBox.critical(self, "Proveedores", f"No se pudieron cargar los productos: {error}")
            return

        self.tabla_productos.setRowCount(len(self.productos))
        for fila, producto in enumerate(self.productos):
            valores = [
                producto.get("id_producto"),
                producto.get("nombre_producto"),
                producto.get("marca_producto"),
                producto.get("nombre_categoria"),
                producto.get("nombre_estado"),
                self._formatear_moneda(producto.get("precio_venta_prod")),
                producto.get("stock_actual"),
            ]
            for columna, valor in enumerate(valores):
                celda = QTableWidgetItem("" if valor is None else str(valor))
                if columna in (0, 5, 6):
                    celda.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if columna == 6 and self._a_entero(valor) <= 20:
                    celda.setForeground(QColor("#B42318"))
                    celda.setFont(QFont("Montserrat", 9, QFont.Weight.Bold))
                self.tabla_productos.setItem(fila, columna, celda)

    def _limpiar_detalle(self):
        for layout in (
            self.lbl_empresa,
            self.lbl_nit,
            self.lbl_telefono,
            self.lbl_email,
            self.lbl_direccion,
            self.lbl_ciudad,
        ):
            layout.valor.setText("-")
        self.tabla_productos.setRowCount(0)

    def _formatear_moneda(self, valor):
        numero = self._a_decimal(valor)
        return f"${numero:,.0f}".replace(",", ".")

    def _a_decimal(self, valor):
        if isinstance(valor, Decimal):
            return valor
        try:
            return Decimal(str(valor or 0))
        except Exception:
            return Decimal("0")

    def _a_entero(self, valor):
        try:
            return int(valor or 0)
        except (TypeError, ValueError):
            return 0