import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QGraphicsDropShadowEffect, QStackedLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QFontDatabase


class CajaVista(QWidget):
    def __init__(self, controlador_flujo):
        super().__init__()
        self.controlador = controlador_flujo
        self.productos_venta = []
        self.total_actual = 0

        ruta_vistas = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz = os.path.dirname(ruta_vistas)
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")

        QFontDatabase.addApplicationFont(os.path.join(carpeta_fuentes, "Montserrat-Bold.ttf"))
        QFontDatabase.addApplicationFont(os.path.join(carpeta_fuentes, "Montserrat-Regular.ttf"))
        QFontDatabase.addApplicationFont(os.path.join(carpeta_fuentes, "Montserrat-Medium.ttf"))

        self.fuente_heavy = QFont("Montserrat", 34, QFont.Weight.Bold)
        self.fuente_heavy.setHintingPreference(QFont.HintingPreference.PreferNoHinting)

        self.fuente_titulos = QFont("Montserrat", 25, QFont.Weight.Bold)
        self.fuente_titulos.setHintingPreference(QFont.HintingPreference.PreferNoHinting)

        self.fuente_normal = QFont("Montserrat", 11, QFont.Weight.Medium)
        self.fuente_tags = QFont("Montserrat", 9, QFont.Weight.Bold)

        self.COLOR_FONDO = "#F4F7F5"
        self.BRAND_DEFAULT = "#17813D"
        self.BRAND_LIGHT = "#228E49"
        self.BRAND_MUTED = "#E9F7EF"
        self.BRAND_BORDER = "#A9DDBC"
        self.DANGER_DEFAULT = "#DC6468"
        self.DANGER_LIGHT = "#FDEEEF"

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(12, 13, 12, 13)
        layout_principal.setSpacing(0)

        self.contenedor_blanco = QFrame()
        self.contenedor_blanco.setObjectName("ContenedorCaja")
        self.contenedor_blanco.setStyleSheet("""
            QFrame#ContenedorCaja {
                background-color: #FFFFFF;
                border: 1px solid #B8E3C8;
                border-radius: 14px;
            }
        """)

        sombra_general = QGraphicsDropShadowEffect(self)
        sombra_general.setBlurRadius(18)
        sombra_general.setColor(QColor(23, 129, 61, 35))
        sombra_general.setOffset(0, 4)
        self.contenedor_blanco.setGraphicsEffect(sombra_general)

        layout_contenedor = QVBoxLayout(self.contenedor_blanco)
        layout_contenedor.setContentsMargins(0, 0, 0, 0)
        layout_contenedor.setSpacing(0)

        navbar = QFrame()
        navbar.setObjectName("NavbarCaja")
        navbar.setFixedHeight(74)
        navbar.setStyleSheet(
            "QFrame#NavbarCaja { background-color: #FFFFFF; border: none; border-bottom: 1px solid #EEF0F2; }"
        )

        layout_navbar = QHBoxLayout(navbar)
        layout_navbar.setContentsMargins(0, 0, 25, 0)
        layout_navbar.setSpacing(0)

        layout_pestanas = QHBoxLayout()
        layout_pestanas.setSpacing(0)

        estilo_pestana_activa = f"""
            QPushButton {{
                background-color: transparent;
                color: {self.BRAND_DEFAULT};
                font-family: 'Montserrat', sans-serif;
                font-size: 11px;
                font-weight: 900;
                border: none;
                border-bottom: 4px solid {self.BRAND_DEFAULT};
                padding: 0px 34px;
                text-transform: uppercase;
                height: 74px;
            }}
        """

        estilo_pestana_inactiva = f"""
            QPushButton {{
                background-color: transparent;
                color: #9CA3AF;
                font-family: 'Montserrat', sans-serif;
                font-size: 11px;
                font-weight: 800;
                border: none;
                border-bottom: 4px solid transparent;
                padding: 0px 33px;
                text-transform: uppercase;
                height: 74px;
            }}
            QPushButton:hover {{
                color: {self.BRAND_DEFAULT};
            }}
        """

        btn_tab_caja = QPushButton("Caja")
        btn_tab_caja.setStyleSheet(estilo_pestana_activa)

        btn_tab_factura = QPushButton("Factura\nElectrónica")
        btn_tab_factura.setStyleSheet(estilo_pestana_inactiva)

        btn_tab_devoluciones = QPushButton("Devoluciones")
        btn_tab_devoluciones.setStyleSheet(estilo_pestana_inactiva)

        btn_tab_proveedores = QPushButton("Recibo\nProveedores")
        btn_tab_proveedores.setStyleSheet(estilo_pestana_inactiva)

        layout_pestanas.addWidget(btn_tab_caja)
        layout_pestanas.addWidget(btn_tab_factura)
        layout_pestanas.addWidget(btn_tab_devoluciones)
        layout_pestanas.addWidget(btn_tab_proveedores)

        layout_usuario_acciones = QHBoxLayout()
        layout_usuario_acciones.setSpacing(16)

        widget_perfil = QFrame()
        widget_perfil.setStyleSheet("background: transparent; border: none;")

        layout_perfil = QHBoxLayout(widget_perfil)
        layout_perfil.setContentsMargins(0, 0, 0, 0)
        layout_perfil.setSpacing(10)

        layout_meta_usuario = QVBoxLayout()
        layout_meta_usuario.setSpacing(1)
        layout_meta_usuario.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_nombre_cajero = QLabel("Edwin Acosta")
        self.lbl_nombre_cajero.setFont(self.fuente_tags)
        self.lbl_nombre_cajero.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_nombre_cajero.setStyleSheet(
            f"color: {self.BRAND_DEFAULT}; background: transparent; font-weight: 900; font-size: 11px;"
        )

        lbl_rol = QLabel("CAJERO")
        lbl_rol.setFont(QFont("Montserrat", 8, QFont.Weight.Bold))
        lbl_rol.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl_rol.setStyleSheet("color: #9CA3AF; background: transparent;")

        layout_meta_usuario.addWidget(self.lbl_nombre_cajero)
        layout_meta_usuario.addWidget(lbl_rol)

        self.lbl_avatar = QLabel("EA")
        self.lbl_avatar.setFixedSize(38, 38)
        self.lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {self.BRAND_MUTED};
                border: 1px solid {self.BRAND_BORDER};
                border-radius: 19px;
                color: {self.BRAND_DEFAULT};
                font-family: 'Montserrat';
                font-weight: 800;
                font-size: 11px;
            }}
        """)

        layout_perfil.addLayout(layout_meta_usuario)
        layout_perfil.addWidget(self.lbl_avatar)

        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.setFixedSize(103, 35)
        btn_logout.setFont(QFont("Montserrat", 8, QFont.Weight.Bold))
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #DC2626;
                border: 1px solid #FEE2E2;
                border-radius: 9px;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: #FFFFFF;
            }
        """)
        btn_logout.clicked.connect(self.cerrar_sesion)

        btn_salir = QPushButton("X")
        btn_salir.setFixedSize(40, 40)
        btn_salir.setFont(QFont("Montserrat", 13, QFont.Weight.Black))
        btn_salir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salir.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {self.BRAND_DEFAULT};
                border: 1px solid #E5E7EB;
                border-radius: 11px;
            }}
            QPushButton:hover {{
                background-color: {self.DANGER_LIGHT};
                color: {self.DANGER_DEFAULT};
                border: 1px solid #FCA5A5;
            }}
        """)
        btn_salir.clicked.connect(self.volver_dashboard)

        layout_usuario_acciones.addWidget(widget_perfil)
        layout_usuario_acciones.addWidget(btn_logout)
        layout_usuario_acciones.addWidget(btn_salir)

        layout_navbar.addLayout(layout_pestanas)
        layout_navbar.addStretch()
        layout_navbar.addLayout(layout_usuario_acciones)

        layout_contenedor.addWidget(navbar)

        cuerpo_central = QHBoxLayout()
        cuerpo_central.setContentsMargins(0, 0, 0, 0)
        cuerpo_central.setSpacing(0)

        panel_cobros = QFrame()
        panel_cobros.setObjectName("PanelCobros")
        panel_cobros.setFixedWidth(320)
        panel_cobros.setStyleSheet(
            "QFrame#PanelCobros { background-color: #FBFCFC; border: none; border-right: 1px solid #EEF0F2; }"
        )

        layout_panel = QVBoxLayout(panel_cobros)
        layout_panel.setContentsMargins(24, 24, 24, 24)
        layout_panel.setSpacing(20)

        card_total = QFrame()
        card_total.setObjectName("CardTotal")
        card_total.setFixedHeight(123)
        card_total.setStyleSheet(
            f"QFrame#CardTotal {{ background-color: {self.BRAND_DEFAULT}; border: none; border-radius: 24px; }}"
        )

        sombra_total = QGraphicsDropShadowEffect(self)
        sombra_total.setBlurRadius(16)
        sombra_total.setColor(QColor(23, 129, 61, 55))
        sombra_total.setOffset(0, 7)
        card_total.setGraphicsEffect(sombra_total)

        layout_card_total = QVBoxLayout(card_total)
        layout_card_total.setContentsMargins(27, 27, 24, 20)
        layout_card_total.setSpacing(0)

        lbl_title_total = QLabel("TOTAL A PAGAR:")
        lbl_title_total.setFont(self.fuente_tags)
        lbl_title_total.setStyleSheet(
            "color: #FFFFFF; background: transparent; border: none; letter-spacing: 1px;"
        )

        self.lbl_display_total = QLabel("$0")
        self.lbl_display_total.setFont(self.fuente_heavy)
        self.lbl_display_total.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")

        layout_card_total.addWidget(lbl_title_total)
        layout_card_total.addWidget(self.lbl_display_total)

        card_efectivo = QFrame()
        card_efectivo.setObjectName("CardEfectivo")
        card_efectivo.setFixedHeight(119)
        card_efectivo.setStyleSheet(
            f"QFrame#CardEfectivo {{ background-color: #FFFFFF; border: 2px solid {self.BRAND_BORDER}; border-radius: 24px; }}"
        )

        layout_card_efectivo = QVBoxLayout(card_efectivo)
        layout_card_efectivo.setContentsMargins(27, 27, 24, 18)
        layout_card_efectivo.setSpacing(0)

        lbl_title_efectivo = QLabel("EFECTIVO:")
        lbl_title_efectivo.setFont(self.fuente_tags)
        lbl_title_efectivo.setStyleSheet(
            f"color: {self.BRAND_DEFAULT}; background: transparent; border: none; letter-spacing: 1px;"
        )

        self.txt_efectivo = QLineEdit()
        self.txt_efectivo.setPlaceholderText("0")
        self.txt_efectivo.setFont(self.fuente_heavy)
        self.txt_efectivo.setFixedHeight(48)
        self.txt_efectivo.setStyleSheet(
            "QLineEdit { color: #99A1B2; background: transparent; border: none; padding: 0px; }"
        )
        self.txt_efectivo.textChanged.connect(self.actualizar_cambio)

        layout_card_efectivo.addWidget(lbl_title_efectivo)
        layout_card_efectivo.addWidget(self.txt_efectivo)

        card_cambio = QFrame()
        card_cambio.setObjectName("CardCambio")
        card_cambio.setFixedHeight(118)
        card_cambio.setStyleSheet(
            f"QFrame#CardCambio {{ background-color: {self.DANGER_LIGHT}; border: 2px solid #F8CBCD; border-radius: 24px; }}"
        )

        layout_card_cambio = QVBoxLayout(card_cambio)
        layout_card_cambio.setContentsMargins(27, 28, 24, 18)
        layout_card_cambio.setSpacing(0)

        lbl_title_cambio = QLabel("CAMBIO:")
        lbl_title_cambio.setFont(self.fuente_tags)
        lbl_title_cambio.setStyleSheet(
            f"color: {self.DANGER_DEFAULT}; background: transparent; border: none; letter-spacing: 1px;"
        )

        self.lbl_display_cambio = QLabel("$0")
        self.lbl_display_cambio.setFont(self.fuente_heavy)
        self.lbl_display_cambio.setStyleSheet(
            f"color: {self.DANGER_DEFAULT}; background: transparent; border: none;"
        )

        layout_card_cambio.addWidget(lbl_title_cambio)
        layout_card_cambio.addWidget(self.lbl_display_cambio)

        layout_panel.addWidget(card_total)
        layout_panel.addWidget(card_efectivo)
        layout_panel.addStretch()
        layout_panel.addWidget(card_cambio)

        area_tabla = QFrame()
        area_tabla.setObjectName("AreaFacturacion")
        area_tabla.setStyleSheet("QFrame#AreaFacturacion { border: none; background-color: #FFFFFF; }")

        layout_area_tabla = QVBoxLayout(area_tabla)
        layout_area_tabla.setContentsMargins(32, 22, 40, 20)
        layout_area_tabla.setSpacing(17)

        lbl_titulo_seccion = QLabel("FACTURACIÓN")
        lbl_titulo_seccion.setFont(self.fuente_titulos)
        lbl_titulo_seccion.setFixedHeight(56)
        lbl_titulo_seccion.setStyleSheet(
            f"color: {self.BRAND_DEFAULT}; font-weight: 900; letter-spacing: 0px; background: transparent;"
        )

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels([
            "ID",
            "NOMBRE DEL PRODUCTO",
            "CANTIDAD/PESO",
            "PRECIO UNITARIO"
        ])

        self.tabla_productos.horizontalHeaderItem(0).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.tabla_productos.horizontalHeaderItem(1).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.tabla_productos.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabla_productos.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.tabla_productos.verticalHeader().setDefaultSectionSize(54)
        self.tabla_productos.verticalHeader().setVisible(False)
        self.tabla_productos.setShowGrid(False)
        self.tabla_productos.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_productos.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: transparent;
                background-color: #FFFFFF;
                outline: none;
            }
            QTableWidget::item {
                border-bottom: 1px solid #EEF0F2;
                color: #1F2937;
                font-family: 'Montserrat';
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #E8F5EE;
                color: #1A7C3E;
            }
        """)

        header = self.tabla_productos.horizontalHeader()
        header.setFixedHeight(43)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #FFFFFF;
                color: #86B896;
                font-family: 'Montserrat';
                font-size: 11px;
                font-weight: 800;
                border: none;
                border-bottom: 1px solid #EEF0F2;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                padding-left: 0px;
                padding-right: 0px;
            }
        """)

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)

        self.tabla_productos.setColumnWidth(0, 58)
        self.tabla_productos.setColumnWidth(1, 743)
        self.tabla_productos.setColumnWidth(3, 220)

        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_productos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.lbl_estado_tabla = QLabel("ESPERANDO PRODUCTOS...")
        self.lbl_estado_tabla.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.lbl_estado_tabla.setStyleSheet("""
            QLabel {
                color: #DFE3E8;
                background: transparent;
                font-family: 'Montserrat';
                font-size: 12px;
                font-style: italic;
                font-weight: 700;
                padding-top: 84px;
            }
        """)

        table_shell = QFrame()
        table_shell.setObjectName("TablaShell")
        table_shell.setStyleSheet("QFrame#TablaShell { background-color: #FFFFFF; border: none; }")

        self.table_stack = QStackedLayout(table_shell)
        self.table_stack.setContentsMargins(0, 0, 0, 0)
        self.table_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.table_stack.addWidget(self.tabla_productos)
        self.table_stack.addWidget(self.lbl_estado_tabla)

        layout_area_tabla.addWidget(lbl_titulo_seccion)
        layout_area_tabla.addWidget(table_shell, 1)

        cuerpo_central.addWidget(panel_cobros)
        cuerpo_central.addWidget(area_tabla)

        layout_contenedor.addLayout(cuerpo_central, 1)

        barra_inferior = QFrame()
        barra_inferior.setObjectName("BarraInferiorCaja")
        barra_inferior.setFixedHeight(102)
        barra_inferior.setStyleSheet(
            "QFrame#BarraInferiorCaja { border: none; border-top: 1px solid #EEF0F2; background-color: #FFFFFF; }"
        )

        layout_inferior = QHBoxLayout(barra_inferior)
        layout_inferior.setContentsMargins(33, 0, 32, 0)

        self.btn_cobrar = QPushButton("COBRAR")
        self.btn_cobrar.setFixedSize(222, 60)
        self.btn_cobrar.setFont(QFont("Montserrat", 14, QFont.Weight.Black))
        self.btn_cobrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cobrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.BRAND_DEFAULT};
                color: #FFFFFF;
                border: none;
                border-radius: 16px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: {self.BRAND_LIGHT};
            }}
        """)

        sombra_cobrar = QGraphicsDropShadowEffect(self)
        sombra_cobrar.setBlurRadius(12)
        sombra_cobrar.setColor(QColor(23, 129, 61, 50))
        sombra_cobrar.setOffset(0, 5)
        self.btn_cobrar.setGraphicsEffect(sombra_cobrar)
        self.btn_cobrar.clicked.connect(self.ejecutar_cobro)

        layout_botones_secundarios = QHBoxLayout()
        layout_botones_secundarios.setSpacing(17)

        estilo_btn_secundario = """
            QPushButton {
                background-color: #FFFFFF;
                color: #9CA3AF;
                border: 2px solid #F0F1F4;
                border-radius: 15px;
                padding: 0px 25px;
                min-height: 49px;
                font-family: 'Montserrat';
                font-size: 11px;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #FAFBFB;
                color: #1A7C3E;
                border-color: #B6DFC6;
            }
        """

        btn_agregar = QPushButton("Agregar")
        btn_agregar.setFixedSize(139, 52)
        btn_agregar.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {self.BRAND_DEFAULT};
                border: 2px solid {self.BRAND_BORDER};
                border-radius: 15px;
                padding: 0px 25px;
                min-height: 49px;
                font-family: 'Montserrat';
                font-size: 11px;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {self.BRAND_MUTED};
            }}
        """)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setFixedSize(141, 52)
        btn_eliminar.setStyleSheet(estilo_btn_secundario)

        btn_modificar = QPushButton("Modificar")
        btn_modificar.setFixedSize(153, 52)
        btn_modificar.setStyleSheet(estilo_btn_secundario)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.setFixedSize(129, 52)
        btn_buscar.setStyleSheet(estilo_btn_secundario)

        btn_agregar.clicked.connect(self.agregar_producto_mock)
        btn_eliminar.clicked.connect(self.eliminar_producto_seleccionado)

        layout_botones_secundarios.addWidget(btn_agregar)
        layout_botones_secundarios.addWidget(btn_eliminar)
        layout_botones_secundarios.addWidget(btn_modificar)
        layout_botones_secundarios.addWidget(btn_buscar)

        layout_inferior.addWidget(self.btn_cobrar)
        layout_inferior.addStretch()
        layout_inferior.addLayout(layout_botones_secundarios)

        layout_contenedor.addWidget(barra_inferior)
        layout_principal.addWidget(self.contenedor_blanco)

    def showEvent(self, event):
        self.renderizar_tabla()
        super().showEvent(event)

    def renderizar_tabla(self):
        self.tabla_productos.setRowCount(0)
        self.total_actual = 0

        for p in self.productos_venta:
            self.total_actual += p["precio"] * p["cantidad"]
            row = self.tabla_productos.rowCount()
            self.tabla_productos.insertRow(row)

            item_id = QTableWidgetItem(str(p["id"]))
            item_id.setFont(QFont("Courier New", 11, QFont.Weight.Bold))
            item_id.setForeground(QColor("#9CA3AF"))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            item_nombre = QTableWidgetItem(p["nombre"].upper())
            item_nombre.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
            item_nombre.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            item_cant = QTableWidgetItem(str(p["cantidad"]))
            item_cant.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_cant.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
            item_cant.setForeground(QColor(self.BRAND_DEFAULT))

            item_precio = QTableWidgetItem(f"${p['precio']:,}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_precio.setFont(QFont("Montserrat", 11, QFont.Weight.Black))

            self.tabla_productos.setItem(row, 0, item_id)
            self.tabla_productos.setItem(row, 1, item_nombre)
            self.tabla_productos.setItem(row, 2, item_cant)
            self.tabla_productos.setItem(row, 3, item_precio)

        self.lbl_display_total.setText(f"${self.total_actual:,}")

        if self.productos_venta:
            self.table_stack.setCurrentWidget(self.tabla_productos)
            self.lbl_estado_tabla.hide()
        else:
            self.lbl_estado_tabla.show()
            self.table_stack.setCurrentWidget(self.lbl_estado_tabla)
            self.lbl_estado_tabla.raise_()

        self.actualizar_cambio()

    def agregar_producto_mock(self):
        nuevo_id = 1000 + len(self.productos_venta) + 1
        self.productos_venta.append({
            "id": nuevo_id,
            "nombre": f"Producto de Prueba {nuevo_id}",
            "cantidad": 1,
            "precio": 4500
        })
        self.renderizar_tabla()

    def eliminar_producto_seleccionado(self):
        fila = self.tabla_productos.currentRow()

        if fila >= 0:
            self.productos_venta.pop(fila)
            self.renderizar_tabla()
        else:
            QMessageBox.warning(
                self,
                "Caja",
                "Por favor seleccione un producto de la tabla para eliminar."
            )

    def actualizar_cambio(self):
        try:
            texto_limpio = self.txt_efectivo.text().replace(".", "").replace(",", "")
            efectivo = int(texto_limpio) if texto_limpio else 0
        except ValueError:
            efectivo = 0

        cambio = efectivo - self.total_actual

        if cambio > 0:
            self.lbl_display_cambio.setText(f"${cambio:,}")
        else:
            self.lbl_display_cambio.setText("$0")

    def ejecutar_cobro(self):
        try:
            texto_limpio = self.txt_efectivo.text().replace(".", "").replace(",", "")
            efectivo = int(texto_limpio) if texto_limpio else 0
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
            self,
            "Éxito",
            f"COBRO EXITOSO\n\nTotal: ${self.total_actual:,}\nCambio: ${cambio:,}"
        )

        self.productos_venta = []
        self.txt_efectivo.clear()
        self.renderizar_tabla()

    def cerrar_sesion(self):
        respuesta = QMessageBox.question(
            self,
            "Salir",
            "¿Estás seguro de que deseas cerrar la sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.controlador.cambiar_pantalla("Login")

    def volver_dashboard(self):
        self.controlador.cambiar_pantalla("AdminDashboard")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(self.COLOR_FONDO)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())