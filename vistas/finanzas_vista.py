import os
from datetime import datetime, timedelta
from PySide6.QtCore import Qt, QDate, QStringListModel, QPoint
from PySide6.QtGui import QFont, QFontDatabase, QColor, QPainter, QBrush, QAction
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLineEdit, QComboBox, QTabWidget,
    QGraphicsDropShadowEffect, QGridLayout, QGroupBox,
    QDateEdit, QCompleter, QMenu, QSizePolicy
)

# Importar matplotlib para gráficas
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class FinanzasVista(QWidget):
    def __init__(self, controlador, conexion):
        super().__init__()
        self.controlador = controlador
        self.conexion = conexion
        self.datos_facturas = []
        self.tipo_actual = "VENTAS"
        self.filtro_fecha = "TODOS"
        self.COLOR_FONDO = "#F0F4F2"
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

        # ── NAVBAR ──
        navbar = QFrame()
        navbar.setObjectName("NavbarFinanzas")
        navbar.setFixedHeight(68)
        navbar.setStyleSheet("""
            QFrame#NavbarFinanzas { 
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
        lbl_titulo = QLabel("FINANZAS")
        lbl_titulo.setFont(QFont("Montserrat", 20, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent;")
        titulo_layout.addWidget(lbl_titulo)

        # Panel de usuario (derecha)
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

        # ── PESTAÑAS ──
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
                padding: 10px 30px;
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

    # ========== PÁGINA FACTURAS (con botones con flecha) ==========
    def crear_pagina_facturas(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # ── FILA DE FILTROS (botones con menú) ──
        filtros = QHBoxLayout()
        filtros.setSpacing(10)

        # Botón de tipo (VENTAS/COMPRAS) - ahora con flecha visible
        self.btn_tipo = QPushButton("VENTAS")
        self.btn_tipo.setFixedHeight(40)
        self.btn_tipo.setFixedWidth(120)
        self.btn_tipo.setFont(QFont("Montserrat", 11, QFont.Weight.Black))
        self.btn_tipo.setCursor(Qt.PointingHandCursor)
        self.btn_tipo.setStyleSheet("""
            QPushButton {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                color: #1F2937;
                padding: 0 15px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #FFFFFF;
                border: 2px solid #17813D;
            }
        """)
        menu_tipo = QMenu(self.btn_tipo)
        act_ventas = QAction("VENTAS", self.btn_tipo)
        act_ventas.triggered.connect(lambda: self.cambiar_tipo("VENTAS"))
        act_compras = QAction("COMPRAS", self.btn_tipo)
        act_compras.triggered.connect(lambda: self.cambiar_tipo("COMPRAS"))
        menu_tipo.addAction(act_ventas)
        menu_tipo.addAction(act_compras)
        self.btn_tipo.setMenu(menu_tipo)

        # Buscador con autocompletado
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por número, cliente...")
        self.txt_buscar.setFixedHeight(40)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 0 16px;
                font-family: 'Montserrat';
                font-size: 13px;
                color: #1F2937;
            }
            QLineEdit:focus { border: 2px solid #17813D; }
        """)
        self.txt_buscar.textChanged.connect(self.filtrar_facturas)
        self.completer_model = QStringListModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.txt_buscar.setCompleter(self.completer)
        self.cargar_sugerencias_busqueda()

        # Botón de fecha (TODOS) - con flecha visible
        self.btn_fecha = QPushButton("TODOS")
        self.btn_fecha.setFixedHeight(40)
        self.btn_fecha.setFixedWidth(150)
        self.btn_fecha.setFont(QFont("Montserrat", 11, QFont.Weight.Black))
        self.btn_fecha.setCursor(Qt.PointingHandCursor)
        self.btn_fecha.setStyleSheet("""
            QPushButton {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                color: #1F2937;
                padding: 0 15px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #FFFFFF;
                border: 2px solid #17813D;
            }
        """)
        menu_fecha = QMenu(self.btn_fecha)
        opciones_fecha = ["TODOS", "HOY", "ESTA SEMANA", "ESTE MES", "ESTE AÑO", "PERSONALIZADO"]
        for opcion in opciones_fecha:
            act = QAction(opcion, self.btn_fecha)
            act.triggered.connect(lambda checked, opt=opcion: self.cambiar_fecha(opt))
            menu_fecha.addAction(act)
        self.btn_fecha.setMenu(menu_fecha)

        # Selectores de fecha personalizada (ocultos inicialmente)
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate.currentDate())
        self.date_inicio.setFixedHeight(40)
        self.date_inicio.setFixedWidth(120)
        self.date_inicio.setStyleSheet("""
            QDateEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 0 10px;
                font-family: 'Montserrat';
                font-size: 12px;
                color: #1F2937;
            }
            QDateEdit:focus { border: 2px solid #17813D; }
        """)
        self.date_inicio.hide()

        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())
        self.date_fin.setFixedHeight(40)
        self.date_fin.setFixedWidth(120)
        self.date_fin.setStyleSheet("""
            QDateEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 0 10px;
                font-family: 'Montserrat';
                font-size: 12px;
                color: #1F2937;
            }
            QDateEdit:focus { border: 2px solid #17813D; }
        """)
        self.date_fin.hide()

        self.btn_aplicar_fechas = QPushButton("APLICAR")
        self.btn_aplicar_fechas.setFixedHeight(40)
        self.btn_aplicar_fechas.setFixedWidth(90)
        self.btn_aplicar_fechas.setFont(QFont("Montserrat", 10, QFont.Weight.Black))
        self.btn_aplicar_fechas.setCursor(Qt.PointingHandCursor)
        self.btn_aplicar_fechas.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        self.btn_aplicar_fechas.hide()
        self.btn_aplicar_fechas.clicked.connect(self.aplicar_filtro_fecha_personalizada)

        filtros.addWidget(self.btn_tipo)
        filtros.addWidget(self.txt_buscar, 1)
        filtros.addWidget(self.btn_fecha)
        filtros.addWidget(self.date_inicio)
        filtros.addWidget(self.date_fin)
        filtros.addWidget(self.btn_aplicar_fechas)
        layout.addLayout(filtros)

        # ── TABLA DE FACTURAS ──
        self.tabla_facturas = QTableWidget()
        self.tabla_facturas.setColumnCount(7)
        self.tabla_facturas.setHorizontalHeaderLabels([
            "N°", "Fecha", "Cliente/Proveedor", "Total", "Estado", "Tipo", ""
        ])
        self.tabla_facturas.setShowGrid(False)
        self.tabla_facturas.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_facturas.verticalHeader().setVisible(False)
        self.tabla_facturas.verticalHeader().setDefaultSectionSize(45)
        self.tabla_facturas.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_facturas.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_facturas.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla_facturas.setStyleSheet("""
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
                padding: 8px 12px;
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
                padding: 10px 12px;
                font-family: 'Montserrat';
            }
            QTableWidget QTableCornerButton::section {
                background: transparent;
                border: none;
            }
        """)
        header = self.tabla_facturas.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_facturas.setColumnWidth(0, 80)
        self.tabla_facturas.setColumnWidth(1, 130)
        self.tabla_facturas.setColumnWidth(2, 280)
        self.tabla_facturas.setColumnWidth(3, 120)
        self.tabla_facturas.setColumnWidth(4, 100)
        self.tabla_facturas.setColumnWidth(5, 80)
        self.tabla_facturas.setColumnWidth(6, 80)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)

        layout.addWidget(self.tabla_facturas, 1)

        self.cargar_facturas()
        return widget

    # ── Funciones de los botones de menú ──
    def cambiar_tipo(self, tipo):
        self.btn_tipo.setText(tipo)
        self.tipo_actual = tipo
        self.cargar_facturas()

    def cambiar_fecha(self, opcion):
        self.btn_fecha.setText(opcion)
        self.filtro_fecha = opcion
        # Mostrar u ocultar selectores de fecha personalizada
        es_personalizado = (opcion == "PERSONALIZADO")
        self.date_inicio.setVisible(es_personalizado)
        self.date_fin.setVisible(es_personalizado)
        self.btn_aplicar_fechas.setVisible(es_personalizado)
        if not es_personalizado:
            self.filtrar_facturas()

    def aplicar_filtro_fecha_personalizada(self):
        self.filtro_fecha = "PERSONALIZADO"
        self.filtrar_facturas()

    def obtener_fechas_filtro(self):
        hoy = QDate.currentDate()
        filtro = self.btn_fecha.text()
        if filtro == "HOY":
            inicio = hoy
            fin = hoy
        elif filtro == "ESTA SEMANA":
            dia_semana = hoy.dayOfWeek()
            inicio = hoy.addDays(-(dia_semana - 1))
            fin = hoy.addDays(7 - dia_semana)
        elif filtro == "ESTE MES":
            inicio = QDate(hoy.year(), hoy.month(), 1)
            fin = QDate(hoy.year(), hoy.month(), hoy.daysInMonth())
        elif filtro == "ESTE AÑO":
            inicio = QDate(hoy.year(), 1, 1)
            fin = QDate(hoy.year(), 12, 31)
        elif filtro == "PERSONALIZADO":
            inicio = self.date_inicio.date()
            fin = self.date_fin.date()
        else:
            return None, None
        return inicio, fin

    # ── Carga y filtrado de facturas ──
    def cargar_sugerencias_busqueda(self):
        if not self.conexion:
            return
        try:
            cursor = self.conexion.cursor()
            query = """
                SELECT DISTINCT 
                    CAST(f.id_factura AS CHAR) AS valor
                FROM facturas f
                UNION
                SELECT DISTINCT c.nombre_cliente
                FROM clientes c
                UNION
                SELECT DISTINCT p.nombre_empresa
                FROM proveedores p
                LIMIT 100
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            sugerencias = [str(row[0]) for row in resultados if row[0]]
            self.completer_model.setStringList(sugerencias)
            cursor.close()
        except Exception as e:
            print(f"Error cargando sugerencias: {e}")

    def cargar_facturas(self):
        tipo = self.btn_tipo.text()
        if tipo == "VENTAS":
            self.cargar_facturas_ventas()
        else:
            self.cargar_facturas_compras()
        self.cargar_sugerencias_busqueda()

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
            mock = [
                (11, datetime(2026, 6, 24), "N/A", 2000, "Pagada"),
                (10, datetime(2026, 6, 24), "N/A", 2000, "Pagada"),
                (9, datetime(2026, 6, 23, 23, 23), "edwin acosta", 4500, "Pagada"),
                (8, datetime(2026, 6, 23, 23, 23), "N/A", 4500, "Pagada"),
                (7, datetime(2024, 4, 8, 10, 10), "Ricardo Esteban Pinto", 19800, "Pagada"),
                (6, datetime(2024, 4, 5), "Camila Andrea Ospina", 27400, "Pagada"),
                (5, datetime(2024, 4, 2, 11, 20), "Pedro Antonio Vargas", 34500, "Pagada"),
                (4, datetime(2024, 3, 20), "Luisa Valentina Torres", 22700, "Pagada"),
                (3, datetime(2024, 3, 18), "Juan Pablo Martínez", 41700, "Pagada"),
                (2, datetime(2024, 3, 16, 14, 30), "María Fernanda López", 18500, "Pagada"),
                (1, datetime(2024, 3, 15, 10, 15), "Carlos Andrés Gómez", 26200, "Pagada"),
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
        if not self.conexion:
            return []
        try:
            cursor = self.conexion.cursor()
            cursor.execute(query, params or ())
            resultados = cursor.fetchall()
            cursor.close()
            if resultados and isinstance(resultados[0], dict):
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
            id_fact = registro[0]
            fecha = registro[1]
            cliente = registro[2] or "N/A"
            total = registro[3] or 0
            estado = registro[4] or "Pendiente"

            fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if hasattr(fecha, 'strftime') else str(fecha)
            total_str = f"${float(total):,.0f}" if total else "$0"

            item_id = QTableWidgetItem(str(id_fact))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            item_fecha = QTableWidgetItem(fecha_str)
            item_fecha.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item_cliente = QTableWidgetItem(cliente)
            item_cliente.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item_total = QTableWidgetItem(total_str)
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_estado = QTableWidgetItem(estado)
            item_estado.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            if estado == "Pagada":
                item_estado.setForeground(QColor("#008F39"))
            elif estado == "Pendiente":
                item_estado.setForeground(QColor("#EAB308"))
            else:
                item_estado.setForeground(QColor("#DC2626"))
            item_tipo = QTableWidgetItem(tipo)
            item_tipo.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

            btn_ver = QPushButton("VER")
            btn_ver.setFixedSize(60, 30)
            btn_ver.setFont(QFont("Montserrat", 9, QFont.Weight.Bold))
            btn_ver.setStyleSheet("""
                QPushButton {
                    background-color: #17813D;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #228E49;
                }
            """)
            btn_ver.clicked.connect(lambda checked, fid=id_fact, t=tipo: self.mostrar_detalle_por_id(fid, t))
            self.tabla_facturas.setCellWidget(fila, 6, btn_ver)

            self.tabla_facturas.setItem(fila, 0, item_id)
            self.tabla_facturas.setItem(fila, 1, item_fecha)
            self.tabla_facturas.setItem(fila, 2, item_cliente)
            self.tabla_facturas.setItem(fila, 3, item_total)
            self.tabla_facturas.setItem(fila, 4, item_estado)
            self.tabla_facturas.setItem(fila, 5, item_tipo)
            self.tabla_facturas.setRowHeight(fila, 45)

        self.filtrar_facturas()

    def filtrar_facturas(self):
        texto = self.txt_buscar.text().strip().lower()
        inicio, fin = self.obtener_fechas_filtro()
        for fila in range(self.tabla_facturas.rowCount()):
            mostrar = True
            if texto:
                coincide = False
                for col in range(5):
                    item = self.tabla_facturas.item(fila, col)
                    if item and texto in item.text().lower():
                        coincide = True
                        break
                mostrar = mostrar and coincide
            if mostrar and inicio and fin:
                item_fecha = self.tabla_facturas.item(fila, 1)
                if item_fecha:
                    try:
                        fecha_str = item_fecha.text().split()[0]
                        dia, mes, anio = map(int, fecha_str.split('/'))
                        fecha_qdate = QDate(anio, mes, dia)
                        if fecha_qdate < inicio or fecha_qdate > fin:
                            mostrar = False
                    except:
                        pass
            self.tabla_facturas.setRowHidden(fila, not mostrar)

    # ========== DIÁLOGO DE DETALLE (más grande) ==========
    def mostrar_detalle_por_id(self, id_factura, tipo):
        if tipo == "VENTA":
            self.mostrar_detalle_venta(id_factura)
        else:
            self.mostrar_detalle_compra(id_factura)

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
        row = enc[0]
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
            'cliente': cliente or "N/A",
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
            'cliente': proveedor or "N/A",
            'documento': nit or "N/A",
            'telefono': telefono or "N/A",
            'email': email or "N/A",
            'total': total or 0
        }, detalles, "COMPRA")

    def mostrar_dialogo_detalle(self, encabezado, detalles, tipo):
        dlg = QDialog(self, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dlg.setModal(True)
        dlg.setMinimumSize(800, 650)  # Más grande

        layout_fondo = QVBoxLayout(dlg)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("MainCard")
        card.setFixedSize(820, 680)  # Más grande
        card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 28px;
                border: 2px solid #D1E2D9;
            }
        """)
        sombra = QGraphicsDropShadowEffect(card)
        sombra.setBlurRadius(40)
        sombra.setColor(QColor(0, 0, 0, 50))
        sombra.setOffset(0, 10)
        card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(card)
        layout_card.setContentsMargins(40, 32, 40, 32)
        layout_card.setSpacing(16)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return font

        # HEADER
        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("DETALLE DE FACTURA")
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
        btn_cerrar.clicked.connect(dlg.accept)

        layout_header.addWidget(lbl_titulo)
        layout_header.addStretch()
        layout_header.addWidget(btn_cerrar)
        layout_card.addLayout(layout_header)

        # INFO
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
        info_text = f"""
            <b>Factura N°:</b> {encabezado['id']} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Fecha:</b> {encabezado['fecha'].strftime('%d/%m/%Y %H:%M') if hasattr(encabezado['fecha'], 'strftime') else encabezado['fecha']} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Tipo:</b> {tipo}
        """
        lbl_info = QLabel(info_text)
        lbl_info.setFont(_f(11, QFont.Weight.Medium))
        lbl_info.setStyleSheet("color: #1F2937; background: transparent;")
        info_layout.addWidget(lbl_info)

        info_cliente = f"""
            <b>Cliente:</b> {encabezado['cliente']} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Documento:</b> {encabezado['documento']} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Teléfono:</b> {encabezado['telefono']} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Email:</b> {encabezado['email']}
        """
        lbl_cliente = QLabel(info_cliente)
        lbl_cliente.setFont(_f(10, QFont.Weight.Medium))
        lbl_cliente.setStyleSheet("color: #6B7280; background: transparent;")
        info_layout.addWidget(lbl_cliente)
        layout_card.addWidget(info_frame)

        # TABLA PRODUCTOS
        lbl_productos = QLabel("PRODUCTOS DE LA FACTURA")
        lbl_productos.setFont(_f(11, QFont.Weight.Black))
        lbl_productos.setStyleSheet("color: #17813D; background: transparent;")
        layout_card.addWidget(lbl_productos)

        tabla_det = QTableWidget()
        if tipo == "VENTA":
            tabla_det.setColumnCount(4)
            tabla_det.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit.", "Subtotal"])
            if detalles:
                for fila, det in enumerate(detalles):
                    nombre, cant, precio, subtotal = det
                    tabla_det.insertRow(fila)
                    tabla_det.setItem(fila, 0, QTableWidgetItem(nombre))
                    tabla_det.setItem(fila, 1, QTableWidgetItem(str(cant)))
                    tabla_det.setItem(fila, 2, QTableWidgetItem(f"${float(precio):,.0f}"))
                    tabla_det.setItem(fila, 3, QTableWidgetItem(f"${float(subtotal):,.0f}"))
            else:
                tabla_det.insertRow(0)
                item = QTableWidgetItem("No hay productos registrados en esta factura")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabla_det.setSpan(0, 0, 1, 4)
                tabla_det.setItem(0, 0, item)
        else:
            tabla_det.setColumnCount(2)
            tabla_det.setHorizontalHeaderLabels(["Producto", "Cantidad"])
            if detalles:
                for fila, det in enumerate(detalles):
                    nombre, cant = det
                    tabla_det.insertRow(fila)
                    tabla_det.setItem(fila, 0, QTableWidgetItem(nombre))
                    tabla_det.setItem(fila, 1, QTableWidgetItem(str(cant)))
            else:
                tabla_det.insertRow(0)
                item = QTableWidgetItem("No hay productos registrados en esta factura")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabla_det.setSpan(0, 0, 1, 2)
                tabla_det.setItem(0, 0, item)

        tabla_det.setShowGrid(False)
        tabla_det.setFrameShape(QFrame.Shape.NoFrame)
        tabla_det.verticalHeader().setVisible(False)
        tabla_det.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla_det.setStyleSheet("""
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
        tabla_det.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_card.addWidget(tabla_det, 1)

        # TOTAL
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
        lbl_total_text = QLabel("TOTAL DE LA FACTURA:")
        lbl_total_text.setFont(_f(14, QFont.Weight.Black))
        lbl_total_text.setStyleSheet("color: #17813D; background: transparent;")
        lbl_total_valor = QLabel(f"${float(encabezado['total']):,.0f}")
        lbl_total_valor.setFont(_f(22, QFont.Weight.Black))
        lbl_total_valor.setStyleSheet("color: #17813D; background: transparent;")
        total_layout.addStretch()
        total_layout.addWidget(lbl_total_text)
        total_layout.addWidget(lbl_total_valor)
        total_layout.addStretch()
        layout_card.addWidget(total_frame)

        # BOTÓN CERRAR
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
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        btn_cerrar_dialog.clicked.connect(dlg.accept)
        layout_card.addWidget(btn_cerrar_dialog)

        layout_fondo.addWidget(card)
        dlg.exec()

    # ========== PÁGINA ÍNDICES (con gráficas) ==========
    def crear_pagina_indices(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        grid = QGridLayout()
        grid.setSpacing(20)

        # TOP 5 (tabla)
        top5 = self.crear_tarjeta_top5()
        grid.addWidget(top5, 0, 0)

        # BOTTOM 5 (tabla)
        bottom5 = self.crear_tarjeta_bottom5()
        grid.addWidget(bottom5, 0, 1)

        # Ventas por período (texto)
        ventas = self.crear_tarjeta_ventas_periodos()
        grid.addWidget(ventas, 1, 0, 1, 2)

        # Histórico mensual (gráfica de líneas)
        historico = self.crear_tarjeta_historico_mensual()
        grid.addWidget(historico, 2, 0, 1, 2)

        # Días de la semana (gráfica de barras)
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
        self.tabla_top5.setShowGrid(False)
        self.tabla_top5.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_top5.verticalHeader().setVisible(False)
        self.tabla_top5.setEditTriggers(QTableWidget.NoEditTriggers)
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
        self.tabla_bottom5.setShowGrid(False)
        self.tabla_bottom5.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_bottom5.verticalHeader().setVisible(False)
        self.tabla_bottom5.setEditTriggers(QTableWidget.NoEditTriggers)
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
        self.lbl_ventas_periodos.setStyleSheet("padding: 15px; background: #F8FAF9; border-radius: 12px; color: #1F2937;")
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
        # Crear figura y canvas
        self.fig_historico = Figure(figsize=(5, 3), dpi=100, facecolor='white')
        self.canvas_historico = FigureCanvas(self.fig_historico)
        self.canvas_historico.setMinimumHeight(250)
        self.canvas_historico.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.canvas_historico)
        return group

    def crear_tarjeta_dias_semana(self):
        group = QGroupBox("VENTAS POR DÍA DE LA SEMANA")
        group.setStyleSheet(self.estilo_grupo())
        layout = QVBoxLayout(group)
        self.fig_dias = Figure(figsize=(5, 3), dpi=100, facecolor='white')
        self.canvas_dias = FigureCanvas(self.fig_dias)
        self.canvas_dias.setMinimumHeight(250)
        self.canvas_dias.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.canvas_dias)
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
                outline: none;
                font-family: 'Montserrat';
                font-size: 11px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 6px 10px;
                border-bottom: 1px solid #F0F2F0;
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
                font-size: 10px;
                border: none;
                padding: 8px 10px;
                font-family: 'Montserrat';
            }
            QTableWidget QTableCornerButton::section {
                background: transparent;
                border: none;
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
                self.tabla_top5.setRowHeight(fila, 40)
        else:
            mock = [("Manzana Roja", 150), ("Leche Entera", 120), ("Arroz Blanco", 90)]
            for fila, (nombre, total) in enumerate(mock):
                self.tabla_top5.insertRow(fila)
                self.tabla_top5.setItem(fila, 0, QTableWidgetItem(nombre))
                self.tabla_top5.setItem(fila, 1, QTableWidgetItem(str(total)))
                self.tabla_top5.setRowHeight(fila, 40)

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
                self.tabla_bottom5.setRowHeight(fila, 40)
        else:
            mock = [("Zanahoria", 5), ("Yogur Fresa", 3), ("Shampoo", 2)]
            for fila, (nombre, total) in enumerate(mock):
                self.tabla_bottom5.insertRow(fila)
                self.tabla_bottom5.setItem(fila, 0, QTableWidgetItem(nombre))
                self.tabla_bottom5.setItem(fila, 1, QTableWidgetItem(str(total)))
                self.tabla_bottom5.setRowHeight(fila, 40)

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
            <b style="color:#17813D;">ÚLTIMA SEMANA:</b> <span style="font-size:16px; font-weight:bold;">${total_sem:,.0f}</span><br>
            <b style="color:#17813D;">ÚLTIMO MES:</b> <span style="font-size:16px; font-weight:bold;">${total_mes:,.0f}</span><br>
            <b style="color:#17813D;">ÚLTIMO AÑO:</b> <span style="font-size:16px; font-weight:bold;">${total_anio:,.0f}</span>
        """)

    def cargar_historico_mensual(self):
        query = """
            SELECT DATE_FORMAT(fecha_fac, '%Y-%m') AS mes, COALESCE(SUM(total_fac), 0) AS total
            FROM facturas
            GROUP BY mes
            ORDER BY mes ASC
        """
        datos = self.ejecutar_consulta(query)
        self.fig_historico.clear()
        ax = self.fig_historico.add_subplot(111)
        if datos:
            meses = [row[0] for row in datos]
            totales = [float(row[1]) for row in datos]
            ax.plot(meses, totales, marker='o', linestyle='-', color='#17813D', linewidth=2, markersize=5)
            # Decoración
            ax.set_facecolor('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#E2E8F0')
            ax.spines['bottom'].set_color('#E2E8F0')
            ax.tick_params(colors='#64748B', labelsize=9)
            ax.set_xlabel('Mes', color='#64748B', fontsize=9)
            ax.set_ylabel('Total Vendido', color='#64748B', fontsize=9)
            if len(meses) > 6:
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            self.fig_historico.tight_layout()
        else:
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', color='#9CA3AF', fontsize=12)
        self.canvas_historico.draw()

    def cargar_dias_semana(self):
        query = """
            SELECT DAYOFWEEK(fecha_fac) AS dia, COALESCE(SUM(total_fac), 0) AS total,
                   COUNT(*) AS num_facturas
            FROM facturas
            GROUP BY dia
            ORDER BY dia
        """
        datos = self.ejecutar_consulta(query)
        self.fig_dias.clear()
        ax = self.fig_dias.add_subplot(111)
        dias_nombres = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
        if datos:
            totales_por_dia = {i: 0 for i in range(1, 8)}
            for dia_num, total, num in datos:
                totales_por_dia[dia_num] = float(total)
            valores = [totales_por_dia[i] for i in range(1, 8)]
            ax.bar(dias_nombres, valores, color='#17813D', edgecolor='#A9DDBC', linewidth=1.5)
            ax.set_facecolor('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#E2E8F0')
            ax.spines['bottom'].set_color('#E2E8F0')
            ax.tick_params(colors='#64748B', labelsize=9)
            ax.set_ylabel('Total Vendido', color='#64748B', fontsize=9)
            self.fig_dias.tight_layout()
        else:
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', color='#9CA3AF', fontsize=12)
        self.canvas_dias.draw()