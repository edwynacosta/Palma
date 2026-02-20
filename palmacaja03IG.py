import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox

# --- CONFIGURACIÓN ESTÉTICA ---
VERDE_PALMA = "#008F39"
BLANCO = "#FFFFFF"
VERDE_TEXTO = "#2A401A"
GRIS_SUAVE = "#F2F2F2"
NARANJA_NUEVA_VENTA = "#FFB347" # Color sugerido para resaltar el cambio de botón

class AppPalma(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Facturación - Palma")
        self.geometry("1200x800")
        self.configure(fg_color=VERDE_PALMA)

        # Variables de control
        self.total_actual = 0
        self.contador_id = 1
        self.venta_finalizada = False 

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # PANEL IZQUIERDO: TOTALES
        # ==========================================
        self.panel_izquierdo = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_izquierdo.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")

        self.box_total, self.lbl_total_izq = self.crear_panel_valor("Total a pagar:", "$0")
        self.box_efectivo, self.ent_efectivo = self.crear_panel_input("Efectivo")
        self.box_cambio, self.lbl_cambio = self.crear_panel_valor("Cambio", "$0")


        # ==========================================
        # PANEL DERECHO: FACTURACIÓN
        # ==========================================
        self.panel_derecho = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_derecho.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")

        # Botones Superiores
        self.frame_top_btns = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        self.frame_top_btns.pack(fill="x", pady=(0, 10))
        for txt in ["CAJA", "FACTURA\nELECTRÓNICA", "DEVOLUCIONES", "RECIBO\nPROVEEDORES"]:
            ctk.CTkButton(self.frame_top_btns, text=txt, fg_color=BLANCO, text_color="black", font=("Arial Black", 11), height=55, corner_radius=15).pack(side="left", padx=5, expand=True, fill="x")

        # Cuerpo de Facturación
        self.frame_tabla_bg = ctk.CTkFrame(self.panel_derecho, fg_color=BLANCO, corner_radius=25)
        self.frame_tabla_bg.pack(fill="both", expand=True)

        self.lbl_titulo_factura = ctk.CTkLabel(self.frame_tabla_bg, text="FACTURACIÓN", font=("Arial Black", 32), text_color=VERDE_TEXTO)
        self.lbl_titulo_factura.pack(pady=(20, 10))

        # Tabla
        self.tabla = ttk.Treeview(self.frame_tabla_bg, columns=("id", "nombre", "cant", "precio"), show="headings")
        for col, head in zip(("id", "nombre", "cant", "precio"), ("ID", "NOMBRE", "CANTIDAD/ PESO", "PRECIO")):
            self.tabla.heading(col, text=head)
            self.tabla.column(col, anchor="center")
        
        self.tabla.tag_configure('total_row', background='#D5E8D4', font=('Arial Black', 12))
        self.tabla.pack(fill="both", expand=True, padx=40, pady=10)

        # --- BOTONES INFERIORES ---
        self.frame_bot_btns = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        self.frame_bot_btns.pack(fill="x", pady=(15, 0))

        # El botón dinámico (Cobrar / Nueva Venta)
        self.btn_accion_principal = ctk.CTkButton(self.frame_bot_btns, text="COBRAR", fg_color=GRIS_SUAVE, text_color="black", font=("Arial Black", 16), height=65, corner_radius=18, width=280, command=self.gestionar_boton_principal)
        self.btn_accion_principal.pack(side="left", padx=(0, 10))

        self.btn_agregar = self.crear_btn_accion("AGREGAR", self.acc_agregar)
        self.btn_eliminar = self.crear_btn_accion("ELIMINAR", self.acc_eliminar)
        self.btn_modificar = self.crear_btn_accion("MODIFICAR", self.acc_modificar)
        self.btn_buscar = self.crear_btn_accion("BUSCAR", self.acc_buscar)

    # --- MÉTODOS DE INTERFAZ ---
    def crear_panel_valor(self, titulo, valor_inicial):
        frame = ctk.CTkFrame(self.panel_izquierdo, fg_color=BLANCO, corner_radius=25, height=170)
        frame.pack(fill="x", pady=8); frame.pack_propagate(False)
        ctk.CTkLabel(frame, text=titulo, font=("Arial Black", 18), text_color=VERDE_TEXTO).pack(anchor="w", padx=25, pady=(15, 0))
        lbl = ctk.CTkLabel(frame, text=valor_inicial, font=("Arial Black", 68), text_color=VERDE_TEXTO)
        lbl.pack(expand=True)
        return frame, lbl

    def crear_panel_input(self, titulo):
        frame = ctk.CTkFrame(self.panel_izquierdo, fg_color=BLANCO, corner_radius=25, height=170)
        frame.pack(fill="x", pady=8); frame.pack_propagate(False)
        ctk.CTkLabel(frame, text=titulo, font=("Arial Black", 18), text_color=VERDE_TEXTO).pack(anchor="w", padx=25, pady=(15, 0))
        ent = ctk.CTkEntry(frame, font=("Arial Black", 60), text_color=VERDE_TEXTO, fg_color="transparent", border_width=0, justify="center")
        ent.pack(expand=True, fill="x", padx=10)
        ent.bind("<KeyRelease>", self.formatear_efectivo)
        return frame, ent

    def crear_btn_accion(self, texto, comando):
        btn = ctk.CTkButton(self.frame_bot_btns, text=texto, fg_color=BLANCO, text_color="black", font=("Arial Black", 13), height=65, corner_radius=18, command=comando)
        btn.pack(side="left", padx=5, expand=True, fill="x")
        return btn

    # --- LÓGICA DINÁMICA DEL BOTÓN ---
    def gestionar_boton_principal(self):
        if not self.venta_finalizada:
            self.acc_cobrar()
        else:
            self.nueva_venta()

    # --- FUNCIONALIDADES ---
    def formatear_efectivo(self, event=None):
        texto = self.ent_efectivo.get().replace("$", "").replace(".", "").strip()
        if texto.isdigit():
            valor = int(texto)
            formateado = f"${valor:,.0f}".replace(",", ".")
            self.ent_efectivo.delete(0, tk.END)
            self.ent_efectivo.insert(0, formateado)
        self.calcular_cambio()

    def calcular_cambio(self, event=None):
        try:
            efectivo_texto = self.ent_efectivo.get().replace("$", "").replace(".", "").strip()
            efectivo = int(efectivo_texto) if efectivo_texto else 0
            cambio = efectivo - self.total_actual
            self.lbl_cambio.configure(text=f"${max(0, cambio):,.0f}".replace(",", "."))
        except: pass

    def actualizar_totales(self):
        if self.venta_finalizada: return
        self.total_actual = 0
        for item in self.tabla.get_children():
            if 'total_row' in self.tabla.item(item, 'tags'):
                self.tabla.delete(item)
                continue
            v = self.tabla.item(item, "values")[3].replace("$", "").replace(".", "")
            self.total_actual += int(v)
        
        fmt = f"${self.total_actual:,.0f}".replace(",", ".")
        self.lbl_total_izq.configure(text=fmt)
        if self.total_actual > 0:
            self.tabla.insert("", "end", values=("", "", "TOTAL:", fmt), tags=('total_row',))
        self.calcular_cambio()

    def acc_cobrar(self):
        if self.total_actual > 0:
            res = messagebox.askyesno("Facturación", "¿Finalizar cuenta?")
            if res:
                self.venta_finalizada = True
                self.lbl_titulo_factura.configure(text="FACTURA CERRADA", text_color="red")
                # Cambio visual del botón
                self.btn_accion_principal.configure(text="NUEVA VENTA", fg_color=NARANJA_NUEVA_VENTA)
                messagebox.showinfo("Éxito", "Cobro realizado. Pulse 'NUEVA VENTA' para continuar.")
        else:
            messagebox.showwarning("Atención", "No hay productos para cobrar.")

    def nueva_venta(self):
        self.venta_finalizada = False
        self.lbl_titulo_factura.configure(text="FACTURACIÓN", text_color=VERDE_TEXTO)
        # Restaurar botón
        self.btn_accion_principal.configure(text="COBRAR", fg_color=GRIS_SUAVE)
        # Limpiar datos
        for item in self.tabla.get_children(): self.tabla.delete(item)
        self.ent_efectivo.delete(0, tk.END)
        self.contador_id = 1
        self.actualizar_totales()

    def acc_agregar(self):
        if self.venta_finalizada: return
        pop = ctk.CTkToplevel(self); pop.geometry("300x400"); pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text="Producto:").pack(pady=5)
        e_nom = ctk.CTkEntry(pop); e_nom.pack()
        ctk.CTkLabel(pop, text="Cantidad:").pack(pady=5)
        e_can = ctk.CTkEntry(pop); e_can.pack()
        ctk.CTkLabel(pop, text="Precio Unit:").pack(pady=5)
        e_pre = ctk.CTkEntry(pop); e_pre.pack()

        def guardar():
            try:
                sub = int(e_can.get()) * int(e_pre.get())
                self.tabla.insert("", 0, values=(self.contador_id, e_nom.get(), e_can.get(), f"${sub:,.0f}".replace(",", ".")))
                self.contador_id += 1
                self.actualizar_totales()
                pop.destroy()
            except: messagebox.showerror("Error", "Datos inválidos")
        ctk.CTkButton(pop, text="GUARDAR", command=guardar).pack(pady=20)

    def acc_modificar(self):
        if self.venta_finalizada: return
        selected = self.tabla.selection()
        if not selected or 'total_row' in self.tabla.item(selected)['tags']: return
        item_data = self.tabla.item(selected)['values']
        pop = ctk.CTkToplevel(self); pop.geometry("300x200"); pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text="Nueva Cantidad:").pack(pady=10)
        e_new = ctk.CTkEntry(pop); e_new.insert(0, item_data[2]); e_new.pack()

        def aplicar():
            try:
                p_v = int(item_data[3].replace("$", "").replace(".", "")) // int(item_data[2])
                n_c = int(e_new.get())
                self.tabla.item(selected, values=(item_data[0], item_data[1], n_c, f"${n_c*p_v:,.0f}".replace(",", ".")))
                self.actualizar_totales(); pop.destroy()
            except: pass
        ctk.CTkButton(pop, text="APLICAR", command=aplicar).pack(pady=20)

    def acc_eliminar(self):
        if self.venta_finalizada: return
        sel = self.tabla.selection()
        if sel and 'total_row' not in self.tabla.item(sel)['tags']:
            self.tabla.delete(sel); self.actualizar_totales()

    def acc_buscar(self):
        messagebox.showinfo("Buscador", "Función de búsqueda lista.")

if __name__ == "__main__":
    app = AppPalma()
    app.mainloop()