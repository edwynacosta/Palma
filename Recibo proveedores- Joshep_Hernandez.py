"""
PALMA Software - Módulo: Recibo Proveedores
Base de datos: SQLite (palma_software.db)
Pantalla completa, CRUD completo, filtros rápidos, notas y estado de envío.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import sqlite3
import os
from datetime import date, timedelta
from pathlib import Path

#  Colores 
C_BG        = "#F5F7F4"
C_WHITE     = "#FFFFFF"
C_GREEN_DK  = "#1A5C2E"
C_GREEN_MD  = "#2D8C4E"
C_GREEN_LT  = "#E8F5ED"
C_GREEN_HED = "#C8E6CF"
C_BORDER    = "#D0D8D3"
C_TEXT_DK   = "#1A2E22"
C_TEXT_MD   = "#4A5E52"
C_TEXT_LT   = "#8CA898"
C_ORANGE    = "#E67E22"
C_RED       = "#C0392B"
C_BLUE      = "#2980B9"
C_WARN_BG   = "#FFF3CD"

# Ruta BD 
DB_PATH = Path.home() / "palma_software.db"


#  BASE DE DATOS

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT    NOT NULL,
            contacto    TEXT,
            telefono    TEXT,
            email       TEXT,
            activo      INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS recibo_proveedores (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proveedor    INTEGER NOT NULL REFERENCES proveedores(id),
            producto        TEXT    NOT NULL,
            cantidad        INTEGER DEFAULT 0,
            costo_unitario  REAL    DEFAULT 0,
            costo_total     REAL    DEFAULT 0,
            estado          TEXT    DEFAULT 'Pendiente',
            observaciones   TEXT    DEFAULT '',
            nota_recibo     TEXT    DEFAULT '',
            fecha           TEXT    NOT NULL,
            FOREIGN KEY (id_proveedor) REFERENCES proveedores(id)
        );
    """)

#  VALIDADORES DE ENTRADA NUMÉRICA
# Unidades permitidas para el campo "Cantidad" (se pueden ajustar/ampliar)
UNIDADES_VALIDAS = ["kg", "lb", "g", "gr", "ton", "lt", "l", "und", "oz", "u"]


def _validar_cantidad(valor):
    """
    Permite escribir solo dígitos y, opcionalmente al final, una unidad
    de medida válida (kg, lb, g, etc.). Cualquier letra que no forme
    parte (o prefijo) de una unidad válida es rechazada.
    """
    if valor == "":
        return True
    i = 0
    while i < len(valor) and (valor[i].isdigit() or valor[i] == "."):
        i += 1
    numero = valor[:i]
    letras = valor[i:].lower()

    if numero.count(".") > 1:
        return False
    if letras == "":
        return True
    return any(u.startswith(letras) for u in UNIDADES_VALIDAS)


def _validar_decimal(valor):
    """Permite solo dígitos y un único separador decimal (punto o coma)."""
    if valor == "":
        return True
    if (valor.count(".") + valor.count(",")) > 1:
        return False
    resto = valor.replace(".", "").replace(",", "")
    return resto.isdigit()


def _validar_fecha_chars(valor):
    """Permite solo dígitos y guiones, para el formato AAAA-MM-DD."""
    if valor == "":
        return True
    return all(c.isdigit() or c == "-" for c in valor)


#  VENTANA PRINCIPAL
class PALMAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PALMA Software – Recibo Proveedores")
        self.configure(bg=C_BG)
        self.state("zoomed")          # pantalla completa en Windows/Linux

        # Fallback pantalla completa
        self.after(100, lambda: self._ensure_fullscreen())

        self._build_fonts()
        self._build_ui()
        self.refresh_table()
        self.update_total()

    # pantalla completa 
    def _ensure_fullscreen(self):
        try:
            self.state("zoomed")
        except Exception:
            self.attributes("-fullscreen", True)

    # fuentes 
    def _build_fonts(self):
        self.f_nav     = tkfont.Font(family="Segoe UI", size=9,  weight="bold")
        self.f_title   = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.f_cost_lbl= tkfont.Font(family="Segoe UI", size=8,  weight="bold")
        self.f_cost_val= tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.f_label   = tkfont.Font(family="Segoe UI", size=9,  weight="bold")
        self.f_normal  = tkfont.Font(family="Segoe UI", size=9)
        self.f_btn     = tkfont.Font(family="Segoe UI", size=9,  weight="bold")
        self.f_id      = tkfont.Font(family="Segoe UI", size=8)
        self.f_estado  = tkfont.Font(family="Segoe UI", size=13, weight="bold")

    # UI 
    def _build_ui(self):
        # Barra navegación superior
        self._build_navbar()

        # Contenido principal
        content = tk.Frame(self, bg=C_BG)
        content.pack(fill="both", expand=True, padx=24, pady=16)

        # Columna izquierda
        left = tk.Frame(content, bg=C_BG, width=220)
        left.pack(side="left", fill="y", padx=(0, 20))
        left.pack_propagate(False)
        self._build_left_panel(left)

        # Columna derecha
        right = tk.Frame(content, bg=C_BG)
        right.pack(side="left", fill="both", expand=True)
        self._build_right_panel(right)

    # NAVBAR 
    def _build_navbar(self):
        nav = tk.Frame(self, bg=C_WHITE, height=48)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        tabs = ["CAJA", "FACTURA\nELECTRÓNICA", "DEVOLUCIONES", "RECIBO\nPROVEEDORES"]
        for i, tab in enumerate(tabs):
            active = (tab == "RECIBO\nPROVEEDORES")
            fg = C_GREEN_DK if active else C_TEXT_LT
            underline_color = C_GREEN_MD if active else C_WHITE
            frame = tk.Frame(nav, bg=C_WHITE, cursor="hand2")
            frame.pack(side="left", padx=6)
            lbl = tk.Label(frame, text=tab, font=self.f_nav, bg=C_WHITE,
                           fg=fg, justify="center", pady=6)
            lbl.pack()
            # Subrayado activo
            if active:
                line = tk.Frame(frame, bg=C_GREEN_MD, height=3)
                line.pack(fill="x")

        # Usuario
        user_frame = tk.Frame(nav, bg=C_WHITE)
        user_frame.pack(side="right", padx=16)

        avatar = tk.Label(user_frame, text="👤", font=self.f_normal, bg=C_WHITE)
        avatar.pack(side="left")
        tk.Label(user_frame, text="Nicolas", font=self.f_normal,
                 bg=C_WHITE, fg=C_TEXT_DK).pack(side="left", padx=4)
        close_btn = tk.Label(user_frame, text="✕", font=self.f_btn,
                             bg=C_WHITE, fg=C_TEXT_MD, cursor="hand2", padx=6)
        close_btn.pack(side="left")
        close_btn.bind("<Button-1>", lambda e: self.destroy())

        # Línea separadora
        sep = tk.Frame(self, bg=C_BORDER, height=1)
        sep.pack(fill="x")

    #  PANEL IZQUIERDO 
    def _build_left_panel(self, parent):
        # Costo total
        cost_frame = tk.Frame(parent, bg=C_GREEN_MD, bd=0,
                              relief="flat", padx=16, pady=14)
        cost_frame.pack(fill="x", pady=(0, 20))
        tk.Label(cost_frame, text="COSTO TOTAL PEDIDO:", font=self.f_cost_lbl,
                 bg=C_GREEN_MD, fg="#D4EDDA").pack(anchor="w")
        self.lbl_total = tk.Label(cost_frame, text="$0", font=self.f_cost_val,
                                  bg=C_GREEN_MD, fg=C_WHITE)
        self.lbl_total.pack(anchor="w")

        # Filtros rápidos (solo Fecha)
        filter_box = tk.LabelFrame(parent, text="Filtros rápidos:", bg=C_WHITE,
                                   font=self.f_label, fg=C_TEXT_DK,
                                   bd=1, relief="solid", padx=12, pady=10)
        filter_box.pack(fill="x", pady=(0, 20))

        self.filter_fecha = ttk.Combobox(filter_box, font=self.f_normal,
            values=["Todos", "Hoy", "Mañana", "Esta semana", "Este mes"],
            state="readonly", width=16)
        self.filter_fecha.set("Todos")
        self.filter_fecha.pack(pady=4)
        self.filter_fecha.bind("<<ComboboxSelected>>", self._on_filter_change)

        btn_clear = tk.Button(filter_box, text="↺ Limpiar filtro",
                              font=self.f_normal, bg=C_WHITE, fg=C_GREEN_MD,
                              bd=1, relief="solid", cursor="hand2",
                              command=self._clear_filters)
        btn_clear.pack(fill="x", pady=(6, 0))

        # Estado
        estado_box = tk.Frame(parent, bg=C_GREEN_LT, bd=1,
                              relief="solid", padx=14, pady=12)
        estado_box.pack(fill="x", pady=(0, 20))
        tk.Label(estado_box, text="ESTADO:", font=self.f_cost_lbl,
                 bg=C_GREEN_LT, fg=C_GREEN_DK).pack(anchor="w")
        self.lbl_estado = tk.Label(estado_box, text="—", font=self.f_estado,
                                   bg=C_GREEN_LT, fg=C_GREEN_DK)
        self.lbl_estado.pack(anchor="w")

        # Botón cargar inventario
        btn_inv = tk.Button(parent, text="⬆  CARGAR INVENTARIO",
                            font=self.f_btn, bg=C_GREEN_DK, fg=C_WHITE,
                            activebackground=C_GREEN_MD, bd=0, relief="flat",
                            cursor="hand2", pady=12,
                            command=self._cargar_inventario)
        btn_inv.pack(fill="x")

    # PANEL DERECHO 
    def _build_right_panel(self, parent):
        # Encabezado
        header = tk.Frame(parent, bg=C_BG)
        header.pack(fill="x", pady=(0, 12))

        tk.Label(header, text="RECIBO PROVEEDORES", font=self.f_title,
                 bg=C_BG, fg=C_GREEN_DK).pack(side="left")

        id_frame = tk.Frame(header, bg=C_BG)
        id_frame.pack(side="right")
        tk.Label(id_frame, text="ID OPERACIÓN", font=self.f_id,
                 bg=C_BG, fg=C_TEXT_LT).pack(anchor="e")
        self.lbl_id_op = tk.Label(id_frame, text="#0000-0000",
                                  font=tkfont.Font(family="Segoe UI", size=11, weight="bold"),
                                  bg=C_BG, fg=C_TEXT_DK)
        self.lbl_id_op.pack(anchor="e")

        # Tabla
        self._build_table(parent)

        # Área inferior: observaciones + nota + botones CRUD
        bottom = tk.Frame(parent, bg=C_BG)
        bottom.pack(fill="x", pady=(16, 0))

        # Observaciones
        self.cmb_obs = ttk.Combobox(bottom, font=self.f_normal,
            values=["Observaciones de entrega...",
                    "Llegada esperada tarde",
                    "Empaque estándar",
                    "Calidad premium",
                    "Pedido urgente",
                    "Verificar temperatura",
                    "Sin novedad"],
            width=36)
        self.cmb_obs.set("Observaciones de entrega...")
        self.cmb_obs.pack(side="left", padx=(0, 8))

        # Nota de recibo
        self.txt_nota = tk.Text(bottom, font=self.f_normal, height=2,
                                width=36, bd=1, relief="solid",
                                fg=C_TEXT_LT, bg=C_WHITE)
        self.txt_nota.insert("1.0", "Añadir nota de recibo...")
        self.txt_nota.bind("<FocusIn>",  self._clear_nota_placeholder)
        self.txt_nota.bind("<FocusOut>", self._set_nota_placeholder)
        self.txt_nota.pack(side="left", padx=(0, 8))

        # Botones CRUD
        crud = tk.Frame(bottom, bg=C_BG)
        crud.pack(side="right")
        btns = [
            ("AGREGAR",   C_GREEN_DK, C_WHITE,  self._agregar),
            ("ELIMINAR",  C_WHITE,    C_RED,     self._eliminar),
            ("MODIFICAR", C_WHITE,    C_TEXT_DK, self._modificar),
            ("BUSCAR",    C_WHITE,    C_TEXT_DK, self._buscar),
        ]
        for txt, bg, fg, cmd in btns:
            b = tk.Button(crud, text=txt, font=self.f_btn, bg=bg, fg=fg,
                          bd=1, relief="solid", cursor="hand2",
                          padx=14, pady=6, command=cmd)
            b.pack(side="left", padx=3)

    # TABLA 
    def _build_table(self, parent):
        cols = ("id", "proveedor", "producto", "estado", "fecha")
        labels = ("ID", "PROVEEDOR", "PRODUCTO", "ESTADO", "FECHA")
        widths = (60, 200, 200, 130, 110)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("PALMA.Treeview",
                        background=C_WHITE, fieldbackground=C_WHITE,
                        foreground=C_TEXT_DK, rowheight=36,
                        font=("Segoe UI", 9))
        style.configure("PALMA.Treeview.Heading",
                        background=C_BG, foreground=C_TEXT_LT,
                        font=("Segoe UI", 8, "bold"), relief="flat")
        style.map("PALMA.Treeview",
                  background=[("selected", C_GREEN_LT)],
                  foreground=[("selected", C_GREEN_DK)])

        frame = tk.Frame(parent, bg=C_BORDER, bd=1, relief="solid")
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(frame, columns=cols, show="headings",
                                 style="PALMA.Treeview", selectmode="browse")
        for col, lbl, w in zip(cols, labels, widths):
            self.tree.heading(col, text=lbl)
            self.tree.column(col, width=w, minwidth=w, anchor="w")

        scroll_y = ttk.Scrollbar(frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        scroll_y.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)
        self.tree.bind("<Double-1>", lambda e: self._modificar())

    
    #  DATOS
    def _get_filter_dates(self):
        hoy = date.today()
        f = self.filter_fecha.get()
        if f == "Hoy":
            return str(hoy), str(hoy)
        elif f == "Mañana":
            m = hoy + timedelta(days=1)
            return str(m), str(m)
        elif f == "Esta semana":
            lunes = hoy - timedelta(days=hoy.weekday())
            domingo = lunes + timedelta(days=6)
            return str(lunes), str(domingo)
        elif f == "Este mes":
            ini = hoy.replace(day=1)
            fin = (ini.replace(month=ini.month % 12 + 1, day=1)
                   - timedelta(days=1)) if ini.month < 12 else ini.replace(day=31)
            return str(ini), str(fin)
        return None, None

    def refresh_table(self, search_term=None):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT rp.id, p.nombre, rp.producto, rp.estado, rp.fecha,
                   rp.costo_total
            FROM recibo_proveedores rp
            JOIN proveedores p ON p.id = rp.id_proveedor
            WHERE 1=1
        """
        params = []

        fecha_ini, fecha_fin = self._get_filter_dates()
        if fecha_ini:
            query += " AND rp.fecha BETWEEN ? AND ?"
            params += [fecha_ini, fecha_fin]

        if search_term:
            query += " AND (p.nombre LIKE ? OR rp.producto LIKE ?)"
            params += [f"%{search_term}%", f"%{search_term}%"]

        query += " ORDER BY rp.fecha DESC, rp.id DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        hoy = str(date.today())
        manana = str(date.today() + timedelta(days=1))
    
        # (manejado por style.map en _build_table).
        tag_colors = {
            "Pendiente": (C_WHITE, C_TEXT_DK),
            "En camino": (C_WHITE, C_TEXT_DK),
            "Recibido":  (C_WHITE, C_TEXT_DK),
        }

        for row in rows:
            rid, prov, prod, estado, fecha, _ = row
            # Formatear fecha
            try:
                y, m, d = fecha.split("-")
                meses = ["","Ene","Feb","Mar","Abr","May","Jun",
                         "Jul","Ago","Sep","Oct","Nov","Dic"]
                fecha_fmt = f"{d}/{meses[int(m)]}/{y}"
            except Exception:
                fecha_fmt = fecha

            icon = {"Pendiente": "⚠ ", "En camino": "🚚 ",
                    "Recibido": "✓ "}.get(estado, "")
            estado_txt = icon + estado

            tag = estado.replace(" ", "_")
            self.tree.insert("", "end",
                             values=(rid, prov, prod, estado_txt, fecha_fmt),
                             iid=str(rid), tags=(tag,))

        for estado, (bg, fg) in tag_colors.items():
            self.tree.tag_configure(estado.replace(" ", "_"),
                                    background=bg, foreground=fg)

        # Placeholder si está vacío
        if not rows:
            self.tree.insert("", "end",
                             values=("—", "Sin resultados", "", "", ""),
                             tags=("empty",))
            self.tree.tag_configure("empty", foreground=C_TEXT_LT)

    def _format_money(self, total):
        """Formatea un valor numérico como moneda colombiana ($1.234.567)."""
        return f"${total:,.0f}".replace(",", ".")

    def update_total(self):
        conn = get_connection()
        cur = conn.cursor()

        # Solo se suman los pedidos en estado "Pendiente" o "En camino".
        # Los pedidos "Recibido" (ya entregados/cargados al inventario)
        # no deben contar dentro del costo total del pedido.
        query = """
            SELECT COALESCE(SUM(rp.costo_total), 0)
            FROM recibo_proveedores rp
            WHERE rp.estado != 'Recibido'
        """
        params = []
        fecha_ini, fecha_fin = self._get_filter_dates()
        if fecha_ini:
            query += " AND rp.fecha BETWEEN ? AND ?"
            params += [fecha_ini, fecha_fin]

        cur.execute(query, params)
        total = cur.fetchone()[0]
        conn.close()

        self.lbl_total.config(text=self._format_money(total))

        # ID operación: mayor id
        conn2 = get_connection()
        cur2 = conn2.cursor()
        cur2.execute("SELECT MAX(id) FROM recibo_proveedores")
        max_id = cur2.fetchone()[0] or 0
        conn2.close()
        yr = date.today().year
        self.lbl_id_op.config(text=f"#{max_id:04d}-{yr}")

    # Selección de fila 
    def _on_row_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        rid = sel[0]
        try:
            rid = int(rid)
        except ValueError:
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT rp.estado, rp.observaciones, rp.nota_recibo, rp.costo_total
            FROM recibo_proveedores rp WHERE rp.id = ?
        """, (rid,))
        row = cur.fetchone()
        conn.close()
        if row:
            self.lbl_estado.config(text=row["estado"])
            self.cmb_obs.set(row["observaciones"] or "Observaciones de entrega...")
            self._set_nota_text(row["nota_recibo"] or "")
            # Al seleccionar una factura se muestra únicamente su costo,
            # no la suma de todos los pedidos.
            self.lbl_total.config(text=self._format_money(row["costo_total"]))

    def _set_nota_text(self, text):
        self.txt_nota.delete("1.0", "end")
        if text:
            self.txt_nota.config(fg=C_TEXT_DK)
            self.txt_nota.insert("1.0", text)
        else:
            self.txt_nota.config(fg=C_TEXT_LT)
            self.txt_nota.insert("1.0", "Añadir nota de recibo...")

    def _clear_nota_placeholder(self, e):
        if self.txt_nota.get("1.0", "end-1c") == "Añadir nota de recibo...":
            self.txt_nota.delete("1.0", "end")
            self.txt_nota.config(fg=C_TEXT_DK)

    def _set_nota_placeholder(self, e):
        if not self.txt_nota.get("1.0", "end-1c").strip():
            self.txt_nota.config(fg=C_TEXT_LT)
            self.txt_nota.insert("1.0", "Añadir nota de recibo...")

    # Filtros 
    def _on_filter_change(self, event=None):
        self.refresh_table()
        self.update_total()

    def _clear_filters(self):
        self.filter_fecha.set("Todos")
        self.refresh_table()
        self.update_total()

    #  Cargar inventario 
    def _cargar_inventario(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un recibo para cargar al inventario.")
            return
        rid = sel[0]
        try:
            rid = int(rid)
        except ValueError:
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT estado FROM recibo_proveedores WHERE id=?", (rid,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return
        if row["estado"] == "Recibido":
            messagebox.showinfo("Info", "Este recibo ya fue cargado al inventario.")
            conn.close()
            return

        nota = self.txt_nota.get("1.0", "end-1c").strip()
        if nota == "Añadir nota de recibo...":
            nota = ""
        obs = self.cmb_obs.get()
        if obs == "Observaciones de entrega...":
            obs = ""

        cur.execute("""
            UPDATE recibo_proveedores
            SET estado='Recibido', nota_recibo=?, observaciones=?
            WHERE id=?
        """, (nota, obs, rid))
        conn.commit()
        conn.close()
        messagebox.showinfo("✓ Inventario", "Recibo cargado al inventario exitosamente.")
        self.refresh_table()
        self.update_total()

    #  CRUD
    
    def _agregar(self):
        FormDialog(self, titulo="Agregar Recibo", modo="agregar")

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un recibo para eliminar.")
            return
        rid = sel[0]
        try:
            rid = int(rid)
        except ValueError:
            return
        if not messagebox.askyesno("Eliminar", f"¿Eliminar recibo #{rid}?"):
            return
        conn = get_connection()
        conn.execute("DELETE FROM recibo_proveedores WHERE id=?", (rid,))
        conn.commit()
        conn.close()
        self.refresh_table()
        self.update_total()
        self.lbl_estado.config(text="—")

    def _modificar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un recibo para modificar.")
            return
        rid = sel[0]
        try:
            rid = int(rid)
        except ValueError:
            return
        FormDialog(self, titulo="Modificar Recibo", modo="modificar", recibo_id=rid)

    def _buscar(self):
        BuscarDialog(self)


#  DIÁLOGO FORMULARIO (Agregar / Modificar)
class FormDialog(tk.Toplevel):
    def __init__(self, master, titulo, modo, recibo_id=None):
        super().__init__(master)
        self.master_app = master
        self.modo = modo
        self.recibo_id = recibo_id
        self.title(titulo)
        self.configure(bg=C_WHITE)
        self.geometry("500x580")
        self.resizable(False, False)
        self.grab_set()
        self.transient(master)

        # Centrar
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width()  - 500) // 2
        y = master.winfo_y() + (master.winfo_height() - 580) // 2
        self.geometry(f"+{x}+{y}")

        self._load_proveedores()
        self._build_form()
        if modo == "modificar" and recibo_id:
            self._cargar_datos(recibo_id)

    def _load_proveedores(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre FROM proveedores WHERE activo=1 ORDER BY nombre")
        self.proveedores = cur.fetchall()
        conn.close()
        self.prov_names = [f"{p['id']} – {p['nombre']}" for p in self.proveedores]
        self.prov_ids   = [p["id"] for p in self.proveedores]

    def _build_form(self):
        tk.Label(self, text=self.title(), font=tkfont.Font(family="Segoe UI", size=14, weight="bold"),
                 bg=C_WHITE, fg=C_GREEN_DK).pack(pady=(20, 16))

        form = tk.Frame(self, bg=C_WHITE, padx=32)
        form.pack(fill="both", expand=True)

        fields = [
            ("Proveedor:",         "cmb_prov"),
            ("Producto:",          "ent_prod"),
            ("Cantidad:",          "ent_cant"),
            ("Costo unitario ($):","ent_cu"),
            ("Estado:",            "cmb_estado"),
            ("Observaciones:",     "cmb_obs"),
            ("Fecha (AAAA-MM-DD):","ent_fecha"),
        ]

        f_lbl = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        f_ent = tkfont.Font(family="Segoe UI", size=9)

        self.widgets = {}
        for lbl_txt, attr in fields:
            row = tk.Frame(form, bg=C_WHITE)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=lbl_txt, font=f_lbl, bg=C_WHITE,
                     fg=C_TEXT_DK, width=20, anchor="w").pack(side="left")

            if attr == "cmb_prov":
                w = ttk.Combobox(row, values=self.prov_names,
                                 font=f_ent, state="readonly", width=28)
                if self.prov_names:
                    w.current(0)
            elif attr == "cmb_estado":
                w = ttk.Combobox(row, values=["Pendiente", "En camino", "Recibido"],
                                 font=f_ent, state="readonly", width=28)
                w.current(0)
            elif attr == "cmb_obs":
                w = ttk.Combobox(row, font=f_ent, width=28,
                    values=["", "Llegada esperada tarde", "Empaque estándar",
                            "Calidad premium", "Pedido urgente",
                            "Verificar temperatura", "Sin novedad"])
            else:
                w = tk.Entry(row, font=f_ent, bd=1, relief="solid", width=30)
                if attr == "ent_fecha":
                    w.insert(0, str(date.today()))
                    vcmd = self.register(_validar_fecha_chars)
                    w.config(validate="key", validatecommand=(vcmd, "%P"))
                elif attr == "ent_cant":
                    # Permite números y, opcionalmente, una unidad válida (kg, lb, etc.)
                    vcmd = self.register(_validar_cantidad)
                    w.config(validate="key", validatecommand=(vcmd, "%P"))
                elif attr == "ent_cu":
                    # Solo números y un separador decimal
                    vcmd = self.register(_validar_decimal)
                    w.config(validate="key", validatecommand=(vcmd, "%P"))

            w.pack(side="left")
            self.widgets[attr] = w

        # Nota
        nota_row = tk.Frame(form, bg=C_WHITE)
        nota_row.pack(fill="x", pady=5)
        tk.Label(nota_row, text="Nota de recibo:", font=f_lbl, bg=C_WHITE,
                 fg=C_TEXT_DK, width=20, anchor="w").pack(side="left")
        self.txt_nota = tk.Text(nota_row, font=f_ent, height=3, width=30,
                                bd=1, relief="solid")
        self.txt_nota.pack(side="left")

        # Botones
        btn_frame = tk.Frame(self, bg=C_WHITE, pady=16)
        btn_frame.pack()
        tk.Button(btn_frame, text="Guardar", font=f_lbl,
                  bg=C_GREEN_DK, fg=C_WHITE, bd=0, padx=20, pady=8,
                  cursor="hand2", command=self._guardar).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Cancelar", font=f_lbl,
                  bg=C_WHITE, fg=C_TEXT_DK, bd=1, relief="solid",
                  padx=20, pady=8, cursor="hand2",
                  command=self.destroy).pack(side="left", padx=8)

    def _cargar_datos(self, rid):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM recibo_proveedores WHERE id=?", (rid,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return

        # Proveedor
        try:
            idx = self.prov_ids.index(row["id_proveedor"])
            self.widgets["cmb_prov"].current(idx)
        except ValueError:
            pass

        self.widgets["ent_prod"].insert(0, row["producto"])
        self.widgets["ent_cant"].insert(0, str(row["cantidad"]))
        self.widgets["ent_cu"].insert(0, str(row["costo_unitario"]))
        self.widgets["cmb_estado"].set(row["estado"])
        self.widgets["cmb_obs"].set(row["observaciones"] or "")
        self.widgets["ent_fecha"].delete(0, "end")
        self.widgets["ent_fecha"].insert(0, row["fecha"])
        self.txt_nota.insert("1.0", row["nota_recibo"] or "")

    def _guardar(self):
        # Validar
        prov_idx = self.widgets["cmb_prov"].current()
        if prov_idx < 0:
            messagebox.showwarning("Validación", "Selecciona un proveedor.", parent=self)
            return
        id_prov = self.prov_ids[prov_idx]
        prod    = self.widgets["ent_prod"].get().strip()
        cant_s  = self.widgets["ent_cant"].get().strip()
        cu_s    = self.widgets["ent_cu"].get().strip()
        estado  = self.widgets["cmb_estado"].get()
        obs     = self.widgets["cmb_obs"].get()
        fecha   = self.widgets["ent_fecha"].get().strip()
        nota    = self.txt_nota.get("1.0", "end-1c").strip()

        if not prod:
            messagebox.showwarning("Validación", "El producto no puede estar vacío.", parent=self)
            return

        # Separar la parte numérica de la unidad en "Cantidad" (p. ej. "100kg")
        i = 0
        while i < len(cant_s) and (cant_s[i].isdigit() or cant_s[i] == "."):
            i += 1
        cant_num_s = cant_s[:i]
        unidad     = cant_s[i:].strip().lower()
        if unidad and unidad not in UNIDADES_VALIDAS:
            messagebox.showwarning(
                "Validación",
                f"Unidad '{unidad}' no es válida. Usa: {', '.join(UNIDADES_VALIDAS)}.",
                parent=self)
            return

        try:
            cant = int(float(cant_num_s)) if cant_num_s else 0
            cu   = float(cu_s.replace(",", ".")) if cu_s else 0.0
        except ValueError:
            messagebox.showwarning("Validación", "Cantidad y costo deben ser numéricos.", parent=self)
            return
        total = cant * cu

        conn = get_connection()
        try:
            if self.modo == "agregar":
                conn.execute("""
                    INSERT INTO recibo_proveedores
                    (id_proveedor, producto, cantidad, costo_unitario, costo_total,
                     estado, observaciones, nota_recibo, fecha)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (id_prov, prod, cant, cu, total, estado, obs, nota, fecha))
            else:
                conn.execute("""
                    UPDATE recibo_proveedores
                    SET id_proveedor=?, producto=?, cantidad=?, costo_unitario=?,
                        costo_total=?, estado=?, observaciones=?, nota_recibo=?, fecha=?
                    WHERE id=?
                """, (id_prov, prod, cant, cu, total, estado, obs, nota, fecha,
                      self.recibo_id))
            conn.commit()
        except Exception as e:
            messagebox.showerror("Error BD", str(e), parent=self)
            conn.close()
            return
        conn.close()

        self.master_app.refresh_table()
        self.master_app.update_total()
        self.destroy()


#  DIÁLOGO BUSCAR
class BuscarDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master_app = master
        self.title("Buscar Recibo")
        self.configure(bg=C_WHITE)
        self.geometry("360x160")
        self.resizable(False, False)
        self.grab_set()
        self.transient(master)

        x = master.winfo_x() + (master.winfo_width()  - 360) // 2
        y = master.winfo_y() + (master.winfo_height() - 160) // 2
        self.geometry(f"+{x}+{y}")

        f = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        fe = tkfont.Font(family="Segoe UI", size=9)

        tk.Label(self, text="Buscar por proveedor o producto:",
                 font=f, bg=C_WHITE, fg=C_TEXT_DK).pack(pady=(20, 8))

        self.ent = tk.Entry(self, font=fe, bd=1, relief="solid", width=36)
        self.ent.pack()
        self.ent.focus()
        self.ent.bind("<Return>", self._buscar)

        btn_f = tk.Frame(self, bg=C_WHITE, pady=12)
        btn_f.pack()
        tk.Button(btn_f, text="Buscar", font=f, bg=C_GREEN_DK, fg=C_WHITE,
                  bd=0, padx=16, pady=7, cursor="hand2",
                  command=self._buscar).pack(side="left", padx=6)
        tk.Button(btn_f, text="Cancelar", font=f, bg=C_WHITE, fg=C_TEXT_DK,
                  bd=1, relief="solid", padx=16, pady=7, cursor="hand2",
                  command=self.destroy).pack(side="left", padx=6)

    def _buscar(self, event=None):
        term = self.ent.get().strip()
        self.master_app.refresh_table(search_term=term if term else None)
        self.destroy()

#  MAIN
if __name__ == "__main__":
    init_db()
    app = PALMAApp()
    app.mainloop()