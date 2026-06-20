import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame,
    QPushButton, QLabel, QDialog, QGraphicsDropShadowEffect,
    QScrollArea, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QColor, QFontDatabase, QPainter


def _mf(size, weight):
    f = QFont("Montserrat", size, weight)
    f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    return f

# ══════════════════════════════════════════════════════════════════════════════
# CLASE PERSONALIZADA PARA FORZAR UN FONDO SÓLIDO Y EVITAR QUE LA SOMBRA SE FILTRE
# ══════════════════════════════════════════════════════════════════════════════
class TarjetaFondo(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        # Esto dibuja un bloque blanco absoluto a nivel de píxel. 
        # La sombra no podrá atravesarlo.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 22, 22)


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO PRINCIPAL — CONFIGURACIÓN DE CUENTA
# ══════════════════════════════════════════════════════════════════════════════
class CuentaDialog(QDialog):
    def __init__(self, conexion=None, datos_usuario=None, parent=None):
        super().__init__(parent,
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.Dialog)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setStyleSheet("QDialog { background: transparent; border: none; }")

        self._conexion       = conexion
        self._datos_usuario  = datos_usuario or {}
        self._usuarios_cache = []
        self._id_seleccionado = None

        ruta_modulo     = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz       = os.path.dirname(ruta_modulo)
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")
        for fn in ("Montserrat-Bold.ttf", "Montserrat-Regular.ttf",
                   "Montserrat-Medium.ttf", "Montserrat-Black.ttf"):
            rp = os.path.join(carpeta_fuentes, fn)
            if os.path.exists(rp):
                QFontDatabase.addApplicationFont(rp)

        self.BRAND       = "#17813D"
        self.BRAND_LIGHT = "#228E49"

        # ── Overlay (Fondo oscuro semitransparente) ──────────────────────
        self._overlay = QFrame(self)
        self._overlay.setObjectName("Overlay")
        self._overlay.setStyleSheet(
            "QFrame#Overlay { background:rgba(0,0,0,0.45); border:none; }"
        )

        # ── Tarjeta grande (USAMOS LA NUEVA CLASE NATIVA) ────────────────
        self.card = TarjetaFondo(self)
        self.card.setObjectName("CuentaCard")
        # Ya no usamos background-color por CSS aquí, la clase se encarga.
        
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(50)
        sombra.setColor(QColor(0, 0, 0, 65))
        sombra.setOffset(0, 14)
        self.card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(0, 0, 0, 0)
        layout_card.setSpacing(0)

        # ── BARRA SUPERIOR ───────────────────────────────────────────────
        top_bar = QFrame()
        top_bar.setFixedHeight(64)
        top_bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        top_bar.setStyleSheet(
            "QFrame { background:#FFFFFF; border:none;"
            " border-bottom:1px solid #EEF0F2; border-top-left-radius:22px;"
            " border-top-right-radius:22px; }"
        )
        lt = QHBoxLayout(top_bar)
        lt.setContentsMargins(30, 0, 24, 0)

        lbl_titulo_top = QLabel("CONFIGURACIÓN DE CUENTA")
        lbl_titulo_top.setFont(_mf(10, QFont.Weight.Black))
        lbl_titulo_top.setStyleSheet(
            "color:#17813D; background:transparent; letter-spacing:1px;"
        )

        btn_x = QPushButton("X")
        btn_x.setFixedSize(36, 36)
        btn_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_x.setFont(_mf(11, QFont.Weight.Black))
        btn_x.setStyleSheet(
            "QPushButton { background:#FFFFFF; color:#17813D;"
            " border:1px solid #E5E7EB; border-radius:10px; }"
            " QPushButton:hover { background:#DC2626; color:#FFFFFF; border-color:#DC2626; }"
        )
        btn_x.clicked.connect(self.reject)

        lt.addWidget(lbl_titulo_top)
        lt.addStretch()
        lt.addWidget(btn_x)
        layout_card.addWidget(top_bar)

        # ── CUERPO ───────────────────────────────────────────────────────
        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.setSpacing(0)

        # ── SIDEBAR ──────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        sidebar.setStyleSheet(
            "QFrame { background:#F8FAF9; border:none;"
            " border-right:1px solid #EEF0F2; }"
        )
        ls = QVBoxLayout(sidebar)
        ls.setContentsMargins(20, 20, 20, 20)
        ls.setSpacing(14)

        # ── Card admin de cuenta ──────────────────────────────────────────
        card_admin = QFrame()
        card_admin.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card_admin.setFixedHeight(74)
        card_admin.setStyleSheet(
            "QFrame { background:#FFFFFF; border:2px solid #E5ECE7;"
            " border-radius:18px; }"
        )
        lca = QHBoxLayout(card_admin)
        lca.setContentsMargins(14, 0, 14, 0)
        lca.setSpacing(12)

        nombre_admin = str(self._datos_usuario.get("nombre", "Nicolás Herrán")).title()
        inicial = nombre_admin[0].upper() if nombre_admin else "A"

        avatar_admin = QLabel(inicial)
        avatar_admin.setFixedSize(40, 40)
        avatar_admin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_admin.setFont(_mf(13, QFont.Weight.Black))
        avatar_admin.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        avatar_admin.setStyleSheet(
            "QLabel { background:#17813D; border-radius:20px; color:#FFFFFF; }"
        )

        col_admin = QVBoxLayout()
        col_admin.setSpacing(2)
        col_admin.setContentsMargins(0, 0, 0, 0)
        col_admin.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        lbl_rol_admin = QLabel("ADMINISTRADOR DE CUENTA")
        lbl_rol_admin.setFont(_mf(7, QFont.Weight.Black))
        lbl_rol_admin.setStyleSheet(
            "color:#9CA3AF; background:transparent; letter-spacing:0.3px;"
        )
        lbl_rol_admin.setWordWrap(True)
        lbl_rol_admin.setFixedWidth(195)

        lbl_nombre_admin = QLabel(nombre_admin)
        lbl_nombre_admin.setFont(_mf(12, QFont.Weight.Black))
        lbl_nombre_admin.setStyleSheet("color:#1F2937; background:transparent;")

        col_admin.addWidget(lbl_rol_admin)
        col_admin.addWidget(lbl_nombre_admin)

        lca.addWidget(avatar_admin)
        lca.addLayout(col_admin, 1)
        ls.addWidget(card_admin)

        # ── Card estado del software ──────────────────────────────────────
        card_estado = QFrame()
        card_estado.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card_estado.setFixedHeight(190)
        card_estado.setStyleSheet(
            "QFrame { background:#17813D; border-radius:20px; border:none; }"
        )
        lce = QVBoxLayout(card_estado)
        lce.setContentsMargins(22, 20, 22, 20)
        lce.setSpacing(6)

        lbl_estado_tag = QLabel("ESTADO DEL SOFTWARE:")
        lbl_estado_tag.setFont(_mf(8, QFont.Weight.Black))
        lbl_estado_tag.setStyleSheet(
            "color:#A9DDBC; background:transparent; letter-spacing:0.5px;"
        )

        lbl_version = QLabel("VERSIÓN\nGRATUITA")
        f_version = _mf(19, QFont.Weight.Black)
        f_version.setItalic(True)
        lbl_version.setFont(f_version)
        lbl_version.setStyleSheet("color:#FFFFFF; background:transparent;")
        lbl_version.setWordWrap(True)

        btn_full = QPushButton("ADQUIRIR VERSIÓN FULL")
        btn_full.setFixedHeight(38)
        btn_full.setFont(_mf(9, QFont.Weight.Black))
        btn_full.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_full.setStyleSheet(
            "QPushButton { background:#FFFFFF; color:#17813D;"
            " border:none; border-radius:11px; }"
            " QPushButton:hover { background:#E9F7EF; }"
        )

        lce.addWidget(lbl_estado_tag)
        lce.addWidget(lbl_version)
        lce.addStretch()
        lce.addWidget(btn_full)
        ls.addWidget(card_estado)

        ls.addStretch()

        # ── Card asistencia ──────────────────────────────────────────────
        card_soporte = QFrame()
        card_soporte.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card_soporte.setFixedHeight(108)
        card_soporte.setCursor(Qt.CursorShape.PointingHandCursor)
        card_soporte.setStyleSheet(
            "QFrame { background:#E9F7EF; border-radius:18px; border:none; }"
        )
        lcs = QVBoxLayout(card_soporte)
        lcs.setContentsMargins(20, 16, 20, 16)
        lcs.setSpacing(3)

        lbl_asis_tag = QLabel("ASISTENCIA:")
        lbl_asis_tag.setFont(_mf(8, QFont.Weight.Black))
        lbl_asis_tag.setStyleSheet("color:#5C9C75; background:transparent;")

        lbl_servicio = QLabel("SERVICIO TÉCNICO")
        lbl_servicio.setFont(_mf(14, QFont.Weight.Black))
        lbl_servicio.setStyleSheet("color:#17813D; background:transparent;")

        lbl_click = QLabel("CLICK PARA CONTACTAR")
        f_click = _mf(8, QFont.Weight.Bold)
        f_click.setItalic(True)
        lbl_click.setFont(f_click)
        lbl_click.setStyleSheet("color:#5C9C75; background:transparent;")

        lcs.addWidget(lbl_asis_tag)
        lcs.addWidget(lbl_servicio)
        lcs.addWidget(lbl_click)
        ls.addWidget(card_soporte)

        cuerpo.addWidget(sidebar)

        # ── CONTENIDO PRINCIPAL ──────────────────────────────────────────
        contenido = QWidget()
        # Se establece totalmente transparente para que deje ver el fondo blanco nativo
        contenido.setStyleSheet("background: transparent;")
        lcont = QVBoxLayout(contenido)
        lcont.setContentsMargins(32, 24, 32, 20)
        lcont.setSpacing(10)

        fila_header = QHBoxLayout()
        lbl_gestion = QLabel("GESTIÓN DE USUARIOS")
        lbl_gestion.setFont(_mf(24, QFont.Weight.Black))
        lbl_gestion.setStyleSheet("color:#17813D; background:transparent;")

        def _filtro_btn(texto, activo=False):
            b = QPushButton(texto)
            b.setFixedHeight(34)
            b.setFont(_mf(9, QFont.Weight.Black))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if activo:
                b.setStyleSheet(
                    "QPushButton { background:#FFFFFF; color:#17813D;"
                    " border:2px solid #17813D; border-radius:9px; padding:0 16px; }"
                )
            else:
                b.setStyleSheet(
                    "QPushButton { background:#F3F5F4; color:#9CA3AF;"
                    " border:none; border-radius:9px; padding:0 16px; }"
                    " QPushButton:hover { color:#17813D; }"
                )
            return b

        btn_todos   = _filtro_btn("TODOS", activo=True)
        btn_ultimos = _filtro_btn("ÚLTIMOS ACCESOS")
        btn_por_rol = _filtro_btn("POR ROL  ▾")

        fila_filtros = QHBoxLayout()
        fila_filtros.setSpacing(6)
        fila_filtros.addWidget(btn_todos)
        fila_filtros.addWidget(btn_ultimos)
        fila_filtros.addWidget(btn_por_rol)

        fila_header.addWidget(lbl_gestion)
        fila_header.addStretch()
        fila_header.addLayout(fila_filtros)
        lcont.addLayout(fila_header)
        lcont.addSpacing(6)

        # Encabezados de columna
        fila_cols = QHBoxLayout()
        fila_cols.setContentsMargins(4, 0, 4, 0)
        lbl_c1 = QLabel("NOMBRE COMPLETO")
        lbl_c2 = QLabel("ROL DE USUARIO")
        lbl_c3 = QLabel("ÚLTIMO ACCESO")
        for lbl in (lbl_c1, lbl_c2, lbl_c3):
            lbl.setFont(_mf(9, QFont.Weight.Black))
            lbl.setStyleSheet("color:#9CA3AF; background:transparent; letter-spacing:0.5px;")
        lbl_c3.setAlignment(Qt.AlignmentFlag.AlignRight)

        fila_cols.addWidget(lbl_c1, 3)
        fila_cols.addWidget(lbl_c2, 2)
        fila_cols.addWidget(lbl_c3, 1)
        lcont.addLayout(fila_cols)

        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet("background:#EEF0F2; border:none;")
        lcont.addWidget(sep)

        # ── Lista de usuarios ────────────────────────────────────────────
        self.contenedor_filas = QWidget()
        # Mantenemos transparente para aprovechar el fondo inquebrantable de la TarjetaFondo
        self.contenedor_filas.setStyleSheet("background: transparent;")
        
        self.layout_filas = QVBoxLayout(self.contenedor_filas)
        self.layout_filas.setContentsMargins(0, 0, 0, 0)
        self.layout_filas.setSpacing(0)

        lcont.addWidget(self.contenedor_filas)
        lcont.addStretch(1)

        cuerpo.addWidget(contenido, 1)
        layout_card.addLayout(cuerpo, 1)

        # ── BARRA INFERIOR ───────────────────────────────────────────────
        barra_inf = QFrame()
        barra_inf.setFixedHeight(90)
        barra_inf.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        barra_inf.setStyleSheet(
            "QFrame { background:#FFFFFF; border:none;"
            " border-top:1px solid #EEF0F2; border-bottom-left-radius:22px;"
            " border-bottom-right-radius:22px; }"
        )
        li = QHBoxLayout(barra_inf)
        li.setContentsMargins(30, 0, 28, 0)

        self.btn_nuevo = QPushButton("NUEVO USUARIO")
        self.btn_nuevo.setFixedSize(195, 54)
        self.btn_nuevo.setFont(_mf(12, QFont.Weight.Black))
        self.btn_nuevo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nuevo.setStyleSheet(
            "QPushButton { background:#17813D; color:#FFFFFF; border:none;"
            " border-radius:16px; letter-spacing:0.5px; }"
            " QPushButton:hover { background:#228E49; }"
        )
        sc = QGraphicsDropShadowEffect(self)
        sc.setBlurRadius(14); sc.setColor(QColor(23, 129, 61, 55)); sc.setOffset(0, 5)
        self.btn_nuevo.setGraphicsEffect(sc)
        self.btn_nuevo.clicked.connect(self.abrir_nuevo_usuario)

        def _bsec(txt, ancho, verde=False):
            b = QPushButton(txt)
            b.setFixedSize(ancho, 50)
            b.setFont(_mf(10, QFont.Weight.Black))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if verde:
                b.setStyleSheet(
                    "QPushButton { background:#FFFFFF; color:#17813D;"
                    " border:2px solid #A9DDBC; border-radius:16px; }"
                    " QPushButton:hover { background:#E9F7EF; }"
                )
            else:
                b.setStyleSheet(
                    "QPushButton { background:#FFFFFF; color:#9CA3AF;"
                    " border:2px solid #EEEFF2; border-radius:16px; }"
                    " QPushButton:hover { color:#17813D; border-color:#A9DDBC; }"
                )
            return b

        self.btn_password    = _bsec("CAMBIAR CONTRASEÑA", 188, verde=True)
        self.btn_eliminar_u  = _bsec("ELIMINAR USUARIO",   158)
        self.btn_modificar_u = _bsec("MODIFICAR USUARIO",  165)
        self.btn_buscar_u    = _bsec("BUSCAR",             110)

        self.btn_password.clicked.connect(self.abrir_cambiar_password)
        self.btn_eliminar_u.clicked.connect(self.abrir_eliminar_usuario)
        self.btn_modificar_u.clicked.connect(self.abrir_modificar_usuario)
        self.btn_buscar_u.clicked.connect(self.abrir_buscar_usuario)

        lbs = QHBoxLayout(); lbs.setSpacing(10)
        for b in [self.btn_password, self.btn_eliminar_u,
                  self.btn_modificar_u, self.btn_buscar_u]:
            lbs.addWidget(b)

        li.addWidget(self.btn_nuevo)
        li.addStretch()
        li.addLayout(lbs)
        layout_card.addWidget(barra_inf)

        self._cargar_usuarios()

    # ══════════════════════════════════════════════════════════════════════
    # CARGA DE USUARIOS DESDE BD
    # ══════════════════════════════════════════════════════════════════════
    def _cargar_usuarios(self):
        self._usuarios_cache = []
        if self._conexion:
            try:
                with self._conexion.cursor() as cur:
                    cur.execute("""
                        SELECT u.id_usuario, u.username_log, u.id_rol,
                               e.nombre_empleado
                        FROM usuarios u
                        LEFT JOIN empleados e ON e.id_empleado = u.id_empleado
                        ORDER BY u.id_usuario ASC
                    """)
                    filas = cur.fetchall()
                    for f in filas:
                        if isinstance(f, dict):
                            uid    = f["id_usuario"]
                            uname  = f["username_log"]
                            idrol  = f["id_rol"]
                            nombre = f.get("nombre_empleado") or uname
                        else:
                            uid, uname, idrol, nombre = f[0], f[1], f[2], f[3] or f[1]
                        self._usuarios_cache.append({
                            "id"     : uid,
                            "nombre" : str(nombre).strip().title(),
                            "rol"    : "ADMINISTRADOR" if str(idrol) == "1" else "CAJERO",
                            "acceso" : "—",
                        })
            except Exception:
                self._usuarios_cache = []

        self._renderizar_usuarios()

    def _renderizar_usuarios(self):
        while self.layout_filas.count():
            item = self.layout_filas.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for u in self._usuarios_cache:
            fila = self._crear_fila_usuario(u)
            self.layout_filas.addWidget(fila)

    def _crear_fila_usuario(self, u):
        fila = QFrame()
        fila.setObjectName("FilaUsuario")
        fila.setFixedHeight(64)
        fila.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        fila.setStyleSheet(
            "QFrame#FilaUsuario { background:#FFFFFF;"
            " border:none; border-bottom:1px solid #F0F2F0; }"
        )
        lf = QHBoxLayout(fila)
        lf.setContentsMargins(4, 0, 4, 0)
        lf.setSpacing(0)

        # Columna nombre
        col_nombre = QHBoxLayout()
        col_nombre.setSpacing(12)
        col_nombre.setContentsMargins(0, 0, 0, 0)

        inicial = "".join([n[0] for n in u["nombre"].split()[:2]]).upper()
        avatar = QLabel(inicial)
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(_mf(10, QFont.Weight.Black))
        avatar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        avatar.setStyleSheet(
            "QLabel { background:#E9F7EF; border:1px solid #A9DDBC;"
            " border-radius:18px; color:#17813D; }"
        )

        lbl_nombre = QLabel(u["nombre"])
        lbl_nombre.setFont(_mf(12, QFont.Weight.Black))
        lbl_nombre.setStyleSheet(
            "QLabel { color:#1F2937; background:transparent; border:none; }"
        )

        col_nombre.addWidget(avatar)
        col_nombre.addWidget(lbl_nombre)
        col_nombre.addStretch()

        contenedor_nombre = QWidget()
        contenedor_nombre.setStyleSheet("background:transparent;")
        contenedor_nombre.setLayout(col_nombre)

        # Columna rol
        badge = QLabel(u["rol"])
        badge.setFont(_mf(8, QFont.Weight.Black))
        badge.setFixedHeight(26)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        if u["rol"] == "ADMINISTRADOR":
            badge.setStyleSheet(
                "QLabel { background:#E9F7EF; color:#17813D;"
                " border-radius:13px; border:none; }"
            )
        else:
            badge.setStyleSheet(
                "QLabel { background:#F3F5F4; color:#9CA3AF;"
                " border-radius:13px; border:none; }"
            )
        badge.setMinimumWidth(120)
        badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        contenedor_badge = QWidget()
        contenedor_badge.setStyleSheet("background:transparent;")
        lb = QHBoxLayout(contenedor_badge)
        lb.setContentsMargins(0, 0, 0, 0)
        lb.addWidget(badge)
        lb.addStretch()

        # Columna último acceso
        lbl_acceso = QLabel(u["acceso"])
        f_acceso = _mf(10, QFont.Weight.Bold)
        f_acceso.setItalic(True)
        lbl_acceso.setFont(f_acceso)
        lbl_acceso.setStyleSheet(
            "QLabel { color:#9CA3AF; background:transparent; border:none; }"
        )
        lbl_acceso.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        lf.addWidget(contenedor_nombre, 3)
        lf.addWidget(contenedor_badge, 2)
        lf.addWidget(lbl_acceso, 1)

        fila.setProperty("id_usuario", u["id"])
        fila.mousePressEvent = lambda e, uid=u["id"]: self._seleccionar_fila(uid)
        return fila

    def _seleccionar_fila(self, id_usuario):
        self._id_seleccionado = id_usuario

    # ══════════════════════════════════════════════════════════════════════
    # ACCIONES
    # ══════════════════════════════════════════════════════════════════════
    def abrir_nuevo_usuario(self):
        QMessageBox.information(self, "Nuevo usuario",
            "Aquí se abrirá el formulario para crear un nuevo usuario.")

    def abrir_cambiar_password(self):
        QMessageBox.information(self, "Cambiar contraseña",
            "Selecciona un usuario y aquí podrás cambiar su contraseña.")

    def abrir_eliminar_usuario(self):
        QMessageBox.information(self, "Eliminar usuario",
            "Selecciona un usuario de la lista para eliminarlo.")

    def abrir_modificar_usuario(self):
        QMessageBox.information(self, "Modificar usuario",
            "Selecciona un usuario de la lista para modificar sus datos.")

    def abrir_buscar_usuario(self):
        QMessageBox.information(self, "Buscar usuario",
            "Aquí se abrirá el buscador de usuarios.")

    # ══════════════════════════════════════════════════════════════════════
    # POSICIONAMIENTO
    # ══════════════════════════════════════════════════════════════════════
    def _reposicionar(self):
        margen = 16
        self.card.setGeometry(
            margen, margen,
            self.width() - margen * 2,
            self.height() - margen * 2
        )
        self.card.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._overlay.setGeometry(0, 0, self.width(), self.height())
        self._reposicionar()

    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            p = self.parent()
            pos = p.mapToGlobal(QPoint(0, 0))
            self.setGeometry(pos.x(), pos.y(), p.width(), p.height())
        self._overlay.setGeometry(0, 0, self.width(), self.height())
        self._reposicionar()