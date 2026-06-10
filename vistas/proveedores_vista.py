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
)

from modelos.proveedor_modelo import ProveedorModelo


class ProveedoresVista(QWidget):
    def __init__(self, controlador_flujo, conexion):
        super().__init__()
        self.controlador = controlador_flujo
        self.modelo = ProveedorModelo(conexion)
        self.proveedores = []
        self.productos = []

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
        for fuente in ("Montserrat-Regular.ttf", "Montserrat-Bold.ttf", "Montserrat-Medium.ttf"):
            ruta = os.path.join(carpeta_fuentes, fuente)
            if os.path.exists(ruta):
                QFontDatabase.addApplicationFont(ruta)

    def _construir_interfaz(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(34, 28, 34, 28)
        layout_principal.setSpacing(18)

        barra = QHBoxLayout()
        barra.setSpacing(12)

        self.btn_volver = QPushButton("Volver")
        self.btn_volver.setObjectName("BotonSecundario")
        self.btn_volver.clicked.connect(lambda: self.controlador.cambiar_pantalla("Inventario"))

        titulo = QLabel("Proveedores")
        titulo.setObjectName("TituloModulo")

        self.btn_recargar = QPushButton("Recargar")
        self.btn_recargar.setObjectName("BotonSecundario")
        self.btn_recargar.clicked.connect(self.cargar_proveedores)

        barra.addWidget(self.btn_volver)
        barra.addStretch()
        barra.addWidget(titulo)
        barra.addStretch()
        barra.addWidget(self.btn_recargar)
        layout_principal.addLayout(barra)

        filtros = QFrame()
        filtros.setObjectName("PanelBlanco")
        filtros_layout = QHBoxLayout(filtros)
        filtros_layout.setContentsMargins(18, 14, 18, 14)
        filtros_layout.setSpacing(12)

        self.txt_busqueda = QLineEdit()
        self.txt_busqueda.setPlaceholderText("Buscar proveedor por nombre, NIT, telefono, email o ciudad")
        self.txt_busqueda.returnPressed.connect(self.cargar_proveedores)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setObjectName("BotonPrincipal")
        self.btn_buscar.clicked.connect(self.cargar_proveedores)

        filtros_layout.addWidget(self.txt_busqueda, stretch=1)
        filtros_layout.addWidget(self.btn_buscar)
        layout_principal.addWidget(filtros)

        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(18)

        panel_proveedores = QFrame()
        panel_proveedores.setObjectName("PanelBlanco")
        panel_proveedores.setFixedWidth(470)
        proveedores_layout = QVBoxLayout(panel_proveedores)
        proveedores_layout.setContentsMargins(18, 18, 18, 18)
        proveedores_layout.setSpacing(12)

        lbl_proveedores = QLabel("Lista de proveedores")
        lbl_proveedores.setObjectName("Subtitulo")
        proveedores_layout.addWidget(lbl_proveedores)

        self.tabla_proveedores = QTableWidget()
        self.tabla_proveedores.setColumnCount(4)
        self.tabla_proveedores.setHorizontalHeaderLabels(["ID", "Proveedor", "Ciudad", "Productos"])
        self.tabla_proveedores.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_proveedores.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_proveedores.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla_proveedores.verticalHeader().setVisible(False)
        self.tabla_proveedores.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_proveedores.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_proveedores.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_proveedores.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_proveedores.itemSelectionChanged.connect(self.cargar_proveedor_seleccionado)
        proveedores_layout.addWidget(self.tabla_proveedores)

        panel_detalle = QFrame()
        panel_detalle.setObjectName("PanelBlanco")
        detalle_layout = QVBoxLayout(panel_detalle)
        detalle_layout.setContentsMargins(18, 18, 18, 18)
        detalle_layout.setSpacing(14)

        lbl_detalle = QLabel("Contacto y productos")
        lbl_detalle.setObjectName("Subtitulo")
        detalle_layout.addWidget(lbl_detalle)

        contacto = QFrame()
        contacto.setObjectName("Contacto")
        contacto_layout = QGridLayout(contacto)
        contacto_layout.setContentsMargins(16, 14, 16, 14)
        contacto_layout.setHorizontalSpacing(18)
        contacto_layout.setVerticalSpacing(10)

        self.lbl_empresa = self._crear_dato_contacto("Empresa", "-")
        self.lbl_nit = self._crear_dato_contacto("NIT", "-")
        self.lbl_telefono = self._crear_dato_contacto("Telefono", "-")
        self.lbl_email = self._crear_dato_contacto("Email", "-")
        self.lbl_direccion = self._crear_dato_contacto("Direccion", "-")
        self.lbl_ciudad = self._crear_dato_contacto("Ciudad", "-")

        contacto_layout.addLayout(self.lbl_empresa, 0, 0)
        contacto_layout.addLayout(self.lbl_nit, 0, 1)
        contacto_layout.addLayout(self.lbl_telefono, 1, 0)
        contacto_layout.addLayout(self.lbl_email, 1, 1)
        contacto_layout.addLayout(self.lbl_direccion, 2, 0)
        contacto_layout.addLayout(self.lbl_ciudad, 2, 1)
        detalle_layout.addWidget(contacto)

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(7)
        self.tabla_productos.setHorizontalHeaderLabels(
            ["ID", "Producto", "Marca", "Categoria", "Estado", "Precio", "Stock"]
        )
        self.tabla_productos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_productos.verticalHeader().setVisible(False)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        detalle_layout.addWidget(self.tabla_productos, stretch=1)

        cuerpo.addWidget(panel_proveedores)
        cuerpo.addWidget(panel_detalle, stretch=1)
        layout_principal.addLayout(cuerpo, stretch=1)

    def _crear_dato_contacto(self, titulo, valor):
        layout = QVBoxLayout()
        layout.setSpacing(2)
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("DatoTitulo")
        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("DatoValor")
        lbl_valor.setWordWrap(True)
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        layout.valor = lbl_valor
        return layout

    def _aplicar_estilos(self):
        self.setStyleSheet(
            """
            QWidget#ProveedoresRoot {
                background-color: #008037;
                font-family: 'Montserrat';
            }
            QLabel {
                color: #1B4314;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#TituloModulo {
                color: #FFFFFF;
                font-size: 34px;
                font-weight: 900;
            }
            QLabel#Subtitulo {
                color: #1B4314;
                font-size: 18px;
                font-weight: 900;
            }
            QLabel#DatoTitulo {
                color: #58705E;
                font-size: 11px;
                font-weight: 800;
            }
            QLabel#DatoValor {
                color: #1B4314;
                font-size: 13px;
                font-weight: 900;
            }
            QFrame#PanelBlanco {
                background-color: #FFFFFF;
                border-radius: 18px;
                border: none;
            }
            QFrame#Contacto {
                background-color: #ECF5EF;
                border-radius: 12px;
                border: none;
            }
            QLineEdit {
                background-color: #ECF5EF;
                color: #1B4314;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 8px 12px;
                min-height: 20px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #008037;
            }
            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 9px 18px;
                font-size: 12px;
                font-weight: 900;
            }
            QPushButton#BotonPrincipal {
                background-color: #008037;
                color: white;
            }
            QPushButton#BotonPrincipal:hover {
                background-color: #1B4314;
            }
            QPushButton#BotonSecundario {
                background-color: #FFFFFF;
                color: #008037;
            }
            QPushButton#BotonSecundario:hover {
                background-color: #1B4314;
                color: #FFFFFF;
            }
            QTableWidget {
                background-color: #FFFFFF;
                color: #1B4314;
                border: 1px solid #DFE9E2;
                border-radius: 10px;
                gridline-color: #E7EFEA;
                selection-background-color: #DCEFE3;
                selection-color: #1B4314;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #ECF5EF;
                color: #1B4314;
                border: none;
                padding: 9px;
                font-weight: 900;
            }
            """
        )

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
                    celda.setFont(QFont("Montserrat", 10, QFont.Weight.Bold))
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
