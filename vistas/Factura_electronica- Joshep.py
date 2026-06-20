# Facturación Electrónica - PALMA Software S.A.S
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from datetime import datetime
from reportlab.pdfgen import canvas
from pathlib import Path

# BASE DE DATOS 
def conectar_db():
    conn = sqlite3.connect("facturas.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id_factura     TEXT PRIMARY KEY,
            id_cliente     TEXT NOT NULL,
            fecha          TEXT NOT NULL,
            nombre_cliente TEXT NOT NULL,
            monto_cli      REAL NOT NULL DEFAULT 0,
            monto_emp      REAL NOT NULL DEFAULT 0,
            nit_empresa    TEXT          DEFAULT '',
            pdf            TEXT          DEFAULT 'Descargar'
        )
    """)
    # Migración segura por si la base de datos ya existía con otras estructuras
    for col, tipo in [("monto_emp",   "REAL DEFAULT 0"),
                      ("nit_empresa", "TEXT DEFAULT ''"),
                      ("monto_cli",   "REAL DEFAULT 0"),
                      ("total",       "REAL DEFAULT 0")]:
        try:
            cursor.execute(f"ALTER TABLE facturas ADD COLUMN {col} {tipo}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()

def generar_id_factura(nit_emp, razon, fecha_hora):
    semilla = f"{nit_emp}{razon}{fecha_hora}".encode()
    return "FAC-" + hashlib.sha256(semilla).hexdigest()[:8].upper()

def generar_id_cliente(num_id, nombre, correo, ciudad):
    semilla = f"{num_id}{nombre}{correo}{ciudad}".encode()
    return "CLI-" + hashlib.sha256(semilla).hexdigest()[:8].upper()

#Listas de configuración y Mock Data
LISTA_CIUDADES    = ["Bogotá D.C.", "Medellín", "Cali", "Barranquilla", "Cartagena",
                     "Bucaramanga", "Cúcuta", "Pereira", "Santa Marta", "Ibagué",
                     "Pastos", "Manizales", "Neiva", "Villavicencio", "Tunja", "Armenia"]
LISTA_TIPOS_ID    = ["Cédula de Ciudadanía (CC)", "NIT (Número de Identificación Tributaria)",
                     "Cédula de Extranjería (CE)", "Pasaporte", "Tarjeta de Identidad (TI)"]
LISTA_REGIMEN     = ["Responsable de IVA (Régimen Común)",
                     "No Responsable de IVA (Régimen Simplificado)",
                     "Régimen Simple de Tributación (RST)", "Gran Contribuyente"]
LISTA_RESP_FISCAL = ["O-13 Gran Contribuyente", "O-15 Autorretenedor",
                     "O-23 Agente de retención IVA", "O-47 Régimen Simple",
                     "R-99-PN No Responsable"]

DATOS_EMPRESAS = {
    "900.123.456-1": {"razon": "PALMA Software S.A.S",
                      "regimen": "Régimen Simple de Tributación (RST)",
                      "dir": "Cl 45 #12-34", "ciudad": "Bogotá D.C.",
                      "resol": "Res. 120000345"}
}
DATOS_CLIENTES = {
    "1.015.456.789": {"nombre": "Juan Carlos Pérez",
                      "tipo":   "Cédula de Ciudadanía (CC)",
                      "correo": "juan.perez@mail.com",
                      "ciudad": "Bogotá D.C.",
                      "resp":   "R-99-PN No Responsable"}
}

# HELPERS DE CAMPO CON GRID ─────────────────────────────────────────────────
def campo_en_fila(master, label_text, fila, is_combo=False, values=None):
    """Crea label + widget en dos subfilas de `master` usando grid."""
    tk.Label(master, text=label_text, font=("Arial", 9, "bold"),
             fg="#555555", bg="white").grid(row=fila*2, column=0,
             sticky="w", padx=10, pady=(4, 0))
    if is_combo:
        w = ttk.Combobox(master, values=values, font=("Arial", 11), state="readonly")
    else:
        w = tk.Entry(master, bg="#DCECE0", fg="#333333",
                     font=("Arial", 11), relief="flat", bd=0)
    w.grid(row=fila*2+1, column=0, sticky="ew", padx=10, pady=(0, 2), ipady=3)
    return w

def campo_monto_en_fila(master, label_text, fila):
    """Campo de monto diferenciado en grid."""
    tk.Label(master, text=label_text, font=("Arial", 9, "bold"),
             fg="#555555", bg="white").grid(row=fila*2, column=0,
             sticky="w", padx=10, pady=(4, 0))
    w = tk.Entry(master, bg="#DCECE0", fg="#333333",
                 font=("Arial", 11), relief="flat", bd=0)
    w.insert(0, "0")
    w.grid(row=fila*2+1, column=0, sticky="ew", padx=10, pady=(0, 2), ipady=3)
    return w

#INTERFAZ GRÁFICA PRINCIPAL 
class FacturaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PALMA Software - Facturación Electrónica")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#EBEBEB")

        conectar_db()
        self.crear_interfaz_superior()
        self.contenedor_principal = tk.Frame(self.root, bg="white", bd=0)
        self.contenedor_principal.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self.mostrar_vista_generar()

    #Validación
    def filtrar_solo_numeros(self, widget):
        """Bloquea cualquier carácter que no sea número o guion/punto."""
        texto = "".join(c for c in widget.get() if c.isdigit() or c in ".-")
        if widget.get() != texto:
            widget.delete(0, tk.END)
            widget.insert(0, texto)

    def filtrar_monto(self, widget):
        texto = widget.get()
        resultado = "".join(c for c in texto if c.isdigit() or c in ".")
        if texto != resultado:
            pos = widget.index(tk.INSERT)
            widget.delete(0, tk.END)
            widget.insert(0, resultado)
            widget.icursor(min(pos, len(resultado)))

    def leer_monto(self, widget):
        try:
            return float(widget.get().strip() or "0")
        except ValueError:
            return 0

    #Barra superior 
    def crear_interfaz_superior(self):
        frame_busqueda = tk.Frame(self.root, bg="#EBEBEB")
        frame_busqueda.pack(fill="x", padx=20, pady=10)
        self.entry_buscar = tk.Entry(frame_busqueda, font=("Arial", 12), fg="#A0A0A0")
        self.entry_buscar.insert(0, "Buscar por número de factura, nombre de cliente...")
        self.entry_buscar.bind("<FocusIn>",
            lambda e: self.entry_buscar.delete(0, tk.END)
            if self.entry_buscar.get().startswith("Buscar") else None)
        self.entry_buscar.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        tk.Button(frame_busqueda, text="BUSCAR", bg="#008F39", fg="white",
                  font=("Arial", 11, "bold"), width=15,
                  command=self.buscar_factura).pack(side="left", ipady=5)
        tk.Button(frame_busqueda, text="X", bg="white", fg="darkgreen",
                  font=("Arial", 11, "bold"), width=3,
                  command=self.mostrar_vista_generar).pack(side="left", padx=5, ipady=5)

        frame_filtros = tk.Frame(self.root, bg="#EBEBEB")
        frame_filtros.pack(fill="x", padx=20, pady=5)
        tk.Button(frame_filtros, text="Más recientes", bg="white", fg="#A0A0A0",
                  relief="flat", width=15,
                  command=lambda: self.mostrar_vista_historial(orden="DESC")).pack(side="left", padx=5, ipady=5)
        tk.Button(frame_filtros, text="Más Antiguas", bg="white", fg="#A0A0A0",
                  relief="flat", width=15,
                  command=lambda: self.mostrar_vista_historial(orden="ASC")).pack(side="left", padx=5, ipady=5)
        tk.Button(frame_filtros, text="Filtrar por fecha", bg="white", fg="#A0A0A0",
                  relief="flat", width=15,
                  command=self.filtrar_por_fecha_input).pack(side="left", padx=5, ipady=5)

    def limpiar_contenedor(self):
        for w in self.contenedor_principal.winfo_children():
            w.destroy()

    #Formulario principal 
    def mostrar_vista_generar(self):
        self.limpiar_contenedor()
        self.contenedor_principal.columnconfigure(0, weight=1)
        self.contenedor_principal.columnconfigure(1, weight=1)
        self.contenedor_principal.rowconfigure(0, weight=1)

        #Panel De EMPRESA 
        f_emp = tk.Frame(self.contenedor_principal, bg="white", padx=20)
        f_emp.grid(row=0, column=0, sticky="nsew")
        f_emp.columnconfigure(0, weight=1)

        for r in range(20):
            f_emp.rowconfigure(r, weight=1)

        tk.Label(f_emp, text="EMPRESA", font=("Arial", 16, "bold"),
                 fg="#008F39", bg="white").grid(row=0, column=0, pady=(8, 4))

        self.ent_razon_emp    = campo_en_fila(f_emp, "Razón social",           1)
        self.ent_nit_emp      = campo_en_fila(f_emp, "NIT",                    2)
        self.ent_nit_emp.bind("<KeyRelease>",
            lambda e: [self.filtrar_solo_numeros(self.ent_nit_emp),
                       self.autocompletar_empresa(e)])
        self.combo_regimen    = campo_en_fila(f_emp, "Régimen Contable",       3, True, LISTA_REGIMEN)
        self.ent_dir          = campo_en_fila(f_emp, "Dirección",              4)
        self.combo_ciudad_emp = campo_en_fila(f_emp, "Ciudad",                 5, True, LISTA_CIUDADES)
        self.ent_resol        = campo_en_fila(f_emp, "Resolución de facturación", 6)
        
        #Monto único e independiente para Empresa
        self.ent_monto_emp    = campo_monto_en_fila(f_emp, "Monto específico Empresa", 7)
        self.ent_monto_emp.bind("<KeyRelease>", lambda e: self.filtrar_monto(self.ent_monto_emp))
        self.ent_monto_emp.bind("<Control-v>",  lambda e: self.filtrar_monto(self.ent_monto_emp))

        tk.Button(f_emp, text="GENERAR", bg="#137E36", fg="white",
                  font=("Arial", 12, "bold"), width=20,
                  command=self.guardar_factura).grid(row=16, column=0, pady=10, ipady=4)

        # ── Panel CLIENTE ──────────────────────────────────────────────────────
        f_cli = tk.Frame(self.contenedor_principal, bg="white", padx=20)
        f_cli.grid(row=0, column=1, sticky="nsew")
        f_cli.columnconfigure(0, weight=1)

        for r in range(20):
            f_cli.rowconfigure(r, weight=1)

        tk.Label(f_cli, text="CLIENTE", font=("Arial", 16, "bold"),
                 fg="#008F39", bg="white").grid(row=0, column=0, pady=(8, 4))

        self.ent_nom_cli       = campo_en_fila(f_cli, "Nombre o Razón social",     1)
        self.combo_tipo_id     = campo_en_fila(f_cli, "Tipo de identificación",    2, True, LISTA_TIPOS_ID)
        self.ent_id_cli        = campo_en_fila(f_cli, "Número de identificación",  3)
        self.ent_id_cli.bind("<KeyRelease>",
            lambda e: [self.filtrar_solo_numeros(self.ent_id_cli),
                       self.autocompletar_cliente(e)])
        self.ent_correo        = campo_en_fila(f_cli, "Correo electrónico",        4)
        self.combo_ciudad_cli  = campo_en_fila(f_cli, "Ciudad",                    5, True, LISTA_CIUDADES)
        self.combo_resp_fiscal = campo_en_fila(f_cli, "Responsabilidad fiscal",    6, True, LISTA_RESP_FISCAL)
        
        #Monto único e independiente para El Cliente
        self.ent_monto_cli     = campo_monto_en_fila(f_cli, "Monto específico Cliente", 7)
        self.ent_monto_cli.bind("<KeyRelease>", lambda e: self.filtrar_monto(self.ent_monto_cli))
        self.ent_monto_cli.bind("<Control-v>",  lambda e: self.filtrar_monto(self.ent_monto_cli))

        tk.Button(f_cli, text="GENERAR", bg="#137E36", fg="white",
                  font=("Arial", 12, "bold"), width=20,
                  command=self.guardar_factura).grid(row=16, column=0, pady=10, ipady=4)

    #Autocompletado  
    def autocompletar_empresa(self, event):
        nit = self.ent_nit_emp.get().strip()
        if nit in DATOS_EMPRESAS:
            info = DATOS_EMPRESAS[nit]
            self.ent_razon_emp.delete(0, tk.END);  self.ent_razon_emp.insert(0, info["razon"])
            self.combo_regimen.set(info["regimen"])
            self.ent_dir.delete(0, tk.END);        self.ent_dir.insert(0, info["dir"])
            self.combo_ciudad_emp.set(info["ciudad"])
            self.ent_resol.delete(0, tk.END);      self.ent_resol.insert(0, info["resol"])

    def autocompletar_cliente(self, event):
        doc = self.ent_id_cli.get().strip()
        if doc in DATOS_CLIENTES:
            info = DATOS_CLIENTES[doc]
            self.ent_nom_cli.delete(0, tk.END);  self.ent_nom_cli.insert(0, info["nombre"])
            self.combo_tipo_id.set(info["tipo"])
            self.ent_correo.delete(0, tk.END);   self.ent_correo.insert(0, info["correo"])
            self.combo_ciudad_cli.set(info["ciudad"])
            self.combo_resp_fiscal.set(info["resp"])

    #Guardar 
    def guardar_factura(self):
        nit_emp = self.ent_nit_emp.get().strip()
        razon   = self.ent_razon_emp.get().strip()
        id_num  = self.ent_id_cli.get().strip()
        nombre  = self.ent_nom_cli.get().strip()
        correo  = self.ent_correo.get().strip()
        ciudad  = self.combo_ciudad_cli.get().strip()

        monto_emp  = self.leer_monto(self.ent_monto_emp)
        monto_cli  = self.leer_monto(self.ent_monto_cli)
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fecha_solo = fecha_hora[:10]

        id_factura = generar_id_factura(nit_emp, razon, fecha_hora)
        id_cliente = generar_id_cliente(id_num, nombre, correo, ciudad)

        conn = sqlite3.connect("facturas.db")
        cursor = conn.cursor()
        while True:
            try:
                cursor.execute(
                    "INSERT INTO facturas "
                    "(id_factura, id_cliente, fecha, nombre_cliente, "
                    "monto_cli, monto_emp, nit_empresa) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (id_factura, id_cliente, fecha_solo, nombre,
                     monto_cli, monto_emp, nit_emp)
                )
                break
            except sqlite3.IntegrityError:
                id_factura = generar_id_factura(nit_emp, razon, fecha_hora + "x")
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Factura guardada correctamente.")
        self.mostrar_vista_historial()

    #Historial 
    def mostrar_vista_historial(self, datos_filtrados=None, orden="DESC"):
        self.limpiar_contenedor()

        tk.Button(self.contenedor_principal,
                  text="DESCARGAR PDF DE FACTURA SELECCIONADA",
                  bg="#008F39", fg="white", font=("Arial", 11, "bold"),
                  command=self.generar_pdf).pack(side="bottom", pady=15, ipady=6)

        columnas = ("id_factura", "id_cliente", "nit_empresa", "fecha",
                    "nombre_cliente", "monto_emp", "monto_cli", "total", "pdf")
        self.tabla = ttk.Treeview(self.contenedor_principal, columns=columnas, show="headings")

        self.tabla.heading("id_factura",     text="ID FACTURA")
        self.tabla.heading("id_cliente",     text="ID CLIENTE")
        self.tabla.heading("nit_empresa",    text="NIT EMPRESA")
        self.tabla.heading("fecha",          text="FECHA")
        self.tabla.heading("nombre_cliente", text="NOMBRE CLIENTE")
        self.tabla.heading("monto_emp",      text="MONTO EMPRESA")
        self.tabla.heading("monto_cli",      text="MONTO CLIENTE")
        self.tabla.heading("total",          text="TOTAL")
        self.tabla.heading("pdf",            text="PDF")

        self.tabla.column("id_factura",     width=110, anchor="center")
        self.tabla.column("id_cliente",     width=110, anchor="center")
        self.tabla.column("nit_empresa",    width=110, anchor="center")
        self.tabla.column("fecha",          width=90,  anchor="center")
        self.tabla.column("nombre_cliente", width=160, anchor="w")
        self.tabla.column("monto_emp",      width=110, anchor="e")
        self.tabla.column("monto_cli",      width=110, anchor="e")
        self.tabla.column("total",          width=90,  anchor="e")
        self.tabla.column("pdf",            width=70,  anchor="center")

        self.tabla.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        if datos_filtrados is not None:
            registros = datos_filtrados
        else:
            conn = sqlite3.connect("facturas.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_factura, id_cliente, nit_empresa, fecha, nombre_cliente, "
                "monto_emp, monto_cli, pdf "
                f"FROM facturas ORDER BY fecha {orden}"
            )
            registros = cursor.fetchall()
            conn.close()

        for reg in registros:
            m_emp = reg[5] if reg[5] is not None else 0
            m_cli = reg[6] if reg[6] is not None else 0
            nit   = reg[2] if reg[2] else "—"
            pdf   = reg[7] if len(reg) > 7 else "Descargar"
            total = m_emp + m_cli
            self.tabla.insert("", tk.END, values=(
                reg[0], reg[1], nit, reg[3], reg[4],
                f"${m_emp:,.2f}", f"${m_cli:,.2f}", f"${total:,.2f}", pdf
            ))

    #Filtrar por fecha 
    def filtrar_por_fecha_input(self):
        criterio = self.entry_buscar.get()
        if "Buscar" in criterio or criterio == "":
            messagebox.showwarning("Atención",
                "Escribe una fecha en la barra superior (ej: 2026-05) "
                "y presiona Filtrar por fecha.")
            return
        conn = sqlite3.connect("facturas.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_factura, id_cliente, nit_empresa, fecha, nombre_cliente, "
            "monto_emp, monto_cli, pdf "
            "FROM facturas WHERE fecha LIKE ?", (f"%{criterio}%",)
        )
        resultados = cursor.fetchall()
        conn.close()
        self.mostrar_vista_historial(datos_filtrados=resultados)

    #Búsqueda 
    def buscar_factura(self):
        """Busca facturas por el nombre del cliente o por la fecha escrita."""
        criterio = self.entry_buscar.get()
        if "Buscar" in criterio or criterio == "":
            self.mostrar_vista_historial()
            return
        conn = sqlite3.connect("facturas.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_factura, id_cliente, nit_empresa, fecha, nombre_cliente, "
            "monto_emp, monto_cli, pdf "
            "FROM facturas WHERE id_factura LIKE ? OR id_cliente LIKE ? "
            "OR nombre_cliente LIKE ? OR fecha LIKE ?",
            (f"%{criterio}%", f"%{criterio}%",
             f"%{criterio}%", f"%{criterio}%")
        )
        resultados = cursor.fetchall()
        conn.close()
        self.mostrar_vista_historial(datos_filtrados=resultados)

    #Generar PDF (Hijueputa para dificil) 
    def generar_pdf(self):
        """Genera y descarga el PDF calculando correctamente los montos independientes."""
        seleccion = self.tabla.focus()
        if not seleccion:
            messagebox.showwarning("Atención",
                "Primero debes hacer clic en una factura de la tabla.")
            return

        valores = self.tabla.item(seleccion)['values']
        id_fac      = valores[0]
        id_cli      = valores[1]
        nit_empresa = str(valores[2]) if valores[2] != "—" else ""
        fecha       = valores[3]
        cliente     = valores[4]

        #Extraer los montos únicos desde la base de datos
        conn = sqlite3.connect("facturas.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT monto_emp, monto_cli FROM facturas WHERE id_factura = ?", (id_fac,)
        )
        fila = cursor.fetchone()
        conn.close()
        monto_emp_val   = fila[0] if fila and fila[0] is not None else 0
        monto_cli_val   = fila[1] if fila and fila[1] is not None else 0
        total_calculado = monto_emp_val + monto_cli_val

        monto_emp_str   = f"${monto_emp_val:,.2f}"
        monto_cli_str   = f"${monto_cli_val:,.2f}"
        total_final_str = f"${total_calculado:,.2f}"

        PAGE_W, PAGE_H = 612, 792
        MARGEN        = 50
        COLOR_VERDE   = (0.031, 0.557, 0.224)
        COLOR_GRIS    = (0.929, 0.929, 0.929)
        COLOR_TEXTO   = (0.2, 0.2, 0.2)

        nombre_archivo    = f"Factura_{id_fac}_{str(cliente).replace(' ', '_')}.pdf"
        carpeta_descargas = Path.home() / "Downloads"
        carpeta_descargas.mkdir(parents=True, exist_ok=True)
        ruta_completa     = str(carpeta_descargas / nombre_archivo)

        c = canvas.Canvas(ruta_completa, pagesize=(PAGE_W, PAGE_H))

        def set_color(rgb):   c.setFillColorRGB(*rgb)
        def rect_fill(x, y, w, h, rgb):
            c.setFillColorRGB(*rgb); c.rect(x, y, w, h, stroke=0, fill=1)
        def linea(x1, y1, x2, y2, rgb=(0.8, 0.8, 0.8), grosor=0.5):
            c.setStrokeColorRGB(*rgb); c.setLineWidth(grosor); c.line(x1, y1, x2, y2)

        #Encabezado
        rect_fill(0, PAGE_H - 80, PAGE_W, 80, COLOR_VERDE)
        c.setFont("Helvetica-Bold", 22); c.setFillColorRGB(1, 1, 1)
        c.drawString(MARGEN, PAGE_H - 45, "PALMA Software")
        c.setFont("Helvetica", 10); c.setFillColorRGB(0.85, 0.97, 0.88)
        c.drawString(MARGEN, PAGE_H - 62, "Facturación Electrónica")
        c.setFont("Helvetica-Bold", 13); c.setFillColorRGB(1, 1, 1)
        c.drawRightString(PAGE_W - MARGEN, PAGE_H - 40, f"FACTURA N.° {id_fac}")
        c.setFont("Helvetica", 9); c.setFillColorRGB(0.85, 0.97, 0.88)
        c.drawRightString(PAGE_W - MARGEN, PAGE_H - 56, f"Fecha de emisión: {fecha}")

        #Datos Del Emisor
        y_info = PAGE_H - 110
        c.setFont("Helvetica-Bold", 9); set_color(COLOR_VERDE)
        c.drawString(MARGEN, y_info, "EMISOR")
        linea(MARGEN, y_info - 3, MARGEN + 80, y_info - 3, COLOR_VERDE, 1)
        c.setFont("Helvetica-Bold", 10); set_color(COLOR_TEXTO)
        c.drawString(MARGEN, y_info - 16, "PALMA Software S.A.S")
        c.setFont("Helvetica", 9); c.setFillColorRGB(0.4, 0.4, 0.4)
        nit_txt = nit_empresa if nit_empresa else "900.123.456-1"
        for i, t in enumerate([f"NIT: {nit_txt}", "Régimen Simple de Tributación (RST)",
                                "Cl 45 #12-34 — Bogotá D.C.", "Res. Facturación: Res. 120000345"]):
            c.drawString(MARGEN, y_info - 30 - i * 13, t)

        #Datos Del Cliente
        col2 = PAGE_W // 2 + 10
        c.setFont("Helvetica-Bold", 9); set_color(COLOR_VERDE)
        c.drawString(col2, y_info, "CLIENTE")
        linea(col2, y_info - 3, col2 + 80, y_info - 3, COLOR_VERDE, 1)
        c.setFont("Helvetica-Bold", 10); set_color(COLOR_TEXTO)
        c.drawString(col2, y_info - 16, str(cliente))
        c.setFont("Helvetica", 9); c.setFillColorRGB(0.4, 0.4, 0.4)
        for i, t in enumerate([f"Identificación (NIT/CC): {id_cli}", f"Fecha de pago: {fecha}"]):
            c.drawString(col2, y_info - 30 - i * 13, t)

        y_sep = y_info - 90
        linea(MARGEN, y_sep, PAGE_W - MARGEN, y_sep, (0.7, 0.7, 0.7), 0.8)

        #Tabla del PDF
        y_tabla = y_sep - 20
        rect_fill(MARGEN, y_tabla - 4, PAGE_W - 2 * MARGEN, 20, COLOR_VERDE)
        c.setFont("Helvetica-Bold", 9); c.setFillColorRGB(1, 1, 1)
        for texto, x in [("DESCRIPCIÓN", MARGEN + 8), ("CANT.", PAGE_W - 260),
                          ("VALOR UNIT.", PAGE_W - 200), ("SUBTOTAL", PAGE_W - 110)]:
            c.drawString(x, y_tabla + 3, texto)

        #Monto De La Empresa
        y_fila1 = y_tabla - 22
        rect_fill(MARGEN, y_fila1 - 4, PAGE_W - 2 * MARGEN, 20, COLOR_GRIS)
        c.setFont("Helvetica", 9); set_color(COLOR_TEXTO)
        c.drawString(MARGEN + 8,   y_fila1 + 3, "Servicio Corporativo / Monto Empresa")
        c.drawString(PAGE_W - 260, y_fila1 + 3, "1")
        c.drawString(PAGE_W - 200, y_fila1 + 3, monto_emp_str)
        c.drawString(PAGE_W - 110, y_fila1 + 3, monto_emp_str)

        #Monto Del Cliente
        y_fila2 = y_fila1 - 22
        rect_fill(MARGEN, y_fila2 - 4, PAGE_W - 2 * MARGEN, 20, (0.97, 0.97, 0.97))
        c.drawString(MARGEN + 8,   y_fila2 + 3, "Servicio de Facturación / Monto Cliente")
        c.drawString(PAGE_W - 260, y_fila2 + 3, "1")
        c.drawString(PAGE_W - 200, y_fila2 + 3, monto_cli_str)
        c.drawString(PAGE_W - 110, y_fila2 + 3, monto_cli_str)

        #Totales
        y_tot = y_fila2 - 50
        linea(PAGE_W - 230, y_tot + 30, PAGE_W - MARGEN, y_tot + 30, (0.75, 0.75, 0.75))
        c.setFont("Helvetica", 9)
        for i, (label, valor) in enumerate([("Subtotal Empresa:", monto_emp_str),
                                             ("Subtotal Cliente:", monto_cli_str),
                                             ("IVA (0%):", "$0")]):
            yy = y_tot + 15 - i * 14
            set_color(COLOR_TEXTO); c.drawRightString(PAGE_W - 130, yy, label)
            c.setFillColorRGB(0.3, 0.3, 0.3); c.drawRightString(PAGE_W - MARGEN, yy, str(valor))
        rect_fill(PAGE_W - 230, y_tot - 40, 180, 22, COLOR_VERDE)
        c.setFont("Helvetica-Bold", 11); c.setFillColorRGB(1, 1, 1)
        c.drawRightString(PAGE_W - 130, y_tot - 28, "TOTAL:")
        c.drawRightString(PAGE_W - MARGEN, y_tot - 28, total_final_str)

        #Pie de página
        y_nota = y_tot - 80
        linea(MARGEN, y_nota + 10, PAGE_W - MARGEN, y_nota + 10, (0.8, 0.8, 0.8))
        c.setFont("Helvetica-Oblique", 8); c.setFillColorRGB(0.55, 0.55, 0.55)
        c.drawString(MARGEN, y_nota,
            "Este documento es una factura de venta electrónica generada por PALMA Software S.A.S.")
        c.drawString(MARGEN, y_nota - 12,
            "Conserve este documento como soporte de su transacción.")
        rect_fill(0, 0, PAGE_W, 18, COLOR_VERDE)
        c.setFont("Helvetica", 7); c.setFillColorRGB(0.85, 0.97, 0.88)
        c.drawCentredString(PAGE_W / 2, 5,
            "PALMA Software — Facturación Electrónica  |  palmasoftware.co")

        c.save()
        messagebox.showinfo("PDF Guardado", f"Factura generada exitosamente:\n{ruta_completa}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FacturaApp(root)
    root.mainloop()