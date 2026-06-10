import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QFontDatabase

class CajaVista(QWidget):
    def __init__(self, controlador_flujo):
        super().__init__()
        self.controlador = controlador_flujo
        self.productos_venta = []
        self.total_actual = 0

        # --- PALETA DE COLORES (Identidad Palma / Tailwind Config) ---
        self.COLOR_FONDO = "#F4F7F5"
        self.COLOR_BRAND = "#1A7C3E"
        self.COLOR_BRAND_LIGHT = "#25A355"
        self.COLOR_MUTED = "#E8F5EE"
        self.COLOR_BORDE = "#D1E2D9"
        self.COLOR_TEXTO_OSCURO = "#1C2420"
        self.COLOR_PELIGRO = "#D66666"

        # --- CONFIGURACIÓN DE FUENTES ---
        ruta_vistas = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz = os.path.dirname(ruta_vistas)
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")

        for f in ("Montserrat-Bold.ttf", "Montserrat-Regular.ttf",
                  "Montserrat-Medium.ttf", "Montserrat-Black.ttf"):
            ruta_f = os.path.join(carpeta_fuentes, f)
            if os.path.exists(ruta_f):
                QFontDatabase.addApplicationFont(ruta_f)

        # --- CONFIGURACIÓN ESTÁTICA ---
        self.setObjectName("CajaModulo")
        self.setStyleSheet(f"QWidget#CajaModulo {{ background-color: {self.COLOR_FONDO}; }}")

        # Layout Principal de la Ventana
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        # 1. CONSTRUCCIÓN DE COMPONENTES
        self.inicializar_header()
        self.inicializar_cuerpo_pos()

    def inicializar_header(self):
        """Construye la barra superior idéntica a los dashboards corporativos."""
        self.frame_header = QFrame()
        self.frame_header.setFixedHeight(70)
        self.frame_header.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-bottom: 1px solid {self.COLOR_BORDE};
            }}
        """)
        layout_header = QHBoxLayout(self.frame_header)
        layout_header.setContentsMargins(40, 0, 40, 0)

        # Branding Izquierda
        lbl_logo = QLabel("PALMA")
        lbl_logo.setStyleSheet(f"font-family: 'Montserrat'; font-size: 24px; font-weight: 900; color: {self.COLOR_BRAND}; border: none;")
        layout_header.addWidget(lbl_logo)
        
        layout_header.addStretch()

        # Información del Cajero Activo
        container_perfil = QWidget()
        layout_perfil = QHBoxLayout(container_perfil)
        layout_perfil.setContentsMargins(0, 0, 0, 0)
        layout_perfil.setSpacing(12)

        container_texto = QWidget()
        layout_texto_user = QVBoxLayout(container_texto)
        layout_texto_user.setContentsMargins(0, 0, 0, 0)
        layout_texto_user.setSpacing(2)

        self.lbl_nombre_cajero = QLabel("Edwin Acosta")
        self.lbl_nombre_cajero.setStyleSheet(f"font-family: 'Montserrat'; font-size: 14px; font-weight: 700; color: {self.COLOR_TEXTO_OSCURO};")
        self.lbl_nombre_cajero.setAlignment(Qt.AlignmentFlag.AlignRight)

        lbl_rol = QLabel("Cajero de Turno")
        lbl_rol.setStyleSheet("font-family: 'Montserrat'; font-size: 11px; font-weight: 500; color: #708077;")
        lbl_rol.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout_texto_user.addWidget(self.lbl_nombre_cajero)
        layout_texto_user.addWidget(lbl_rol)

        self.lbl_avatar = QLabel("EA")
        self.lbl_avatar.setFixedSize(42, 42)
        self.lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {self.COLOR_MUTED};
                border: 2px solid {self.COLOR_BRAND};
                border-radius: 21px;
                font-family: 'Montserrat';
                font-size: 14px;
                font-weight: 700;
                color: {self.COLOR_BRAND};
            }}
        """)

        # Botón Volver Minimalista (Estilo '✕')
        btn_volver = QPushButton("✕")
        btn_volver.setFixedSize(36, 36)
        btn_volver.setStyleSheet(f"""
            QPushButton {{
                background-color: #F4F7F5;
                border: 1px solid {self.COLOR_BORDE};
                border-radius: 8px;
                font-family: 'Montserrat';
                font-size: 14px;
                font-weight: 700;
                color: {self.COLOR_TEXTO_OSCURO};
            }}
            QPushButton:hover {{
                background-color: #FDF2F2;
                color: {self.COLOR_PELIGRO};
                border-color: #F2DEDE;
            }}
        """)
        btn_volver.clicked.connect(self.volver_dashboard)

        layout_perfil.addWidget(container_texto)
        layout_perfil.addWidget(self.lbl_avatar)
        layout_perfil.addWidget(btn_volver)
        layout_header.addWidget(container_perfil)

        self.layout_principal.addWidget(self.frame_header)

    def inicializar_cuerpo_pos(self):
        """Distribuye la pantalla en el esquema POS de dos paneles de alta fidelidad."""
        container_cuerpo = QWidget()
        layout_cuerpo = QHBoxLayout(container_cuerpo)
        layout_cuerpo.setContentsMargins(40, 30, 40, 30)
        layout_cuerpo.setSpacing(30)

        # ==========================================
        # PANEL IZQUIERDO: Búsqueda y Tabla de Items
        # ==========================================
        panel_izquierdo = QFrame()
        panel_izquierdo.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {self.COLOR_BORDE};
                border-radius: 12px;
            }}
        """)
        layout_izq = QVBoxLayout(panel_izquierdo)
        layout_izq.setContentsMargins(24, 24, 24, 24)
        layout_izq.setSpacing(20)

        # Barra de Entrada / Filtro Automático
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Escribe el nombre del producto o código de barras...")
        self.txt_buscar.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FFFFFF;
                border: 1px solid {self.COLOR_BORDE};
                border-radius: 8px;
                padding: 12px 16px;
                font-family: 'Montserrat';
                font-size: 14px;
                color: {self.COLOR_TEXTO_OSCURO};
            }}
            QLineEdit:focus {{
                border: 2px solid {self.COLOR_BRAND};
            }}
        """)

        # Tabla de Productos en Venta
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels(["Producto", "Precio", "Cant.", "Total", "Acción"])
        self.tabla_productos.setStyleSheet(f"""
            QTableWidget {{
                background-color: #FFFFFF;
                border: none;
                gridline-color: #F4F7F5;
                font-family: 'Montserrat';
                font-size: 13px;
                color: {self.COLOR_TEXTO_OSCURO};
            }}
            QHeaderView::section {{
                background-color: #F4F7F5;
                color: #55635A;
                padding: 12px 8px;
                font-weight: 700;
                font-size: 12px;
                border: none;
                border-bottom: 2px solid {self.COLOR_BORDE};
                text-transform: uppercase;
            }}
        """)
        
        # Configuración elástica de columnas
        header = self.tabla_productos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_productos.verticalHeader().setVisible(False)

        layout_izq.addWidget(self.txt_buscar)
        layout_izq.addWidget(self.tabla_productos)
        layout_cuerpo.addWidget(panel_izquierdo, stretch=65)

        # ==========================================
        # PANEL DERECHO: Liquidación, Totales y Cobro
        # ==========================================
        panel_derecho = QFrame()
        panel_derecho.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {self.COLOR_BORDE};
                border-radius: 12px;
            }}
        """)
        layout_der = QVBoxLayout(panel_derecho)
        layout_der.setContentsMargins(24, 24, 24, 24)
        layout_der.setSpacing(24)

        lbl_titulo_resumen = QLabel("RESUMEN DE VENTA")
        lbl_titulo_resumen.setStyleSheet(f"font-family: 'Montserrat'; font-size: 14px; font-weight: 800; color: #55635A; letter-spacing: 0.5px;")

        # Visor del TOTAL Macizo (Estilo Caja Registradora)
        container_total = QFrame()
        container_total.setStyleSheet(f"background-color: {self.COLOR_MUTED}; border: 1px solid #B6DFC6; border-radius: 8px;")
        layout_total_box = QVBoxLayout(container_total)
        layout_total_box.setContentsMargins(16, 16, 16, 16)
        layout_total_box.setSpacing(4)

        lbl_total_tag = QLabel("TOTAL A COBRAR")
        lbl_total_tag.setStyleSheet(f"font-family: 'Montserrat'; font-size: 11px; font-weight: 700; color: {self.COLOR_BRAND};")
        
        self.lbl_total_display = QLabel("$0")
        self.lbl_total_display.setStyleSheet(f"font-family: 'Montserrat'; font-size: 36px; font-weight: 900; color: {self.COLOR_BRAND};")
        self.lbl_total_display.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout_total_box.addWidget(lbl_total_tag)
        layout_total_box.addWidget(self.lbl_total_display)

        # Sección: Efectivo Recibido
        container_efectivo = QWidget()
        layout_efectivo_field = QVBoxLayout(container_efectivo)
        layout_efectivo_field.setContentsMargins(0, 0, 0, 0)
        layout_efectivo_field.setSpacing(8)

        lbl_efectivo_tag = QLabel("EFECTIVO RECIBIDO")
        lbl_efectivo_tag.setStyleSheet(f"font-family: 'Montserrat'; font-size: 12px; font-weight: 700; color: {self.COLOR_TEXTO_OSCURO};")

        self.txt_efectivo = QLineEdit()
        self.txt_efectivo.setPlaceholderText("$ 0.00")
        self.txt_efectivo.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FFFFFF;
                border: 1px solid {self.COLOR_BORDE};
                border-radius: 8px;
                padding: 14px;
                font-family: 'Montserrat';
                font-size: 18px;
                font-weight: 700;
                color: {self.COLOR_TEXTO_OSCURO};
            }}
            QLineEdit:focus {{
                border: 2px solid {self.COLOR_BRAND};
            }}
        """)
        self.txt_efectivo.textChanged.connect(self.actualizar_cambio)
        layout_efectivo_field.addWidget(lbl_efectivo_tag)
        layout_efectivo_field.addWidget(self.txt_efectivo)

        # Sección: Cambio a Devolver
        container_cambio = QWidget()
        layout_cambio_field = QVBoxLayout(container_cambio)
        layout_cambio_field.setContentsMargins(0, 0, 0, 0)
        layout_cambio_field.setSpacing(4)

        lbl_cambio_tag = QLabel("CAMBIO A DEVOLVER")
        lbl_cambio_tag.setStyleSheet("font-family: 'Montserrat'; font-size: 11px; font-weight: 700; color: #708077;")

        self.lbl_cambio_display = QLabel("$0")
        self.lbl_cambio_display.setStyleSheet(f"font-family: 'Montserrat'; font-size: 24px; font-weight: 800; color: {self.COLOR_TEXTO_OSCURO};")
        layout_cambio_field.addWidget(lbl_cambio_tag)
        layout_cambio_field.addWidget(self.lbl_cambio_display)

        # Botón de Acción Masiva: COBRAR
        self.btn_cobrar = QPushButton("PROCESAR COBRO (ENTER)")
        self.btn_cobrar.setMinimumHeight(55)
        self.btn_cobrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_BRAND};
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-family: 'Montserrat';
                font-size: 14px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {self.COLOR_BRAND_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {self.COLOR_BRAND};
            }}
        """)
        self.btn_cobrar.clicked.connect(self.ejecutar_cobro)

        # Armado del Panel Derecho
        layout_der.addWidget(lbl_titulo_resumen)
        layout_der.addWidget(container_total)
        layout_der.addWidget(container_efectivo)
        layout_der.addWidget(container_cambio)
        layout_der.addStretch()
        layout_der.addWidget(self.btn_cobrar)

        layout_cuerpo.addWidget(panel_derecho, stretch=35)
        self.layout_principal.addWidget(container_cuerpo)

        # Render inicial por si hay datos residuales en memoria
        self.renderizar_tabla()

    # ==========================================
    # LÓGICA DE CONTROL INTERNA (Preservada)
    # ==========================================
    def renderizar_tabla(self):
        """Pinta dinámicamente las filas de productos respetando el look minimalista."""
        self.tabla_productos.setRowCount(0)
        self.total_actual = 0

        for idx, item in enumerate(self.productos_venta):
            # item esperado: dict {'id': 1, 'nombre': 'Manzana', 'precio': 2500, 'cantidad': 2}
            nombre = item.get('nombre', 'Producto')
            precio = item.get('precio', 0)
            cantidad = item.get('cantidad', 1)
            subtotal = precio * cantidad
            self.total_actual += subtotal

            row = self.tabla_productos.rowCount()
            self.tabla_productos.insertRow(row)

            # Celdas estilizadas
            item_nombre = QTableWidgetItem(str(nombre))
            item_nombre.setFlags(Qt.ItemFlag.ItemIsEnabled)
            
            item_precio = QTableWidgetItem(f"${precio:,}")
            item_precio.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_cantidad = QTableWidgetItem(str(cantidad))
            item_cantidad.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_cantidad.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_subtotal = QTableWidgetItem(f"${subtotal:,}")
            item_subtotal.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # Botón Eliminar Fila
            btn_eliminar = QPushButton("✕")
            btn_eliminar.setFixedSize(24, 24)
            btn_eliminar.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FDF2F2;
                    border: none;
                    border-radius: 4px;
                    color: {self.COLOR_PELIGRO};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.COLOR_PELIGRO};
                    color: #FFFFFF;
                }}
            """)
            btn_eliminar.clicked.connect(lambda checked, i=idx: self.eliminar_item(i))

            self.tabla_productos.setItem(row, 0, item_nombre)
            self.tabla_productos.setItem(row, 1, item_precio)
            self.tabla_productos.setItem(row, 2, item_cantidad)
            self.tabla_productos.setItem(row, 3, item_subtotal)
            self.tabla_productos.setCellWidget(row, 4, btn_eliminar)

        # Actualizar visor maestro de precios
        self.lbl_total_display.setText(f"${self.total_actual:,}")
        self.actualizar_cambio()

    def eliminar_item(self, indice):
        """Remueve un elemento del listado actual."""
        if 0 <= indice < len(self.productos_venta):
            self.productos_venta.pop(indice)
            self.renderizar_tabla()

    def actualizar_cambio(self):
        """Calcula el cambio en tiempo real eliminando caracteres de formateo."""
        try:
            texto = self.txt_efectivo.text().replace(".", "").replace(",", "").replace("$", "").strip()
            efectivo = int(texto) if texto else 0
        except ValueError:
            efectivo = 0

        if efectivo >= self.total_actual and self.total_actual > 0:
            cambio = efectivo - self.total_actual
            self.lbl_cambio_display.setText(f"${cambio:,}")
            self.lbl_cambio_display.setStyleSheet(f"font-family: 'Montserrat'; font-size: 24px; font-weight: 800; color: {self.COLOR_BRAND};")
        else:
            self.lbl_cambio_display.setText("$0")
            self.lbl_cambio_display.setStyleSheet(f"font-family: 'Montserrat'; font-size: 24px; font-weight: 800; color: {self.COLOR_TEXTO_OSCURO};")

    def ejecutar_cobro(self):
        """Valida el pago y procesa la transacción."""
        try:
            texto = self.txt_efectivo.text().replace(".", "").replace(",", "").replace("$", "").strip()
            efectivo = int(texto) if texto else 0
        except ValueError:
            efectivo = 0

        if self.total_actual == 0:
            QMessageBox.warning(self, "Cobro", "No hay productos en la lista actual.")
            return
        if efectivo < self.total_actual:
            QMessageBox.warning(self, "Cobro", "El efectivo ingresado es insuficiente.")
            return

        cambio = efectivo - self.total_actual
        QMessageBox.information(
            self, "Éxito",
            f"COBRO EXITOSO\n\nTotal: ${self.total_actual:,}\nCambio: ${cambio:,}"
        )
        
        # Reset de la interfaz de venta
        self.productos_venta = []
        self.txt_efectivo.clear()
        self.renderizar_tabla()

    def volver_dashboard(self):
        """Regresa con seguridad al área del Dashboard correspondiente a través del ruteador central."""
        self.controlador.cambiar_pantalla("AdminDashboard")