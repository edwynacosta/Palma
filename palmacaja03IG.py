import customtkinter as ctk
from tkinter import ttk, messagebox
import datetime

# --- PALETA DE COLORES (Ajustada a tus capturas) ---
COLOR_FONDO_VERDE = "#008F39" 
COLOR_BLANCO = "#FFFFFF"
VERDE_PANELES = "#E2EFDA"   
AMARILLO_PANEL = "#FFF2CC"  
ROJO_PANEL = "#F8CECC"      
VERDE_TEXTO = "#385723"     
GRIS_NUMEROS = "#595959"    

class CajaPalmaPOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de ventana
        self.title("Caja Palma POS")
        self.geometry("1150x750")
        self.configure(fg_color=COLOR_FONDO_VERDE)

        self.contador_id = 1

        # Estructura principal: 2 columnas
        self.grid_columnconfigure(0, weight=4) # Panel de Precios
        self.grid_columnconfigure(1, weight=6) # Panel de Tabla
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        #       PANEL IZQUIERDO (PRECIOS)
        # ==========================================
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Total a pagar (Corregido para evitar AttributeError)
        self.box_total, self.lbl_total_num = self.crear_caja_info(
            self.left_panel, "Total a pagar:", "$0", VERDE_PANELES, 80
        )

        # Efectivo (Input)
        self.box_efectivo = ctk.CTkFrame(self.left_panel, fg_color=AMARILLO_PANEL, corner_radius=20)
        self.box_efectivo.pack(fill="x", pady=10)
        ctk.CTkLabel(self.box_efectivo, text="Efectivo", font=("Arial", 18, "bold"), text_color=VERDE_TEXTO).pack(anchor="w", padx=20, pady=(10,0))
        self.ent_efectivo = ctk.CTkEntry(self.box_efectivo, font=("Arial", 60, "bold"), text_color=GRIS_NUMEROS, 
                                        fg_color="transparent", border_width=0, justify="center")
        self.ent_efectivo.pack(fill="x", pady=10)
        self.ent_efectivo.bind("<KeyRelease>", self.update_cambio)

        # Cambio
        self.box_cambio, self.lbl_cambio_num = self.crear_caja_info(
            self.left_panel, "Cambio", "$0", ROJO_PANEL, 60
        )

        # Footer Identificador
        ctk.CTkLabel(self.left_panel, text="CAJA 1 EDWIN", font=("Arial Black", 16), text_color="white").pack(side="bottom", anchor="w", pady=10)

        # ==========================================
        #       PANEL DERECHO (FACTURACIÓN)
        # ==========================================
        self.right_panel = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=30)
        self.right_panel.grid(row=0, column=1, padx=20, pady=(20, 100), sticky="nsew")

        ctk.CTkLabel(self.right_panel, text="FACTURACIÓN", font=("Arial Black", 30), text_color=VERDE_TEXTO).pack(pady=20)

        # Configuración de Tabla
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=COLOR_BLANCO, fieldbackground=COLOR_BLANCO, 
                        borderwidth=0, font=("Arial", 12), rowheight=40)
        style.configure("Treeview.Heading", background=COLOR_BLANCO, font=("Arial", 11, "bold"), 
                        borderwidth=0, foreground=VERDE_TEXTO)

        self.tabla = ttk.Treeview(self.right_panel, columns=("id", "nombre", "cant", "precio"), show="headings")
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="NOMBRE")
        self.tabla.heading("cant", text="CANTIDAD/ PESO")
        self.tabla.heading("precio", text="PRECIO")
        
        self.tabla.column("id", width=60, anchor="center")
        self.tabla.column("nombre", width=200)
        self.tabla.column("cant", width=150, anchor="center")
        self.tabla.column("precio", width=120, anchor="center")
        self.tabla.pack(padx=20, pady=10, fill="both", expand=True)

        # --- BOTONES DE ACCIÓN ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.place(relx=0.68, rely=0.93, anchor="center")

        self.btn_cobrar = ctk.CTkButton(self.btn_frame, text="COBRAR", fg_color="#E0E0E0", text_color="black", 
                                        font=("Arial Black", 18), width=180, height=55, corner_radius=15, 
                                        command=self.finalizar_venta)
        self.btn_cobrar.pack(side="left", padx=10)

        self.btn_add = self.crear_boton_accion("AGREGAR", self.abrir_formulario)
        self.btn_del = self.crear_boton_accion("ELIMINAR", self.eliminar)
        self.btn_mod = self.crear_boton_accion("MODIFICAR", None)

    # --- FUNCIONES DE SOPORTE ---

    def crear_caja_info(self, parent, titulo, valor, color, size):
        """Crea la caja y devuelve la referencia al label del número para evitar errores"""
        frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=25)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text=titulo, font=("Arial", 20, "bold"), text_color=VERDE_TEXTO).pack(anchor="w", padx=25, pady=(15,0))
        
        lbl_num = ctk.CTkLabel(frame, text=valor, font=("Arial", size, "bold"), text_color=GRIS_NUMEROS)
        lbl_num.pack(pady=(0,20))
        
        return frame, lbl_num

    def crear_boton_accion(self, texto, comando):
        btn = ctk.CTkButton(self.btn_frame, text=texto, fg_color=VERDE_PANELES, text_color=VERDE_TEXTO, 
                            font=("Arial Black", 12), width=110, height=55, corner_radius=15, command=comando)
        btn.pack(side="left", padx=5)
        return btn

    def update_cambio(self, e=None):
        try:
            total = int(self.lbl_total_num.cget("text").replace("$", "").replace(".", ""))
            val_ent = self.ent_efectivo.get().replace(".", "")
            efectivo = int(val_ent) if val_ent else 0
            cambio = efectivo - total
            self.lbl_cambio_num.configure(text=f"${max(0, cambio):,.0f}".replace(",", "."))
        except: pass

    def abrir_formulario(self):
        pop = ctk.CTkToplevel(self)
        pop.title("Agregar Producto")
        pop.geometry("350x400")
        pop.attributes("-topmost", True)
        
        ctk.CTkLabel(pop, text="Nombre del Producto:").pack(pady=(20,5))
        en = ctk.CTkEntry(pop, width=250); en.pack()
        
        ctk.CTkLabel(pop, text="Cantidad / Peso:").pack(pady=5)
        ec = ctk.CTkEntry(pop, width=250); ec.pack()
        
        ctk.CTkLabel(pop, text="Precio Unitario:").pack(pady=5)
        ep = ctk.CTkEntry(pop, width=250); ep.pack()

        def guardar():
            try:
                subtotal = int(float(ec.get()) * int(ep.get()))
                self.tabla.insert("", "end", values=(
                    self.contador_id, en.get(), ec.get(), f"${subtotal:,.0f}".replace(",", ".")
                ))
                self.contador_id += 1
                self.recalc_total()
                pop.destroy()
            except: 
                messagebox.showerror("Error", "Ingresa valores numéricos válidos")
        
        ctk.CTkButton(pop, text="Añadir a Factura", fg_color=COLOR_FONDO_VERDE, command=guardar).pack(pady=30)

    def recalc_total(self):
        t = 0
        for item in self.tabla.get_children():
            valor = self.tabla.item(item, "values")[3].replace("$", "").replace(".", "")
            t += int(valor)
        self.lbl_total_num.configure(text=f"${t:,.0f}".replace(",", "."))
        self.update_cambio()

    def eliminar(self):
        selected = self.tabla.selection()
        if not selected: return
        for s in selected:
            self.tabla.delete(s)
        self.recalc_total()

    def finalizar_venta(self):
        if not self.tabla.get_children(): return
        messagebox.showinfo("Éxito", "Venta procesada correctamente")
        self.reset_todo()

    def reset_todo(self):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        self.ent_efectivo.delete(0, 'end')
        self.lbl_total_num.configure(text="$0")
        self.lbl_cambio_num.configure(text="$0")
        self.contador_id = 1

if __name__ == "__main__":
    app = CajaPalmaPOS()
    app.mainloop()