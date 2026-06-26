import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox,
    QPushButton, QLabel, QFrame, QTableWidget, QListWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QGraphicsDropShadowEffect, QStackedLayout, QStackedWidget, QCompleter,
    QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt, QPoint, QStringListModel
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QFontDatabase

from vistas.facturaelectronica_vista import FacturaElectronicaVista
from vistas.reciboproveedores_vista import ReciboProveedoresVista
from vistas.devoluciones_vista import DevolucionesVista


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO AGREGAR FACTURA (sin cambios)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoAgregarFactura(QDialog):
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self._conexion = conexion
        self.resultado = None
        
        self.productos_db = {}
        self.producto_actual = None

        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(650, 680)
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

        # HEADER
        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("AGREGAR A LA FACTURA")
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

        estilo_input = """
            QLineEdit, QSpinBox {
                background-color: #F8FAF9; border: 2px solid #D1E2D9;
                border-radius: 14px; padding: 0 16px; color: #1F2937;
            }
            QLineEdit:focus, QSpinBox:focus { border: 2px solid #17813D; background-color: #FFFFFF; }
            QSpinBox::up-button, QSpinBox::down-button { width: 30px; }
        """

        # NOMBRE DEL PRODUCTO
        box_nombre = QVBoxLayout()
        box_nombre.setSpacing(8)
        lbl_nom = QLabel("NOMBRE DEL PRODUCTO")
        lbl_nom.setFont(_f(10, QFont.Weight.Bold))
        lbl_nom.setStyleSheet("color: #708077; border: none;")
        
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Escribe para buscar (Ej: Manzana...)")
        self.txt_nombre.setFont(_f(14, QFont.Weight.Medium))
        self.txt_nombre.setFixedHeight(56)
        self.txt_nombre.setStyleSheet(estilo_input)
        self.txt_nombre.textChanged.connect(self._verificar_producto)
        
        box_nombre.addWidget(lbl_nom)
        box_nombre.addWidget(self.txt_nombre)
        layout_card.addLayout(box_nombre)

        # FILA: CANTIDAD Y PESO
        fila_cantidades = QHBoxLayout()
        fila_cantidades.setSpacing(20)

        col_cant = QVBoxLayout()
        col_cant.setSpacing(8)
        lbl_cant = QLabel("CANTIDAD (Und)")
        lbl_cant.setFont(_f(10, QFont.Weight.Bold))
        lbl_cant.setStyleSheet("color: #708077; border: none;")
        self.spin_cant = QSpinBox()
        self.spin_cant.setMaximum(9999)
        self.spin_cant.setFont(_f(14, QFont.Weight.Bold))
        self.spin_cant.setFixedHeight(56)
        self.spin_cant.setStyleSheet(estilo_input)
        self.spin_cant.valueChanged.connect(self._calcular_total)
        col_cant.addWidget(lbl_cant)
        col_cant.addWidget(self.spin_cant)

        col_peso = QVBoxLayout()
        col_peso.setSpacing(8)
        lbl_peso = QLabel("PESO (Gramos)")
        lbl_peso.setFont(_f(10, QFont.Weight.Bold))
        lbl_peso.setStyleSheet("color: #708077; border: none;")
        self.spin_peso = QSpinBox()
        self.spin_peso.setMaximum(99999)
        self.spin_peso.setFont(_f(14, QFont.Weight.Bold))
        self.spin_peso.setFixedHeight(56)
        self.spin_peso.setSuffix(" g")
        self.spin_peso.setStyleSheet(estilo_input)
        self.spin_peso.valueChanged.connect(self._calcular_total)
        col_peso.addWidget(lbl_peso)
        col_peso.addWidget(self.spin_peso)

        fila_cantidades.addLayout(col_cant)
        fila_cantidades.addLayout(col_peso)
        layout_card.addLayout(fila_cantidades)

        # PRECIO UNITARIO
        box_precio = QVBoxLayout()
        box_precio.setSpacing(8)
        lbl_precio = QLabel("PRECIO UNITARIO / KG (Tomado de la BD)")
        lbl_precio.setFont(_f(10, QFont.Weight.Bold))
        lbl_precio.setStyleSheet("color: #17813D; border: none;")
        
        self.txt_precio = QLineEdit()
        self.txt_precio.setReadOnly(True)
        self.txt_precio.setText("$0")
        self.txt_precio.setFont(_f(16, QFont.Weight.Bold))
        self.txt_precio.setFixedHeight(56)
        self.txt_precio.setStyleSheet("""
            QLineEdit { background: #EDF7F1; color: #17813D; border: 2px dashed #A9DDBC; border-radius: 14px; padding: 0 16px; }
        """)
        
        box_precio.addWidget(lbl_precio)
        box_precio.addWidget(self.txt_precio)
        layout_card.addLayout(box_precio)

        # TOTAL CALCULADO
        fila_total = QHBoxLayout()
        self.lbl_info_total = QLabel("Total a sumar:")
        self.lbl_info_total.setFont(_f(12, QFont.Weight.Medium))
        self.lbl_info_total.setStyleSheet("color: #708077; background: transparent; border: none;")
        self.lbl_total_calc = QLabel("$0")
        self.lbl_total_calc.setFont(_f(22, QFont.Weight.Black))
        self.lbl_total_calc.setStyleSheet("color: #17813D; background: transparent; border: none;")
        fila_total.addStretch()
        fila_total.addWidget(self.lbl_info_total)
        fila_total.addWidget(self.lbl_total_calc)
        layout_card.addLayout(fila_total)

        # FOOTER BOTONES
        layout_footer = QHBoxLayout()
        btn_cancelar = QPushButton("CANCELAR")
        btn_cancelar.setFont(_f(12, QFont.Weight.Bold))
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setStyleSheet("QPushButton { background: transparent; color: #9CA3AF; border: none; } QPushButton:hover { color: #DC2626; }")
        btn_cancelar.clicked.connect(self.reject)

        self.btn_anadir = QPushButton("AÑADIR A LA FACTURA")
        self.btn_anadir.setFixedHeight(60)
        self.btn_anadir.setFixedWidth(280)
        self.btn_anadir.setFont(_f(13, QFont.Weight.Black))
        self.btn_anadir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_anadir.setStyleSheet("""
            QPushButton { background-color: #17813D; border: none; border-radius: 16px; color: #FFFFFF; letter-spacing: 0.5px; }
            QPushButton:hover { background-color: #228E49; }
            QPushButton:disabled { background-color: #A9DDBC; color: #E8F5EE; }
        """)
        self.btn_anadir.setEnabled(False)
        self.btn_anadir.clicked.connect(self._confirmar)

        layout_footer.addWidget(btn_cancelar)
        layout_footer.addStretch()
        layout_footer.addWidget(self.btn_anadir)
        layout_card.addLayout(layout_footer)

        layout_fondo.addWidget(self.card)

        self._cargar_productos_bd()

    def _cargar_productos_bd(self):
        if not self._conexion:
            print("Error: El diálogo recibió una conexión vacía (None).")
            return

        try:
            cursor = self._conexion.cursor()
            cursor.execute("SELECT id_producto, nombre_producto, precio_venta_prod FROM productos")
            
            filas = cursor.fetchall()
            for fila in filas:
                if isinstance(fila, dict):
                    pid = fila.get("id_producto")
                    nombre = str(fila.get("nombre_producto")).upper()
                    precio = float(fila.get("precio_venta_prod"))
                else:
                    pid = fila[0]
                    nombre = str(fila[1]).upper()
                    precio = float(fila[2])
                
                self.productos_db[nombre] = {
                    "id": pid, 
                    "precio": precio
                }
            cursor.close()
            
            lista_nombres = list(self.productos_db.keys())
            self.modelo_completer = QStringListModel(lista_nombres)
            self.completer = QCompleter(self.modelo_completer, self)
            self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.txt_nombre.setCompleter(self.completer)
            
        except Exception as e:
            print(f"Error inesperado al cargar productos: {repr(e)}")

    def _verificar_producto(self):
        texto_ingresado = self.txt_nombre.text().upper().strip()
        
        if texto_ingresado in self.productos_db:
            self.producto_actual = self.productos_db[texto_ingresado]
            self.producto_actual["nombre"] = texto_ingresado
            
            precio = self.producto_actual["precio"]
            self.txt_precio.setText(f"${int(precio):,}")
            
            self.btn_anadir.setEnabled(True)
            if self.spin_cant.value() == 0 and self.spin_peso.value() == 0:
                self.spin_cant.setValue(1)
            
            self.txt_nombre.setStyleSheet("""
                QLineEdit { background-color: #E8F5EE; border: 2px solid #17813D; border-radius: 14px; padding: 0 16px; color: #17813D; font-weight: bold; }
            """)
        else:
            self.producto_actual = None
            self.txt_precio.setText("$0")
            self.btn_anadir.setEnabled(False)
            self.lbl_total_calc.setText("$0")
            
            self.txt_nombre.setStyleSheet("""
                QLineEdit { background-color: #F8FAF9; border: 2px solid #D1E2D9; border-radius: 14px; padding: 0 16px; color: #1F2937; }
                QLineEdit:focus { border: 2px solid #17813D; background-color: #FFFFFF; }
            """)

        self._calcular_total()

    def _calcular_total(self):
        if not self.producto_actual: 
            return
            
        precio_base = self.producto_actual["precio"]
        cant = self.spin_cant.value()
        peso_g = self.spin_peso.value()

        total = (precio_base * cant) + (precio_base * (peso_g / 1000.0))
        self.lbl_total_calc.setText(f"${int(total):,}")

    def _confirmar(self):
        if not self.producto_actual: return
        cant = self.spin_cant.value()
        peso = self.spin_peso.value()
        
        if cant == 0 and peso == 0:
            QMessageBox.warning(self, "Atención", "Debes ingresar una cantidad o un peso.")
            return

        precio_base = self.producto_actual["precio"]
        total_linea = (precio_base * cant) + (precio_base * (peso / 1000.0))

        self.resultado = {
            "id": self.producto_actual["id"],
            "nombre": self.producto_actual["nombre"],
            "cantidad": cant,
            "peso": peso,
            "precio_unitario": precio_base,
            "precio_total": int(total_linea)
        }
        self.accept()

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


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO ELIMINAR – QUITAR BORDES GRISES (Imagen 1)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoEliminar(QDialog):
    def __init__(self, productos, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.productos = productos
        self.indice_seleccionado = -1

        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(24, 24, 24, 24)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(650, 680)
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 28px;
                border: 2px solid #D1E2D9;
            }
        """)
        
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(40)
        sombra.setColor(QColor(0, 0, 0, 45))
        sombra.setOffset(0, 10)
        self.card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(40, 40, 40, 40)
        layout_card.setSpacing(20)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            return font

        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("QUITAR DE LA FACTURA")
        lbl_titulo.setFont(_f(18, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #DC6468; background: transparent; border: none;")
        
        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(36, 36)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #F4F7F5;
                border-radius: 18px;
                color: #708077;
                border: none;
            }
            QPushButton:hover { background-color: #FDF2F2; color: #DC2626; }
        """)
        btn_cerrar.clicked.connect(self.reject)
        layout_header.addWidget(lbl_titulo)
        layout_header.addStretch()
        layout_header.addWidget(btn_cerrar)
        layout_card.addLayout(layout_header)

        lbl_info = QLabel("SELECCIONA EL PRODUCTO A ELIMINAR")
        lbl_info.setFont(_f(11, QFont.Weight.Bold))
        lbl_info.setStyleSheet("color: #708077; background: transparent;")
        layout_card.addWidget(lbl_info)

        if not productos:
            self.lbl_vacio = QLabel("LA LISTA DE LA FACTURA ESTÁ VACÍA")
            self.lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl_vacio.setFont(_f(13, QFont.Weight.Bold))
            self.lbl_vacio.setStyleSheet("color: #C0CCC5; background: #F8FAF9; border-radius: 14px; border: 2px dashed #D1E2D9;")
            self.lbl_vacio.setFixedHeight(340)
            layout_card.addWidget(self.lbl_vacio)
            
            self.btn_eliminar = QPushButton("ELIMINAR PRODUCTO")
            self.btn_eliminar.setFixedHeight(60)
            self.btn_eliminar.setEnabled(False)
            self.btn_eliminar.setStyleSheet("QPushButton { background-color: #E2E8F0; color: #94A3B8; border-radius: 16px; font-weight: bold; }")
            layout_card.addWidget(self.btn_eliminar)
        else:
            self.lista = QListWidget()
            self.lista.setStyleSheet("""
                QListWidget {
                    background-color: #F8FAF9;
                    border: 2px solid #D1E2D9;
                    border-radius: 14px;
                    padding: 0;
                    outline: none;
                }
                QListWidget::item {
                    padding: 14px 16px;
                    border-bottom: 1px solid #EAEFEA;
                    color: #1F2937;
                }
                QListWidget::item:hover {
                    background-color: #F1F5F2;
                    border-radius: 8px;
                }
                QListWidget::item:selected {
                    background-color: #FADBD8;
                    color: #DC6468;
                    border-radius: 10px;
                    font-weight: bold;
                }
            """)
            self.lista.setFont(_f(13, QFont.Weight.Medium))
            self.lista.setFixedHeight(340)
            
            for p in productos:
                self.lista.addItem(f"ID {p['id']}   ·   {p['nombre'].upper()}   ·   ${int(p['precio_total']):,}")
                
            self.lista.currentRowChanged.connect(self._verificar_seleccion)
            layout_card.addWidget(self.lista)

            self.btn_eliminar = QPushButton("ELIMINAR PRODUCTO")
            self.btn_eliminar.setFixedHeight(60)
            self.btn_eliminar.setEnabled(False)
            self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_eliminar.setStyleSheet(
                "QPushButton { background-color: #DC6468; color: #FFFFFF; border-radius: 16px; font-weight: bold; }"
                "QPushButton:disabled { background-color: #E2E8F0; color: #94A3B8; }"
            )
            self.btn_eliminar.clicked.connect(self._confirmar)
            layout_card.addWidget(self.btn_eliminar)

        layout_fondo.addWidget(self.card)

    def _verificar_seleccion(self, row):
        self.btn_eliminar.setEnabled(row >= 0)

    def _confirmar(self):
        if hasattr(self, "lista") and self.lista.currentRow() >= 0:
            self.indice_seleccionado = self.lista.currentRow()
            self.accept()
        else:
            self.reject()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(40, 55, 45, 95))


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO MODIFICAR – más grande y sin ID (Imagen 2)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoModificar(QDialog):
    def __init__(self, productos, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self._productos = productos
        self.resultado = None

        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(24, 24, 24, 24)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(750, 650)
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 28px;
                border: 2px solid #D1E2D9;
            }
        """)
        
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(40)
        sombra.setColor(QColor(0, 0, 0, 45))
        sombra.setOffset(0, 10)
        self.card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(40, 40, 40, 40)
        layout_card.setSpacing(18)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            return font

        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("EDITAR CANTIDAD DEL PRODUCTO")
        lbl_titulo.setFont(_f(20, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent; border: none;")
        
        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(36, 36)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #F4F7F5;
                border-radius: 18px;
                color: #708077;
                border: none;
            }
            QPushButton:hover { background-color: #FDF2F2; color: #DC2626; }
        """)
        btn_cerrar.clicked.connect(self.reject)
        layout_header.addWidget(lbl_titulo)
        layout_header.addStretch()
        layout_header.addWidget(btn_cerrar)
        layout_card.addLayout(layout_header)

        lbl_buscar = QLabel("SELECCIONA EL PRODUCTO A MODIFICAR")
        lbl_buscar.setFont(_f(13, QFont.Weight.Bold))
        lbl_buscar.setStyleSheet("color: #708077; background: transparent;")
        layout_card.addWidget(lbl_buscar)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Filtrar por nombre...")
        self.txt_buscar.setFixedHeight(56)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 14px;
                padding: 0 16px;
                color: #1F2937;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #17813D;
                background-color: #FFFFFF;
            }
        """)
        self.txt_buscar.textChanged.connect(self._buscar)
        layout_card.addWidget(self.txt_buscar)

        self.lista = QListWidget()
        self.lista.setStyleSheet("""
            QListWidget {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 14px;
                padding: 0;
                outline: none;
            }
            QListWidget::item {
                padding: 14px 16px;
                border-bottom: 1px solid #EAEFEA;
                color: #1F2937;
                font-size: 14px;
            }
            QListWidget::item:hover {
                background-color: #F1F5F2;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background-color: #E2ECE6;
                color: #17813D;
                border-radius: 10px;
                font-weight: bold;
            }
        """)
        self.lista.setFont(_f(14, QFont.Weight.Medium))
        self.lista.setFixedHeight(180)
        
        self._indices = list(range(len(productos)))
        for p in productos:
            # Mostrar solo NOMBRE (sin ID)
            self.lista.addItem(f"{p['nombre'].upper()}   ·   Cant: {p['cantidad']}")
            
        self.lista.currentRowChanged.connect(self._cargar_valores_item)
        layout_card.addWidget(self.lista)

        # Campo cantidad con número más grande
        fila_cant = QVBoxLayout()
        fila_cant.setSpacing(8)
        lbl_cant = QLabel("NUEVA CANTIDAD")
        lbl_cant.setFont(_f(14, QFont.Weight.Bold))
        lbl_cant.setStyleSheet("color: #708077; background: transparent;")
        self.spin_cant = QSpinBox()
        self.spin_cant.setRange(1, 9999)
        self.spin_cant.setFixedHeight(70)
        self.spin_cant.setStyleSheet("""
            QSpinBox {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 14px;
                padding: 0 20px;
                color: #1F2937;
                font-size: 24px;
                font-weight: bold;
            }
            QSpinBox:focus {
                border: 2px solid #17813D;
            }
        """)
        fila_cant.addWidget(lbl_cant)
        fila_cant.addWidget(self.spin_cant)
        layout_card.addLayout(fila_cant)

        self.btn_guardar = QPushButton("GUARDAR CAMBIOS")
        self.btn_guardar.setFixedHeight(64)
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setFont(_f(14, QFont.Weight.Black))
        self.btn_guardar.setStyleSheet(
            "QPushButton { background-color: #17813D; color: #FFFFFF; border-radius: 16px; font-weight: bold; }"
            "QPushButton:disabled { background-color: #E2E8F0; color: #94A3B8; }"
        )
        self.btn_guardar.clicked.connect(self._confirmar)
        layout_card.addWidget(self.btn_guardar)

        layout_fondo.addWidget(self.card)

    def _buscar(self, texto):
        texto = texto.strip().lower()
        self.lista.clear()
        self._indices = []
        for i, p in enumerate(self._productos):
            if texto in p["nombre"].lower():
                self.lista.addItem(f"{p['nombre'].upper()}   ·   Cant: {p['cantidad']}")
                self._indices.append(i)

    def _cargar_valores_item(self, row):
        if row >= 0 and row < len(self._indices):
            self.btn_guardar.setEnabled(True)
            idx_real = self._indices[row]
            prod_sel = self._productos[idx_real]
            if "cantidad" in prod_sel:
                self.spin_cant.setValue(int(prod_sel["cantidad"]))
            self._indice_actual = idx_real
        else:
            self.btn_guardar.setEnabled(False)

    def _confirmar(self):
        row = self.lista.currentRow()
        if row < 0 or row >= len(self._indices):
            return
            
        self.resultado = {
            "indice"  : self._indices[row],
            "cantidad": self.spin_cant.value(),
        }
        self.accept()


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO BUSCAR – autocompletado y campos específicos (Imagen 3)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoBuscar(QDialog):
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self._conexion = conexion

        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(900, 650)
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
        layout_card.setSpacing(20)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return font

        # HEADER
        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("BUSCAR PRODUCTOS")
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

        # CAMPO DE BÚSQUEDA CON AUTOCOMPLETADO
        layout_busqueda = QHBoxLayout()
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Escribe el nombre del producto...")
        self.txt_buscar.setFont(_f(14, QFont.Weight.Medium))
        self.txt_buscar.setFixedHeight(56)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 14px;
                padding: 0 16px;
                color: #1F2937;
            }
            QLineEdit:focus {
                border: 2px solid #17813D;
                background-color: #FFFFFF;
            }
        """)
        layout_busqueda.addWidget(self.txt_buscar)

        self.btn_buscar = QPushButton("BUSCAR")
        self.btn_buscar.setFixedHeight(56)
        self.btn_buscar.setFixedWidth(140)
        self.btn_buscar.setFont(_f(13, QFont.Weight.Black))
        self.btn_buscar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buscar.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                border: none;
                border-radius: 16px;
                color: #FFFFFF;
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        self.btn_buscar.clicked.connect(self._buscar)
        layout_busqueda.addWidget(self.btn_buscar)

        self.btn_limpiar = QPushButton("LIMPIAR")
        self.btn_limpiar.setFixedHeight(56)
        self.btn_limpiar.setFixedWidth(140)
        self.btn_limpiar.setFont(_f(13, QFont.Weight.Black))
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                border: none;
                border-radius: 16px;
                color: #1F2937;
            }
            QPushButton:hover { background-color: #CBD5E1; }
        """)
        self.btn_limpiar.clicked.connect(self._limpiar)
        layout_busqueda.addWidget(self.btn_limpiar)

        layout_card.addLayout(layout_busqueda)

        # TABLA DE RESULTADOS – solo 4 columnas
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(4)
        self.tabla_resultados.setHorizontalHeaderLabels(["NOMBRE", "MARCA", "CATEGORÍA", "PRECIO UNIT."])
        self.tabla_resultados.setShowGrid(False)
        self.tabla_resultados.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_resultados.setStyleSheet("""
            QTableWidget {
                border: 2px solid #D1E2D9;
                border-radius: 14px;
                background-color: #FFFFFF;
                padding: 8px;
                outline: none;
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #EAEFEA;
                color: #1F2937;
                font-family: 'Montserrat';
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #E8F5EE;
                color: #17813D;
            }
        """)
        self.tabla_resultados.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tabla_resultados.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #F8FAF9;
                color: #86B896;
                font-family: 'Montserrat';
                font-size: 11px;
                font-weight: 800;
                border: none;
                border-bottom: 2px solid #EEF0F2;
                padding: 8px 12px;
            }
        """)
        self.tabla_resultados.verticalHeader().setVisible(False)
        self.tabla_resultados.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_resultados.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.tabla_resultados.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout_card.addWidget(self.tabla_resultados)

        # BOTÓN CERRAR
        layout_footer = QHBoxLayout()
        btn_cerrar_dialog = QPushButton("CERRAR")
        btn_cerrar_dialog.setFixedHeight(50)
        btn_cerrar_dialog.setFixedWidth(160)
        btn_cerrar_dialog.setFont(_f(12, QFont.Weight.Black))
        btn_cerrar_dialog.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar_dialog.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                border: none;
                border-radius: 16px;
                color: #1F2937;
            }
            QPushButton:hover { background-color: #CBD5E1; }
        """)
        btn_cerrar_dialog.clicked.connect(self.reject)

        layout_footer.addStretch()
        layout_footer.addWidget(btn_cerrar_dialog)
        layout_card.addLayout(layout_footer)

        layout_fondo.addWidget(self.card)

        # Cargar nombres para autocompletado
        self._cargar_nombres_autocompletado()

    def _cargar_nombres_autocompletado(self):
        if not self._conexion:
            return
        try:
            cursor = self._conexion.cursor()
            cursor.execute("SELECT nombre_producto FROM productos")
            nombres = [row[0] for row in cursor.fetchall()]
            cursor.close()
            modelo = QStringListModel(nombres)
            completer = QCompleter(modelo, self)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.txt_buscar.setCompleter(completer)
        except Exception as e:
            print(f"Error al cargar nombres para autocompletado: {e}")

    def _buscar(self):
        termino = self.txt_buscar.text().strip()
        if not termino:
            QMessageBox.information(self, "Buscar", "Ingresa un término de búsqueda.")
            return

        if not self._conexion:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return

        try:
            cursor = self._conexion.cursor()
            # Consulta con JOIN para obtener categoría y proveedor (si existen)
            query = """
                SELECT 
                    p.nombre_producto,
                    p.marca_producto,
                    c.nombre_categoria,
                    p.precio_venta_prod
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.nombre_producto LIKE %s
                   OR p.marca_producto LIKE %s
                   OR c.nombre_categoria LIKE %s
            """
            like = f"%{termino}%"
            cursor.execute(query, (like, like, like))
            filas = cursor.fetchall()
            cursor.close()

            self.tabla_resultados.setRowCount(len(filas))
            for i, fila in enumerate(filas):
                nombre = fila[0] or ""
                marca = fila[1] or ""
                categoria = fila[2] or ""
                precio = fila[3] if fila[3] is not None else 0
                self.tabla_resultados.setItem(i, 0, QTableWidgetItem(str(nombre)))
                self.tabla_resultados.setItem(i, 1, QTableWidgetItem(str(marca)))
                self.tabla_resultados.setItem(i, 2, QTableWidgetItem(str(categoria)))
                self.tabla_resultados.setItem(i, 3, QTableWidgetItem(f"${int(precio):,}"))

            if len(filas) == 0:
                QMessageBox.information(self, "Buscar", "No se encontraron productos con ese término.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar productos: {e}")

    def _limpiar(self):
        self.txt_buscar.clear()
        self.tabla_resultados.setRowCount(0)

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


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO DE COBRO (sin cambios)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoCobro(QDialog):
    def __init__(self, total, efectivo, cambio, empleado_id, productos, conexion, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        
        self.total = total
        self.efectivo = efectivo
        self.cambio = cambio
        self.empleado_id = empleado_id
        self.productos = productos
        self.conexion = conexion
        self.exito = False

        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(750, 850)
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
        layout_card.setSpacing(18)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return font

        # HEADER
        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("CONFIRMAR COBRO")
        lbl_titulo.setFont(_f(22, QFont.Weight.Black))
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

        # RESUMEN DEL COBRO
        resumen_frame = QFrame()
        resumen_frame.setStyleSheet("""
            QFrame {
                background: #F8FAF9;
                border-radius: 16px;
                border: 1px solid #D1E2D9;
                padding: 20px;
            }
        """)
        resumen_layout = QVBoxLayout(resumen_frame)
        resumen_layout.setSpacing(8)

        lbl_total = QLabel(f"<b>TOTAL A PAGAR:</b> ${self.total:,.0f}")
        lbl_total.setFont(_f(18, QFont.Weight.Bold))
        lbl_total.setStyleSheet("color: #17813D;")
        resumen_layout.addWidget(lbl_total)

        lbl_efectivo = QLabel(f"<b>EFECTIVO ENTREGADO:</b> ${self.efectivo:,.0f}")
        lbl_efectivo.setFont(_f(18, QFont.Weight.Bold))
        lbl_efectivo.setStyleSheet("color: #1F2937;")
        resumen_layout.addWidget(lbl_efectivo)

        lbl_cambio = QLabel(f"<b>CAMBIO:</b> ${self.cambio:,.0f}")
        lbl_cambio.setFont(_f(18, QFont.Weight.Bold))
        lbl_cambio.setStyleSheet("color: #DC6468;")
        resumen_layout.addWidget(lbl_cambio)

        layout_card.addWidget(resumen_frame)

        # DATOS DEL CLIENTE (OPCIONAL)
        lbl_cliente = QLabel("DATOS DEL CLIENTE (OPCIONAL)")
        lbl_cliente.setFont(_f(13, QFont.Weight.Black))
        lbl_cliente.setStyleSheet("color: #708077; letter-spacing: 0.5px;")
        layout_card.addWidget(lbl_cliente)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        scroll_layout = QFormLayout(scroll_content)
        scroll_layout.setSpacing(12)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        estilo_input = """
            QLineEdit {
                background-color: #F8FAF9;
                border: 2px solid #D1E2D9;
                border-radius: 12px;
                padding: 0 16px;
                color: #1F2937;
                font-family: 'Montserrat';
                font-size: 14px;
                height: 44px;
            }
            QLineEdit:focus {
                border: 2px solid #17813D;
                background-color: #FFFFFF;
            }
        """

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre completo (opcional)")
        self.txt_nombre.setStyleSheet(estilo_input)

        self.txt_documento = QLineEdit()
        self.txt_documento.setPlaceholderText("Documento de identidad (opcional)")
        self.txt_documento.setStyleSheet(estilo_input)

        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Teléfono (opcional)")
        self.txt_telefono.setStyleSheet(estilo_input)

        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Email (opcional)")
        self.txt_email.setStyleSheet(estilo_input)

        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText("Dirección (opcional)")
        self.txt_direccion.setStyleSheet(estilo_input)

        self.txt_ciudad = QLineEdit()
        self.txt_ciudad.setPlaceholderText("Ciudad (opcional)")
        self.txt_ciudad.setStyleSheet(estilo_input)

        self.txt_departamento = QLineEdit()
        self.txt_departamento.setPlaceholderText("Departamento (opcional)")
        self.txt_departamento.setStyleSheet(estilo_input)

        scroll_layout.addRow("Nombre:", self.txt_nombre)
        scroll_layout.addRow("Documento:", self.txt_documento)
        scroll_layout.addRow("Teléfono:", self.txt_telefono)
        scroll_layout.addRow("Email:", self.txt_email)
        scroll_layout.addRow("Dirección:", self.txt_direccion)
        scroll_layout.addRow("Ciudad:", self.txt_ciudad)
        scroll_layout.addRow("Departamento:", self.txt_departamento)

        scroll.setWidget(scroll_content)
        scroll.setMaximumHeight(360)
        layout_card.addWidget(scroll)

        # BOTONES
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(16)

        btn_cancelar = QPushButton("CANCELAR")
        btn_cancelar.setFont(_f(13, QFont.Weight.Bold))
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #9CA3AF;
                border: none;
            }
            QPushButton:hover { color: #DC2626; }
        """)
        btn_cancelar.clicked.connect(self.reject)

        self.btn_cobrar = QPushButton("COBRAR")
        self.btn_cobrar.setFixedHeight(60)
        self.btn_cobrar.setFont(_f(16, QFont.Weight.Black))
        self.btn_cobrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cobrar.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 16px;
                padding: 0 40px;
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        self.btn_cobrar.clicked.connect(self._confirmar_cobro)

        layout_botones.addStretch()
        layout_botones.addWidget(btn_cancelar)
        layout_botones.addWidget(self.btn_cobrar)

        layout_card.addLayout(layout_botones)

        layout_fondo.addWidget(self.card)

    def _confirmar_cobro(self):
        nombre = self.txt_nombre.text().strip() or None
        documento = self.txt_documento.text().strip() or None
        telefono = self.txt_telefono.text().strip() or None
        email = self.txt_email.text().strip() or None
        direccion = self.txt_direccion.text().strip() or None
        ciudad = self.txt_ciudad.text().strip() or "Bogotá"
        departamento = self.txt_departamento.text().strip() or "Cundinamarca"

        id_cliente = None
        if nombre or documento:
            try:
                cursor = self.conexion.cursor()
                if documento:
                    cursor.execute("SELECT id_cliente FROM clientes WHERE documento_identidad = %s", (documento,))
                    row = cursor.fetchone()
                    if row:
                        id_cliente = row[0]
                    else:
                        cursor.execute("""
                            INSERT INTO clientes
                            (nombre_cliente, documento_identidad, telefono, email, direccion, ciudad, departamento)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (nombre, documento, telefono, email, direccion, ciudad, departamento))
                        id_cliente = cursor.lastrowid
                        self.conexion.commit()
                else:
                    cursor.execute("""
                        INSERT INTO clientes
                        (nombre_cliente, documento_identidad, telefono, email, direccion, ciudad, departamento)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (nombre, documento, telefono, email, direccion, ciudad, departamento))
                    id_cliente = cursor.lastrowid
                    self.conexion.commit()
                cursor.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el cliente: {e}")
                return

        # Insertar factura
        try:
            cursor = self.conexion.cursor()
            fecha_actual = datetime.now()
            cursor.execute("""
                INSERT INTO facturas (id_empleado, id_cliente, fecha_fac, total_fac)
                VALUES (%s, %s, %s, %s)
            """, (self.empleado_id, id_cliente, fecha_actual, self.total))
            id_factura = cursor.lastrowid
            self.conexion.commit()
            cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la factura: {e}")
            return

        # Insertar detalles y actualizar inventario
        try:
            cursor = self.conexion.cursor()
            for producto in self.productos:
                cursor.execute("SELECT precio_venta_prod FROM productos WHERE id_producto = %s", (producto["id"],))
                row = cursor.fetchone()
                precio_unitario = row[0] if row else producto.get("precio_unitario", 0)
                cantidad = producto["cantidad"]
                subtotal = cantidad * precio_unitario
                cursor.execute("""
                    INSERT INTO detalle_factura
                    (id_factura, id_producto, cantidad_detfac, precio_unitario_detfac, subtotal_detfac)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_factura, producto["id"], cantidad, precio_unitario, subtotal))

                cursor.execute("""
                    UPDATE inventarios SET stock_actual = stock_actual - %s
                    WHERE id_producto = %s
                """, (cantidad, producto["id"]))

                cursor.execute("""
                    INSERT INTO movimientos
                    (id_inventario, id_tipo_mov, id_empleado, id_factura, cantidad_movimiento)
                    SELECT id_inventario, 2, %s, %s, %s
                    FROM inventarios WHERE id_producto = %s
                """, (self.empleado_id, id_factura, cantidad, producto["id"]))
            self.conexion.commit()
            cursor.close()
        except Exception as e:
            self.conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo guardar el detalle de la factura: {e}")
            return

        self.exito = True
        self.accept()

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


# ══════════════════════════════════════════════════════════════════════════════
# VISTA PRINCIPAL DE CAJA (sin cambios relevantes)
# ══════════════════════════════════════════════════════════════════════════════
class CajaVista(QWidget):
    def __init__(self, controlador_flujo):
        super().__init__()
        self.controlador = controlador_flujo
        self.productos_venta = []
        self.total_actual = 0
        self.filtro_actual = ""

        ruta_vistas = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz = os.path.dirname(ruta_vistas)
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")

        for f in ("Montserrat-Bold.ttf", "Montserrat-Regular.ttf", "Montserrat-Medium.ttf", "Montserrat-Black.ttf"):
            ruta_f = os.path.join(carpeta_fuentes, f)
            if os.path.exists(ruta_f):
                QFontDatabase.addApplicationFont(ruta_f)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return font

        self.fuente_heavy = _f(44, QFont.Weight.Bold)
        self.fuente_titulos = _f(22, QFont.Weight.Black)
        self.fuente_tags = _f(10, QFont.Weight.Bold)
        self.fuente_nav = _f(11, QFont.Weight.Black)
        self.fuente_btns = _f(11, QFont.Weight.Black)

        self.COLOR_FONDO = "#F0F4F2"
        self.BRAND = "#17813D"

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(12, 13, 12, 13)
        layout_principal.setSpacing(0)

        self.contenedor_blanco = QFrame()
        self.contenedor_blanco.setObjectName("ContenedorCaja")
        self.contenedor_blanco.setStyleSheet("""
            QFrame#ContenedorCaja {
                background-color: #FFFFFF;
                border: 1px solid #C8E6D4;
                border-radius: 18px; 
            }
        """)
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(22)
        sombra.setColor(QColor(23, 129, 61, 30))
        sombra.setOffset(0, 4)
        self.contenedor_blanco.setGraphicsEffect(sombra)

        layout_contenedor = QVBoxLayout(self.contenedor_blanco)
        layout_contenedor.setContentsMargins(0, 0, 0, 0)
        layout_contenedor.setSpacing(0)

        # ── NAVBAR ──
        navbar = QFrame()
        navbar.setObjectName("NavbarCaja")
        navbar.setFixedHeight(68)
        navbar.setStyleSheet("""
            QFrame#NavbarCaja { 
                background: #FFFFFF; border: none; border-bottom: 1px solid #EEF0F2; 
                border-top-left-radius: 18px; border-top-right-radius: 18px; 
            }
        """)
        layout_navbar = QHBoxLayout(navbar)
        layout_navbar.setContentsMargins(0, 0, 20, 0)
        layout_navbar.setSpacing(0)

        tab_on = "QPushButton { background:transparent; color:#17813D; font-family:'Montserrat'; font-size:11px; font-weight:900; border:none; border-bottom:3px solid #17813D; padding:0 30px; height:68px; }"
        tab_off = "QPushButton { background:transparent; color:#9CA3AF; font-family:'Montserrat'; font-size:11px; font-weight:800; border:none; border-bottom:3px solid transparent; padding:0 24px; height:68px; } QPushButton:hover { color:#17813D; }"

        self.btn_caja = QPushButton("CAJA")
        self.btn_caja.setStyleSheet(tab_on)
        self.btn_caja.setFont(self.fuente_nav)
        self.btn_caja.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_factura = QPushButton("FACTURA\nELECTRÓNICA")
        self.btn_factura.setStyleSheet(tab_off)
        self.btn_factura.setFont(self.fuente_nav)
        self.btn_factura.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_devoluciones = QPushButton("DEVOLUCIONES")
        self.btn_devoluciones.setStyleSheet(tab_off)
        self.btn_devoluciones.setFont(self.fuente_nav)
        self.btn_devoluciones.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_recibo = QPushButton("RECIBO\nPROVEEDORES")
        self.btn_recibo.setStyleSheet(tab_off)
        self.btn_recibo.setFont(self.fuente_nav)
        self.btn_recibo.setCursor(Qt.CursorShape.PointingHandCursor)

        tabs = QHBoxLayout()
        tabs.setSpacing(0)
        tabs.addWidget(self.btn_caja)
        tabs.addWidget(self.btn_factura)
        tabs.addWidget(self.btn_devoluciones)
        tabs.addWidget(self.btn_recibo)

        layout_meta = QVBoxLayout()
        layout_meta.setSpacing(0)
        layout_meta.setContentsMargins(0, 0, 0, 0)
        layout_meta.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        self.lbl_nombre_cajero = QLabel("Cajero Palma")
        self.lbl_nombre_cajero.setFont(_f(11, QFont.Weight.Black))
        self.lbl_nombre_cajero.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_nombre_cajero.setStyleSheet("color:#17813D; background:transparent;")

        self.lbl_rol_caja = QLabel("CAJERO")
        self.lbl_rol_caja.setFont(_f(8, QFont.Weight.Bold))
        self.lbl_rol_caja.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_rol_caja.setStyleSheet("color:#9CA3AF; background:transparent;")

        layout_meta.addWidget(self.lbl_nombre_cajero)
        layout_meta.addWidget(self.lbl_rol_caja)

        self.lbl_avatar = QLabel("CP")
        self.lbl_avatar.setFixedSize(36, 36)
        self.lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_avatar.setFont(_f(11, QFont.Weight.Black))
        self.lbl_avatar.setStyleSheet("QLabel { background:#E9F7EF; border:1px solid #A9DDBC; border-radius:18px; color:#17813D; }")

        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.setFixedSize(105, 34)
        btn_logout.setFont(_f(8, QFont.Weight.Bold))
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet("QPushButton { background:#FFFFFF; color:#DC2626; border:1px solid #FECACA; border-radius:9px; } QPushButton:hover { background:#DC2626; color:#FFFFFF; border-color:#DC2626; }")
        btn_logout.clicked.connect(self.cerrar_sesion)

        btn_salir = QPushButton("✕")
        btn_salir.setFixedSize(36, 36)
        btn_salir.setFont(_f(12, QFont.Weight.Black))
        btn_salir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salir.setStyleSheet("QPushButton { background:#FFFFFF; color:#9CA3AF; border:1px solid #E5E7EB; border-radius:10px; } QPushButton:hover { background:#DC2626; color:#FFFFFF; border-color:#DC2626; }")
        btn_salir.clicked.connect(self.volver_dashboard)

        layout_usuario = QHBoxLayout()
        layout_usuario.setSpacing(12)
        layout_usuario.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout_usuario.addLayout(layout_meta)
        layout_usuario.addWidget(self.lbl_avatar)
        layout_usuario.addWidget(btn_logout)
        layout_usuario.addWidget(btn_salir)

        layout_navbar.addLayout(tabs)
        layout_navbar.addStretch()
        layout_navbar.addLayout(layout_usuario)
        layout_contenedor.addWidget(navbar)

        # ── STACKED WIDGET ──
        self.stack_central = QStackedWidget()
        layout_contenedor.addWidget(self.stack_central)

        # 1. Pantalla CAJA
        self.pantalla_caja = QFrame()
        layout_caja_contenido = QVBoxLayout(self.pantalla_caja)
        layout_caja_contenido.setContentsMargins(0, 0, 0, 0)
        layout_caja_contenido.setSpacing(0)

        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.setSpacing(0)

        # ── PANEL LATERAL ──
        panel_cobros = QFrame()
        panel_cobros.setObjectName("PanelCobros")
        panel_cobros.setFixedWidth(320)
        panel_cobros.setStyleSheet("QFrame#PanelCobros { background:#FAFCFB; border:none; border-right:1px solid #EEF0F2; }")

        layout_panel = QVBoxLayout(panel_cobros)
        layout_panel.setContentsMargins(20, 20, 20, 20)
        layout_panel.setSpacing(18)

        # TOTAL
        card_total = QFrame()
        card_total.setFixedHeight(150)
        card_total.setStyleSheet("QFrame { background:#17813D; border:none; border-radius:22px; }")
        st = QGraphicsDropShadowEffect(self)
        st.setBlurRadius(14)
        st.setColor(QColor(23, 129, 61, 60))
        st.setOffset(0, 6)
        card_total.setGraphicsEffect(st)
        lct = QVBoxLayout(card_total)
        lct.setContentsMargins(24, 18, 24, 18)
        lct.setSpacing(2)
        lbl_tt = QLabel("TOTAL A PAGAR:")
        lbl_tt.setFont(self.fuente_tags)
        lbl_tt.setStyleSheet("color:#FFFFFF; background:transparent;")
        self.lbl_display_total = QLabel("$0")
        self.lbl_display_total.setFont(self.fuente_heavy)
        self.lbl_display_total.setStyleSheet("color:#FFFFFF; background:transparent;")
        lct.addWidget(lbl_tt)
        lct.addWidget(self.lbl_display_total)

        # ── EFECTIVO ──
        card_efectivo = QFrame()
        card_efectivo.setFixedHeight(140)
        card_efectivo.setStyleSheet("QFrame { background:#FFFFFF; border:2px solid #A9DDBC; border-radius:22px; }")
        lce = QVBoxLayout(card_efectivo)
        lce.setContentsMargins(24, 18, 24, 12)
        lce.setSpacing(2)
        lbl_te = QLabel("EFECTIVO:")
        lbl_te.setFont(self.fuente_tags)
        lbl_te.setStyleSheet("color:#17813D; background:transparent; border: none; padding: 0; margin: 0;")
        self.txt_efectivo = QLineEdit()
        self.txt_efectivo.setPlaceholderText("")
        self.txt_efectivo.setFont(self.fuente_heavy)
        self.txt_efectivo.setFixedHeight(54)
        self.txt_efectivo.setStyleSheet("""
            QLineEdit {
                color: #1F2937;
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        self.txt_efectivo.textChanged.connect(self.actualizar_cambio)
        lce.addWidget(lbl_te)
        lce.addWidget(self.txt_efectivo)

        # ── CAMBIO ──
        card_cambio = QFrame()
        card_cambio.setFixedHeight(140)
        card_cambio.setStyleSheet("QFrame { background:#FDEEEF; border:2px solid #F8CBCD; border-radius:22px; }")
        lcc = QVBoxLayout(card_cambio)
        lcc.setContentsMargins(24, 18, 24, 12)
        lcc.setSpacing(2)
        lbl_tc = QLabel("CAMBIO:")
        lbl_tc.setFont(self.fuente_tags)
        lbl_tc.setStyleSheet("color:#DC6468; background:transparent; border: none; padding: 0; margin: 0;")
        self.lbl_display_cambio = QLabel("$0")
        self.lbl_display_cambio.setFont(self.fuente_heavy)
        self.lbl_display_cambio.setStyleSheet("""
            QLabel {
                color: #DC6468;
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        lcc.addWidget(lbl_tc)
        lcc.addWidget(self.lbl_display_cambio)

        layout_panel.addWidget(card_total)
        layout_panel.addWidget(card_efectivo)
        layout_panel.addStretch()
        layout_panel.addWidget(card_cambio)

        # ── ÁREA DE TABLA ──
        area_tabla = QFrame()
        area_tabla.setStyleSheet("QFrame { border:none; background:transparent; }")
        layout_area = QVBoxLayout(area_tabla)
        layout_area.setContentsMargins(26, 16, 32, 12)
        layout_area.setSpacing(10)

        lbl_fact = QLabel("FACTURACIÓN")
        lbl_fact.setFont(self.fuente_titulos)
        lbl_fact.setFixedHeight(50)
        lbl_fact.setStyleSheet("color:#17813D; background:transparent;")

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels(["ID", "NOMBRE DEL PRODUCTO", "CANT / PESO", "PRECIO TOTAL"])
        self.tabla_productos.verticalHeader().setVisible(False)
        self.tabla_productos.verticalHeader().setDefaultSectionSize(50)
        self.tabla_productos.setShowGrid(False)
        self.tabla_productos.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_productos.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_productos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
                outline: none;
            }
            QTableWidget::item {
                border-bottom: 1px solid #F0F2F0;
                color: #1F2937;
                font-family: 'Montserrat';
                font-size: 14px;
                padding: 6px 4px;
            }
            QTableWidget::item:selected {
                background: #E8F5EE;
                color: #17813D;
            }
        """)
        hdr = self.tabla_productos.horizontalHeader()
        hdr.setFixedHeight(38)
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hdr.setStyleSheet("""
            QHeaderView::section {
                background: transparent;
                color: #86B896;
                font-family: 'Montserrat';
                font-size: 11px;
                font-weight: 800;
                border: none;
                border-bottom: 1px solid #EEF0F2;
                padding: 4px 4px;
            }
        """)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tabla_productos.setColumnWidth(0, 50)
        self.tabla_productos.setColumnWidth(2, 160)
        self.tabla_productos.setColumnWidth(3, 160)

        self.lbl_estado_tabla = QLabel("ESPERANDO PRODUCTOS...")
        self.lbl_estado_tabla.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        fe2 = _f(11, QFont.Weight.Bold)
        fe2.setItalic(True)
        self.lbl_estado_tabla.setFont(fe2)
        self.lbl_estado_tabla.setStyleSheet("color:#DFE3E8; background:transparent; padding-top:70px;")

        table_shell = QFrame()
        table_shell.setStyleSheet("QFrame { background:transparent; border: none; }")
        self.table_stack = QStackedLayout(table_shell)
        self.table_stack.setContentsMargins(0, 0, 0, 0)
        self.table_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.table_stack.addWidget(self.tabla_productos)
        self.table_stack.addWidget(self.lbl_estado_tabla)

        layout_area.addWidget(lbl_fact)
        layout_area.addWidget(table_shell, 1)

        cuerpo.addWidget(panel_cobros)
        cuerpo.addWidget(area_tabla)
        layout_caja_contenido.addLayout(cuerpo, 1)

        # ── BARRA INFERIOR ──
        barra_inferior = QFrame()
        barra_inferior.setFixedHeight(100)
        barra_inferior.setStyleSheet("""
            QFrame { 
                border: none; border-top: 1px solid #EEF0F2; background: #FFFFFF; 
                border-bottom-left-radius: 18px; border-bottom-right-radius: 18px; 
            }
        """)
        layout_inferior = QHBoxLayout(barra_inferior)
        layout_inferior.setContentsMargins(28, 0, 28, 0)

        self.btn_cobrar = QPushButton("COBRAR")
        self.btn_cobrar.setFixedSize(240, 64)
        self.btn_cobrar.setFont(_f(15, QFont.Weight.Black))
        self.btn_cobrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cobrar.setStyleSheet("""
            QPushButton { background:#17813D; color:#FFFFFF; border:none; border-radius:18px; letter-spacing:1px; }
            QPushButton:hover { background:#228E49; }
        """)
        sc = QGraphicsDropShadowEffect(self)
        sc.setBlurRadius(14)
        sc.setColor(QColor(23, 129, 61, 55))
        sc.setOffset(0, 5)
        self.btn_cobrar.setGraphicsEffect(sc)
        self.btn_cobrar.clicked.connect(self.ejecutar_cobro)

        def _btn_sec(texto, ancho, destacado=False):
            b = QPushButton(texto)
            b.setFixedSize(ancho, 52)
            b.setFont(self.fuente_btns)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if destacado:
                b.setStyleSheet("QPushButton { background:#FFFFFF; color:#17813D; border:2px solid #A9DDBC; border-radius:16px; font-family:'Montserrat'; font-size:11px; font-weight:900; } QPushButton:hover { background:#E9F7EF; }")
            else:
                b.setStyleSheet("QPushButton { background:#FFFFFF; color:#9CA3AF; border:2px solid #EEEFF2; border-radius:16px; font-family:'Montserrat'; font-size:11px; font-weight:900; } QPushButton:hover { color:#17813D; border-color:#A9DDBC; }")
            return b

        self.btn_agregar = _btn_sec("AGREGAR", 150, destacado=True)
        self.btn_eliminar = _btn_sec("ELIMINAR", 150)
        self.btn_modificar = _btn_sec("MODIFICAR", 150)
        self.btn_buscar = _btn_sec("BUSCAR", 150)

        self.btn_agregar.clicked.connect(self.abrir_buscador_agregar)
        self.btn_eliminar.clicked.connect(self.abrir_eliminar)
        self.btn_modificar.clicked.connect(self.abrir_modificar)
        self.btn_buscar.clicked.connect(self.abrir_buscar)

        self.btn_eliminar.setEnabled(False)
        self.btn_modificar.setEnabled(False)

        self.tabla_productos.itemSelectionChanged.connect(self.actualizar_estado_botones)

        layout_bsec = QHBoxLayout()
        layout_bsec.setSpacing(12)
        layout_bsec.addWidget(self.btn_agregar)
        layout_bsec.addWidget(self.btn_eliminar)
        layout_bsec.addWidget(self.btn_modificar)
        layout_bsec.addWidget(self.btn_buscar)

        layout_inferior.addWidget(self.btn_cobrar)
        layout_inferior.addStretch()
        layout_inferior.addLayout(layout_bsec)

        layout_caja_contenido.addWidget(barra_inferior)

        self.stack_central.addWidget(self.pantalla_caja)

        # 2. Pantalla FACTURA ELECTRÓNICA
        conexion_db = getattr(self.controlador, "conexion", None)
        self.pantalla_factura = FacturaElectronicaVista(conexion=conexion_db)
        self.stack_central.addWidget(self.pantalla_factura)

        # 3. Pantalla DEVOLUCIONES
        self.pantalla_devoluciones = DevolucionesVista(conexion=conexion_db)
        self.stack_central.addWidget(self.pantalla_devoluciones)

        # 4. Pantalla RECIBO PROVEEDORES
        self.pantalla_recibo = ReciboProveedoresVista(conexion=conexion_db)
        self.stack_central.addWidget(self.pantalla_recibo)

        self.btn_caja.clicked.connect(lambda: self.cambiar_pestana(0))
        self.btn_factura.clicked.connect(lambda: self.cambiar_pestana(1))
        self.btn_devoluciones.clicked.connect(lambda: self.cambiar_pestana(2))
        self.btn_recibo.clicked.connect(lambda: self.cambiar_pestana(3))

        self.stack_central.setCurrentIndex(0)

        layout_principal.addWidget(self.contenedor_blanco)

    # ── MÉTODOS DE NAVEGACIÓN ──
    def cambiar_pestana(self, indice):
        self.stack_central.setCurrentIndex(indice)
        tab_on = "QPushButton { background:transparent; color:#17813D; font-family:'Montserrat'; font-size:11px; font-weight:900; border:none; border-bottom:3px solid #17813D; padding:0 30px; height:68px; }"
        tab_off = "QPushButton { background:transparent; color:#9CA3AF; font-family:'Montserrat'; font-size:11px; font-weight:800; border:none; border-bottom:3px solid transparent; padding:0 24px; height:68px; } QPushButton:hover { color:#17813D; }"
        self.btn_caja.setStyleSheet(tab_on if indice == 0 else tab_off)
        self.btn_factura.setStyleSheet(tab_on if indice == 1 else tab_off)
        self.btn_devoluciones.setStyleSheet(tab_on if indice == 2 else tab_off)
        self.btn_recibo.setStyleSheet(tab_on if indice == 3 else tab_off)

    def actualizar_estado_botones(self):
        fila_seleccionada = self.tabla_productos.currentRow() >= 0
        self.btn_eliminar.setEnabled(fila_seleccionada and len(self.productos_venta) > 0)
        self.btn_modificar.setEnabled(fila_seleccionada and len(self.productos_venta) > 0)

    # ── ACCIONES ──
    def abrir_buscador_agregar(self):
        conexion_bd = getattr(self.controlador, "conexion", None)
        if conexion_bd is None:
            QMessageBox.critical(self, "Error de Conexión", "No se encontró la conexión a la base de datos.")
            return
        dlg = DialogoAgregarFactura(conexion_bd, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.resultado:
            self.productos_venta.append(dlg.resultado)
            self.renderizar_tabla()

    def abrir_eliminar(self):
        dlg = DialogoEliminar(self.productos_venta, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            idx = dlg.indice_seleccionado
            if 0 <= idx < len(self.productos_venta):
                self.productos_venta.pop(idx)
                self.renderizar_tabla()

    def abrir_modificar(self):
        if not self.productos_venta:
            return
        dlg = DialogoModificar(self.productos_venta, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.resultado:
            idx = dlg.resultado["indice"]
            nueva_cantidad = dlg.resultado["cantidad"]
            if 0 <= idx < len(self.productos_venta):
                producto = self.productos_venta[idx]
                producto["cantidad"] = nueva_cantidad
                peso = producto.get("peso", 0)
                precio_unit = producto["precio_unitario"]
                total = (precio_unit * nueva_cantidad) + (precio_unit * (peso / 1000.0))
                producto["precio_total"] = int(total)
                self.renderizar_tabla()

    def abrir_buscar(self):
        conexion_bd = getattr(self.controlador, "conexion", None)
        dlg = DialogoBuscar(conexion=conexion_bd, parent=self)
        dlg.exec()

    # ── EJECUTAR COBRO ──
    def ejecutar_cobro(self):
        try:
            texto = self.txt_efectivo.text().replace(".", "").replace(",", "")
            efectivo = int(texto) if texto else 0
        except ValueError:
            efectivo = 0

        if self.total_actual == 0:
            QMessageBox.warning(self, "Cobro", "No hay productos en la lista.")
            return
        if efectivo < self.total_actual:
            QMessageBox.warning(self, "Cobro", "El efectivo ingresado es insuficiente.")
            return

        cambio = efectivo - self.total_actual

        # ── OBTENER ID_EMPLEADO ──
        empleado_id = None
        if hasattr(self.controlador, "usuario_actual") and self.controlador.usuario_actual:
            usuario = self.controlador.usuario_actual
            empleado_id = usuario.get("id_empleado")
            if not empleado_id and self.controlador.conexion:
                id_usuario = usuario.get("id_usuario")
                if id_usuario:
                    try:
                        cursor = self.controlador.conexion.cursor()
                        cursor.execute("SELECT id_empleado FROM usuarios WHERE id_usuario = %s", (id_usuario,))
                        row = cursor.fetchone()
                        if row:
                            empleado_id = row[0]
                        cursor.close()
                    except Exception as e:
                        print(f"Error al consultar id_empleado: {e}")
                if not empleado_id:
                    username = usuario.get("username_log")
                    if username:
                        try:
                            cursor = self.controlador.conexion.cursor()
                            cursor.execute("""
                                SELECT e.id_empleado FROM empleados e
                                JOIN usuarios u ON u.id_empleado = e.id_empleado
                                WHERE u.username_log = %s
                            """, (username,))
                            row = cursor.fetchone()
                            if row:
                                empleado_id = row[0]
                            cursor.close()
                        except Exception as e:
                            print(f"Error al consultar por username: {e}")

        if not empleado_id:
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo identificar al empleado.\n"
                "Asegúrate de haber iniciado sesión correctamente.\n"
                "Contacta al administrador si el problema persiste."
            )
            return

        dlg = DialogoCobro(
            self.total_actual, efectivo, cambio, empleado_id,
            self.productos_venta, self.controlador.conexion, self
        )

        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.exito:
            self.productos_venta = []
            self.txt_efectivo.clear()
            self.filtro_actual = ""
            self.renderizar_tabla()
            QMessageBox.information(
                self, "Éxito",
                f"Venta registrada correctamente.\nTotal: ${self.total_actual:,.0f}\nCambio: ${cambio:,.0f}"
            )

    # ── MÉTODOS DE USUARIO Y RENDERIZADO ──
    def actualizar_usuario(self, nombre, rol):
        nombre_display = str(nombre).strip().title()
        rol_display = str(rol).strip().upper()
        self.lbl_nombre_cajero.setText(nombre_display)
        self.lbl_rol_caja.setText(rol_display)
        iniciales = "".join([n[0] for n in nombre_display.split()[:2]]).upper()
        self.lbl_avatar.setText(iniciales)

    def showEvent(self, event):
        if hasattr(self.controlador, "usuario_actual") and self.controlador.usuario_actual:
            datos = self.controlador.usuario_actual
            self.actualizar_usuario(datos.get("nombre", "Usuario"), datos.get("rol", "cajero"))
        self.renderizar_tabla()
        super().showEvent(event)

    def renderizar_tabla(self):
        self.tabla_productos.setRowCount(0)
        self.total_actual = 0

        def _item_font(w=QFont.Weight.Bold):
            f = QFont("Montserrat", 14, w)
            f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return f

        for p in self.productos_venta:
            self.total_actual += p["precio_total"]
            row = self.tabla_productos.rowCount()
            self.tabla_productos.insertRow(row)

            it_id = QTableWidgetItem(str(p["id"]))
            it_id.setFont(_item_font())
            it_id.setForeground(QColor("#9CA3AF"))
            it_id.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            it_nom = QTableWidgetItem(p["nombre"].upper())
            it_nom.setFont(_item_font())
            it_nom.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            txt_detalle = []
            if p["cantidad"] > 0:
                txt_detalle.append(f"{p['cantidad']} und")
            if p["peso"] > 0:
                txt_detalle.append(f"{p['peso']} g")

            it_cant = QTableWidgetItem(" / ".join(txt_detalle))
            it_cant.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            it_cant.setFont(_item_font())
            it_cant.setForeground(QColor(self.BRAND))

            it_precio = QTableWidgetItem("${:,}".format(p["precio_total"]))
            it_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            it_precio.setFont(_item_font(QFont.Weight.Black))

            self.tabla_productos.setItem(row, 0, it_id)
            self.tabla_productos.setItem(row, 1, it_nom)
            self.tabla_productos.setItem(row, 2, it_cant)
            self.tabla_productos.setItem(row, 3, it_precio)

        self.lbl_display_total.setText("${:,}".format(self.total_actual))

        if self.productos_venta:
            self.table_stack.setCurrentWidget(self.tabla_productos)
            self.lbl_estado_tabla.hide()
        else:
            self.lbl_estado_tabla.show()
            self.table_stack.setCurrentWidget(self.lbl_estado_tabla)
            self.lbl_estado_tabla.raise_()

        self.aplicar_filtro()
        self.actualizar_estado_botones()
        self.actualizar_cambio()

    def actualizar_cambio(self):
        try:
            texto = self.txt_efectivo.text().replace(".", "").replace(",", "")
            efectivo = int(texto) if texto else 0
        except ValueError:
            efectivo = 0
        cambio = efectivo - self.total_actual
        self.lbl_display_cambio.setText("${:,}".format(cambio) if cambio > 0 else "$0")

    def cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Salir", "¿Estás seguro de que deseas cerrar la sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.controlador.cambiar_pantalla("Login")

    def volver_dashboard(self):
        self.controlador.cambiar_pantalla("AdminDashboard")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(self.COLOR_FONDO)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())