import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox,
    QPushButton, QLabel, QFrame, QTableWidget, QListWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QGraphicsDropShadowEffect, QStackedLayout
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QFontDatabase, QPainterPath, QRegion


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO BASE  — estética idéntica a las imágenes de referencia
# ══════════════════════════════════════════════════════════════════════════════
class DialogoBase(QDialog):
    """
    Ventana emergente flotante con:
      • Fondo semitransparente sobre la vista completa
      • Card blanca, border-radius 26px, sombra suave
      • Título verde Bold + botón ✕ gris arriba a la derecha
      • Sin bordes de ventana del SO
    """
    def __init__(self, titulo, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint |
                                Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        def _f(size, weight):
            font = QFont("Montserrat", size, weight)
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return font

        self.BRAND       = "#17813D"
        self.BRAND_MUTED = "#E9F7EF"
        self.BRAND_BRD   = "#A9DDBC"
        self.INPUT_BG    = "#EDF7F1"
        self.DANGER      = "#DC2626"

        # Overlay gris semitransparente
        overlay = QFrame(self)
        overlay.setObjectName("Overlay")
        overlay.setStyleSheet("QFrame#Overlay { background:rgba(60,80,60,0.35); border:none; }")

        # Card blanca centrada
        self.card = QFrame(self)
        self.card.setObjectName("DialogCard")
        self.card.setFixedWidth(370)
        self.card.setStyleSheet("""
            QFrame#DialogCard {
                background-color: #FFFFFF;
                border-radius: 26px;
                border: none;
            }
        """)
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(40)
        sombra.setColor(QColor(0, 0, 0, 55))
        sombra.setOffset(0, 10)
        self.card.setGraphicsEffect(sombra)

        self.layout_card = QVBoxLayout(self.card)
        self.layout_card.setContentsMargins(30, 24, 30, 28)
        self.layout_card.setSpacing(16)

        # ── Fila encabezado ────────────────────────────────────────────────
        fila_titulo = QHBoxLayout()
        fila_titulo.setContentsMargins(0, 0, 0, 0)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(_f(15, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color:#17813D; background:transparent;")

        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(28, 28)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setFont(_f(10, QFont.Weight.Bold))
        btn_cerrar.setStyleSheet(
            "QPushButton { background:transparent; color:#9CA3AF; border:none; }"
            "QPushButton:hover { color:#DC2626; }"
        )
        btn_cerrar.clicked.connect(self.reject)

        fila_titulo.addWidget(lbl_titulo)
        fila_titulo.addStretch()
        fila_titulo.addWidget(btn_cerrar)
        self.layout_card.addLayout(fila_titulo)

    # ── Helpers para agregar campos con el estilo de la imagen ────────────
    def _lbl(self, texto):
        f = QFont("Montserrat", 8, QFont.Weight.Black)
        f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        lbl = QLabel(texto)
        lbl.setFont(f)
        lbl.setStyleSheet("color:#17813D; background:transparent; letter-spacing:0.5px;")
        return lbl

    def _input(self, placeholder="", password=False):
        f = QFont("Montserrat", 13, QFont.Weight.Medium)
        f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        txt = QLineEdit()
        txt.setPlaceholderText(placeholder)
        txt.setFont(f)
        txt.setFixedHeight(48)
        if password:
            txt.setEchoMode(QLineEdit.EchoMode.Password)
        txt.setStyleSheet(
            "QLineEdit { background:#EDF7F1; color:#1F2937; border:none;"
            " border-radius:14px; padding:0 16px; }"
            "QLineEdit:focus { border:2px solid #17813D; }"
        )
        return txt

    def _spin(self, minval=1, maxval=9999):
        f = QFont("Montserrat", 13, QFont.Weight.Medium)
        f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        sp = QSpinBox()
        sp.setMinimum(minval)
        sp.setMaximum(maxval)
        sp.setFont(f)
        sp.setFixedHeight(48)
        sp.setStyleSheet(
            "QSpinBox { background:#EDF7F1; color:#1F2937; border:2px solid #17813D;"
            " border-radius:14px; padding:0 12px; }"
            "QSpinBox::up-button, QSpinBox::down-button { width:20px; }"
        )
        return sp

    def _btn_primario(self, texto, color_bg="#17813D", color_hover="#228E49"):
        f = QFont("Montserrat", 12, QFont.Weight.Black)
        f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        b = QPushButton(texto)
        b.setFixedHeight(48)
        b.setFont(f)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setStyleSheet(
            "QPushButton {{ background:{bg}; color:#FFFFFF; border:none;"
            " border-radius:14px; letter-spacing:0.5px; }}"
            "QPushButton:hover {{ background:{hv}; }}".format(bg=color_bg, hv=color_hover)
        )
        return b

    def _btn_cancelar(self, texto="CANCELAR"):
        f = QFont("Montserrat", 11, QFont.Weight.Bold)
        f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        b = QPushButton(texto)
        b.setFixedHeight(44)
        b.setFont(f)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setStyleSheet(
            "QPushButton { background:transparent; color:#9CA3AF; border:none; }"
            "QPushButton:hover { color:#17813D; }"
        )
        b.clicked.connect(self.reject)
        return b

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Overlay cubre toda la ventana
        for child in self.children():
            if isinstance(child, QFrame) and child.objectName() == "Overlay":
                child.setGeometry(0, 0, self.width(), self.height())
        # Card centrada
        cw, ch = self.card.width(), self.card.height()
        self.card.move((self.width() - cw) // 2, (self.height() - ch) // 2)

    def showEvent(self, event):
        super().showEvent(event)
        # Ajustar tamaño al padre
        if self.parent():
            pg = self.parent().geometry()
            self.setGeometry(self.parent().mapToGlobal(QPoint(0,0)).x(),
                             self.parent().mapToGlobal(QPoint(0,0)).y(),
                             pg.width(), pg.height())
        self.card.adjustSize()
        cw, ch = self.card.width(), self.card.height()
        self.card.move((self.width() - cw) // 2, (self.height() - ch) // 2)


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO 1 — NUEVO ÍTEM  (imagen 1)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoAgregar(DialogoBase):
    def __init__(self, parent=None):
        super().__init__("NUEVO ITEM", parent)
        self.resultado = None

        self.layout_card.addWidget(self._lbl("NOMBRE DEL PRODUCTO"))
        self.txt_nombre = self._input("Escribe el nombre...")
        self.layout_card.addWidget(self.txt_nombre)

        fila = QHBoxLayout()
        fila.setSpacing(12)
        col_cant = QVBoxLayout()
        col_cant.setSpacing(6)
        col_cant.addWidget(self._lbl("CANT / PESO"))
        self.spin_cant = self._spin(1, 9999)
        col_cant.addWidget(self.spin_cant)

        col_precio = QVBoxLayout()
        col_precio.setSpacing(6)
        col_precio.addWidget(self._lbl("PRECIO UNITARIO"))
        self.txt_precio = self._input("0")
        col_precio.addWidget(self.txt_precio)

        fila.addLayout(col_cant)
        fila.addLayout(col_precio)
        self.layout_card.addLayout(fila)

        self.layout_card.addSpacing(4)

        fila_btns = QHBoxLayout()
        fila_btns.addStretch()
        fila_btns.addWidget(self._btn_cancelar())
        btn_añadir = self._btn_primario("AÑADIR")
        btn_añadir.setFixedWidth(120)
        btn_añadir.clicked.connect(self._confirmar)
        fila_btns.addWidget(btn_añadir)
        self.layout_card.addLayout(fila_btns)

    def _confirmar(self):
        nombre = self.txt_nombre.text().strip()
        precio_txt = self.txt_precio.text().strip().replace(",", "").replace(".", "")
        if not nombre:
            self.txt_nombre.setFocus()
            return
        try:
            precio = int(precio_txt) if precio_txt else 0
        except ValueError:
            precio = 0
        self.resultado = {
            "nombre"  : nombre,
            "cantidad": self.spin_cant.value(),
            "precio"  : precio,
        }
        self.accept()


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO 2 — QUITAR DE FACTURA  (imagen 2)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoEliminar(DialogoBase):
    def __init__(self, productos, parent=None):
        super().__init__("QUITAR DE FACTURA", parent)
        self.indice_seleccionado = -1

        self.lista = QListWidget()
        self.lista.setStyleSheet("""
            QListWidget {
                background: #EDF7F1;
                border: none;
                border-radius: 14px;
                font-family: 'Montserrat';
                font-size: 12px;
                color: #1F2937;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid #D1EDD9;
            }
            QListWidget::item:selected {
                background: #17813D;
                color: #FFFFFF;
                border-radius: 10px;
            }
        """)
        f = QFont("Montserrat", 12, QFont.Weight.Medium)
        f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        self.lista.setFont(f)
        self.lista.setFixedHeight(160)

        if productos:
            for p in productos:
                self.lista.addItem(
                    "{}  ·  {}  ·  ${:,}".format(p["id"], p["nombre"], p["precio"])
                )
        else:
            lbl_vacio = QLabel("LISTA VACÍA")
            lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fv = QFont("Montserrat", 11, QFont.Weight.Bold)
            fv.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            lbl_vacio.setFont(fv)
            lbl_vacio.setStyleSheet("color:#C0CCC5; background:transparent;")
            lbl_vacio.setFixedHeight(80)
            self.layout_card.addWidget(lbl_vacio)

        if productos:
            self.layout_card.addWidget(self.lista)

        self.layout_card.addSpacing(4)

        fila_btns = QHBoxLayout()
        fila_btns.addStretch()
        fila_btns.addWidget(self._btn_cancelar())
        btn_elim = self._btn_primario("ELIMINAR", "#DC6468", "#C0484B")
        btn_elim.setFixedWidth(130)
        btn_elim.clicked.connect(self._confirmar)
        fila_btns.addWidget(btn_elim)
        self.layout_card.addLayout(fila_btns)

    def _confirmar(self):
        if self.lista.currentRow() >= 0:
            self.indice_seleccionado = self.lista.currentRow()
            self.accept()
        else:
            self.reject()


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO 3 — EDITAR ÍTEM  (imagen 3)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoModificar(DialogoBase):
    def __init__(self, productos, parent=None):
        super().__init__("EDITAR ITEM", parent)
        self.resultado = None
        self._productos = productos

        self.layout_card.addWidget(self._lbl("BUSCA POR ID O NOMBRE"))
        self.txt_buscar = self._input("Escribe ID o nombre del producto...")
        self.layout_card.addWidget(self.txt_buscar)
        self.txt_buscar.textChanged.connect(self._buscar)

        # Lista de resultados
        self.lista = QListWidget()
        self.lista.setStyleSheet("""
            QListWidget {
                background: #EDF7F1;
                border: none;
                border-radius: 14px;
                font-family: 'Montserrat';
                font-size: 11px;
                color: #1F2937;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #D1EDD9;
            }
            QListWidget::item:selected {
                background: #17813D;
                color: #FFFFFF;
                border-radius: 10px;
            }
        """)
        fl = QFont("Montserrat", 11, QFont.Weight.Medium)
        fl.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        self.lista.setFont(fl)
        self.lista.setFixedHeight(110)
        self._poblar_lista(productos)
        self.layout_card.addWidget(self.lista)

        # Campos de edición
        fila = QHBoxLayout()
        fila.setSpacing(12)

        col_cant = QVBoxLayout()
        col_cant.setSpacing(6)
        col_cant.addWidget(self._lbl("NUEVA CANT / PESO"))
        self.spin_cant = self._spin(1, 9999)
        col_cant.addWidget(self.spin_cant)

        col_precio = QVBoxLayout()
        col_precio.setSpacing(6)
        col_precio.addWidget(self._lbl("NUEVO PRECIO UNITARIO"))
        self.txt_precio = self._input("0")
        col_precio.addWidget(self.txt_precio)

        fila.addLayout(col_cant)
        fila.addLayout(col_precio)
        self.layout_card.addLayout(fila)

        btn_guardar = self._btn_primario("GUARDAR CAMBIOS")
        btn_guardar.clicked.connect(self._confirmar)
        self.layout_card.addWidget(btn_guardar)

    def _poblar_lista(self, productos):
        self.lista.clear()
        self._indices = []
        for i, p in enumerate(productos):
            self.lista.addItem("ID {}  ·  {}".format(p["id"], p["nombre"]))
            self._indices.append(i)

    def _buscar(self, texto):
        texto = texto.strip().lower()
        filtrados = []
        indices   = []
        for i, p in enumerate(self._productos):
            if texto in str(p["id"]).lower() or texto in p["nombre"].lower():
                filtrados.append(p)
                indices.append(i)
        self.lista.clear()
        self._indices = indices
        for p in filtrados:
            self.lista.addItem("ID {}  ·  {}".format(p["id"], p["nombre"]))

    def _confirmar(self):
        fila = self.lista.currentRow()
        if fila < 0 or fila >= len(self._indices):
            return
        precio_txt = self.txt_precio.text().strip().replace(",", "").replace(".", "")
        try:
            precio = int(precio_txt) if precio_txt else None
        except ValueError:
            precio = None
        self.resultado = {
            "indice"  : self._indices[fila],
            "cantidad": self.spin_cant.value(),
            "precio"  : precio,
        }
        self.accept()


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO 4 — BUSCADOR DE VENTA  (imagen 4)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoBuscar(DialogoBase):
    def __init__(self, conexion=None, parent=None):
        super().__init__("BUSCADOR DE VENTA", parent)
        self._conexion = conexion

        self.txt_buscar = self._input("Escribe el nombre aquí...")
        self.layout_card.addWidget(self.txt_buscar)
        self.txt_buscar.textChanged.connect(self._buscar_en_bd)

        lbl_hint = QLabel("LA TABLA SE FILTRARÁ AUTOMÁTICAMENTE")
        fh = QFont("Montserrat", 8, QFont.Weight.Bold)
        fh.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        lbl_hint.setFont(fh)
        lbl_hint.setStyleSheet("color:#A9DDBC; background:transparent; letter-spacing:0.5px;")
        lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_card.addWidget(lbl_hint)

        # Tabla resultado
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "NOMBRE", "PRECIO"])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setShowGrid(False)
        self.tabla.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setStyleSheet("""
            QTableWidget { border:none; background:#EDF7F1;
                border-radius:14px; outline:none; }
            QTableWidget::item { color:#1F2937; font-family:'Montserrat';
                font-size:11px; border-bottom:1px solid #D1EDD9; padding:4px; }
            QTableWidget::item:selected { background:#17813D; color:#FFFFFF; }
        """)
        self.tabla.horizontalHeader().setStyleSheet(
            "QHeaderView::section { background:#EDF7F1; color:#86B896;"
            " font-family:'Montserrat'; font-size:9px; font-weight:800;"
            " border:none; border-bottom:1px solid #C4DFC9; padding:6px; }"
        )
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tabla.setColumnWidth(0, 50)
        self.tabla.setColumnWidth(2, 100)
        self.tabla.setFixedHeight(160)
        self.layout_card.addWidget(self.tabla)

        btn_hecho = self._btn_primario("HECHO")
        btn_hecho.clicked.connect(self.accept)
        self.layout_card.addWidget(btn_hecho)

    def _buscar_en_bd(self, texto):
        self.tabla.setRowCount(0)
        texto = texto.strip()
        if not texto or not self._conexion:
            return
        try:
            with self._conexion.cursor() as cursor:
                sql = """
                    SELECT id_producto, nombre_producto, precio_venta
                    FROM productos
                    WHERE nombre_producto LIKE %s
                    LIMIT 30
                """
                cursor.execute(sql, ("%" + texto + "%",))
                filas = cursor.fetchall()
                for fila in filas:
                    if isinstance(fila, dict):
                        pid    = fila["id_producto"]
                        nombre = fila["nombre_producto"]
                        precio = fila["precio_venta"]
                    else:
                        pid, nombre, precio = fila[0], fila[1], fila[2]
                    row = self.tabla.rowCount()
                    self.tabla.insertRow(row)
                    self.tabla.setItem(row, 0, QTableWidgetItem(str(pid)))
                    self.tabla.setItem(row, 1, QTableWidgetItem(str(nombre)))
                    self.tabla.setItem(row, 2, QTableWidgetItem("${:,}".format(int(precio))))
        except Exception:
            pass


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

        for f in ("Montserrat-Bold.ttf", "Montserrat-Regular.ttf",
                  "Montserrat-Medium.ttf", "Montserrat-Black.ttf"):
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
        self.BRAND_LIGHT   = "#228E49"
        self.BRAND_MUTED   = "#E9F7EF"
        self.BRAND_BORDER  = "#A9DDBC"

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

        # ── NAVBAR ─────────────────────────────────────────────────────────────
        navbar = QFrame()
        navbar.setObjectName("NavbarCaja")
        navbar.setFixedHeight(68)
        navbar.setStyleSheet(
            "QFrame#NavbarCaja { background:#FFFFFF; border:none;"
            " border-bottom:1px solid #EEF0F2; }"
        )
        layout_navbar = QHBoxLayout(navbar)
        layout_navbar.setContentsMargins(0, 0, 20, 0)
        layout_navbar.setSpacing(0)

        tab_on  = ("QPushButton { background:transparent; color:#17813D;"
                   " font-family:'Montserrat'; font-size:11px; font-weight:900;"
                   " border:none; border-bottom:3px solid #17813D;"
                   " padding:0 30px; height:68px; }")
        tab_off = ("QPushButton { background:transparent; color:#9CA3AF;"
                   " font-family:'Montserrat'; font-size:11px; font-weight:800;"
                   " border:none; border-bottom:3px solid transparent;"
                   " padding:0 24px; height:68px; }"
                   " QPushButton:hover { color:#17813D; }")

        tabs = QHBoxLayout()
        tabs.setSpacing(0)
        b_caja = QPushButton("CAJA")
        b_caja.setStyleSheet(tab_on)
        for b, txt in [(QPushButton("FACTURA\nELECTRÓNICA"), ""),
                       (QPushButton("DEVOLUCIONES"), ""),
                       (QPushButton("RECIBO\nPROVEEDORES"), "")]:
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

        self.lbl_nombre_cajero = QLabel("Edwin Acosta")
        fn = _f(11, QFont.Weight.Black)
        self.lbl_nombre_cajero.setFont(fn)
        self.lbl_nombre_cajero.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_nombre_cajero.setStyleSheet("color:#17813D; background:transparent;")

        self.lbl_rol_caja = QLabel("CAJERO")
        fr = _f(8, QFont.Weight.Bold)
        self.lbl_rol_caja.setFont(fr)
        self.lbl_rol_caja.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_rol_caja.setStyleSheet("color:#9CA3AF; background:transparent;")

        layout_meta.addWidget(self.lbl_nombre_cajero)
        layout_meta.addWidget(self.lbl_rol_caja)

        self.lbl_avatar = QLabel("EA")
        self.lbl_avatar.setFixedSize(36, 36)
        self.lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_avatar.setFont(_f(11, QFont.Weight.Black))
        self.lbl_avatar.setStyleSheet(
            "QLabel { background:#E9F7EF; border:1px solid #A9DDBC;"
            " border-radius:18px; color:#17813D; }"
        )

        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.setFixedSize(105, 34)
        btn_logout.setFont(_f(8, QFont.Weight.Bold))
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet(
            "QPushButton { background:#FFFFFF; color:#DC2626;"
            " border:1px solid #FECACA; border-radius:9px; }"
            " QPushButton:hover { background:#DC2626; color:#FFFFFF; border-color:#DC2626; }"
        )
        btn_logout.clicked.connect(self.cerrar_sesion)

        btn_salir = QPushButton("✕")
        btn_salir.setFixedSize(36, 36)
        btn_salir.setFont(_f(12, QFont.Weight.Black))
        btn_salir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salir.setStyleSheet(
            "QPushButton { background:#FFFFFF; color:#9CA3AF;"
            " border:1px solid #E5E7EB; border-radius:10px; }"
            " QPushButton:hover { background:#DC2626; color:#FFFFFF; border-color:#DC2626; }"
        )
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

        # ── CUERPO ─────────────────────────────────────────────────────────────
        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.setSpacing(0)

        panel_cobros = QFrame()
        panel_cobros.setObjectName("PanelCobros")
        panel_cobros.setFixedWidth(268)
        panel_cobros.setStyleSheet(
            "QFrame#PanelCobros { background:#FAFCFB; border:none;"
            " border-right:1px solid #EEF0F2; }"
        )
        layout_panel = QVBoxLayout(panel_cobros)
        layout_panel.setContentsMargins(18, 18, 18, 18)
        layout_panel.setSpacing(14)

        card_total = QFrame()
        card_total.setObjectName("CardTotal")
        card_total.setFixedHeight(112)
        card_total.setStyleSheet(
            "QFrame#CardTotal { background:#17813D; border:none; border-radius:22px; }"
        )
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
        card_efectivo.setObjectName("CardEfectivo")
        card_efectivo.setFixedHeight(108)
        card_efectivo.setStyleSheet(
            "QFrame#CardEfectivo { background:#FFFFFF;"
            " border:2px solid #A9DDBC; border-radius:22px; }"
        )
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
        self.txt_efectivo.setStyleSheet(
            "QLineEdit { color:#9CA3AF; background:transparent; border:none; padding:0; }"
        )
        self.txt_efectivo.textChanged.connect(self.actualizar_cambio)
        lce.addWidget(lbl_te)
        lce.addWidget(self.txt_efectivo)

        card_cambio = QFrame()
        card_cambio.setObjectName("CardCambio")
        card_cambio.setFixedHeight(108)
        card_cambio.setStyleSheet(
            "QFrame#CardCambio { background:#FDEEEF;"
            " border:2px solid #F8CBCD; border-radius:22px; }"
        )
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
        area_tabla.setObjectName("AreaFacturacion")
        area_tabla.setStyleSheet(
            "QFrame#AreaFacturacion { border:none; background:#FFFFFF; }"
        )
        layout_area = QVBoxLayout(area_tabla)
        layout_area.setContentsMargins(26, 16, 32, 12)
        layout_area.setSpacing(10)

        lbl_fact = QLabel("FACTURACIÓN")
        lbl_fact.setFont(self.fuente_titulos)
        lbl_fact.setFixedHeight(50)
        lbl_fact.setStyleSheet("color:#17813D; background:transparent;")

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels([
            "ID", "NOMBRE DEL PRODUCTO", "CANTIDAD/PESO", "PRECIO UNITARIO"
        ])
        self.tabla_productos.verticalHeader().setVisible(False)
        self.tabla_productos.verticalHeader().setDefaultSectionSize(50)
        self.tabla_productos.setShowGrid(False)
        self.tabla_productos.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla_productos.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_productos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_productos.setStyleSheet("""
            QTableWidget { border:none; background:#FFFFFF; outline:none; }
            QTableWidget::item { border-bottom:1px solid #F0F2F0; color:#1F2937;
                font-family:'Montserrat'; font-size:12px; padding-left:4px; }
            QTableWidget::item:selected { background:#E8F5EE; color:#17813D; }
        """)
        hdr = self.tabla_productos.horizontalHeader()
        hdr.setFixedHeight(38)
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hdr.setStyleSheet("""
            QHeaderView::section { background:#FFFFFF; color:#86B896;
                font-family:'Montserrat'; font-size:10px; font-weight:800;
                border:none; border-bottom:1px solid #EEF0F2; padding-left:4px; }
        """)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tabla_productos.setColumnWidth(0, 50)
        self.tabla_productos.setColumnWidth(2, 190)
        self.tabla_productos.setColumnWidth(3, 200)

        self.lbl_estado_tabla = QLabel("ESPERANDO PRODUCTOS...")
        self.lbl_estado_tabla.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        fe2 = _f(11, QFont.Weight.Bold)
        fe2.setItalic(True)
        self.lbl_estado_tabla.setFont(fe2)
        self.lbl_estado_tabla.setStyleSheet(
            "color:#DFE3E8; background:transparent; padding-top:70px;"
        )

        table_shell = QFrame()
        table_shell.setObjectName("TablaShell")
        table_shell.setStyleSheet("QFrame#TablaShell { background:#FFFFFF; border:none; }")
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

        # ── BARRA INFERIOR ─────────────────────────────────────────────────────
        barra_inferior = QFrame()
        barra_inferior.setObjectName("BarraInferior")
        barra_inferior.setFixedHeight(92)
        barra_inferior.setStyleSheet(
            "QFrame#BarraInferior { border:none; border-top:1px solid #EEF0F2;"
            " background:#FFFFFF; }"
        )
        layout_inferior = QHBoxLayout(barra_inferior)
        layout_inferior.setContentsMargins(24, 0, 24, 0)

        self.btn_cobrar = QPushButton("COBRAR")
        self.btn_cobrar.setFixedSize(195, 56)
        fc = _f(13, QFont.Weight.Black)
        self.btn_cobrar.setFont(fc)
        self.btn_cobrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cobrar.setStyleSheet(
            "QPushButton { background:#17813D; color:#FFFFFF; border:none;"
            " border-radius:16px; letter-spacing:1px; }"
            " QPushButton:hover { background:#228E49; }"
        )
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
                b.setStyleSheet(
                    "QPushButton { background:#FFFFFF; color:#17813D;"
                    " border:2px solid #A9DDBC; border-radius:16px;"
                    " font-family:'Montserrat'; font-size:11px; font-weight:900; }"
                    " QPushButton:hover { background:#E9F7EF; }"
                )
            else:
                b.setStyleSheet(
                    "QPushButton { background:#FFFFFF; color:#9CA3AF;"
                    " border:2px solid #EEEFF2; border-radius:16px;"
                    " font-family:'Montserrat'; font-size:11px; font-weight:900; }"
                    " QPushButton:hover { color:#17813D; border-color:#A9DDBC; }"
                )
            return b

        self.btn_agregar   = _btn_sec("AGREGAR",   128, destacado=True)
        self.btn_eliminar  = _btn_sec("ELIMINAR",  128)
        self.btn_modificar = _btn_sec("MODIFICAR", 138)
        self.btn_buscar    = _btn_sec("BUSCAR",    118)

        # Conectar cada botón a su diálogo
        self.btn_agregar.clicked.connect(self.abrir_agregar)
        self.btn_eliminar.clicked.connect(self.abrir_eliminar)
        self.btn_modificar.clicked.connect(self.abrir_modificar)
        self.btn_buscar.clicked.connect(self.abrir_buscar)

        layout_bsec = QHBoxLayout()
        layout_bsec.setSpacing(12)
        layout_bsec.addWidget(self.btn_agregar)
        layout_bsec.addWidget(self.btn_eliminar)
        layout_bsec.addWidget(self.btn_modificar)
        layout_bsec.addWidget(self.btn_buscar)

        layout_inferior.addWidget(self.btn_cobrar)
        layout_inferior.addStretch()
        layout_inferior.addLayout(layout_bsec)

        layout_contenedor.addWidget(barra_inferior)
        layout_principal.addWidget(self.contenedor_blanco)

    # ══════════════════════════════════════════════════════════════════════════
    # ACCIONES DE BOTONES
    # ══════════════════════════════════════════════════════════════════════════
    def abrir_agregar(self):
        dlg = DialogoAgregar(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.resultado:
            nuevo_id = (max(p["id"] for p in self.productos_venta) + 1
                        if self.productos_venta else 1001)
            self.productos_venta.append({
                "id"      : nuevo_id,
                "nombre"  : dlg.resultado["nombre"],
                "cantidad": dlg.resultado["cantidad"],
                "precio"  : dlg.resultado["precio"],
            })
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
            QMessageBox.information(self, "Modificar", "No hay productos en la factura.")
            return
        dlg = DialogoModificar(self.productos_venta, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.resultado:
            idx  = dlg.resultado["indice"]
            cant = dlg.resultado["cantidad"]
            prec = dlg.resultado["precio"]
            if 0 <= idx < len(self.productos_venta):
                self.productos_venta[idx]["cantidad"] = cant
                if prec is not None:
                    self.productos_venta[idx]["precio"] = prec
                self.renderizar_tabla()

    def abrir_buscar(self):
        conexion = getattr(self.controlador, "conexion", None)
        dlg = DialogoBuscar(conexion, self)
        dlg.exec()

    # ══════════════════════════════════════════════════════════════════════════
    # USUARIO
    # ══════════════════════════════════════════════════════════════════════════
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
            self.actualizar_usuario(
                datos.get("nombre", "Usuario"),
                datos.get("rol", "cajero")
            )
        self.renderizar_tabla()
        super().showEvent(event)

    # ══════════════════════════════════════════════════════════════════════════
    # TABLA
    # ══════════════════════════════════════════════════════════════════════════
    def renderizar_tabla(self):
        self.tabla_productos.setRowCount(0)
        self.total_actual = 0

        def _item_font(w=QFont.Weight.Bold):
            f = QFont("Montserrat", 11, w)
            f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            return f

        for p in self.productos_venta:
            self.total_actual += p["precio"] * p["cantidad"]
            row = self.tabla_productos.rowCount()
            self.tabla_productos.insertRow(row)

            it_id = QTableWidgetItem(str(p["id"]))
            it_id.setFont(_item_font())
            it_id.setForeground(QColor("#9CA3AF"))
            it_id.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            it_nom = QTableWidgetItem(p["nombre"].upper())
            it_nom.setFont(_item_font())
            it_nom.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            it_cant = QTableWidgetItem(str(p["cantidad"]))
            it_cant.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_cant.setFont(_item_font())
            it_cant.setForeground(QColor(self.BRAND))

            it_precio = QTableWidgetItem("${:,}".format(p["precio"]))
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
            texto    = self.txt_efectivo.text().replace(".", "").replace(",", "")
            efectivo = int(texto) if texto else 0
        except ValueError:
            efectivo = 0
        cambio = efectivo - self.total_actual
        self.lbl_display_cambio.setText(
            "${:,}".format(cambio) if cambio > 0 else "$0"
        )

    def ejecutar_cobro(self):
        try:
            texto    = self.txt_efectivo.text().replace(".", "").replace(",", "")
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
            self, "Éxito",
            "COBRO EXITOSO\n\nTotal: ${:,}\nCambio: ${:,}".format(
                self.total_actual, cambio)
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
        painter.setBrush(QBrush(QColor(self.COLOR_FONDO)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())