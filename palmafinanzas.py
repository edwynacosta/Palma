import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox

# --- CONFIGURACIÓN ESTÉTICA (Basada en tus imágenes) ---
VERDE_PALMA = "#008F39"
BLANCO = "#FFFFFF"
VERDE_TEXTO = "#2A401A"

class ModuloFinanzasPrueba(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana de prueba
        self.title("Prueba de Módulo: Finanzas")
        self.geometry("1100x700")
        self.configure(fg_color=VERDE_PALMA)

        # Layout Principal del Frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ==========================================
        # 1. PANEL SUPERIOR: BOTONES DE NAVEGACIÓN
        # ==========================================
        self.frame_nav = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_nav.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Definición de botones según tu diseño
        opciones = [
            ("FACTURAS", self.ver_facturas),
            ("BALANCE", self.ver_balance),
            ("RECIBOS PÚBLICOS", self.ver_recibos),
            ("ANALÍTICAS", self.ver_analiticas)
        ]

        for texto, comando in opciones:
            btn = ctk.CTkButton(self.frame_nav, text=texto, fg_color=BLANCO, 
                                text_color=VERDE_TEXTO, font=("Arial Black", 12),
                                height=50, corner_radius=15, command=comando)
            btn.pack(side="left", padx=5, expand=True, fill="x")

        # Botón Cerrar (X)
        self.btn_x = ctk.CTkButton(self.frame_nav, text="X", width=50, height=50, 
                                   fg_color=BLANCO, text_color="red", 
                                   font=("Arial Black", 16), corner_radius=15,
                                   command=self.destroy)
        self.btn_x.pack(side="left", padx=5)

        # ==========================================
        # 2. PANEL CENTRAL: CUERPO BLANCO
        # ==========================================
        self.panel_blanco = ctk.CTkFrame(self, fg_color=BLANCO, corner_radius=25)
        self.panel_blanco.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Título dinámico
        self.lbl_titulo = ctk.CTkLabel(self.panel_blanco, text="FACTURAS", 
                                      font=("Arial Black", 28), text_color=VERDE_TEXTO)
        self.lbl_titulo.pack(pady=15)

        # Contenedor para la tabla Treeview
        self.tree_container = ctk.CTkFrame(self.panel_blanco, fg_color="transparent")
        self.tree_container.pack(expand=True, fill="both", padx=30, pady=10)

        # Configuración del Treeview (Tkinter estándar dentro de CTK)
        self.tabla = ttk.Treeview(self.tree_container, show="headings")
        self.tabla.pack(expand=True, fill="both")

        # Estilo para la tabla
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=30, font=("Arial", 11))
        style.map("Treeview", background=[('selected', VERDE_PALMA)])

        # ==========================================
        # 3. PANEL INFERIOR: BÚSQUEDA
        # ==========================================
        self.frame_busqueda = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_busqueda.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        self.ent_buscar = ctk.CTkEntry(self.frame_busqueda, 
                                       placeholder_text="ID factura, ID cliente, nombre cliente...",
                                       fg_color=BLANCO, text_color=VERDE_TEXTO, 
                                       height=50, corner_radius=15, font=("Arial", 14))
        self.ent_buscar.pack(side="left", padx=(150, 10), expand=True, fill="x")

        self.btn_buscar = ctk.CTkButton(self.frame_busqueda, text="BUSCAR", 
                                        fg_color=BLANCO, text_color=VERDE_TEXTO,
                                        font=("Arial Black", 14), height=50, width=180, 
                                        corner_radius=15, command=self.ejecutar_busqueda)
        self.btn_buscar.pack(side="left", padx=(0, 150))

        # Cargar vista inicial
        self.ver_facturas()

    # --- MÉTODOS DE FUNCIONALIDAD ---

    def limpiar_tabla(self):
        # Solución al error: usamos get_children() para vaciar la tabla
        for i in self.tabla.get_children():
            self.tabla.delete(i)

    def ver_facturas(self):
        self.lbl_titulo.configure(text="FACTURAS")
        self.limpiar_tabla()
        
        columnas = ("ID FACTURA", "ID CLIENTE", "FECHA", "NOMBRE CLIENTE", "TOTAL", "PDF")
        self.tabla["columns"] = columnas
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=120)
        
        # Datos de ejemplo
        self.tabla.insert("", "end", values=("F-001", "C-1020", "20/02/2026", "Edwin Programing", "$123.000", "📄"))
        self.tabla.insert("", "end", values=("F-002", "C-5050", "19/02/2026", "Nicolas Gomez", "$85.000", "📄"))

    def ver_balance(self):
        self.lbl_titulo.configure(text="BALANCE")
        self.limpiar_tabla()
        columnas = ("MES", "INGRESOS", "EGRESOS", "SALDO")
        self.tabla["columns"] = columnas
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=200)
        
        self.tabla.insert("", "end", values=("Enero", "$5.000.000", "$2.100.000", "$2.900.000"))
        self.tabla.insert("", "end", values=("Febrero", "$3.400.000", "$1.200.000", "$2.200.000"))

    def ver_recibos(self):
        # Funcionalidad simple de recordatorio
        messagebox.showinfo("Recibos Públicos", 
                            "ALERTA DE PAGOS:\n\n- Luz: Vence el 25/02\n- Internet: Pagado\n- Agua: Pendiente de Factura")

    def ver_analiticas(self):
        self.lbl_titulo.configure(text="ANALÍTICAS")
        self.limpiar_tabla()
        columnas = ("INDICADOR", "VALOR", "ESTADO")
        self.tabla["columns"] = columnas
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=250)
        
        self.tabla.insert("", "end", values=("Ventas vs Mes Anterior", "+15.4%", "Crecimiento"))
        self.tabla.insert("", "end", values=("Producto más vendido", "Palma x1L", "Estable"))

    def ejecutar_busqueda(self):
        termino = self.ent_buscar.get().lower()
        if not termino:
            messagebox.showwarning("Buscador", "Ingresa un término para buscar.")
            return

        encontrado = False
        for item in self.tabla.get_children():
            # Obtiene todos los valores de la fila
            valores = [str(v).lower() for v in self.tabla.item(item)['values']]
            # Comprueba si el término está en algún valor
            if any(termino in v for v in valores):
                self.tabla.selection_set(item)
                self.tabla.see(item)
                encontrado = True
                break
        
        if not encontrado:
            messagebox.showinfo("Buscador", f"No se encontró: '{termino}'")

if __name__ == "__main__":
    app = ModuloFinanzasPrueba()
    app.mainloop()