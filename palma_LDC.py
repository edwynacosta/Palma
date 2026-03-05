import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image

# --- CONFIGURACIÓN ESTÉTICA GLOBAL ---
ctk.set_appearance_mode("light")
VERDE_PALMA = "#008F39"
BLANCO = "#FFFFFF"
VERDE_TEXTO = "#2A401A"
GRIS_SUAVE = "#F2F2F2"
NARANJA_NUEVA_VENTA = "#FFB347"
VERDE_CLARO_INPUT = "#A8E6CF"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PALMA - Sistema Integral")
        self.geometry("1200x800")
        self.configure(fg_color=VERDE_PALMA)

        # Base de datos de usuarios (Tu original)
        self.usuarios_db = {
            "edwin": {"password": "123", "rol": "admin"},
            "nicolas": {"password": "456", "rol": "usuario"},
            "alejandro": {"password": "789", "rol": "usuario"},
            "juandavid": {"password": "000", "rol": "usuario"}
        }

        # Variable para saber a qué menú regresar desde la caja
        self.rol_actual = "usuario"

        # Contenedor principal
        self.contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor.pack(expand=True, fill="both")
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Inicialización de pantallas
        for F in (LoginFrame, AdminDashboard, UserDashboard, VentasFrame):
            page_name = F.__name__
            frame = F(parent=self.contenedor, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.mostrar_frame("LoginFrame")

    def mostrar_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

# ==========================================
# FRAME 1: LOGIN (TAL CUAL TU DISEÑO)
# ==========================================
class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.card = ctk.CTkFrame(self, corner_radius=30, fg_color="white", width=420, height=580)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        try:
            logo_image = ctk.CTkImage(light_image=Image.open("logo_palma.png"), size=(120, 120))
            self.lbl_logo = ctk.CTkLabel(self.card, image=logo_image, text="")
        except:
            self.lbl_logo = ctk.CTkLabel(self.card, text="🌴", font=("Arial", 60))
        
        self.lbl_logo.pack(pady=(40, 5))
        ctk.CTkLabel(self.card, text="PALMA", text_color="#008037", font=("Fredoka One", 32, "bold")).pack(pady=(0, 20))

        self.combo_tipo = ctk.CTkComboBox(self.card, values=["Administrador", "Usuario"], fg_color=VERDE_CLARO_INPUT, border_color=VERDE_CLARO_INPUT, button_color=VERDE_CLARO_INPUT, corner_radius=22, width=280, height=45)
        self.combo_tipo.set("Tipo de Usuario")
        self.combo_tipo.pack(pady=10)

        self.entry_user = ctk.CTkEntry(self.card, placeholder_text="Usuario", fg_color=VERDE_CLARO_INPUT, border_width=0, width=340, height=55, corner_radius=27)
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self.card, placeholder_text="Contraseña", show="*", fg_color=VERDE_CLARO_INPUT, border_width=0, width=340, height=55, corner_radius=27)
        self.entry_pass.pack(pady=10)

        self.btn_entrar = ctk.CTkButton(self.card, text="ENTRAR", fg_color="#008037", corner_radius=15, width=130, height=50, font=("Arial", 16, "bold"), command=self.verificar)
        self.btn_entrar.pack(pady=25)

    def verificar(self):
        user = self.entry_user.get().lower()
        pw = self.entry_pass.get()
        db = self.controller.usuarios_db

        if user in db and db[user]["password"] == pw:
            self.controller.rol_actual = db[user]["rol"]
            dest = "AdminDashboard" if db[user]["rol"] == "admin" else "UserDashboard"
            self.controller.mostrar_frame(dest)
            self.entry_user.delete(0, 'end'); self.entry_pass.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Datos incorrectos")

# ==========================================
# FRAME 2: DASHBOARD ADMIN
# ==========================================
class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        # El botón VENTAS redirige a la VentasFrame
        ctk.CTkButton(self.grid_frame, text="VENTAS", fg_color="white", text_color="#008037", font=("Arial", 20, "bold"), width=200, height=200, corner_radius=20, command=lambda: controller.mostrar_frame("VentasFrame")).grid(row=0, column=0, padx=15, pady=15)
        
        ctk.CTkButton(self.grid_frame, text="INVENTARIO", fg_color="white", text_color="#008037", font=("Arial", 20, "bold"), width=200, height=200, corner_radius=20).grid(row=0, column=1, padx=15, pady=15)
        ctk.CTkButton(self.grid_frame, text="FINANZAS", fg_color="white", text_color="#008037", font=("Arial", 20, "bold"), width=200, height=200, corner_radius=20).grid(row=1, column=0, padx=15, pady=15)
        ctk.CTkButton(self.grid_frame, text="PERSONAL", fg_color="white", text_color="#008037", font=("Arial", 20, "bold"), width=200, height=200, corner_radius=20).grid(row=1, column=1, padx=15, pady=15)
        ctk.CTkButton(self.grid_frame, text="CUENTA", fg_color="white", text_color="#008037", font=("Arial", 20, "bold"), width=180, height=430, corner_radius=20).grid(row=0, column=2, rowspan=2, padx=15)
        
        ctk.CTkButton(self, text="CERRAR SESIÓN", fg_color="white", text_color="red", command=lambda: controller.mostrar_frame("LoginFrame")).pack(side="bottom", pady=20)

# ==========================================
# FRAME 3: DASHBOARD USUARIO
# ==========================================
class UserDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(self.grid_frame, text="VENTAS", fg_color="white", text_color="#008037", font=("Arial", 20, "bold"), width=430, height=200, corner_radius=20, command=lambda: controller.mostrar_frame("VentasFrame")).grid(row=0, column=0, columnspan=2, pady=15)
        ctk.CTkButton(self.grid_frame, text="INVENTARIO", fg_color="white", text_color="#008037", font=("Arial", 20, "bold"), width=200, height=200, corner_radius=20).grid(row=1, column=0, padx=10)
        ctk.CTkButton(self.grid_frame, text="PERSONAL", fg_color="white", text_color="#008037", font=("Arial", 20, "bold"), width=200, height=200, corner_radius=20).grid(row=1, column=1, padx=10)

        ctk.CTkButton(self, text="SALIR", fg_color="white", text_color="#008037", command=lambda: controller.mostrar_frame("LoginFrame")).pack(side="bottom", pady=20)

# ==========================================
# FRAME 4: LA CAJA (TU CÓDIGO ORIGINAL)
# ==========================================
class VentasFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Variables de control originales
        self.total_actual = 0
        self.contador_id = 1
        self.venta_finalizada = False 

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # PANEL IZQUIERDO: TOTALES
        self.panel_izquierdo = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_izquierdo.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")

        self.box_total, self.lbl_total_izq = self.crear_panel_valor("Total a pagar:", "$0")
        self.box_efectivo, self.ent_efectivo = self.crear_panel_input("Efectivo")
        self.box_cambio, self.lbl_cambio = self.crear_panel_valor("Cambio", "$0")

        # BOTÓN VOLVER AGREGADO
        ctk.CTkButton(self.panel_izquierdo, text="VOLVER AL MENÚ", fg_color="#1a1a1a", text_color="white", corner_radius=15, height=45, command=self.volver_atras).pack(side="bottom", fill="x", pady=10)

        # PANEL DERECHO: FACTURACIÓN
        self.panel_derecho = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_derecho.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")

        self.frame_top_btns = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        self.frame_top_btns.pack(fill="x", pady=(0, 10))
        for txt in ["CAJA", "FACTURA\nELECTRÓNICA", "DEVOLUCIONES", "RECIBO\nPROVEEDORES"]:
            ctk.CTkButton(self.frame_top_btns, text=txt, fg_color=BLANCO, text_color="black", font=("Arial Black", 11), height=55, corner_radius=15).pack(side="left", padx=5, expand=True, fill="x")

        self.frame_tabla_bg = ctk.CTkFrame(self.panel_derecho, fg_color=BLANCO, corner_radius=25)
        self.frame_tabla_bg.pack(fill="both", expand=True)

        self.lbl_titulo_factura = ctk.CTkLabel(self.frame_tabla_bg, text="FACTURACIÓN", font=("Arial Black", 32), text_color=VERDE_TEXTO)
        self.lbl_titulo_factura.pack(pady=(20, 10))

        self.tabla = ttk.Treeview(self.frame_tabla_bg, columns=("id", "nombre", "cant", "precio"), show="headings")
        for col, head in zip(("id", "nombre", "cant", "precio"), ("ID", "NOMBRE", "CANTIDAD/ PESO", "PRECIO")):
            self.tabla.heading(col, text=head); self.tabla.column(col, anchor="center")
        
        self.tabla.tag_configure('total_row', background='#D5E8D4', font=('Arial Black', 12))
        self.tabla.pack(fill="both", expand=True, padx=40, pady=10)

        self.frame_bot_btns = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        self.frame_bot_btns.pack(fill="x", pady=(15, 0))

        self.btn_accion_principal = ctk.CTkButton(self.frame_bot_btns, text="COBRAR", fg_color=GRIS_SUAVE, text_color="black", font=("Arial Black", 16), height=65, corner_radius=18, width=280, command=self.gestionar_boton_principal)
        self.btn_accion_principal.pack(side="left", padx=(0, 10))

        self.btn_agregar = self.crear_btn_accion("AGREGAR", self.acc_agregar)
        self.btn_eliminar = self.crear_btn_accion("ELIMINAR", self.acc_eliminar)
        self.btn_modificar = self.crear_btn_accion("MODIFICAR", self.acc_modificar)
        self.btn_buscar = self.crear_btn_accion("BUSCAR", self.acc_buscar)

    # --- MÉTODOS ORIGINALES DE TU CAJA ---
    def volver_atras(self):
        dest = "AdminDashboard" if self.controller.rol_actual == "admin" else "UserDashboard"
        self.controller.mostrar_frame(dest)

    def crear_panel_valor(self, titulo, valor_inicial):
        frame = ctk.CTkFrame(self.panel_izquierdo, fg_color=BLANCO, corner_radius=25, height=170)
        frame.pack(fill="x", pady=8); frame.pack_propagate(False)
        ctk.CTkLabel(frame, text=titulo, font=("Arial Black", 18), text_color=VERDE_TEXTO).pack(anchor="w", padx=25, pady=(15, 0))
        lbl = ctk.CTkLabel(frame, text=valor_inicial, font=("Arial Black", 68), text_color=VERDE_TEXTO); lbl.pack(expand=True)
        return frame, lbl

    def crear_panel_input(self, titulo):
        frame = ctk.CTkFrame(self.panel_izquierdo, fg_color=BLANCO, corner_radius=25, height=170)
        frame.pack(fill="x", pady=8); frame.pack_propagate(False)
        ctk.CTkLabel(frame, text=titulo, font=("Arial Black", 18), text_color=VERDE_TEXTO).pack(anchor="w", padx=25, pady=(15, 0))
        ent = ctk.CTkEntry(frame, font=("Arial Black", 60), text_color=VERDE_TEXTO, fg_color="transparent", border_width=0, justify="center")
        ent.pack(expand=True, fill="x", padx=10); ent.bind("<KeyRelease>", self.formatear_efectivo)
        return frame, ent

    def crear_btn_accion(self, texto, comando):
        btn = ctk.CTkButton(self.frame_bot_btns, text=texto, fg_color=BLANCO, text_color="black", font=("Arial Black", 13), height=65, corner_radius=18, command=comando)
        btn.pack(side="left", padx=5, expand=True, fill="x")
        return btn

    def gestionar_boton_principal(self):
        if not self.venta_finalizada: self.acc_cobrar()
        else: self.nueva_venta()

    def formatear_efectivo(self, event=None):
        texto = self.ent_efectivo.get().replace("$", "").replace(".", "").strip()
        if texto.isdigit():
            formateado = f"${int(texto):,.0f}".replace(",", ".")
            self.ent_efectivo.delete(0, tk.END); self.ent_efectivo.insert(0, formateado)
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
            if 'total_row' in self.tabla.item(item, 'tags'): self.tabla.delete(item); continue
            v = self.tabla.item(item, "values")[3].replace("$", "").replace(".", "")
            self.total_actual += int(v)
        fmt = f"${self.total_actual:,.0f}".replace(",", ".")
        self.lbl_total_izq.configure(text=fmt)
        if self.total_actual > 0: self.tabla.insert("", "end", values=("", "", "TOTAL:", fmt), tags=('total_row',))
        self.calcular_cambio()

    def acc_cobrar(self):
        if self.total_actual > 0:
            if messagebox.askyesno("Facturación", "¿Finalizar cuenta?"):
                self.venta_finalizada = True
                self.lbl_titulo_factura.configure(text="FACTURA CERRADA", text_color="red")
                self.btn_accion_principal.configure(text="NUEVA VENTA", fg_color=NARANJA_NUEVA_VENTA)
        else: messagebox.showwarning("Atención", "No hay productos para cobrar.")

    def nueva_venta(self):
        self.venta_finalizada = False
        self.lbl_titulo_factura.configure(text="FACTURACIÓN", text_color=VERDE_TEXTO)
        self.btn_accion_principal.configure(text="COBRAR", fg_color=GRIS_SUAVE)
        for item in self.tabla.get_children(): self.tabla.delete(item)
        self.ent_efectivo.delete(0, tk.END); self.contador_id = 1; self.actualizar_totales()

    def acc_agregar(self):
        if self.venta_finalizada: return
        pop = ctk.CTkToplevel(self); pop.geometry("300x400"); pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text="Producto:").pack(pady=5); e_nom = ctk.CTkEntry(pop); e_nom.pack()
        ctk.CTkLabel(pop, text="Cantidad:").pack(pady=5); e_can = ctk.CTkEntry(pop); e_can.pack()
        ctk.CTkLabel(pop, text="Precio Unit:").pack(pady=5); e_pre = ctk.CTkEntry(pop); e_pre.pack()
        def guardar():
            try:
                sub = int(e_can.get()) * int(e_pre.get())
                self.tabla.insert("", 0, values=(self.contador_id, e_nom.get(), e_can.get(), f"${sub:,.0f}".replace(",", ".")))
                self.contador_id += 1; self.actualizar_totales(); pop.destroy()
            except: messagebox.showerror("Error", "Datos inválidos")
        ctk.CTkButton(pop, text="GUARDAR", command=guardar).pack(pady=20)

    def acc_modificar(self):
        if self.venta_finalizada: return
        selected = self.tabla.selection()
        if not selected or 'total_row' in self.tabla.item(selected)['tags']: return
        item_data = self.tabla.item(selected)['values']
        pop = ctk.CTkToplevel(self); pop.geometry("300x200"); pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text="Nueva Cantidad:").pack(pady=10); e_new = ctk.CTkEntry(pop); e_new.insert(0, item_data[2]); e_new.pack()
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
        if sel and 'total_row' not in self.tabla.item(sel)['tags']: self.tabla.delete(sel); self.actualizar_totales()

    def acc_buscar(self): messagebox.showinfo("Buscador", "Función de búsqueda lista.")

if __name__ == "__main__":
    app = App()
    app.mainloop()