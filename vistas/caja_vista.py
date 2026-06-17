import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox,
    QPushButton, QLabel, QFrame, QTableWidget, QListWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QGraphicsDropShadowEffect, QStackedLayout, QCompleter
)
from PySide6.QtCore import Qt, QPoint, QStringListModel
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QFontDatabase

# ══════════════════════════════════════════════════════════════════════════════
# NUEVO DIÁLOGO: AGREGAR PRODUCTO (CON AUTOCOMPLETADO DE BD)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoAgregarFactura(QDialog):
    def __init__(self, conexion=None, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self._conexion = conexion
        self.resultado = None
        
        # Diccionario para almacenar los productos de la BD: { "NOMBRE": {"id": 1, "precio": 1500} }
        self.productos_db = {}
        self.producto_actual = None

        layout_fondo = QVBoxLayout(self)
        layout_fondo.setContentsMargins(0, 0, 0, 0)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Tarjeta Central Blanca (MÁS GRANDE Y CON BORDES CORREGIDOS) ──
        self.card = QFrame()
        self.card.setObjectName("MainCard")
        # Ventana más grande para mejor visibilidad
        self.card.setFixedSize(650, 680) 
        # El ID #MainCard asegura que solo este fondo tenga los bordes y no afecte a los hijos
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

        # Márgenes amplios (40px) para que NADA pise los bordes redondeados
        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(40, 40, 40, 40)
        layout_card.setSpacing(24)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return font

        # ── HEADER ──
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

        # ── ESTILO GLOBAL PARA INPUTS ──
        estilo_input = """
            QLineEdit, QSpinBox {
                background-color: #F8FAF9; border: 2px solid #D1E2D9;
                border-radius: 14px; padding: 0 16px; color: #1F2937;
            }
            QLineEdit:focus, QSpinBox:focus { border: 2px solid #17813D; background-color: #FFFFFF; }
            QSpinBox::up-button, QSpinBox::down-button { width: 30px; }
        """

        # ── NOMBRE DEL PRODUCTO (CON AUTOCOMPLETADO) ──
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

        # ── FILA: CANTIDAD Y PESO ──
        fila_cantidades = QHBoxLayout()
        fila_cantidades.setSpacing(20)

        # Col Cantidad
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

        # Col Peso
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

        # ── PRECIO UNITARIO (AUTOMÁTICO) ──
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

        # ── TOTAL CALCULADO ──
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

        # ── FOOTER BOTONES ──
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

        # Cargar datos de la Base de Datos y configurar el autocompletado
        self._cargar_productos_bd()

    def _cargar_productos_bd(self):
        # 1. Escudo de seguridad
        if not self._conexion:
            print("Error: El diálogo recibió una conexión vacía (None).")
            return 

        try:
            cursor = self._conexion.cursor()
            cursor.execute("SELECT id_producto, nombre_producto, precio_venta_prod FROM productos")
            
            filas = cursor.fetchall()
            for fila in filas:
                # 2. EVALUACIÓN INTELIGENTE: Detectar si es Diccionario o Tupla
                if isinstance(fila, dict):
                    # Si tu BD devuelve diccionarios (por el KeyError: 0 que vimos)
                    pid = fila.get("id_producto")
                    nombre = str(fila.get("nombre_producto")).upper()
                    precio = float(fila.get("precio_venta_prod"))
                else:
                    # Si devuelve listas o tuplas tradicionales
                    pid = fila[0]
                    nombre = str(fila[1]).upper()
                    precio = float(fila[2])
                
                self.productos_db[nombre] = {
                    "id": pid, 
                    "precio": precio
                }
            cursor.close()
            
            # Configurar motor autocompletado
            self.modelo_completer = QStringListModel(list(self.productos_db.keys()))
            self.completer = QCompleter(self.modelo_completer, self)
            self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.completer.activated.connect(self._al_seleccionar)
            self.txt_nombre.setCompleter(self.completer)
            
        except Exception as e:
            # Usamos repr() para que si hay otro error, nos dé el nombre completo y no solo un '0'
            print(f"Error inesperado al cargar productos: {repr(e)}")

        # Configurar Autocompletado
        lista_nombres = list(self.productos_db.keys())
        self.modelo_completer = QStringListModel(lista_nombres)
        self.completer = QCompleter(self.modelo_completer, self)
        
        # Filtra sin importar mayúsculas/minúsculas y busca en cualquier parte de la palabra
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        
        # Aplicamos el completer al input
        self.txt_nombre.setCompleter(self.completer)

    def _verificar_producto(self):
        """Revisa si lo que escribió el usuario coincide con algún producto de la BD"""
        texto_ingresado = self.txt_nombre.text().upper().strip()
        
        if texto_ingresado in self.productos_db:
            # Producto encontrado en la BD
            self.producto_actual = self.productos_db[texto_ingresado]
            self.producto_actual["nombre"] = texto_ingresado
            
            # Autocompletar el precio
            precio = self.producto_actual["precio"]
            self.txt_precio.setText(f"${int(precio):,}")
            
            # Habilitar botón y establecer por defecto 1 unidad
            self.btn_anadir.setEnabled(True)
            if self.spin_cant.value() == 0 and self.spin_peso.value() == 0:
                self.spin_cant.setValue(1)
            
            self.txt_nombre.setStyleSheet("""
                QLineEdit { background-color: #E8F5EE; border: 2px solid #17813D; border-radius: 14px; padding: 0 16px; color: #17813D; font-weight: bold; }
            """)
        else:
            # Aún no se selecciona un producto válido
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

        # Calcula el total de unidades + el total en base al peso
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
# DIÁLOGO DE ELIMINAR 
# ══════════════════════════════════════════════════════════════════════════════
class DialogoEliminar(QDialog):
    def __init__(self, productos, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.productos = productos
        self.indice_seleccionado = -1

        layout_fondo = QVBoxLayout(self)
        # SOLUCCIÓN 1: Damos margen de 24px para que la sombra y las esquinas no se corten contra el borde de la ventana
        layout_fondo.setContentsMargins(24, 24, 24, 24)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Tarjeta Central ──
        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(650, 680) 
        
        # SOLUCIÓN 2: Forzamos a Qt a usar el motor de renderizado de hojas de estilo para evitar el fondo rectangular nativo
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.card.setStyleSheet("QFrame#MainCard { background-color: #FFFFFF; border-radius: 28px; border: 2px solid #D1E2D9; }")
        
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

        # ── HEADER ──
        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("QUITAR DE LA FACTURA")
        lbl_titulo.setFont(_f(18, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #DC6468; background: transparent; border: none;")
        
        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(36, 36)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet("QPushButton { background-color: #F4F7F5; border-radius: 18px; color: #708077; border: none; }")
        btn_cerrar.clicked.connect(self.reject)
        layout_header.addWidget(lbl_titulo)
        layout_header.addStretch()
        layout_header.addWidget(btn_cerrar)
        layout_card.addLayout(layout_header)

        # ── CONTENIDO ──
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
            self.lista.setStyleSheet(
                "QListWidget { background-color: #F8FAF9; border: 2px solid #D1E2D9; border-radius: 14px; padding: 8px; outline: none; }"
                "QListWidget::item { padding: 14px 16px; border-bottom: 1px solid #EAEFEA; color: #1F2937; }"
                "QListWidget::item:hover { background-color: #F1F5F2; border-radius: 8px; }"
                "QListWidget::item:selected { background-color: #FADBD8; color: #DC6468; border-radius: 10px; font-weight: bold; }"
            )
            self.lista.setFont(_f(13, QFont.Weight.Medium))
            self.lista.setFixedHeight(340)
            
            for p in productos:
                self.lista.addItem(f"ID {p['id']}   ·   {p['nombre'].upper()}   ·   ${int(p['precio']):,}")
                
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

class DialogoModificar(QDialog):
    def __init__(self, productos, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self._productos = productos
        self.resultado = None

        layout_fondo = QVBoxLayout(self)
        # SOLUCCIÓN 1: Damos margen de 24px para la correcta renderización de la sombra y esquinas
        layout_fondo.setContentsMargins(24, 24, 24, 24)
        layout_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Tarjeta Central ──
        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(650, 680) 
        
        # SOLUCIÓN 2: Forzamos a Qt a renderizar correctamente los bordes curvos
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.card.setStyleSheet("QFrame#MainCard { background-color: #FFFFFF; border-radius: 28px; border: 2px solid #D1E2D9; }")
        
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(40)
        sombra.setColor(QColor(0, 0, 0, 45))
        sombra.setOffset(0, 10)
        self.card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(40, 40, 40, 40)
        layout_card.setSpacing(16)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            return font

        # ── HEADER ──
        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("EDITAR ITEM DE FACTURA")
        lbl_titulo.setFont(_f(18, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent; border: none;")
        
        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(36, 36)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet("QPushButton { background-color: #F4F7F5; border-radius: 18px; color: #708077; border: none; }")
        btn_cerrar.clicked.connect(self.reject)
        layout_header.addWidget(lbl_titulo)
        layout_header.addStretch()
        layout_header.addWidget(btn_cerrar)
        layout_card.addLayout(layout_header)

        # ── FILTRO / BUSCADOR ──
        lbl_buscar = QLabel("BUSCAR ITEM EN LA FACTURA")
        lbl_buscar.setFont(_f(11, QFont.Weight.Bold))
        lbl_buscar.setStyleSheet("color: #708077; background: transparent;")
        layout_card.addWidget(lbl_buscar)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Escribe ID o nombre para filtrar la lista...")
        self.txt_buscar.setFixedHeight(56)
        self.txt_buscar.setStyleSheet("QLineEdit { background-color: #F8FAF9; border: 2px solid #D1E2D9; border-radius: 14px; padding: 0 16px; color: #1F2937; }")
        self.txt_buscar.textChanged.connect(self._buscar)
        layout_card.addWidget(self.txt_buscar)

        # ── LISTA DE ÍTEMS ──
        self.lista = QListWidget()
        self.lista.setStyleSheet(
            "QListWidget { background-color: #F8FAF9; border: 2px solid #D1E2D9; border-radius: 14px; padding: 8px; outline: none; }"
            "QListWidget::item { padding: 12px 14px; border-bottom: 1px solid #EAEFEA; color: #1F2937; }"
            "QListWidget::item:hover { background-color: #F1F5F2; border-radius: 8px; }"
            "QListWidget::item:selected { background-color: #E2ECE6; color: #17813D; border-radius: 10px; font-weight: bold; }"
        )
        self.lista.setFont(_f(12, QFont.Weight.Medium))
        self.lista.setFixedHeight(160)
        
        self._indices = list(range(len(productos)))
        for p in productos:
            self.lista.addItem(f"ID {p['id']}   ·   {p['nombre'].upper()}")
            
        self.lista.currentRowChanged.connect(self._cargar_valores_item)
        layout_card.addWidget(self.lista)

        # ── FORMULARIO DE EDICIÓN ──
        fila_form = QHBoxLayout()
        fila_form.setSpacing(20)

        # Columna Cantidad
        col_cant = QVBoxLayout()
        col_cant.setSpacing(6)
        lbl_cant = QLabel("NUEVA CANTIDAD")
        lbl_cant.setFont(_f(11, QFont.Weight.Bold))
        lbl_cant.setStyleSheet("color: #708077; background: transparent;")
        self.spin_cant = QSpinBox()
        self.spin_cant.setRange(1, 9999)
        self.spin_cant.setFixedHeight(56)
        self.spin_cant.setStyleSheet(
            "QSpinBox { background-color: #F8FAF9; border: 2px solid #D1E2D9; border-radius: 14px; padding: 0 12px; color: #1F2937; }"
            "QSpinBox:focus { border: 2px solid #17813D; }"
        )
        col_cant.addWidget(lbl_cant)
        col_cant.addWidget(self.spin_cant)

        # Columna Precio
        col_prec = QVBoxLayout()
        col_prec.setSpacing(6)
        lbl_prec = QLabel("NUEVO PRECIO (OPCIONAL)")
        lbl_prec.setFont(_f(11, QFont.Weight.Bold))
        lbl_prec.setStyleSheet("color: #708077; background: transparent;")
        self.txt_precio = QLineEdit()
        self.txt_precio.setPlaceholderText("Vacío para conservar el actual")
        self.txt_precio.setFixedHeight(56)
        self.txt_precio.setStyleSheet("QLineEdit { background-color: #F8FAF9; border: 2px solid #D1E2D9; border-radius: 14px; padding: 0 16px; color: #1F2937; }")
        col_prec.addWidget(lbl_prec)
        col_prec.addWidget(self.txt_precio)

        fila_form.addLayout(col_cant)
        fila_form.addLayout(col_prec)
        layout_card.addLayout(fila_form)

        # ── BOTÓN GUARDAR ──
        self.btn_guardar = QPushButton("GUARDAR CAMBIOS")
        self.btn_guardar.setFixedHeight(60)
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
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
            if texto in str(p["id"]).lower() or texto in p["nombre"].lower():
                self.lista.addItem(f"ID {p['id']}   ·   {p['nombre'].upper()}")
                self._indices.append(i)

    def _cargar_valores_item(self, row):
        if row >= 0 and row < len(self._indices):
            self.btn_guardar.setEnabled(True)
            idx_real = self._indices[row]
            prod_sel = self._productos[idx_real]
            if "cantidad" in prod_sel:
                self.spin_cant.setValue(int(prod_sel["cantidad"]))
        else:
            self.btn_guardar.setEnabled(False)

    def _confirmar(self):
        row = self.lista.currentRow()
        if row < 0 or row >= len(self._indices):
            return
            
        precio_txt = self.txt_precio.text().strip().replace(".", "").replace(",", "")
        try:
            precio = int(float(precio_txt)) if precio_txt else None
        except ValueError:
            precio = None
            
        self.resultado = {
            "indice"  : self._indices[row],
            "cantidad": self.spin_cant.value(),
            "precio"  : precio,
        }
        self.accept()

# ══════════════════════════════════════════════════════════════════════════════
# VISTA PRINCIPAL DE CAJA
# ══════════════════════════════════════════════════════════════════════════════
class CajaVista(QWidget):
    def __init__(self, controlador_flujo):
        super().__init__()
        self.controlador     = controlador_flujo
        self.productos_venta = []
        self.total_actual    = 0

        ruta_vistas     = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz       = os.path.dirname(ruta_vistas)
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")

        for f in ("Montserrat-Bold.ttf", "Montserrat-Regular.ttf", "Montserrat-Medium.ttf", "Montserrat-Black.ttf"):
            ruta_f = os.path.join(carpeta_fuentes, f)
            if os.path.exists(ruta_f):
                QFontDatabase.addApplicationFont(ruta_f)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return font

        self.fuente_heavy   = _f(34, QFont.Weight.Bold)
        self.fuente_titulos = _f(22, QFont.Weight.Black)
        self.fuente_tags    = _f(9,  QFont.Weight.Bold)
        self.fuente_nav     = _f(11, QFont.Weight.Black)
        self.fuente_btns    = _f(11, QFont.Weight.Black)

        self.COLOR_FONDO   = "#F0F4F2"
        self.BRAND         = "#17813D"

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(12, 13, 12, 13)
        layout_principal.setSpacing(0)

        # Contenedor Principal
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

        tab_on  = "QPushButton { background:transparent; color:#17813D; font-family:'Montserrat'; font-size:11px; font-weight:900; border:none; border-bottom:3px solid #17813D; padding:0 30px; height:68px; }"
        tab_off = "QPushButton { background:transparent; color:#9CA3AF; font-family:'Montserrat'; font-size:11px; font-weight:800; border:none; border-bottom:3px solid transparent; padding:0 24px; height:68px; } QPushButton:hover { color:#17813D; }"

        tabs = QHBoxLayout()
        tabs.setSpacing(0)
        b_caja = QPushButton("CAJA")
        b_caja.setStyleSheet(tab_on)
        for b, txt in [(QPushButton("FACTURA\nELECTRÓNICA"), ""), (QPushButton("DEVOLUCIONES"), ""), (QPushButton("RECIBO\nPROVEEDORES"), "")]:
            b.setStyleSheet(tab_off)
            b.setFont(self.fuente_nav)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            tabs.addWidget(b)

        b_caja.setFont(self.fuente_nav)
        b_caja.setCursor(Qt.CursorShape.PointingHandCursor)
        tabs.insertWidget(0, b_caja)

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

        # ── CUERPO ──
        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.setSpacing(0)

        panel_cobros = QFrame()
        panel_cobros.setObjectName("PanelCobros")
        panel_cobros.setFixedWidth(268)
        panel_cobros.setStyleSheet("QFrame#PanelCobros { background:#FAFCFB; border:none; border-right:1px solid #EEF0F2; }")
        
        layout_panel = QVBoxLayout(panel_cobros)
        layout_panel.setContentsMargins(18, 18, 18, 18)
        layout_panel.setSpacing(14)

        card_total = QFrame()
        card_total.setFixedHeight(112)
        card_total.setStyleSheet("QFrame { background:#17813D; border:none; border-radius:22px; }")
        st = QGraphicsDropShadowEffect(self)
        st.setBlurRadius(14)
        st.setColor(QColor(23, 129, 61, 60))
        st.setOffset(0, 6)
        card_total.setGraphicsEffect(st)
        lct = QVBoxLayout(card_total)
        lct.setContentsMargins(20, 16, 20, 14)
        lct.setSpacing(2)
        lbl_tt = QLabel("TOTAL A PAGAR:")
        lbl_tt.setFont(self.fuente_tags)
        lbl_tt.setStyleSheet("color:#FFFFFF; background:transparent;")
        self.lbl_display_total = QLabel("$0")
        self.lbl_display_total.setFont(self.fuente_heavy)
        self.lbl_display_total.setStyleSheet("color:#FFFFFF; background:transparent;")
        lct.addWidget(lbl_tt)
        lct.addWidget(self.lbl_display_total)

        card_efectivo = QFrame()
        card_efectivo.setFixedHeight(108)
        card_efectivo.setStyleSheet("QFrame { background:#FFFFFF; border:2px solid #A9DDBC; border-radius:22px; }")
        lce = QVBoxLayout(card_efectivo)
        lce.setContentsMargins(20, 16, 20, 10)
        lce.setSpacing(2)
        lbl_te = QLabel("EFECTIVO:")
        lbl_te.setFont(self.fuente_tags)
        lbl_te.setStyleSheet("color:#17813D; background:transparent;")
        self.txt_efectivo = QLineEdit()
        self.txt_efectivo.setPlaceholderText("0")
        self.txt_efectivo.setFont(self.fuente_heavy)
        self.txt_efectivo.setFixedHeight(48)
        self.txt_efectivo.setStyleSheet("QLineEdit { color:#9CA3AF; background:transparent; border:none; padding:0; }")
        self.txt_efectivo.textChanged.connect(self.actualizar_cambio)
        lce.addWidget(lbl_te)
        lce.addWidget(self.txt_efectivo)

        card_cambio = QFrame()
        card_cambio.setFixedHeight(108)
        card_cambio.setStyleSheet("QFrame { background:#FDEEEF; border:2px solid #F8CBCD; border-radius:22px; }")
        lcc = QVBoxLayout(card_cambio)
        lcc.setContentsMargins(20, 16, 20, 10)
        lcc.setSpacing(2)
        lbl_tc = QLabel("CAMBIO:")
        lbl_tc.setFont(self.fuente_tags)
        lbl_tc.setStyleSheet("color:#DC6468; background:transparent;")
        self.lbl_display_cambio = QLabel("$0")
        self.lbl_display_cambio.setFont(self.fuente_heavy)
        self.lbl_display_cambio.setStyleSheet("color:#DC6468; background:transparent;")
        lcc.addWidget(lbl_tc)
        lcc.addWidget(self.lbl_display_cambio)

        layout_panel.addWidget(card_total)
        layout_panel.addWidget(card_efectivo)
        layout_panel.addStretch()
        layout_panel.addWidget(card_cambio)

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
            QTableWidget { border:none; background:transparent; outline:none; }
            QTableWidget::item { border-bottom:1px solid #F0F2F0; color:#1F2937; font-family:'Montserrat'; font-size:12px; padding-left:4px; }
            QTableWidget::item:selected { background:#E8F5EE; color:#17813D; }
        """)
        hdr = self.tabla_productos.horizontalHeader()
        hdr.setFixedHeight(38)
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hdr.setStyleSheet("""
            QHeaderView::section { background:transparent; color:#86B896; font-family:'Montserrat'; font-size:10px; font-weight:800; border:none; border-bottom:1px solid #EEF0F2; padding-left:4px; }
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
        table_shell.setStyleSheet("QFrame { background:transparent; border:none; }")
        self.table_stack = QStackedLayout(table_shell)
        self.table_stack.setContentsMargins(0, 0, 0, 0)
        self.table_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.table_stack.addWidget(self.tabla_productos)
        self.table_stack.addWidget(self.lbl_estado_tabla)

        layout_area.addWidget(lbl_fact)
        layout_area.addWidget(table_shell, 1)

        cuerpo.addWidget(panel_cobros)
        cuerpo.addWidget(area_tabla)
        layout_contenedor.addLayout(cuerpo, 1)

        # ── BARRA INFERIOR ──
        barra_inferior = QFrame()
        barra_inferior.setFixedHeight(92)
        barra_inferior.setStyleSheet("""
            QFrame { 
                border: none; border-top: 1px solid #EEF0F2; background: #FFFFFF; 
                border-bottom-left-radius: 18px; border-bottom-right-radius: 18px; 
            }
        """)
        layout_inferior = QHBoxLayout(barra_inferior)
        layout_inferior.setContentsMargins(24, 0, 24, 0)

        self.btn_cobrar = QPushButton("COBRAR")
        self.btn_cobrar.setFixedSize(195, 56)
        self.btn_cobrar.setFont(_f(13, QFont.Weight.Black))
        self.btn_cobrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cobrar.setStyleSheet("""
            QPushButton { background:#17813D; color:#FFFFFF; border:none; border-radius:16px; letter-spacing:1px; }
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
            b.setFixedSize(ancho, 50)
            b.setFont(self.fuente_btns)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if destacado:
                b.setStyleSheet("QPushButton { background:#FFFFFF; color:#17813D; border:2px solid #A9DDBC; border-radius:16px; font-family:'Montserrat'; font-size:11px; font-weight:900; } QPushButton:hover { background:#E9F7EF; }")
            else:
                b.setStyleSheet("QPushButton { background:#FFFFFF; color:#9CA3AF; border:2px solid #EEEFF2; border-radius:16px; font-family:'Montserrat'; font-size:11px; font-weight:900; } QPushButton:hover { color:#17813D; border-color:#A9DDBC; }")
            return b

        self.btn_agregar   = _btn_sec("BUSCAR Y AGREGAR", 190, destacado=True)
        self.btn_eliminar  = _btn_sec("ELIMINAR",  128)

        self.btn_agregar.clicked.connect(self.abrir_buscador_agregar)
        self.btn_eliminar.clicked.connect(self.abrir_eliminar)

        layout_bsec = QHBoxLayout()
        layout_bsec.setSpacing(12)
        layout_bsec.addWidget(self.btn_agregar)
        layout_bsec.addWidget(self.btn_eliminar)

        layout_inferior.addWidget(self.btn_cobrar)
        layout_inferior.addStretch()
        layout_inferior.addLayout(layout_bsec)

        layout_contenedor.addWidget(barra_inferior)
        layout_principal.addWidget(self.contenedor_blanco)

    # ══════════════════════════════════════════════════════════════════════════
    # ACCIONES
    # ══════════════════════════════════════════════════════════════════════════
    def abrir_buscador_agregar(self):
        # 1. Imprimimos todo lo que tiene el controlador para investigar
        print("🔍 Buscando conexión... Variables en el controlador:", dir(self.controlador))
        
        # 2. Intentamos obtener la conexión (quizás se llame diferente a "conexion")
        conexion_bd = getattr(self.controlador, "conexion", None)

        # 3. FRENO DE EMERGENCIA: Si no hay conexión, detenemos el proceso aquí
        if conexion_bd is None:
            QMessageBox.critical(self, "Error de Conexión", 
                                 "No se encontró la conexión a la base de datos.\\n\\nRevisa la consola (terminal) para ver los nombres reales de las variables en tu controlador.")
            return # <-- ESTO ES CLAVE: Evita que el programa continúe y se rompa
        
        # 4. Si la conexión existe, abrimos el diálogo normalmente
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

    def actualizar_usuario(self, nombre, rol):
        nombre_display = str(nombre).strip().title()
        rol_display    = str(rol).strip().upper()
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
            f = QFont("Montserrat", 11, w)
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
            if p["cantidad"] > 0: txt_detalle.append(f"{p['cantidad']} und")
            if p["peso"] > 0: txt_detalle.append(f"{p['peso']} g")
            
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

        self.actualizar_cambio()

    def actualizar_cambio(self):
        try:
            texto = self.txt_efectivo.text().replace(".", "").replace(",", "")
            efectivo = int(texto) if texto else 0
        except ValueError:
            efectivo = 0
        cambio = efectivo - self.total_actual
        self.lbl_display_cambio.setText("${:,}".format(cambio) if cambio > 0 else "$0")

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
        QMessageBox.information(
            self, "Éxito", f"COBRO EXITOSO\n\nTotal: ${self.total_actual:,}\nCambio: ${cambio:,}"
        )
        self.productos_venta = []
        self.txt_efectivo.clear()
        self.renderizar_tabla()

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