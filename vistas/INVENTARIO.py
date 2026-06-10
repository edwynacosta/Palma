import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from tkinter import ttk

# Configuración de apariencia global
ctk.set_appearance_mode("light")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PALMA")
        self.geometry("1000x700")
        self.configure(fg_color="#008F39") # Verde del fondo exterior

# --- CONFIGURACIÓN DEL ICONO DE LA VENTANA ---
        try:
            # Si usas .ico
            self.iconbitmap("logo_palma.ico") 
        except Exception as e:
            print(f"No se pudo cargar el icono de la ventana: {e}")

        # Base de datos de los 4 usuarios solicitados
        self.usuarios_db = {
            "edwin": {"password": "123", "rol": "admin"},
            "nicolas": {"password": "456", "rol": "usuario"},
            "alejandro": {"password": "789", "rol": "usuario"},
            "juandavid": {"password": "000", "rol": "usuario"}
        }
        self.productos = []
        # Contenedor principal para el cambio de frames
        self.contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor.pack(expand=True, fill="both")

        self.frames = {}

        # Inicialización de las pantallas
        for F in (LoginFrame, AdminDashboard, UserDashboard):
            page_name = F.__name__
            frame = F(parent=self.contenedor, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Configurar expansión del grid
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.mostrar_frame("LoginFrame")

    def mostrar_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

# --- FRAME 1: LOGIN (CON LOS CAMPOS DE CÁPSULA EXACTOS) ---
class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Colores constantes para los inputs
        VERDE_CLARO = "#A8E6CF"
        VERDE_TEXTO = "#008037"

        # Tarjeta blanca central siempre centrada
        self.card = ctk.CTkFrame(self, corner_radius=30, fg_color="white", width=420, height=580)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # --- SECCIÓN DEL LOGO (IMAGEN) ---
        try:
            # Cargamos la imagen. Ajusta size=(ancho, alto) según tu logo
            logo_image = ctk.CTkImage(
                light_image=Image.open("logo_palma.png"),
                dark_image=Image.open("logo_palma.png"),
                size=(120, 120) 
            )
            self.lbl_logo = ctk.CTkLabel(self.card, image=logo_image, text="")
        except Exception:
            # Si no encuentra la imagen, pone el emoji por defecto para no romper el programa
            self.lbl_logo = ctk.CTkLabel(self.card, text="🌴", font=("Arial", 60))
        
        self.lbl_logo.pack(pady=(40, 5))
        
        # Título debajo del logo
        ctk.CTkLabel(self.card, text="PALMA", text_color=VERDE_TEXTO, 
                     font=("Fredoka One", 32, "bold")).pack(pady=(0, 20))
        
        # 1. Selector Tipo de Usuario (ESTILO CÁPSULA)
        self.combo_tipo = ctk.CTkComboBox(
            self.card, values=["Administrador", "Usuario"],
            fg_color=VERDE_CLARO, border_color=VERDE_CLARO, 
            button_color=VERDE_CLARO, button_hover_color="#c6ffdf",
            dropdown_fg_color="white", text_color=VERDE_TEXTO,
            corner_radius=22, width=280, height=45
        )
        self.combo_tipo.set("Tipo de Usuario")
        self.combo_tipo.pack(pady=10)

        # 2. Campo Usuario (ESTILO CÁPSULA)
        self.entry_user = ctk.CTkEntry(
            self.card, placeholder_text="Usuario",
            fg_color=VERDE_CLARO, border_width=0, text_color=VERDE_TEXTO,
            placeholder_text_color=VERDE_TEXTO, width=340, height=55, corner_radius=27
        )
        self.entry_user.pack(pady=10)

        # 3. Campo Contraseña (ESTILO CÁPSULA)
        self.entry_pass = ctk.CTkEntry(
            self.card, placeholder_text="Contraseña", show="*",
            fg_color=VERDE_CLARO, border_width=0, text_color=VERDE_TEXTO,
            placeholder_text_color=VERDE_TEXTO, width=340, height=55, corner_radius=27
        )
        self.entry_pass.pack(pady=10)

        # Sección inferior: Botón y Links
        self.bottom_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=40, pady=25)

        self.btn_entrar = ctk.CTkButton(
            self.bottom_frame, text="ENTRAR", fg_color=VERDE_TEXTO,
            hover_color="#005e28", corner_radius=15, width=130, height=50,
            font=("Arial", 16, "bold"), command=self.verificar
        )
        self.btn_entrar.pack(side="left")

        self.links_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.links_frame.pack(side="right")
        
        ctk.CTkLabel(self.links_frame, text="¿Olvidaste el usuario?", text_color=VERDE_TEXTO, font=("Arial", 10, "underline"), cursor="hand2").pack(anchor="e")
        ctk.CTkLabel(self.links_frame, text="¿Olvidaste la contraseña?", text_color=VERDE_TEXTO, font=("Arial", 10, "underline"), cursor="hand2").pack(anchor="e")
        ctk.CTkLabel(self.links_frame, text="Ayuda", text_color=VERDE_TEXTO, font=("Arial", 10)).pack(anchor="e")

    def verificar(self):
        user = self.entry_user.get().lower()
        pw = self.entry_pass.get()
        db = self.controller.usuarios_db

        if user in db and db[user]["password"] == pw:
            if db[user]["rol"] == "admin":
                self.controller.mostrar_frame("AdminDashboard")
            else:
                self.controller.mostrar_frame("UserDashboard")
            self.entry_user.delete(0, 'end')
            self.entry_pass.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Datos incorrectos")

# --- FRAME 2: DASHBOARD ADMIN ---
class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid central
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        botones = [
            ("VENTAS", 0, 0),
            ("INVENTARIO", 0, 1),
            ("FINANZAS", 1, 0),
            ("PERSONAL", 1, 1)
        ]

        for texto, r, c in botones:
            if texto == "INVENTARIO":
                boton = ctk.CTkButton(
                    self.grid_frame,
                    text=texto,
                    fg_color="white",
                    text_color="#008037",
                    font=("Arial", 20, "bold"),
                    width=200,
                    height=200,
                    corner_radius=20,
                    command=self.abrir_inventario
                )
            else:
                boton = ctk.CTkButton(
                    self.grid_frame,
                    text=texto,
                    fg_color="white",
                    text_color="#008037",
                    font=("Arial", 20, "bold"),
                    width=200,
                    height=200,
                    corner_radius=20
                )

            boton.grid(row=r, column=c, padx=15, pady=15)

        ctk.CTkButton(
            self,
            text="CERRAR SESIÓN",
            fg_color="white",
            text_color="red",
            command=lambda: controller.mostrar_frame("LoginFrame")
        ).pack(side="bottom", pady=20)

    # =========================
    # SISTEMA INVENTARIO SIN BD
    # =========================
    def abrir_inventario(self):

        inv = ctk.CTkToplevel(self)
        inv.title("Gestión de Inventario")
        inv.geometry("950x550")
        inv.grab_set()

        inv.columnconfigure(1, weight=1)
        inv.rowconfigure(0, weight=1)

        # ----- FORMULARIO IZQUIERDO -----
        f_reg = ctk.CTkFrame(inv, corner_radius=20)
        f_reg.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(
            f_reg,
            text="NUEVO PRODUCTO",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        e_cod = ctk.CTkEntry(f_reg, placeholder_text="Código de Barras", width=200)
        e_cod.pack(pady=10)

        e_nom = ctk.CTkEntry(f_reg, placeholder_text="Nombre", width=200)
        e_nom.pack(pady=10)

        e_pre = ctk.CTkEntry(f_reg, placeholder_text="Precio", width=200)
        e_pre.pack(pady=10)

        e_sto = ctk.CTkEntry(f_reg, placeholder_text="Stock Inicial", width=200)
        e_sto.pack(pady=10)

        # ----- TABLA DERECHA -----
        f_tab = ctk.CTkFrame(inv, corner_radius=20)
        f_tab.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")

        t_inv = ttk.Treeview(
            f_tab,
            columns=("c", "n", "p", "s"),
            show="headings"
        )

        for col, h in zip(("c", "n", "p", "s"),
                          ("Código", "Nombre", "Precio", "Stock")):
            t_inv.heading(col, text=h)
            t_inv.column(col, width=120, anchor="center")

        t_inv.pack(fill="both", expand=True, padx=10, pady=10)

        # ----- FUNCIONES -----

        def cargar_datos():
            t_inv.delete(*t_inv.get_children())
            for producto in self.controller.productos:
                t_inv.insert("", "end", values=producto)

        def guardar():

            codigo = e_cod.get().strip()
            nombre = e_nom.get().strip()
            precio = e_pre.get().strip()
            stock = e_sto.get().strip()

            if not codigo or not nombre or not precio or not stock:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return

            try:
                precio = float(precio)
                stock = int(stock)

                if precio < 0 or stock < 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror("Error", "Precio debe ser número decimal y Stock número entero positivo")
                return

            # Buscar si existe
            existe = False
            for i in range(len(self.controller.productos)):
                if self.controller.productos[i][0] == codigo:
                    self.controller.productos[i] = (codigo, nombre, precio, stock)
                    existe = True
                    break

            if not existe:
                self.controller.productos.append((codigo, nombre, precio, stock))

            cargar_datos()

            # Limpiar campos
            e_cod.delete(0, "end")
            e_nom.delete(0, "end")
            e_pre.delete(0, "end")
            e_sto.delete(0, "end")

            messagebox.showinfo("Éxito", "Producto guardado correctamente")

        def eliminar():

            seleccionado = t_inv.selection()

            if not seleccionado:
                messagebox.showwarning("Aviso", "Seleccione un producto para eliminar")
                return

            item_id = seleccionado[0]  # 👈 AQUÍ ESTABA EL ERROR
            valores = t_inv.item(item_id, "values")
            codigo = valores[0]

            # Eliminar de la lista
            self.controller.productos = [
                p for p in self.controller.productos if p[0] != codigo
            ]

            cargar_datos()

            messagebox.showinfo("Eliminado", "Producto eliminado correctamente")

        # ----- BOTONES -----

        ctk.CTkButton(
            f_reg,
            text="GUARDAR",
            command=guardar
        ).pack(pady=10)

        ctk.CTkButton(
            f_reg,
            text="ELIMINAR SELECCIONADO",
            fg_color="red",
            command=eliminar
        ).pack(pady=5)

        cargar_datos()
# --- FRAME 3: DASHBOARD USUARIO ---
class UserDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        # -------- PRIMERA FILA --------
        ctk.CTkButton(
            self.grid_frame,
            text="VENTAS",
            fg_color="white",
            text_color="#008037",
            font=("Arial", 20, "bold"),
            width=430,
            height=200,
            corner_radius=20
        ).grid(row=0, column=0, columnspan=2, pady=15)

        # -------- SEGUNDA FILA --------
        ctk.CTkButton(
            self.grid_frame,
            text="INVENTARIO",
            fg_color="white",
            text_color="#008037",
            font=("Arial", 20, "bold"),
            width=200,
            height=200,
            corner_radius=20,
            command=self.ver_inventario  # 👈 SOLO LECTURA
        ).grid(row=1, column=0, padx=10)

        ctk.CTkButton(
            self.grid_frame,
            text="PERSONAL",
            fg_color="white",
            text_color="#008037",
            font=("Arial", 20, "bold"),
            width=200,
            height=200,
            corner_radius=20
        ).grid(row=1, column=1, padx=10)

        # -------- BOTÓN SALIR --------
        ctk.CTkButton(
            self,
            text="SALIR",
            fg_color="white",
            text_color="#008037",
            command=lambda: controller.mostrar_frame("LoginFrame")
        ).pack(side="bottom", pady=20)

    # ==============================
    # INVENTARIO SOLO LECTURA
    # ==============================
    def ver_inventario(self):

        inv = ctk.CTkToplevel(self)
        inv.title("Inventario (Solo lectura)")
        inv.geometry("800x500")
        inv.grab_set()

        f_tab = ctk.CTkFrame(inv, corner_radius=20)
        f_tab.pack(fill="both", expand=True, padx=20, pady=20)

        t_inv = ttk.Treeview(
            f_tab,
            columns=("c", "n", "p", "s"),
            show="headings"
        )

        for col, h in zip(("c", "n", "p", "s"),
                          ("Código", "Nombre", "Precio", "Stock")):
            t_inv.heading(col, text=h)
            t_inv.column(col, width=150, anchor="center")

        t_inv.pack(fill="both", expand=True, padx=10, pady=10)

        # Cargar productos (solo mostrar)
        for producto in self.controller.productos:
            t_inv.insert("", "end", values=producto)


            
if __name__ == "__main__":
    app = App()
    app.mainloop()