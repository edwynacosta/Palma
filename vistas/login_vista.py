import customtkinter as ctk
from PIL import Image

class AppVista(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PALMA")
        self.geometry("1000x700")
        self.configure(fg_color="#008F39") 

        try:
            self.iconbitmap("logo_palma.ico") 
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")

        # Contenedor para el intercambio dinámico de pantallas
        self.contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor.pack(expand=True, fill="both")
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.frames = {}

    def inicializar_frames(self, controlador_global):
        # 1. Creamos e indexamos las tres vistas de tu interfaz
        for F in (LoginFrame, AdminDashboard, UserDashboard):
            page_name = F.__name__
            frame = F(parent=self.contenedor, controller=controlador_global)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # 2. ¡AQUÍ ESTÁ EL TRUCO! 
        # Forzamos a que la pantalla inicial en pantalla sea SIEMPRE el Login
        self.mostrar_frame("LoginFrame")

    def mostrar_frame(self, page_name):
        """Eleva la pantalla solicitada al frente de la interfaz."""
        frame = self.frames[page_name]
        frame.tkraise()

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        VERDE_CLARO = "#A8E6CF"
        VERDE_TEXTO = "#008037"

        self.card = ctk.CTkFrame(self, corner_radius=30, fg_color="white", width=420, height=580)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        try:
            logo_image = ctk.CTkImage(
                light_image=Image.open("logo_palma.png"),
                dark_image=Image.open("logo_palma.png"),
                size=(120, 120) 
            )
            self.lbl_logo = ctk.CTkLabel(self.card, image=logo_image, text="")
        except Exception:
            self.lbl_logo = ctk.CTkLabel(self.card, text="🌴", font=("Arial", 60))
        self.lbl_logo.pack(pady=(40, 5))
        
        ctk.CTkLabel(self.card, text="PALMA", text_color=VERDE_TEXTO, 
                     font=("Fredoka One", 32, "bold")).pack(pady=(0, 20))
        
        self.combo_tipo = ctk.CTkComboBox(
            self.card, values=["Administrador", "Usuario"],
            fg_color=VERDE_CLARO, border_color=VERDE_CLARO, 
            button_color=VERDE_CLARO, button_hover_color="#c6ffdf",
            dropdown_fg_color="white", text_color=VERDE_TEXTO,
            corner_radius=22, width=280, height=45
        )
        self.combo_tipo.set("Tipo de Usuario")
        self.combo_tipo.pack(pady=10)

        self.entry_user = ctk.CTkEntry(
            self.card, placeholder_text="Usuario",
            fg_color=VERDE_CLARO, border_width=0, text_color=VERDE_TEXTO,
            placeholder_text_color=VERDE_TEXTO, width=340, height=55, corner_radius=27
        )
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(
            self.card, placeholder_text="Contraseña", show="*",
            fg_color=VERDE_CLARO, border_width=0, text_color=VERDE_TEXTO,
            placeholder_text_color=VERDE_TEXTO, width=340, height=55, corner_radius=27
        )
        self.entry_pass.pack(pady=10)

        self.bottom_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=40, pady=25)

        self.btn_entrar = ctk.CTkButton(
            self.bottom_frame, text="ENTRAR", fg_color=VERDE_TEXTO,
            hover_color="#005e28", corner_radius=15, width=130, height=50,
            font=("Arial", 16, "bold"),
            command=lambda: self.controller.procesar_login(self.entry_user.get(), self.entry_pass.get())
        )
        self.btn_entrar.pack(side="left")

        self.links_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.links_frame.pack(side="right")
        
        ctk.CTkLabel(self.links_frame, text="¿Olvidaste el usuario?", text_color=VERDE_TEXTO, font=("Arial", 10, "underline"), cursor="hand2").pack(anchor="e")
        ctk.CTkLabel(self.links_frame, text="¿Olvidaste la contraseña?", text_color=VERDE_TEXTO, font=("Arial", 10, "underline"), cursor="hand2").pack(anchor="e")
        ctk.CTkLabel(self.links_frame, text="Ayuda", text_color=VERDE_TEXTO, font=("Arial", 10)).pack(anchor="e")

    def limpiar_campos(self):
        self.entry_user.delete(0, 'end')
        self.entry_pass.delete(0, 'end')


class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        botones = [("VENTAS", 0, 0), ("INVENTARIO", 0, 1), ("FINANZAS", 1, 0), ("PERSONAL", 1, 1)]
        for texto, r, c in botones:
            ctk.CTkButton(self.grid_frame, text=texto, fg_color="white", text_color="#008037",
                          font=("Arial", 20, "bold"), width=200, height=200, corner_radius=20).grid(row=r, column=c, padx=15, pady=15)

        ctk.CTkButton(self.grid_frame, text="CUENTA", fg_color="white", text_color="#008037",
                      font=("Arial", 20, "bold"), width=180, height=430, corner_radius=20).grid(row=0, column=2, rowspan=2, padx=15)
        
        ctk.CTkButton(self, text="CERRAR SESIÓN", fg_color="white", text_color="red", 
                      command=lambda: controller.cambiar_pantalla("LoginFrame")).pack(side="bottom", pady=20)


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

        ctk.CTkButton(self, text="SALIR", fg_color="white", text_color="#008037", 
                      command=lambda: controller.cambiar_pantalla("LoginFrame")).pack(side="bottom", pady=20)