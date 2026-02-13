import customtkinter as ctk
from tkinter import ttk, messagebox

# --- PALETA DE COLORES EXACTA ---
COLOR_FONDO = "#FFFFFF"
VERDE_PANELES = "#E2EFDA"   # Fondos de Total y Facturación
AMARILLO_PANEL = "#FFF2CC"  # Fondo Efectivo
ROJO_PANEL = "#F8CECC"      # Fondo Cambio
VERDE_TEXTO = "#385723"     # Títulos (FACTURACIÓN)
GRIS_NUMEROS = "#595959"    # Color de las cifras grandes

class POSCajaPalma(ctk.CTk): # CLASES Y OBJETOS POO 77777
    def __init__(self):
        super().__init__()

        self.title("Caja Palma POS")
        self.geometry("1100x650")
        self.configure(fg_color=COLOR_FONDO)

        self.contador_id = 1

        # Configuración de columnas
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        #       PANEL IZQUIERDO (PAGOS)
        # ==========================================
        self.frame_pagos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_pagos.grid(row=0, column=0, padx=(50, 25), pady=40, sticky="nsew")

        # TOTAL A PAGAR
        self.box_total = ctk.CTkFrame(self.frame_pagos, fg_color=VERDE_PANELES, corner_radius=30)
        self.box_total.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(self.box_total, text="Total a pagar:", font=("Arial", 20, "bold"), text_color=VERDE_TEXTO).pack(anchor="w", padx=30, pady=(20, 0))
        self.lbl_total_num = ctk.CTkLabel(self.box_total, text="$0", font=("Arial", 85, "bold"), text_color=GRIS_NUMEROS)
        self.lbl_total_num.pack(pady=(0, 20))

        # EFECTIVO (Cuadro redondeado con entrada de texto)
        self.box_efectivo = ctk.CTkFrame(self.frame_pagos, fg_color=AMARILLO_PANEL, corner_radius=30)
        self.box_efectivo.pack(fill="x", pady=15)
        ctk.CTkLabel(self.box_efectivo, text="Efectivo", font=("Arial", 20, "bold"), text_color=VERDE_TEXTO).pack(anchor="w", padx=30, pady=(20, 0))
        self.ent_efectivo = ctk.CTkEntry(self.box_efectivo, font=("Arial", 65, "bold"), text_color=GRIS_NUMEROS, fg_color="transparent", border_width=0, justify="center")
        self.ent_efectivo.pack(fill="x", padx=30, pady=(0, 20))
        self.ent_efectivo.bind("<KeyRelease>", self.update_cambio)

        # CAMBIO
        self.box_cambio = ctk.CTkFrame(self.frame_pagos, fg_color=ROJO_PANEL, corner_radius=30)
        self.box_cambio.pack(fill="x", pady=15)
        ctk.CTkLabel(self.box_cambio, text="Cambio", font=("Arial", 20, "bold"), text_color=VERDE_TEXTO).pack(anchor="w", padx=30, pady=(20, 0))
        self.lbl_cambio_num = ctk.CTkLabel(self.box_cambio, text="$0", font=("Arial", 65, "bold"), text_color=GRIS_NUMEROS)
        self.lbl_cambio_num.pack(pady=(0, 20))

        # ==========================================
        #       PANEL DERECHO (FACTURACIÓN)
        # ==========================================
        self.frame_derecha = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_derecha.grid(row=0, column=1, padx=(25, 50), pady=40, sticky="nsew")

        # Título FACTURACIÓN alineado a la derecha
        ctk.CTkLabel(self.frame_derecha, text="FACTURACIÓN", font=("Arial Black", 32), text_color=VERDE_TEXTO).pack(anchor="e", pady=(0, 15))

        # Cuadro grande de la tabla
        self.box_tabla = ctk.CTkFrame(self.frame_derecha, fg_color=VERDE_PANELES, corner_radius=40)
        self.box_tabla.pack(fill="both", expand=True)

        # Estilo de la tabla
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=VERDE_PANELES, fieldbackground=VERDE_PANELES, borderwidth=0, font=("Arial", 12), rowheight=40)
        style.configure("Treeview.Heading", background=VERDE_PANELES, font=("Arial", 10, "bold"), borderwidth=0, foreground=VERDE_TEXTO)
        style.map("Treeview", background=[('selected', '#C5E0B4')])

        self.tabla = ttk.Treeview(self.box_tabla, columns=("id", "nombre", "cant", "precio"), show="headings")
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="NOMBRE")
        self.tabla.heading("cant", text="CANTIDAD/ PESO")
        self.tabla.heading("precio", text="PRECIO")

        self.tabla.column("id", width=60, anchor="center")
        self.tabla.column("nombre", width=200)
        self.tabla.column("cant", width=180, anchor="center")
        self.tabla.column("precio", width=120, anchor="center")
        self.tabla.pack(padx=30, pady=30, fill="both", expand=True)

        # --- BOTONES INFERIORES ---
        self.frame_actions = ctk.CTkFrame(self.frame_derecha, fg_color="transparent")
        self.frame_actions.pack(fill="x", pady=(20, 0))

        # Botón COBRAR (Izquierda del panel derecho)
        self.btn_cobrar = ctk.CTkButton(self.frame_actions, text="COBRAR", font=("Arial Black", 24),
                                        fg_color=VERDE_PANELES, text_color="white", corner_radius=30,
                                        height=70, width=280, hover_color="#C5E0B4", command=self.finalizar_venta)
        self.btn_cobrar.pack(side="left")

        # Botones +, -, ! (Derecha del panel derecho)
        self.btn_mod = self.draw_action_btn("!", self.modificar)
        self.btn_mod.pack(side="right", padx=(10, 0))

        self.btn_del = self.draw_action_btn("-", self.eliminar)
        self.btn_del.pack(side="right", padx=10)

        self.btn_add = self.draw_action_btn("+", self.abrir_formulario)
        self.btn_add.pack(side="right")

    def draw_action_btn(self, txt, cmd):
        # Botones circulares/redondeados según la imagen
        return ctk.CTkButton(self.frame_actions, text=txt, font=("Arial Black", 30),
                             fg_color=VERDE_PANELES, text_color="white", corner_radius=30,
                             width=90, height=70, hover_color="#C5E0B4", command=cmd)

    # ==========================================
    #               LÓGICA
    # ==========================================

    def update_cambio(self, e=None):
        try:
            total = int(self.lbl_total_num.cget("text").replace("$", "").replace(".", ""))
            efectivo_str = self.ent_efectivo.get().replace(".", "")
            efectivo = int(efectivo_str) if efectivo_str else 0
            cambio = efectivo - total
            self.lbl_cambio_num.configure(text=f"${max(0, cambio):,.0f}".replace(",", "."))
        except:
            self.lbl_cambio_num.configure(text="$0")

    def abrir_formulario(self):
        # Ventana para ingresar productos
        pop = ctk.CTkToplevel(self)
        pop.geometry("400x450")
        pop.title("Nuevo Producto")
        pop.attributes("-topmost", True)

        ctk.CTkLabel(pop, text="Nombre:").pack(pady=10)
        ent_n = ctk.CTkEntry(pop, width=250)
        ent_n.pack()

        ctk.CTkLabel(pop, text="Cantidad/Peso:").pack(pady=10)
        ent_c = ctk.CTkEntry(pop, width=250)
        ent_c.pack()

        ctk.CTkLabel(pop, text="Precio Unitario:").pack(pady=10)
        ent_p = ctk.CTkEntry(pop, width=250)
        ent_p.pack()

        def guardar():
            try:
                nom, can, pre = ent_n.get(), float(ent_c.get()), int(ent_p.get())
                total_item = int(can * pre)
                self.tabla.insert("", "end", values=(self.contador_id, nom, can, f"${total_item:,.0f}".replace(",", ".")))
                self.contador_id += 1
                self.recalcular()
                pop.destroy()
            except: messagebox.showerror("Error", "Datos inválidos")

        ctk.CTkButton(pop, text="AGREGAR", command=guardar).pack(pady=30)

    def recalcular(self):
        total = 0
        for item in self.tabla.get_children():
            valor = self.tabla.item(item, "values")[3].replace("$", "").replace(".", "")
            total += int(valor)
        self.lbl_total_num.configure(text=f"${total:,.0f}".replace(",", "."))
        self.update_cambio()

    def eliminar(self):
        sel = self.tabla.selection()
        if sel: 
            self.tabla.delete(sel)
            self.recalcular()

    def modificar(self):
        # Lógica para modificar producto seleccionado
        pass

    def finalizar_venta(self):
        if self.lbl_total_num.cget("text") != "$0":
            messagebox.showinfo("Caja Palma", "Venta cobrada con éxito")
            for i in self.tabla.get_children(): self.tabla.delete(i)
            self.ent_efectivo.delete(0, 'end')
            self.recalcular()

if __name__ == "__main__":
    app = POSCajaPalma()
    app.mainloop()
