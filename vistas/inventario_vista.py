import os
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QDoubleValidator, QFont, QFontDatabase, QIntValidator
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
        self.btn_volver.clicked.connect(lambda: self.controlador.cambiar_pantalla("AdminDashboard"))

        titulo = QLabel("Inventario")
        titulo.setObjectName("TituloModulo")

        self.btn_recargar = QPushButton("Recargar")
        self.btn_recargar.setObjectName("BotonSecundario")
        self.btn_recargar.clicked.connect(self.cargar_productos)

        self.btn_proveedores = QPushButton("Proveedores")
        self.btn_proveedores.setObjectName("BotonSecundario")
        self.btn_proveedores.clicked.connect(lambda: self.controlador.cambiar_pantalla("Proveedores"))

        barra.addWidget(self.btn_volver)
        barra.addStretch()
        barra.addWidget(titulo)
        barra.addStretch()
        barra.addWidget(self.btn_proveedores)
        barra.addWidget(self.btn_recargar)
        layout_principal.addLayout(barra)

        resumen = QHBoxLayout()
        resumen.setSpacing(14)
        self.card_total = self._crear_indicador("Productos", "0")
        self.card_stock_bajo = self._crear_indicador("Stock bajo", "0")
        self.card_vencidos = self._crear_indicador("Vencidos", "0")
        self.card_valor = self._crear_indicador("Valor inventario", "$0")
        resumen.addWidget(self.card_total)
        resumen.addWidget(self.card_stock_bajo)
        resumen.addWidget(self.card_vencidos)
        resumen.addWidget(self.card_valor)
        layout_principal.addLayout(resumen)

        filtros = QFrame()
        filtros.setObjectName("PanelBlanco")
        filtros_layout = QGridLayout(filtros)
        filtros_layout.setContentsMargins(18, 14, 18, 14)
        filtros_layout.setHorizontalSpacing(12)
        filtros_layout.setVerticalSpacing(10)

        self.txt_busqueda = QLineEdit()
        self.txt_busqueda.setPlaceholderText("Buscar por producto, marca o proveedor")
        self.txt_busqueda.returnPressed.connect(self.cargar_productos)
        self.txt_busqueda.textEdited.connect(self.actualizar_sugerencias_busqueda)

        self.lista_sugerencias = QListWidget()
        self.lista_sugerencias.setObjectName("ListaSugerencias")
        self.lista_sugerencias.setMaximumHeight(170)
        self.lista_sugerencias.hide()
        self.lista_sugerencias.itemClicked.connect(self.aplicar_sugerencia_busqueda)

        self.cmb_categoria_filtro = QComboBox()
        self.cmb_estado_filtro = QComboBox()
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setObjectName("BotonPrincipal")
        self.btn_buscar.clicked.connect(self.cargar_productos)

        filtros_layout.addWidget(QLabel("Busqueda"), 0, 0)
        filtros_layout.addWidget(QLabel("Categoria"), 0, 1)
        filtros_layout.addWidget(QLabel("Estado"), 0, 2)
        filtros_layout.addWidget(self.txt_busqueda, 1, 0)
        filtros_layout.addWidget(self.cmb_categoria_filtro, 1, 1)
        filtros_layout.addWidget(self.cmb_estado_filtro, 1, 2)
        filtros_layout.addWidget(self.btn_buscar, 1, 3)
        filtros_layout.addWidget(self.lista_sugerencias, 2, 0)
        filtros_layout.setColumnStretch(0, 3)
        filtros_layout.setColumnStretch(1, 1)
        filtros_layout.setColumnStretch(2, 1)
        layout_principal.addWidget(filtros)

        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(18)

        tabla_panel = QFrame()
        tabla_panel.setObjectName("PanelBlanco")
        tabla_layout = QVBoxLayout(tabla_panel)
        tabla_layout.setContentsMargins(18, 18, 18, 18)
        tabla_layout.setSpacing(12)

        lbl_tabla = QLabel("Productos registrados")
        lbl_tabla.setObjectName("Subtitulo")
        tabla_layout.addWidget(lbl_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(10)
        self.tabla.setHorizontalHeaderLabels(
            [
                "ID",
                "Producto",
                "Marca",
                "Categoria",
                "Estado",
                "Proveedor",
                "Precio",
                "Stock",
                "Condicion",
                "Actualizado",
            ]
        )
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.itemSelectionChanged.connect(self.cargar_producto_seleccionado)
        tabla_layout.addWidget(self.tabla)

        form_panel = QFrame()
        form_panel.setObjectName("PanelBlanco")
        form_panel.setFixedWidth(360)
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(22, 20, 22, 20)
        form_layout.setSpacing(12)

        lbl_form = QLabel("Detalle del producto")
        lbl_form.setObjectName("Subtitulo")
        form_layout.addWidget(lbl_form)

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
        self.txt_condicion.setPlaceholderText("Condicion")

        self.cmb_categoria = QComboBox()
        self.cmb_estado = QComboBox()
        self.cmb_proveedor = QComboBox()

        for etiqueta, widget in (
            ("Producto", self.txt_nombre),
            ("Marca", self.txt_marca),
            ("Categoria", self.cmb_categoria),
            ("Estado", self.cmb_estado),
            ("Proveedor", self.cmb_proveedor),
            ("Precio", self.txt_precio),
            ("Stock", self.txt_stock),
            ("Condicion", self.txt_condicion),
        ):
            form_layout.addWidget(QLabel(etiqueta))
            form_layout.addWidget(widget)

        form_layout.addStretch()

        acciones = QHBoxLayout()
        acciones.setSpacing(10)
        self.btn_nuevo = QPushButton("Nuevo")
        self.btn_nuevo.setObjectName("BotonSecundario")
        self.btn_nuevo.clicked.connect(self.limpiar_formulario)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setObjectName("BotonPrincipal")
        self.btn_guardar.clicked.connect(self.guardar_producto)

        acciones.addWidget(self.btn_nuevo)
        acciones.addWidget(self.btn_guardar)
        form_layout.addLayout(acciones)

        cuerpo.addWidget(tabla_panel, stretch=1)
        cuerpo.addWidget(form_panel)
        layout_principal.addLayout(cuerpo, stretch=1)

    def _crear_indicador(self, titulo, valor):
        frame = QFrame()
        frame.setObjectName("Indicador")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 14, 18, 14)
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("IndicadorTitulo")
        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("IndicadorValor")
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        frame.valor = lbl_valor
        return frame

    def _aplicar_estilos(self):
        self.setStyleSheet(
            """
            QWidget#InventarioRoot {
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
            QFrame#PanelBlanco,
            QFrame#Indicador {
                background-color: #FFFFFF;
                border-radius: 18px;
                border: none;
            }
            QLabel#IndicadorTitulo {
                color: #4C6251;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#IndicadorValor {
                color: #008037;
                font-size: 25px;
                font-weight: 900;
            }
            QLineEdit,
            QComboBox {
                background-color: #ECF5EF;
                color: #1B4314;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 8px 12px;
                min-height: 20px;
                font-size: 12px;
            }
            QLineEdit:focus,
            QComboBox:focus {
                border: 2px solid #008037;
            }
            QListWidget#ListaSugerencias {
                background-color: #FFFFFF;
                color: #1B4314;
                border: 2px solid #008037;
                border-radius: 10px;
                padding: 4px;
                font-size: 12px;
                outline: none;
            }
            QListWidget#ListaSugerencias::item {
                padding: 8px 10px;
                border-radius: 7px;
            }
            QListWidget#ListaSugerencias::item:hover,
            QListWidget#ListaSugerencias::item:selected {
                background-color: #DCEFE3;
                color: #1B4314;
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
            QFrame#PanelBlanco QPushButton#BotonSecundario {
                background-color: #ECF5EF;
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

    def cargar_catalogos(self):
        try:
            catalogos = self.modelo.obtener_catalogos()
        except Exception as error:
            QMessageBox.critical(self, "Inventario", f"No se pudieron cargar los catalogos: {error}")
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
        self.cmb_categoria_filtro.currentIndexChanged.connect(self.cargar_productos)
        self.cmb_estado_filtro.currentIndexChanged.connect(self.cargar_productos)

    def cargar_sugerencias_busqueda(self):
        try:
            self.sugerencias_busqueda = self.modelo.obtener_sugerencias_busqueda()
        except Exception:
            self.sugerencias_busqueda = []

    def actualizar_sugerencias_busqueda(self, texto):
        texto = texto.strip().lower()
        if not texto:
            self.lista_sugerencias.hide()
            self.lista_sugerencias.clear()
            return

        empiezan = []
        contienen = []
        vistos = set()
        for sugerencia in self.sugerencias_busqueda:
            sugerencia_limpia = str(sugerencia).strip()
            clave = sugerencia_limpia.lower()
            if not sugerencia_limpia or clave in vistos:
                continue
            if clave.startswith(texto):
                empiezan.append(sugerencia_limpia)
                vistos.add(clave)
            elif texto in clave:
                contienen.append(sugerencia_limpia)
                vistos.add(clave)

        mejores = (empiezan + contienen)[:8]
        self.lista_sugerencias.clear()
        self.lista_sugerencias.addItems(mejores)
        self.lista_sugerencias.setVisible(bool(mejores))

    def aplicar_sugerencia_busqueda(self, item):
        self.txt_busqueda.setText(item.text())
        self.lista_sugerencias.hide()
        self.cargar_productos()

    def _llenar_combo(self, combo, datos, llave_id, llave_texto, texto_inicial=None):
        combo.blockSignals(True)
        combo.clear()
        if texto_inicial is not None:
            combo.addItem(texto_inicial, None)
        for item in datos:
            combo.addItem(str(item.get(llave_texto, "")), item.get(llave_id))
        combo.blockSignals(False)

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

        self._actualizar_resumen()
        if self.productos:
            self.tabla.selectRow(0)
        else:
            self.limpiar_formulario()

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
            QMessageBox.warning(self, "Inventario", "Selecciona categoria, estado y proveedor.")
            return None

        try:
            precio = float((self.txt_precio.text().strip() or "0").replace(",", "."))
            stock = int(self.txt_stock.text().strip() or 0)
        except ValueError:
            QMessageBox.warning(self, "Inventario", "Precio y stock deben ser valores numericos.")
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

    def _actualizar_resumen(self):
        total = len(self.productos)
        stock_bajo = sum(1 for item in self.productos if self._a_entero(item.get("stock_actual")) <= 20)
        vencidos = sum(1 for item in self.productos if str(item.get("condicion") or "").lower() == "vencida")
        valor = sum(
            self._a_decimal(item.get("precio_venta_prod")) * self._a_decimal(item.get("stock_actual"))
            for item in self.productos
        )

        self.card_total.valor.setText(str(total))
        self.card_stock_bajo.valor.setText(str(stock_bajo))
        self.card_vencidos.valor.setText(str(vencidos))
        self.card_valor.valor.setText(self._formatear_moneda(valor))

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