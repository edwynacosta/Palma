import os
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QFontDatabase, QColor, QPainter, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame,
    QPushButton, QLabel, QDialog, QGraphicsDropShadowEffect,
    QScrollArea, QMessageBox, QComboBox, QDoubleSpinBox,
    QApplication, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy
)
from PySide6.QtCore import QPoint

# ── Funciones auxiliares de estilo y geometría ──
def _mf(size, weight):
    f = QFont("Montserrat", size, weight)
    f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    return f

def _geometria_ventana_real(widget):
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
    screen = QApplication.primaryScreen()
    if screen:
        geo = screen.availableGeometry()
        return geo.x(), geo.y(), geo.width(), geo.height()
    return 0, 0, 1280, 800

# ── Estilos de inputs (más grandes) ──
SS_INPUT = (
    "QLineEdit { background:#EDF7F1; color:#1F2937; border:2px solid transparent;"
    " border-radius:14px; padding:0 20px; font-size:14px; }"
    " QLineEdit:focus { border:2px solid #17813D; }"
)
SS_COMBO = (
    "QComboBox { background:#EDF7F1; color:#1F2937; border:2px solid transparent;"
    " border-radius:14px; padding:0 20px; font-size:14px; }"
    " QComboBox:focus { border:2px solid #17813D; }"
    " QComboBox::drop-down { border:none; width:30px; }"
    " QComboBox QAbstractItemView { background:#FFFFFF; color:#1F2937;"
    " border:1px solid #A9DDBC; border-radius:10px; selection-background-color:#17813D;"
    " selection-color:#FFFFFF; padding:4px; }"
)
SS_DSPIN = (
    "QDoubleSpinBox { background:#EDF7F1; color:#1F2937; border:2px solid transparent;"
    " border-radius:14px; padding:0 20px; font-size:14px; }"
    " QDoubleSpinBox:focus { border:2px solid #17813D; }"
    " QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width:22px; }"
)

# ── Diálogo base ──
class DialogoBase(QDialog):
    def __init__(self, titulo, ancho=600, parent=None):
        super().__init__(parent,
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self._overlay = QFrame(self)
        self._overlay.setObjectName("Overlay")
        self._overlay.setStyleSheet("QFrame#Overlay { background:rgba(0,0,0,0.45); border:none; }")
        self.card = QFrame(self)
        self.card.setObjectName("DialogCard")
        self.card.setFixedWidth(ancho)
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.card.setStyleSheet("""
            QFrame#DialogCard {
                background-color: #FFFFFF;
                border-radius: 28px;
                border: none;
            }
        """)
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(50)
        sombra.setColor(QColor(0, 0, 0, 50))
        sombra.setOffset(0, 12)
        self.card.setGraphicsEffect(sombra)
        self.layout_card = QVBoxLayout(self.card)
        self.layout_card.setContentsMargins(36, 30, 36, 34)
        self.layout_card.setSpacing(18)
        fila = QHBoxLayout()
        fila.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(titulo)
        lbl.setFont(_mf(18, QFont.Weight.Black))
        lbl.setStyleSheet("color:#17813D; background:transparent;")
        btn_x = QPushButton("✕")
        btn_x.setFixedSize(34, 34)
        btn_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_x.setFont(_mf(12, QFont.Weight.Bold))
        btn_x.setStyleSheet("QPushButton { background:transparent; color:#9CA3AF; border:none; } QPushButton:hover { color:#DC2626; }")
        btn_x.clicked.connect(self.reject)
        fila.addWidget(lbl); fila.addStretch(); fila.addWidget(btn_x)
        self.layout_card.addLayout(fila)

    def _lbl(self, texto):
        l = QLabel(texto)
        l.setFont(_mf(9, QFont.Weight.Black))
        l.setStyleSheet("color:#17813D; background:transparent; letter-spacing:0.5px;")
        return l

    def _input(self, placeholder="", password=False):
        t = QLineEdit()
        t.setPlaceholderText(placeholder)
        t.setFont(_mf(14, QFont.Weight.Medium))
        t.setFixedHeight(56)
        t.setStyleSheet(SS_INPUT)
        if password:
            t.setEchoMode(QLineEdit.EchoMode.Password)
        return t

    def _combo(self, items):
        c = QComboBox()
        c.addItems(items)
        c.setFont(_mf(14, QFont.Weight.Medium))
        c.setFixedHeight(56)
        c.setStyleSheet(SS_COMBO)
        c.setCursor(Qt.CursorShape.PointingHandCursor)
        return c

    def _dspin(self, mn=0.0, mx=99999999.0, dec=0, prefix="$ "):
        s = QDoubleSpinBox()
        s.setRange(mn, mx)
        s.setDecimals(dec)
        s.setPrefix(prefix)
        s.setSingleStep(50000)
        s.setFont(_mf(14, QFont.Weight.Medium))
        s.setFixedHeight(56)
        s.setStyleSheet(SS_DSPIN)
        return s

    def _btn_ok(self, texto, bg="#17813D", hv="#228E49"):
        b = QPushButton(texto)
        b.setFixedHeight(56)
        b.setFont(_mf(13, QFont.Weight.Black))
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setStyleSheet(
            "QPushButton {{ background:{b}; color:#FFFFFF; border:none;"
            " border-radius:18px; letter-spacing:0.5px; }}"
            "QPushButton:hover {{ background:{h}; }}".format(b=bg, h=hv)
        )
        return b

    def _btn_cancel(self, texto="CANCELAR"):
        b = QPushButton(texto)
        b.setFixedHeight(50)
        b.setFont(_mf(12, QFont.Weight.Bold))
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setStyleSheet("QPushButton { background:transparent; color:#9CA3AF; border:none; } QPushButton:hover { color:#17813D; }")
        b.clicked.connect(self.reject)
        return b

    def _reposicionar(self):
        self.card.adjustSize()
        cw, ch = self.card.width(), self.card.height()
        self.card.move((self.width() - cw)//2, max(16, (self.height() - ch)//2))
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
        QTimer.singleShot(0, self._ajustar_geometria_completa)


# ── Diálogos específicos (ampliados) ──
class DialogoNuevoUsuario(DialogoBase):
    def __init__(self, conexion=None, parent=None):
        super().__init__("NUEVO USUARIO", ancho=600, parent=parent)
        self.resultado = None
        self._conexion = conexion

        self.layout_card.addWidget(self._lbl("NOMBRE COMPLETO"))
        self.txt_nombre = self._input("Ej: Carlos Andrés Gómez")
        self.layout_card.addWidget(self.txt_nombre)

        fila1 = QHBoxLayout(); fila1.setSpacing(16)
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

        fila2 = QHBoxLayout(); fila2.setSpacing(16)
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
        btn_crear.setFixedWidth(200)
        btn_crear.clicked.connect(self._confirmar)
        fila_b.addWidget(btn_crear)
        self.layout_card.addLayout(fila_b)

    def _confirmar(self):
        nombre = self.txt_nombre.text().strip()
        usuario = self.txt_usuario.text().strip()
        password = self.txt_password.text().strip()
        rol_txt = self.combo_rol.currentText()
        salario = self.spin_salario.value()
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
            QMessageBox.critical(self, "Sin conexión", "No hay conexión activa a la base de datos.")
            return
        try:
            with self._conexion.cursor() as cur:
                cur.execute("SELECT id_usuario FROM usuarios WHERE username_log = %s", (usuario,))
                if cur.fetchone():
                    QMessageBox.warning(self, "Usuario duplicado", "Ya existe un usuario con ese nombre de usuario.")
                    return
                cur.execute("INSERT INTO empleados (nombre_empleado, id_rol, monto_pago) VALUES (%s, %s, %s)",
                            (nombre, id_rol, salario))
                id_empleado = cur.lastrowid
                cur.execute("INSERT INTO usuarios (id_rol, id_empleado, username_log, contrasena_log) VALUES (%s, %s, %s, %s)",
                            (id_rol, id_empleado, usuario, password))
                self._conexion.commit()
            self.resultado = {"nombre": nombre, "usuario": usuario, "rol": rol_txt, "id_empleado": id_empleado}
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo crear el usuario:\n{e}")

class DialogoCambiarPassword(DialogoBase):
    def __init__(self, usuarios, conexion=None, parent=None):
        super().__init__("CAMBIAR CONTRASEÑA", ancho=540, parent=parent)
        self.resultado = None
        self._conexion = conexion
        self._usuarios = usuarios
        self.layout_card.addWidget(self._lbl("SELECCIONA EL USUARIO"))
        self.combo_usuario = self._combo([f"{u['nombre']}  ·  {u['rol']}" for u in usuarios])
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
        btn_ok.setFixedWidth(180)
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
            QMessageBox.warning(self, "No coinciden", "Las contraseñas escritas no son iguales.")
            self.txt_pass2.setFocus(); return
        if not self._conexion:
            QMessageBox.critical(self, "Sin conexión", "No hay conexión activa a la base de datos.")
            return
        try:
            with self._conexion.cursor() as cur:
                cur.execute("UPDATE usuarios SET contrasena_log = %s WHERE id_usuario = %s", (p1, usuario["id"]))
                self._conexion.commit()
            self.resultado = usuario
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo actualizar la contraseña:\n{e}")

class DialogoEliminarUsuario(DialogoBase):
    def __init__(self, usuarios, conexion=None, parent=None):
        super().__init__("ELIMINAR USUARIO", ancho=580, parent=parent)
        self._conexion = conexion
        self._usuarios = usuarios
        self.eliminados = []
        self.layout_card.addWidget(self._lbl("SELECCIONA LOS USUARIOS A ELIMINAR"))
        self.layout_card.addSpacing(4)
        scroll_frame = QFrame()
        scroll_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        scroll_frame.setStyleSheet("QFrame { background:#F8FAF9; border:2px dashed #C8E6D4; border-radius:16px; }")
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
                chk.setFixedSize(24, 24)
                chk.setStyleSheet(
                    "QCheckBox::indicator { width:22px; height:22px; border-radius:6px; border:2px solid #A9DDBC; background:#FFFFFF; }"
                    "QCheckBox::indicator:checked { background:#DC2626; border:2px solid #DC2626; }"
                )
                self._checks.append((u, chk))
                lbl_nom = QLabel(u["nombre"])
                lbl_nom.setFont(_mf(13, QFont.Weight.Bold))
                lbl_nom.setStyleSheet("color:#1F2937; background:transparent;")
                lbl_rol = QLabel(u["rol"])
                lbl_rol.setFont(_mf(10, QFont.Weight.Black))
                lbl_rol.setStyleSheet("color:#9CA3AF; background:transparent;")
                lbl_rol.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                fila.addWidget(chk)
                fila.addWidget(lbl_nom, 1)
                fila.addWidget(lbl_rol)
                contenedor = QFrame()
                contenedor.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
                contenedor.setStyleSheet("QFrame { background:#FFFFFF; border-radius:12px; border:none; }")
                contenedor.setFixedHeight(58)
                QHBoxLayout(contenedor).addLayout(fila)
                contenedor.layout().setContentsMargins(12, 0, 12, 0)
                scroll_layout.addWidget(contenedor)
        scroll_frame.setMinimumHeight(min(len(usuarios) * 66 + 28, 320) if usuarios else 130)
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
            QMessageBox.critical(self, "Sin conexión", "No hay conexión activa a la base de datos.")
            return
        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Eliminar {len(seleccionados)} usuario(s) seleccionado(s)? Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            with self._conexion.cursor() as cur:
                for u in seleccionados:
                    cur.execute("DELETE FROM usuarios WHERE id_usuario = %s", (u["id"],))
                self._conexion.commit()
            self.eliminados = seleccionados
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al eliminar", f"No se pudieron eliminar los usuarios:\n{e}")

class DialogoModificarUsuario(DialogoBase):
    def __init__(self, usuarios, conexion=None, parent=None):
        super().__init__("MODIFICAR USUARIO", ancho=580, parent=parent)
        self.resultado = None
        self._conexion = conexion
        self._usuarios = usuarios
        self.layout_card.addWidget(self._lbl("SELECCIONA EL USUARIO"))
        self.combo_usuario = self._combo([f"{u['nombre']}  ·  {u['rol']}" for u in usuarios])
        self.combo_usuario.currentIndexChanged.connect(self._cargar_datos)
        self.layout_card.addWidget(self.combo_usuario)
        self.layout_card.addWidget(self._lbl("NOMBRE COMPLETO"))
        self.txt_nombre = self._input("Nombre completo")
        self.layout_card.addWidget(self.txt_nombre)
        fila1 = QHBoxLayout(); fila1.setSpacing(16)
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
        btn_g.setFixedWidth(200)
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
        u = self._usuarios[idx]
        nombre = self.txt_nombre.text().strip()
        usuario = self.txt_usuario.text().strip()
        rol_txt = self.combo_rol.currentText()
        salario = self.spin_salario.value()
        id_rol = 1 if rol_txt == "ADMINISTRADOR" else 2
        if not nombre:
            QMessageBox.warning(self, "Falta información", "Ingresa el nombre completo.")
            self.txt_nombre.setFocus(); return
        if not usuario:
            QMessageBox.warning(self, "Falta información", "Ingresa el nombre de usuario.")
            self.txt_usuario.setFocus(); return
        if not self._conexion:
            QMessageBox.critical(self, "Sin conexión", "No hay conexión activa a la base de datos.")
            return
        try:
            with self._conexion.cursor() as cur:
                cur.execute("SELECT id_usuario FROM usuarios WHERE username_log = %s AND id_usuario != %s", (usuario, u["id"]))
                if cur.fetchone():
                    QMessageBox.warning(self, "Usuario duplicado", "Ya existe otro usuario con ese nombre de usuario.")
                    return
                cur.execute("UPDATE empleados SET nombre_empleado=%s, id_rol=%s, monto_pago=%s WHERE id_empleado=(SELECT id_empleado FROM usuarios WHERE id_usuario=%s)",
                            (nombre, id_rol, salario, u["id"]))
                cur.execute("UPDATE usuarios SET username_log=%s, id_rol=%s WHERE id_usuario=%s", (usuario, id_rol, u["id"]))
                self._conexion.commit()
            self.resultado = {"id": u["id"], "nombre": nombre, "usuario": usuario, "rol": rol_txt}
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo modificar el usuario:\n{e}")


# ── CLASE PRINCIPAL: CuentaDialog ──
class CuentaDialog(QDialog):
    def __init__(self, conexion=None, datos_usuario=None, parent=None):
        super().__init__(parent,
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        self._conexion = conexion
        self._datos_usuario = datos_usuario or {}
        self._usuarios_cache = []
        self.COLOR_FONDO = "#F4F6F8"

        # Cargar fuentes
        ruta_vistas = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz = os.path.dirname(ruta_vistas)
        carpeta_fuentes = os.path.join(ruta_raiz, "fuentes")
        for f in ("Montserrat-Bold.ttf", "Montserrat-Regular.ttf",
                  "Montserrat-Medium.ttf", "Montserrat-Black.ttf"):
            rp = os.path.join(carpeta_fuentes, f)
            if os.path.exists(rp):
                QFontDatabase.addApplicationFont(rp)

        self.BRAND = "#17813D"
        self.BRAND_LIGHT = "#228E49"

        # ── Overlay ──
        self._overlay = QFrame(self)
        self._overlay.setObjectName("Overlay")
        self._overlay.setStyleSheet("QFrame#Overlay { background:rgba(0,0,0,0.45); border:none; }")

        # ── Tarjeta principal ──
        self.card = QFrame(self)
        self.card.setObjectName("CuentaCard")
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.card.setStyleSheet("""
            QFrame#CuentaCard {
                background-color: #FFFFFF;
                border-radius: 32px;
                border: none;
            }
        """)
        sombra = QGraphicsDropShadowEffect(self.card)
        sombra.setBlurRadius(40)
        sombra.setColor(QColor(0, 0, 0, 35))
        sombra.setOffset(0, 10)
        self.card.setGraphicsEffect(sombra)

        layout_card = QVBoxLayout(self.card)
        layout_card.setContentsMargins(0, 0, 0, 0)
        layout_card.setSpacing(0)

        # ── BARRA SUPERIOR ──
        navbar = QFrame()
        navbar.setObjectName("NavbarCuenta")
        navbar.setFixedHeight(68)
        navbar.setStyleSheet("""
            QFrame#NavbarCuenta {
                background: #FFFFFF;
                border: none;
                border-top-left-radius: 32px;
                border-top-right-radius: 32px;
            }
        """)
        layout_navbar = QHBoxLayout(navbar)
        layout_navbar.setContentsMargins(0, 0, 20, 0)
        layout_navbar.setSpacing(0)

        titulo_layout = QHBoxLayout()
        titulo_layout.setContentsMargins(20, 0, 0, 0)
        lbl_titulo = QLabel("CONFIGURACIÓN DE CUENTA")
        lbl_titulo.setFont(QFont("Montserrat", 20, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: #17813D; background: transparent;")
        titulo_layout.addWidget(lbl_titulo)

        # Panel de usuario
        layout_meta = QVBoxLayout()
        layout_meta.setSpacing(0)
        layout_meta.setContentsMargins(0, 0, 0, 0)
        layout_meta.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        self.lbl_nombre = QLabel("Usuario")
        self.lbl_nombre.setFont(QFont("Montserrat", 11, QFont.Weight.Black))
        self.lbl_nombre.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_nombre.setStyleSheet("color:#17813D; background:transparent;")

        self.lbl_rol = QLabel("ROL")
        self.lbl_rol.setFont(QFont("Montserrat", 8, QFont.Weight.Bold))
        self.lbl_rol.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_rol.setStyleSheet("color:#9CA3AF; background:transparent;")

        layout_meta.addWidget(self.lbl_nombre)
        layout_meta.addWidget(self.lbl_rol)

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
        layout_card.addWidget(navbar)

        # ── CUERPO ──
        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.setSpacing(0)

        # ── SIDEBAR (izquierda) ──
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        sidebar.setStyleSheet("""
            QFrame {
                background: #F8FAF9;
                border: none;
                border-right: 1px solid #E5E7EB;
            }
        """)
        ls = QVBoxLayout(sidebar)
        ls.setContentsMargins(16, 20, 16, 20)
        ls.setSpacing(14)

        # Card administrador (sin bordes molestos)
        card_admin = QFrame()
        card_admin.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card_admin.setFixedHeight(74)
        card_admin.setStyleSheet("QFrame { background: transparent; border: none; }")
        lca = QHBoxLayout(card_admin)
        lca.setContentsMargins(14, 0, 14, 0)
        lca.setSpacing(12)

        nombre_admin = str(self._datos_usuario.get("nombre", "Administrador")).title()
        inicial = nombre_admin[0].upper() if nombre_admin else "A"

        avatar_admin = QLabel(inicial)
        avatar_admin.setFixedSize(40, 40)
        avatar_admin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_admin.setFont(_mf(13, QFont.Weight.Black))
        avatar_admin.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        avatar_admin.setStyleSheet("QLabel { background:#17813D; border-radius:20px; color:#FFFFFF; }")

        col_admin = QVBoxLayout()
        col_admin.setSpacing(2)
        col_admin.setContentsMargins(0, 0, 0, 0)
        col_admin.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        lbl_rol_admin = QLabel("ADMINISTRADOR DE CUENTA")
        lbl_rol_admin.setFont(_mf(7, QFont.Weight.Black))
        lbl_rol_admin.setStyleSheet("color:#9CA3AF; background:transparent; letter-spacing:0.3px;")
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

        # Card estado del software
        card_estado = QFrame()
        card_estado.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card_estado.setFixedHeight(180)
        card_estado.setStyleSheet("QFrame { background:#17813D; border-radius:18px; border:none; }")
        lce = QVBoxLayout(card_estado)
        lce.setContentsMargins(20, 18, 20, 18)
        lce.setSpacing(6)

        lbl_estado_tag = QLabel("ESTADO DEL SOFTWARE:")
        lbl_estado_tag.setFont(_mf(8, QFont.Weight.Black))
        lbl_estado_tag.setStyleSheet("color:#A9DDBC; background:transparent; letter-spacing:0.5px;")

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
        btn_full.setStyleSheet("QPushButton { background:#FFFFFF; color:#17813D; border:none; border-radius:11px; } QPushButton:hover { background:#E9F7EF; }")

        lce.addWidget(lbl_estado_tag)
        lce.addWidget(lbl_version)
        lce.addStretch()
        lce.addWidget(btn_full)
        ls.addWidget(card_estado)

        # Card asistencia
        card_soporte = QFrame()
        card_soporte.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card_soporte.setFixedHeight(100)
        card_soporte.setCursor(Qt.CursorShape.PointingHandCursor)
        card_soporte.setStyleSheet("QFrame { background:#E9F7EF; border-radius:18px; border:none; }")
        lcs = QVBoxLayout(card_soporte)
        lcs.setContentsMargins(18, 14, 18, 14)
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
        ls.addStretch()

        cuerpo.addWidget(sidebar)

        # ── CONTENIDO PRINCIPAL ──
        contenido = QFrame()
        contenido.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        contenido.setStyleSheet("QFrame { background:#FFFFFF; border:none; }")
        lcont = QVBoxLayout(contenido)
        lcont.setContentsMargins(24, 20, 24, 20)
        lcont.setSpacing(12)

        # ── Fila de gestión de usuarios ──
        fila_header = QHBoxLayout()
        lbl_gestion = QLabel("GESTIÓN DE USUARIOS")
        lbl_gestion.setFont(QFont("Montserrat", 20, QFont.Weight.Black))
        lbl_gestion.setStyleSheet("color:#17813D; background:transparent;")
        fila_header.addWidget(lbl_gestion)
        fila_header.addStretch()
        lcont.addLayout(fila_header)

        # ── Barra de búsqueda y filtros (con bordes) ──
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(10)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por nombre o rol...")
        self.txt_buscar.setFixedHeight(40)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #EEEFF2;
                border-radius: 16px;
                padding: 0 16px;
                font-family: 'Montserrat';
                font-size: 13px;
                color: #1F2937;
            }
            QLineEdit:focus { border: 2px solid #17813D; }
        """)
        self.txt_buscar.textChanged.connect(self._filtrar_usuarios)
        filtros_layout.addWidget(self.txt_buscar, 1)

        self.btn_todos = QPushButton("TODOS")
        self.btn_ultimos = QPushButton("ÚLTIMOS ACCESOS")
        self.btn_por_rol = QPushButton("POR ROL  ▾")

        for btn in (self.btn_todos, self.btn_ultimos, self.btn_por_rol):
            btn.setFixedHeight(40)
            btn.setFont(QFont("Montserrat", 11, QFont.Weight.Black))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 2px solid #EEEFF2;
                    border-radius: 16px;
                    color: #9CA3AF;
                    padding: 0 18px;
                    text-align: center;
                    font-family: 'Montserrat';
                    font-size: 11px;
                    font-weight: 900;
                }
                QPushButton:hover {
                    color: #17813D;
                    border-color: #A9DDBC;
                }
            """)
            filtros_layout.addWidget(btn)

        self.btn_todos.clicked.connect(self._filtro_todos)
        self.btn_ultimos.clicked.connect(self._filtro_ultimos_accesos)
        self.btn_por_rol.clicked.connect(self._filtro_por_rol)

        lcont.addLayout(filtros_layout)

        # ── Línea separadora antes de la tabla ──
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background:#EEF0F2; border:none;")
        lcont.addWidget(sep)

        # ── Tabla de usuarios (con sus propios encabezados) ──
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["NOMBRE COMPLETO", "ROL DE USUARIO", "ÚLTIMO ACCESO"])
        self.tabla.setShowGrid(False)
        self.tabla.setFrameShape(QFrame.Shape.NoFrame)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(50)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
                outline: none;
                font-family: 'Montserrat';
                font-size: 14px;
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
                font-size: 11px;
                border: none;
                padding: 10px 12px;
                font-family: 'Montserrat';
            }
            QTableWidget QTableCornerButton::section {
                background: transparent;
                border: none;
            }
        """)
        header = self.tabla.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla.setColumnWidth(0, 300)
        self.tabla.setColumnWidth(1, 150)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        # Alinear el encabezado de la columna "ÚLTIMO ACCESO" a la derecha
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # ya estaba
        # Para alinear el texto del encabezado a la derecha, necesitamos un item de encabezado
        header_item = self.tabla.horizontalHeaderItem(2)
        if header_item:
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)

        lcont.addWidget(self.tabla)

        # ── Botones de acción (inferior, con bordes y esquinas redondeadas) ──
        barra_inf = QFrame()
        barra_inf.setFixedHeight(80)
        barra_inf.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border: none;
                border-top: 1px solid #EEF0F2;
                border-bottom-left-radius: 32px;
                border-bottom-right-radius: 32px;
            }
        """)
        li = QHBoxLayout(barra_inf)
        li.setContentsMargins(0, 0, 0, 0)

        self.btn_nuevo = QPushButton("NUEVO USUARIO")
        self.btn_nuevo.setFixedSize(200, 48)
        self.btn_nuevo.setFont(_mf(13, QFont.Weight.Black))
        self.btn_nuevo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #17813D;
                color: #FFFFFF;
                border: none;
                border-radius: 16px;
                letter-spacing: 0.5px;
                font-family: 'Montserrat';
                font-size: 13px;
                font-weight: 900;
            }
            QPushButton:hover { background-color: #228E49; }
        """)
        self.btn_nuevo.clicked.connect(self.abrir_nuevo_usuario)

        def _btn_sec(texto, ancho):
            b = QPushButton(texto)
            b.setFixedSize(ancho, 46)
            b.setFont(_mf(12, QFont.Weight.Black))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton {
                    background: #FFFFFF;
                    color: #9CA3AF;
                    border: 2px solid #EEEFF2;
                    border-radius: 16px;
                    font-family: 'Montserrat';
                    font-size: 12px;
                    font-weight: 900;
                }
                QPushButton:hover {
                    color: #17813D;
                    border-color: #A9DDBC;
                }
            """)
            return b

        self.btn_password = _btn_sec("CAMBIAR CONTRASEÑA", 190)
        self.btn_eliminar = _btn_sec("ELIMINAR USUARIO", 160)
        self.btn_modificar = _btn_sec("MODIFICAR USUARIO", 170)

        self.btn_password.clicked.connect(self.abrir_cambiar_password)
        self.btn_eliminar.clicked.connect(self.abrir_eliminar_usuario)
        self.btn_modificar.clicked.connect(self.abrir_modificar_usuario)

        lbs = QHBoxLayout()
        lbs.setSpacing(10)
        for b in (self.btn_password, self.btn_eliminar, self.btn_modificar):
            lbs.addWidget(b)

        li.addWidget(self.btn_nuevo)
        li.addStretch()
        li.addLayout(lbs)
        lcont.addWidget(barra_inf)

        cuerpo.addWidget(contenido, 1)
        layout_card.addLayout(cuerpo, 1)

        # Actualizar UI con los datos del usuario recibidos
        self._actualizar_usuario_desde_datos()

        self._cargar_usuarios()

    def _actualizar_usuario_desde_datos(self):
        nombre = self._datos_usuario.get("nombre", "Usuario")
        rol = self._datos_usuario.get("rol", "CAJERO")
        self.actualizar_usuario(nombre, rol)

    def actualizar_usuario(self, nombre, rol):
        nombre_display = str(nombre).strip().title()
        rol_display = str(rol).strip().upper()
        self.lbl_nombre.setText(nombre_display)
        self.lbl_rol.setText(rol_display)
        iniciales = "".join([n[0] for n in nombre_display.split()[:2]]).upper()
        self.lbl_avatar.setText(iniciales)

    def cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Salir", "¿Estás seguro de que deseas cerrar la sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            if hasattr(self.parent(), "cambiar_pantalla"):
                self.parent().cambiar_pantalla("Login")
            else:
                self.reject()

    def volver_dashboard(self):
        self.accept()

    def showEvent(self, event):
        if not self._datos_usuario and hasattr(self.parent(), "usuario_actual"):
            self._datos_usuario = self.parent().usuario_actual or {}
            self._actualizar_usuario_desde_datos()
        super().showEvent(event)

    # ── Carga y renderizado de usuarios ──
    def _cargar_usuarios(self):
        self._usuarios_cache = []
        if self._conexion:
            try:
                with self._conexion.cursor() as cur:
                    cur.execute("""
                        SELECT u.id_usuario, u.username_log, u.id_rol,
                               e.nombre_empleado, e.monto_pago, e.fecha_ingreso
                        FROM usuarios u
                        LEFT JOIN empleados e ON e.id_empleado = u.id_empleado
                        ORDER BY u.id_usuario ASC
                    """)
                    filas = cur.fetchall()
                    for f in filas:
                        if isinstance(f, dict):
                            uid = f["id_usuario"]
                            uname = f["username_log"]
                            idrol = f["id_rol"]
                            nombre = f.get("nombre_empleado") or uname
                            salario = f.get("monto_pago") or 0
                            fecha_ingreso = f.get("fecha_ingreso")
                        else:
                            uid, uname, idrol = f[0], f[1], f[2]
                            nombre = f[3] or f[1]
                            salario = f[4] or 0
                            fecha_ingreso = f[5] if len(f) > 5 else None
                        # Formatear fecha de último acceso
                        if fecha_ingreso:
                            if hasattr(fecha_ingreso, 'strftime'):
                                ultimo_acceso = fecha_ingreso.strftime("%d/%m/%Y %H:%M")
                            else:
                                ultimo_acceso = str(fecha_ingreso)
                        else:
                            ultimo_acceso = "—"
                        self._usuarios_cache.append({
                            "id": uid,
                            "nombre": str(nombre).strip().title(),
                            "username": uname,
                            "rol": "ADMINISTRADOR" if str(idrol) == "1" else "CAJERO",
                            "salario": float(salario),
                            "ultimo_acceso": ultimo_acceso,
                        })
            except Exception as e:
                print(f"Error cargando usuarios: {e}")
                self._usuarios_cache = []

        self._renderizar_usuarios()

    def _renderizar_usuarios(self, lista=None):
        if lista is None:
            lista = self._usuarios_cache
        self.tabla.setRowCount(len(lista))
        for fila, u in enumerate(lista):
            inicial = "".join([n[0] for n in u["nombre"].split()[:2]]).upper()
            item_nombre = QTableWidgetItem(f"   {u['nombre']}")
            item_nombre.setIcon(self._crear_avatar_icon(inicial))
            item_nombre.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.tabla.setItem(fila, 0, item_nombre)

            item_rol = QTableWidgetItem(u["rol"])
            item_rol.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            if u["rol"] == "ADMINISTRADOR":
                item_rol.setForeground(QColor("#17813D"))
            else:
                item_rol.setForeground(QColor("#9CA3AF"))
            self.tabla.setItem(fila, 1, item_rol)

            item_acceso = QTableWidgetItem(u["ultimo_acceso"])
            # Alinear a la derecha
            item_acceso.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_acceso.setForeground(QColor("#9CA3AF"))
            self.tabla.setItem(fila, 2, item_acceso)

        for fila in range(self.tabla.rowCount()):
            self.tabla.setRowHeight(fila, 50)

    def _crear_avatar_icon(self, letras):
        from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#E9F7EF"))
        painter.setPen(QColor("#A9DDBC"))
        painter.drawEllipse(0, 0, 32, 32)
        painter.setPen(QColor("#17813D"))
        painter.setFont(QFont("Montserrat", 10, QFont.Weight.Bold))
        painter.drawText(0, 0, 32, 32, Qt.AlignmentFlag.AlignCenter, letras)
        painter.end()
        from PySide6.QtGui import QIcon
        return QIcon(pixmap)

    # ── Filtros ──
    def _filtrar_usuarios(self, texto):
        texto = texto.strip().lower()
        if not texto:
            self._renderizar_usuarios()
            return
        filtrados = [u for u in self._usuarios_cache if texto in u["nombre"].lower() or texto in u["rol"].lower()]
        self._renderizar_usuarios(filtrados)

    def _filtro_todos(self):
        self.txt_buscar.clear()
        self._renderizar_usuarios()

    def _filtro_por_rol(self):
        self._rol_filtro_actual = getattr(self, "_rol_filtro_actual", None)
        if self._rol_filtro_actual == "ADMINISTRADOR":
            self._rol_filtro_actual = "CAJERO"
        else:
            self._rol_filtro_actual = "ADMINISTRADOR"
        filtrados = [u for u in self._usuarios_cache if u["rol"] == self._rol_filtro_actual]
        self._renderizar_usuarios(filtrados)

    def _filtro_ultimos_accesos(self):
        # Ordenar por fecha de último acceso descendente (más reciente primero)
        ordenados = sorted(self._usuarios_cache, key=lambda u: u["ultimo_acceso"], reverse=True)
        self._renderizar_usuarios(ordenados)

    # ── Acciones de botones ──
    def abrir_nuevo_usuario(self):
        dlg = DialogoNuevoUsuario(self._conexion, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.resultado:
            QMessageBox.information(self, "Usuario creado", f"El usuario '{dlg.resultado['usuario']}' fue creado correctamente.")
            self._cargar_usuarios()

    def abrir_cambiar_password(self):
        if not self._usuarios_cache:
            QMessageBox.information(self, "Cambiar contraseña", "No hay usuarios registrados.")
            return
        dlg = DialogoCambiarPassword(self._usuarios_cache, self._conexion, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.resultado:
            QMessageBox.information(self, "Contraseña actualizada", f"La contraseña de '{dlg.resultado['nombre']}' fue actualizada correctamente.")

    def abrir_eliminar_usuario(self):
        dlg = DialogoEliminarUsuario(self._usuarios_cache, self._conexion, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.eliminados:
            QMessageBox.information(self, "Usuario(s) eliminado(s)", f"{len(dlg.eliminados)} usuario(s) eliminado(s) correctamente.")
            self._cargar_usuarios()

    def abrir_modificar_usuario(self):
        if not self._usuarios_cache:
            QMessageBox.information(self, "Modificar usuario", "No hay usuarios registrados.")
            return
        dlg = DialogoModificarUsuario(self._usuarios_cache, self._conexion, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.resultado:
            QMessageBox.information(self, "Usuario modificado", f"Los datos de '{dlg.resultado['nombre']}' fueron actualizados correctamente.")
            self._cargar_usuarios()

    # ── Posicionamiento y estilos ──
    def _reposicionar(self):
        margen = 16
        self.card.setGeometry(margen, margen, self.width() - margen * 2, self.height() - margen * 2)
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
        QTimer.singleShot(0, self._ajustar_geometria_completa)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(self.COLOR_FONDO)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())