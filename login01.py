import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

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
            # Si usas .ico en Windows:
            self.iconbitmap("logo_palma.ico") 
            # Si prefieres usar .png, usa estas dos líneas en su lugar:
            # img_icon = tk.PhotoImage(file="logo_palma.png")
            # self.iconphoto(False, img_icon)
        except Exception as e:
            print(f"No se pudo cargar el icono de la ventana: {e}")

        # Base de datos de los 4 usuarios solicitados
        self.usuarios_db = {
            "edwin": {"password": "123", "rol": "admin"},
            "nicolas": {"password": "456", "rol": "usuario"},
            "alejandro": {"password": "789", "rol": "usuario"},
            "juandavid": {"password": "000", "rol": "usuario"}
        }

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
        
        # Grid de botones centrado
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        botones = [("VENTAS", 0, 0), ("INVENTARIO", 0, 1), ("FINANZAS", 1, 0), ("PERSONAL", 1, 1)]
        for texto, r, c in botones:
            ctk.CTkButton(self.grid_frame, text=texto, fg_color="white", text_color="#008037",
                          font=("Arial", 20, "bold"), width=200, height=200, corner_radius=20).grid(row=r, column=c, padx=15, pady=15)

        ctk.CTkButton(self.grid_frame, text="CUENTA", fg_color="white", text_color="#008037",
                      font=("Arial", 20, "bold"), width=180, height=430, corner_radius=20).grid(row=0, column=2, rowspan=2, padx=15)
        
        ctk.CTkButton(self, text="CERRAR SESIÓN", fg_color="white", text_color="red", command=lambda: controller.mostrar_frame("LoginFrame")).pack(side="bottom", pady=20)

# --- FRAME 3: DASHBOARD USUARIO ---
class UserDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(self.grid_frame, text="VENTAS", fg_color="white", text_color="#008037", 
                      font=("Arial", 20, "bold"), width=430, height=200, corner_radius=20).grid(row=0, column=0, columnspan=2, pady=15)
        
        ctk.CTkButton(self.grid_frame, text="INVENTARIO", fg_color="white", text_color="#008037", 
                      font=("Arial", 20, "bold"), width=200, height=200, corner_radius=20).grid(row=1, column=0, padx=10)
        
        ctk.CTkButton(self.grid_frame, text="PERSONAL", fg_color="white", text_color="#008037", 
                      font=("Arial", 20, "bold"), width=200, height=200, corner_radius=20).grid(row=1, column=1, padx=10)

        ctk.CTkButton(self, text="SALIR", fg_color="white", text_color="#008037", command=lambda: controller.mostrar_frame("LoginFrame")).pack(side="bottom", pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()