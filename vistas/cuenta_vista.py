import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame,
    QPushButton, QLabel, QDialog, QGraphicsDropShadowEffect,
    QScrollArea, QMessageBox, QSizePolicy, QComboBox, QDoubleSpinBox,
    QApplication
)
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QFont, QColor, QFontDatabase


def _mf(size, weight):
    f = QFont("Montserrat", size, weight)
    f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    return f


def _geometria_ventana_real(widget):
    """
    Devuelve (x, y, ancho, alto) en coordenadas GLOBALES de la ventana
    de la aplicación que realmente está visible en pantalla.

    BUG QUE CORRIGE: widget.window() a veces devuelve geometrías
    incorrectas o diminutas (p.ej. 400x300) cuando se llama desde
    showEvent() de un QDialog FramelessWindowHint recién creado, porque
    en ese instante exacto Qt aún no resolvió por completo la cadena de
    ventanas top-level. En vez de confiar en window(), subimos
    manualmente por widget.parentWidget() hasta encontrar el widget
    de mayor nivel disponible, y si ninguno tiene un tamaño razonable
    (> 200x200), usamos la geometría física de la pantalla principal
    como última garantía — nunca un número pequeño inventado.
    """
    candidato = widget
    mejor = None
    while candidato is not None:
        w, h = candidato.width(), candidato.height()
        if w > 200 and h > 200:
            mejor = candidato
        candidato = candidato.parentWidget()

    if mejor is not None:
        pos = mejor.mapToGlobal(QPoint(0, 0))
        return pos.x(), pos.y(), mejor.width(), mejor.height()

    # Último recurso: geometría completa de la pantalla física
    screen = QApplication.primaryScreen()
    if screen:
        geo = screen.availableGeometry()
        return geo.x(), geo.y(), geo.width(), geo.height()

    return 0, 0, 1280, 800


SS_INPUT = (
    "QLineEdit { background:#EDF7F1; color:#1F2937; border:2px solid transparent;"
    " border-radius:14px; padding:0 16px; }"
    " QLineEdit:focus { border:2px solid #17813D; }"
)
SS_COMBO = (
    "QComboBox { background:#EDF7F1; color:#1F2937; border:2px solid transparent;"
    " border-radius:14px; padding:0 16px; }"
    " QComboBox:focus { border:2px solid #17813D; }"
    " QComboBox::drop-down { border:none; width:30px; }"
    " QComboBox QAbstractItemView { background:#FFFFFF; color:#1F2937;"
    " border:1px solid #A9DDBC; border-radius:10px; selection-background-color:#17813D;"
    " selection-color:#FFFFFF; padding:4px; }"
)
SS_DSPIN = (
    "QDoubleSpinBox { background:#EDF7F1; color:#1F2937; border:2px solid transparent;"
    " border-radius:14px; padding:0 12px; }"
    " QDoubleSpinBox:focus { border:2px solid #17813D; }"
    " QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width:22px; }"
)


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO BASE — mismo patrón estético usado en caja_vista.py
# ══════════════════════════════════════════════════════════════════════════════
class DialogoBase(QDialog):
    def __init__(self, titulo, ancho=480, parent=None):
        super().__init__(parent,
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        self._overlay = QFrame(self)
        self._overlay.setObjectName("Overlay")
        self._overlay.setStyleSheet(
            "QFrame#Overlay { background:rgba(0,0,0,0.45); border:none; }"
        )

        self.card = QFrame(self)
        self.card.setObjectName("DialogCard")
        self.card.setFixedWidth(ancho)
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.card.setStyleSheet(
            "QFrame#DialogCard { background-color:#FFFFFF;"
            " border-radius:26px; border:none; }"
        )
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(50)
        sombra.setColor(QColor(0, 0, 0, 65))
        sombra.setOffset(0, 14)
        self.card.setGraphicsEffect(sombra)

        self.layout_card = QVBoxLayout(self.card)
        self.layout_card.setContentsMargins(32, 26, 32, 30)
        self.layout_card.setSpacing(14)

        fila = QHBoxLayout()
        fila.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(titulo)
        lbl.setFont(_mf(16, QFont.Weight.Black))
        lbl.setStyleSheet("color:#17813D; background:transparent;")
        btn_x = QPushButton("✕")
        btn_x.setFixedSize(30, 30)
        btn_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_x.setFont(_mf(10, QFont.Weight.Bold))
        btn_x.setStyleSheet(
            "QPushButton { background:transparent; color:#9CA3AF; border:none; }"
            "QPushButton:hover { color:#DC2626; }"
        )
        btn_x.clicked.connect(self.reject)
        fila.addWidget(lbl); fila.addStretch(); fila.addWidget(btn_x)
        self.layout_card.addLayout(fila)

    def _lbl(self, texto):
        l = QLabel(texto)
        l.setFont(_mf(8, QFont.Weight.Black))
        l.setStyleSheet("color:#17813D; background:transparent; letter-spacing:0.5px;")
        return l

    def _input(self, placeholder="", password=False):
        t = QLineEdit()
        t.setPlaceholderText(placeholder)
        t.setFont(_mf(13, QFont.Weight.Medium))
        t.setFixedHeight(50)
        t.setStyleSheet(SS_INPUT)
        if password:
            t.setEchoMode(QLineEdit.EchoMode.Password)
        return t

    def _combo(self, items):
        c = QComboBox()
        c.addItems(items)
        c.setFont(_mf(13, QFont.Weight.Medium))
        c.setFixedHeight(50)
        c.setStyleSheet(SS_COMBO)
        c.setCursor(Qt.CursorShape.PointingHandCursor)
        return c

    def _dspin(self, mn=0.0, mx=99999999.0, dec=0, prefix="$ "):
        s = QDoubleSpinBox()
        s.setRange(mn, mx)
        s.setDecimals(dec)
        s.setPrefix(prefix)
        s.setSingleStep(50000)
        s.setFont(_mf(13, QFont.Weight.Medium))
        s.setFixedHeight(50)
        s.setStyleSheet(SS_DSPIN)
        return s

    def _btn_ok(self, texto, bg="#17813D", hv="#228E49"):
        b = QPushButton(texto)
        b.setFixedHeight(50)
        b.setFont(_mf(12, QFont.Weight.Black))
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setStyleSheet(
            "QPushButton {{ background:{b}; color:#FFFFFF; border:none;"
            " border-radius:16px; letter-spacing:0.5px; }}"
            "QPushButton:hover {{ background:{h}; }}".format(b=bg, h=hv)
        )
        return b

    def _btn_cancel(self, texto="CANCELAR"):
        b = QPushButton(texto)
        b.setFixedHeight(46)
        b.setFont(_mf(11, QFont.Weight.Bold))
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setStyleSheet(
            "QPushButton { background:transparent; color:#9CA3AF; border:none; }"
            "QPushButton:hover { color:#17813D; }"
        )
        b.clicked.connect(self.reject)
        return b

    def _reposicionar(self):
        self.card.adjustSize()
        cw, ch = self.card.width(), self.card.height()
        self.card.move((self.width() - cw)//2, max(16, (self.height() - ch)//2))
        # Asegura que ambos queden visibles y por encima de cualquier
        # widget previo; sin esto a veces el card queda invisible aunque
        # tenga geometria correcta (bug de stacking order en Windows).
        self._overlay.show()
        self._overlay.raise_()
        self.card.show()
        self.card.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._overlay.setGeometry(0, 0, self.width(), self.height())
        self._reposicionar()

    def _ajustar_geometria_completa(self):
        """
        Usa _geometria_ventana_real() en vez de self.window(), que es
        poco confiable en el primer frame de un FramelessWindowHint
        creado dinámicamente — evita el bug de quedar atascado en un
        tamaño pequeño (400x300) que parecía una 'ventana fantasma'.
        """
        x, y, ancho, alto = _geometria_ventana_real(self.parent() or self)
        self.setGeometry(x, y, ancho, alto)
        self._overlay.setGeometry(0, 0, self.width(), self.height())
        self._reposicionar()

    def showEvent(self, event):
        super().showEvent(event)
        self._ajustar_geometria_completa()
        QTimer.singleShot(0, self._ajustar_geometria_completa)


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO — NUEVO USUARIO
# ══════════════════════════════════════════════════════════════════════════════
class DialogoNuevoUsuario(DialogoBase):
    """
    Crea un registro en `empleados` y otro vinculado en `usuarios`.
    Campos según tu BD:
      empleados: nombre_empleado, id_rol, monto_pago  (fecha_ingreso = ahora, automática)
      usuarios : username_log, contrasena_log, id_rol, id_empleado
    """
    def __init__(self, conexion=None, parent=None):
        super().__init__("NUEVO USUARIO", ancho=480, parent=parent)
        self.resultado  = None
        self._conexion  = conexion

        # Nombre completo del empleado
        self.layout_card.addWidget(self._lbl("NOMBRE COMPLETO"))
        self.txt_nombre = self._input("Ej: Carlos Andrés Gómez")
        self.layout_card.addWidget(self.txt_nombre)

        # Usuario / contraseña
        fila1 = QHBoxLayout(); fila1.setSpacing(14)
        col_u = QVBoxLayout(); col_u.setSpacing(6)
        col_u.addWidget(self._lbl("NOMBRE DE USUARIO"))
        self.txt_usuario = self._input("Ej: carlosgomez")
        col_u.addWidget(self.txt_usuario)

        col_p = QVBoxLayout(); col_p.setSpacing(6)
        col_p.addWidget(self._lbl("CONTRASEÑA"))
        self.txt_password = self._input("••••••", password=True)
        col_p.addWidget(self.txt_password)

        fila1.addLayout(col_u); fila1.addLayout(col_p)
        self.layout_card.addLayout(fila1)

        # Rol / salario
        fila2 = QHBoxLayout(); fila2.setSpacing(14)
        col_r = QVBoxLayout(); col_r.setSpacing(6)
        col_r.addWidget(self._lbl("ROL DE USUARIO"))
        self.combo_rol = self._combo(["ADMINISTRADOR", "CAJERO"])
        col_r.addWidget(self.combo_rol)

        col_s = QVBoxLayout(); col_s.setSpacing(6)
        col_s.addWidget(self._lbl("SALARIO (MONTO DE PAGO)"))
        self.spin_salario = self._dspin(0, 99999999, 0, "$ ")
        self.spin_salario.setValue(1300000)
        col_s.addWidget(self.spin_salario)

        fila2.addLayout(col_r); fila2.addLayout(col_s)
        self.layout_card.addLayout(fila2)

        self.layout_card.addSpacing(4)
        fila_b = QHBoxLayout()
        fila_b.addStretch()
        fila_b.addWidget(self._btn_cancel())
        btn_crear = self._btn_ok("CREAR USUARIO")
        btn_crear.setFixedWidth(170)
        btn_crear.clicked.connect(self._confirmar)
        fila_b.addWidget(btn_crear)
        self.layout_card.addLayout(fila_b)

    def _confirmar(self):
        nombre   = self.txt_nombre.text().strip()
        usuario  = self.txt_usuario.text().strip()
        password = self.txt_password.text().strip()
        rol_txt  = self.combo_rol.currentText()
        salario  = self.spin_salario.value()

        if not nombre:
            QMessageBox.warning(self, "Falta información", "Ingresa el nombre completo.")
            self.txt_nombre.setFocus(); return
        if not usuario:
            QMessageBox.warning(self, "Falta información", "Ingresa el nombre de usuario.")
            self.txt_usuario.setFocus(); return
        if not password:
            QMessageBox.warning(self, "Falta información", "Ingresa una contraseña.")
            self.txt_password.setFocus(); return

        id_rol = 1 if rol_txt == "ADMINISTRADOR" else 2

        if not self._conexion:
            QMessageBox.critical(self, "Sin conexión",
                "No hay conexión activa a la base de datos.")
            return

        try:
            with self._conexion.cursor() as cur:
                # Verificar que el username no exista ya
                cur.execute(
                    "SELECT id_usuario FROM usuarios WHERE username_log = %s",
                    (usuario,)
                )
                if cur.fetchone():
                    QMessageBox.warning(self, "Usuario duplicado",
                        "Ya existe un usuario con ese nombre de usuario.")
                    return

                # 1. Crear el empleado
                cur.execute(
                    "INSERT INTO empleados (nombre_empleado, id_rol, monto_pago)"
                    " VALUES (%s, %s, %s)",
                    (nombre, id_rol, salario)
                )
                id_empleado = cur.lastrowid

                # 2. Crear el usuario vinculado a ese empleado
                cur.execute(
                    "INSERT INTO usuarios"
                    " (id_rol, id_empleado, username_log, contrasena_log)"
                    " VALUES (%s, %s, %s, %s)",
                    (id_rol, id_empleado, usuario, password)
                )
                self._conexion.commit()

            self.resultado = {
                "nombre"     : nombre,
                "usuario"    : usuario,
                "rol"        : rol_txt,
                "id_empleado": id_empleado,
            }
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error al guardar",
                "No se pudo crear el usuario:\n{}".format(e))


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO — CAMBIAR CONTRASEÑA
# ══════════════════════════════════════════════════════════════════════════════
class DialogoCambiarPassword(DialogoBase):
    """
    Busca un usuario por nombre o username y permite asignarle una
    nueva contraseña, escrita dos veces para confirmar.
    """
    def __init__(self, usuarios, conexion=None, parent=None):
        super().__init__("CAMBIAR CONTRASEÑA", ancho=460, parent=parent)
        self.resultado   = None
        self._conexion   = conexion
        self._usuarios   = usuarios
        self._seleccionado = None

        self.layout_card.addWidget(self._lbl("SELECCIONA EL USUARIO"))
        self.combo_usuario = self._combo(
            ["{}  ·  {}".format(u["nombre"], u["rol"]) for u in usuarios]
        )
        self.layout_card.addWidget(self.combo_usuario)

        self.layout_card.addSpacing(4)

        self.layout_card.addWidget(self._lbl("NUEVA CONTRASEÑA"))
        self.txt_pass1 = self._input("Escribe la nueva contraseña...", password=True)
        self.layout_card.addWidget(self.txt_pass1)

        self.layout_card.addWidget(self._lbl("CONFIRMAR CONTRASEÑA"))
        self.txt_pass2 = self._input("Repite la contraseña...", password=True)
        self.layout_card.addWidget(self.txt_pass2)

        self.layout_card.addSpacing(4)
        fila_b = QHBoxLayout()
        fila_b.addStretch()
        fila_b.addWidget(self._btn_cancel())
        btn_ok = self._btn_ok("ACTUALIZAR")
        btn_ok.setFixedWidth(150)
        btn_ok.clicked.connect(self._confirmar)
        fila_b.addWidget(btn_ok)
        self.layout_card.addLayout(fila_b)

    def _confirmar(self):
        if not self._usuarios:
            self.reject(); return

        idx = self.combo_usuario.currentIndex()
        usuario = self._usuarios[idx]

        p1 = self.txt_pass1.text().strip()
        p2 = self.txt_pass2.text().strip()

        if not p1:
            QMessageBox.warning(self, "Falta información", "Ingresa la nueva contraseña.")
            self.txt_pass1.setFocus(); return
        if p1 != p2:
            QMessageBox.warning(self, "No coinciden",
                "Las contraseñas escritas no son iguales.")
            self.txt_pass2.setFocus(); return

        if not self._conexion:
            QMessageBox.critical(self, "Sin conexión",
                "No hay conexión activa a la base de datos.")
            return

        try:
            with self._conexion.cursor() as cur:
                cur.execute(
                    "UPDATE usuarios SET contrasena_log = %s WHERE id_usuario = %s",
                    (p1, usuario["id"])
                )
                self._conexion.commit()
            self.resultado = usuario
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar",
                "No se pudo actualizar la contraseña:\n{}".format(e))


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO — ELIMINAR USUARIO  (checkboxes, mismo patrón que caja_vista.py)
# ══════════════════════════════════════════════════════════════════════════════
class DialogoEliminarUsuario(DialogoBase):
    def __init__(self, usuarios, conexion=None, parent=None):
        super().__init__("ELIMINAR USUARIO", ancho=480, parent=parent)
        self._conexion = conexion
        self._usuarios = usuarios
        self.eliminados = []

        self.layout_card.addWidget(self._lbl("SELECCIONA LOS USUARIOS A ELIMINAR"))
        self.layout_card.addSpacing(4)

        scroll_frame = QFrame()
        scroll_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        scroll_frame.setStyleSheet(
            "QFrame { background:#F8FAF9; border:2px dashed #C8E6D4;"
            " border-radius:16px; }"
        )
        scroll_layout = QVBoxLayout(scroll_frame)
        scroll_layout.setContentsMargins(16, 14, 16, 14)
        scroll_layout.setSpacing(8)

        self._checks = []

        if not usuarios:
            lbl_v = QLabel("NO HAY USUARIOS PARA ELIMINAR")
            lbl_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_v.setFont(_mf(10, QFont.Weight.Bold))
            lbl_v.setStyleSheet("color:#C5D4CC; background:transparent;")
            lbl_v.setFixedHeight(100)
            scroll_layout.addWidget(lbl_v)
        else:
            from PySide6.QtWidgets import QCheckBox
            for u in usuarios:
                fila = QHBoxLayout()
                fila.setContentsMargins(0, 0, 0, 0)
                fila.setSpacing(12)

                chk = QCheckBox()
                chk.setFixedSize(22, 22)
                chk.setStyleSheet(
                    "QCheckBox::indicator { width:20px; height:20px;"
                    " border-radius:6px; border:2px solid #A9DDBC; background:#FFFFFF; }"
                    "QCheckBox::indicator:checked { background:#DC2626; border:2px solid #DC2626; }"
                )
                self._checks.append((u, chk))

                lbl_nom = QLabel(u["nombre"])
                lbl_nom.setFont(_mf(12, QFont.Weight.Bold))
                lbl_nom.setStyleSheet("color:#1F2937; background:transparent;")

                lbl_rol = QLabel(u["rol"])
                lbl_rol.setFont(_mf(9, QFont.Weight.Black))
                lbl_rol.setStyleSheet("color:#9CA3AF; background:transparent;")
                lbl_rol.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                fila.addWidget(chk)
                fila.addWidget(lbl_nom, 1)
                fila.addWidget(lbl_rol)

                contenedor = QFrame()
                contenedor.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
                contenedor.setStyleSheet(
                    "QFrame { background:#FFFFFF; border-radius:12px; border:none; }"
                )
                contenedor.setFixedHeight(52)
                QHBoxLayout(contenedor).addLayout(fila)
                contenedor.layout().setContentsMargins(12, 0, 12, 0)
                scroll_layout.addWidget(contenedor)

        scroll_frame.setMinimumHeight(
            min(len(usuarios) * 60 + 28, 280) if usuarios else 130
        )
        self.layout_card.addWidget(scroll_frame)

        self.layout_card.addSpacing(8)
        btn_elim = self._btn_ok("ELIMINAR USUARIO(S)", "#DC6468", "#C0484B")
        btn_elim.clicked.connect(self._confirmar)
        self.layout_card.addWidget(btn_elim)

    def _confirmar(self):
        seleccionados = [u for u, chk in self._checks if chk.isChecked()]
        if not seleccionados:
            self.reject(); return

        if not self._conexion:
            QMessageBox.critical(self, "Sin conexión",
                "No hay conexión activa a la base de datos.")
            return

        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            "¿Eliminar {} usuario(s) seleccionado(s)? Esta acción no se puede deshacer.".format(
                len(seleccionados)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        try:
            with self._conexion.cursor() as cur:
                for u in seleccionados:
                    cur.execute(
                        "DELETE FROM usuarios WHERE id_usuario = %s", (u["id"],)
                    )
                self._conexion.commit()
            self.eliminados = seleccionados
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al eliminar",
                "No se pudieron eliminar los usuarios:\n{}".format(e))


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO — MODIFICAR USUARIO
# ══════════════════════════════════════════════════════════════════════════════
class DialogoModificarUsuario(DialogoBase):
    """
    Busca un usuario por nombre o username y permite editar:
    nombre completo, rol, salario y nombre de usuario.
    La contraseña se cambia desde el diálogo de Cambiar Contraseña.
    """
    def __init__(self, usuarios, conexion=None, parent=None):
        super().__init__("MODIFICAR USUARIO", ancho=480, parent=parent)
        self.resultado  = None
        self._conexion  = conexion
        self._usuarios  = usuarios

        self.layout_card.addWidget(self._lbl("SELECCIONA EL USUARIO"))
        self.combo_usuario = self._combo(
            ["{}  ·  {}".format(u["nombre"], u["rol"]) for u in usuarios]
        )
        self.combo_usuario.currentIndexChanged.connect(self._cargar_datos)
        self.layout_card.addWidget(self.combo_usuario)

        self.layout_card.addWidget(self._lbl("NOMBRE COMPLETO"))
        self.txt_nombre = self._input("Nombre completo")
        self.layout_card.addWidget(self.txt_nombre)

        fila1 = QHBoxLayout(); fila1.setSpacing(14)
        col_u = QVBoxLayout(); col_u.setSpacing(6)
        col_u.addWidget(self._lbl("NOMBRE DE USUARIO"))
        self.txt_usuario = self._input("Usuario de acceso")
        col_u.addWidget(self.txt_usuario)

        col_r = QVBoxLayout(); col_r.setSpacing(6)
        col_r.addWidget(self._lbl("ROL"))
        self.combo_rol = self._combo(["ADMINISTRADOR", "CAJERO"])
        col_r.addWidget(self.combo_rol)

        fila1.addLayout(col_u); fila1.addLayout(col_r)
        self.layout_card.addLayout(fila1)

        self.layout_card.addWidget(self._lbl("SALARIO (MONTO DE PAGO)"))
        self.spin_salario = self._dspin(0, 99999999, 0, "$ ")
        self.layout_card.addWidget(self.spin_salario)

        self.layout_card.addSpacing(4)
        fila_b = QHBoxLayout()
        fila_b.addStretch()
        fila_b.addWidget(self._btn_cancel())
        btn_g = self._btn_ok("GUARDAR CAMBIOS")
        btn_g.setFixedWidth(170)
        btn_g.clicked.connect(self._confirmar)
        fila_b.addWidget(btn_g)
        self.layout_card.addLayout(fila_b)

        if usuarios:
            self._cargar_datos(0)

    def _cargar_datos(self, idx):
        if idx < 0 or idx >= len(self._usuarios):
            return
        u = self._usuarios[idx]
        self.txt_nombre.setText(u["nombre"])
        self.txt_usuario.setText(u.get("username", ""))
        self.combo_rol.setCurrentText(u["rol"])
        self.spin_salario.setValue(u.get("salario", 0) or 0)

    def _confirmar(self):
        if not self._usuarios:
            self.reject(); return

        idx = self.combo_usuario.currentIndex()
        u   = self._usuarios[idx]

        nombre   = self.txt_nombre.text().strip()
        usuario  = self.txt_usuario.text().strip()
        rol_txt  = self.combo_rol.currentText()
        salario  = self.spin_salario.value()
        id_rol   = 1 if rol_txt == "ADMINISTRADOR" else 2

        if not nombre:
            QMessageBox.warning(self, "Falta información", "Ingresa el nombre completo.")
            self.txt_nombre.setFocus(); return
        if not usuario:
            QMessageBox.warning(self, "Falta información", "Ingresa el nombre de usuario.")
            self.txt_usuario.setFocus(); return

        if not self._conexion:
            QMessageBox.critical(self, "Sin conexión",
                "No hay conexión activa a la base de datos.")
            return

        try:
            with self._conexion.cursor() as cur:
                # Username único, salvo que sea el mismo usuario
                cur.execute(
                    "SELECT id_usuario FROM usuarios"
                    " WHERE username_log = %s AND id_usuario != %s",
                    (usuario, u["id"])
                )
                if cur.fetchone():
                    QMessageBox.warning(self, "Usuario duplicado",
                        "Ya existe otro usuario con ese nombre de usuario.")
                    return

                cur.execute(
                    "UPDATE empleados SET nombre_empleado=%s, id_rol=%s, monto_pago=%s"
                    " WHERE id_empleado=("
                    "   SELECT id_empleado FROM usuarios WHERE id_usuario=%s"
                    ")",
                    (nombre, id_rol, salario, u["id"])
                )
                cur.execute(
                    "UPDATE usuarios SET username_log=%s, id_rol=%s WHERE id_usuario=%s",
                    (usuario, id_rol, u["id"])
                )
                self._conexion.commit()

            self.resultado = {
                "id"     : u["id"],
                "nombre" : nombre,
                "usuario": usuario,
                "rol"    : rol_txt,
            }
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar",
                "No se pudo modificar el usuario:\n{}".format(e))


# ══════════════════════════════════════════════════════════════════════════════
# DIÁLOGO PRINCIPAL — CONFIGURACIÓN DE CUENTA
# ══════════════════════════════════════════════════════════════════════════════
class CuentaDialog(QDialog):

    def __init__(self, conexion=None, datos_usuario=None, parent=None):
        super().__init__(parent,
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

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

        # ── Overlay ──────────────────────────────────────────────────────
        self._overlay = QFrame(self)
        self._overlay.setObjectName("Overlay")
        self._overlay.setStyleSheet(
            "QFrame#Overlay { background:rgba(0,0,0,0.45); border:none; }"
        )

        # ── Tarjeta grande ───────────────────────────────────────────────
        self.card = QFrame(self)
        self.card.setObjectName("CuentaCard")
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.card.setStyleSheet(
            "QFrame#CuentaCard {"
            " background-color:#FFFFFF;"
            " border-radius:22px;"
            " border:none;"
            "}"
        )
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

        # ── Card admin de cuenta — CORREGIDA: badge ya no flota suelto ─────
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

        # ── Card estado del software — CORREGIDA: tamaño fijo, sin scroll ──
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
        contenido = QFrame()
        contenido.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        contenido.setStyleSheet("QFrame { background:#FFFFFF; border:none; }")
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

        # Barra de búsqueda — filtra en vivo por nombre o rol, a la IZQUIERDA de los filtros
        self.txt_buscar_usuario = QLineEdit()
        self.txt_buscar_usuario.setPlaceholderText("Buscar por nombre o rol...")
        self.txt_buscar_usuario.setFont(_mf(10, QFont.Weight.Medium))
        self.txt_buscar_usuario.setFixedSize(210, 34)
        self.txt_buscar_usuario.setStyleSheet(
            "QLineEdit { background:#F3F5F4; color:#1F2937; border:2px solid transparent;"
            " border-radius:9px; padding:0 14px; }"
            " QLineEdit:focus { border:2px solid #17813D; background:#FFFFFF; }"
        )
        self.txt_buscar_usuario.textChanged.connect(self._filtrar_usuarios)

        btn_todos   = _filtro_btn("TODOS", activo=True)
        btn_ultimos = _filtro_btn("ÚLTIMOS ACCESOS")
        btn_por_rol = _filtro_btn("POR ROL  ▾")

        btn_todos.clicked.connect(self._filtro_todos)
        btn_ultimos.clicked.connect(self._filtro_ultimos_accesos)
        btn_por_rol.clicked.connect(self._filtro_por_rol)

        fila_filtros = QHBoxLayout()
        fila_filtros.setSpacing(8)
        fila_filtros.addWidget(self.txt_buscar_usuario)
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

        # ── Lista de usuarios — SIN scroll si caben, igual que la imagen ───
        self.contenedor_filas = QWidget()
        self.contenedor_filas.setStyleSheet("background:#FFFFFF;")
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

        self.btn_password    = _bsec("CAMBIAR CONTRASEÑA", 195, verde=True)
        self.btn_eliminar_u  = _bsec("ELIMINAR USUARIO",   165)
        self.btn_modificar_u = _bsec("MODIFICAR USUARIO",  172)

        self.btn_password.clicked.connect(self.abrir_cambiar_password)
        self.btn_eliminar_u.clicked.connect(self.abrir_eliminar_usuario)
        self.btn_modificar_u.clicked.connect(self.abrir_modificar_usuario)

        lbs = QHBoxLayout(); lbs.setSpacing(10)
        for b in [self.btn_password, self.btn_eliminar_u, self.btn_modificar_u]:
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
                               e.nombre_empleado, e.monto_pago
                        FROM usuarios u
                        LEFT JOIN empleados e ON e.id_empleado = u.id_empleado
                        ORDER BY u.id_usuario ASC
                    """)
                    filas = cur.fetchall()
                    for f in filas:
                        if isinstance(f, dict):
                            uid     = f["id_usuario"]
                            uname   = f["username_log"]
                            idrol   = f["id_rol"]
                            nombre  = f.get("nombre_empleado") or uname
                            salario = f.get("monto_pago") or 0
                        else:
                            uid, uname, idrol = f[0], f[1], f[2]
                            nombre  = f[3] or f[1]
                            salario = f[4] or 0
                        self._usuarios_cache.append({
                            "id"      : uid,
                            "nombre"  : str(nombre).strip().title(),
                            "username": uname,
                            "rol"     : "ADMINISTRADOR" if str(idrol) == "1" else "CAJERO",
                            "salario" : float(salario),
                            "acceso"  : "—",
                        })
            except Exception:
                self._usuarios_cache = []

        if hasattr(self, "txt_buscar_usuario"):
            self.txt_buscar_usuario.blockSignals(True)
            self.txt_buscar_usuario.clear()
            self.txt_buscar_usuario.blockSignals(False)

        self._renderizar_usuarios()

    def _renderizar_usuarios(self, lista=None):
        if lista is None:
            lista = self._usuarios_cache

        while self.layout_filas.count():
            item = self.layout_filas.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not lista:
            lbl_vacio = QLabel("NO SE ENCONTRARON USUARIOS")
            lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_vacio.setFont(_mf(11, QFont.Weight.Bold))
            lbl_vacio.setStyleSheet(
                "color:#C5D4CC; background:transparent; padding:40px 0;"
            )
            self.layout_filas.addWidget(lbl_vacio)
            return

        for u in lista:
            fila = self._crear_fila_usuario(u)
            self.layout_filas.addWidget(fila)

    def _filtrar_usuarios(self, texto):
        """Filtra en vivo la lista de usuarios por nombre o rol (texto libre)."""
        texto = texto.strip().lower()
        if not texto:
            self._renderizar_usuarios()
            return
        filtrados = [
            u for u in self._usuarios_cache
            if texto in u["nombre"].lower() or texto in u["rol"].lower()
        ]
        self._renderizar_usuarios(filtrados)

    def _filtro_todos(self):
        """Boton TODOS: limpia cualquier filtro y muestra la lista completa."""
        self.txt_buscar_usuario.blockSignals(True)
        self.txt_buscar_usuario.clear()
        self.txt_buscar_usuario.blockSignals(False)
        self._renderizar_usuarios()

    def _filtro_por_rol(self):
        """
        Boton POR ROL: alterna entre mostrar solo ADMINISTRADOR o solo CAJERO.
        Nota: la BD no registra fecha/hora de ultimo acceso, asi que
        ULTIMOS ACCESOS ordena alfabeticamente como aproximacion honesta
        en vez de inventar fechas falsas.
        """
        self._rol_filtro_actual = getattr(self, "_rol_filtro_actual", None)
        if self._rol_filtro_actual == "ADMINISTRADOR":
            self._rol_filtro_actual = "CAJERO"
        else:
            self._rol_filtro_actual = "ADMINISTRADOR"
        filtrados = [u for u in self._usuarios_cache if u["rol"] == self._rol_filtro_actual]
        self._renderizar_usuarios(filtrados)

    def _filtro_ultimos_accesos(self):
        ordenados = sorted(self._usuarios_cache, key=lambda u: u["nombre"])
        self._renderizar_usuarios(ordenados)

    def _crear_fila_usuario(self, u):
        """
        CORRECCIÓN: el borde inferior se aplica al QFrame completo (toda
        la fila), no a un widget interno — por eso antes se veía como un
        subrayado corto bajo el texto del nombre en vez de una línea
        completa separando cada fila.
        """
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

        # Columna rol — CORREGIDA: ancho suficiente para "ADMINISTRADOR" completo
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
        dlg = DialogoNuevoUsuario(self._conexion, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.resultado:
            QMessageBox.information(
                self, "Usuario creado",
                "El usuario '{}' fue creado correctamente.".format(dlg.resultado["usuario"])
            )
            self._cargar_usuarios()

    def abrir_cambiar_password(self):
        if not self._usuarios_cache:
            QMessageBox.information(self, "Cambiar contraseña",
                "No hay usuarios registrados.")
            return
        dlg = DialogoCambiarPassword(self._usuarios_cache, self._conexion, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.resultado:
            QMessageBox.information(
                self, "Contraseña actualizada",
                "La contraseña de '{}' fue actualizada correctamente.".format(
                    dlg.resultado["nombre"])
            )

    def abrir_eliminar_usuario(self):
        dlg = DialogoEliminarUsuario(self._usuarios_cache, self._conexion, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.eliminados:
            QMessageBox.information(
                self, "Usuario(s) eliminado(s)",
                "{} usuario(s) eliminado(s) correctamente.".format(len(dlg.eliminados))
            )
            self._cargar_usuarios()

    def abrir_modificar_usuario(self):
        if not self._usuarios_cache:
            QMessageBox.information(self, "Modificar usuario",
                "No hay usuarios registrados.")
            return
        dlg = DialogoModificarUsuario(self._usuarios_cache, self._conexion, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.resultado:
            QMessageBox.information(
                self, "Usuario modificado",
                "Los datos de '{}' fueron actualizados correctamente.".format(
                    dlg.resultado["nombre"])
            )
            self._cargar_usuarios()

    # ══════════════════════════════════════════════════════════════════════
    # POSICIONAMIENTO — márgenes simétricos + fix de geometría diferida
    # ══════════════════════════════════════════════════════════════════════
    def _reposicionar(self):
        margen = 16
        self.card.setGeometry(
            margen, margen,
            self.width() - margen * 2,
            self.height() - margen * 2
        )
        # Misma corrección que en DialogoBase: garantiza que overlay y
        # card queden visibles y al frente, evitando el bug de "ventana
        # invisible que sigue bloqueando clicks".
        self._overlay.show()
        self._overlay.raise_()
        self.card.show()
        self.card.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._overlay.setGeometry(0, 0, self.width(), self.height())
        self._reposicionar()

    def _ajustar_geometria_completa(self):
        x, y, ancho, alto = _geometria_ventana_real(self.parent() or self)
        self.setGeometry(x, y, ancho, alto)
        self._overlay.setGeometry(0, 0, self.width(), self.height())
        self._reposicionar()

    def showEvent(self, event):
        super().showEvent(event)
        self._ajustar_geometria_completa()
        # Recalcula en el siguiente ciclo del event loop, cuando Qt ya
        # garantiza que el padre tiene su geometría final resuelta.
        QTimer.singleShot(0, self._ajustar_geometria_completa)