import customtkinter as ctk
import datetime

try:
    from PIL import Image
    PILLOW_INSTALADO = True
except ImportError:
    PILLOW_INSTALADO = False

class AppVista(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PALMA")
        self.geometry("1200().800")  # Proporción panorámica ideal para tus dashboards
        self.configure(fg_color="#008F39")  # Fondo verde corporativo Palma

        try:
            self.iconbitmap("logo_palma.ico") 
        except Exception:
            pass

        # Contenedor para el intercambio dinámico de pantallas
        self.contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor.pack(expand=True, fill="both")
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.frames = {}

    def inicializar_frames(self, controlador_global):
        # CORRECCIÓN: Verifica que las 3 clases estén escritas exactamente así:
        for F in (LoginFrame, AdminDashboard, UserDashboard):
            page_name = F.__name__
            frame = F(parent=self.contenedor, controller=controlador_global)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.mostrar_frame("LoginFrame")

    def mostrar_frame(self, page_name):
        """Eleva la pantalla solicitada al frente de la interfaz."""
        frame = self.frames[page_name]
        frame.tkraise()
        # Sincroniza el reloj si el dashboard cuenta con la función
        if hasattr(frame, "actualizar_reloj"):
            frame.actualizar_reloj()


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        VERDE_CLARO = "#D6EFE2"  # Tono exacto pastel para el fondo de los inputs
        VERDE_TEXTO = "#008037"  # Verde oscuro para fuentes y botones principales

        # Tarjeta Central Blanca Redondeada
        self.card = ctk.CTkFrame(self, corner_radius=35, fg_color="white", width=420, height=580)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # Logotipo (Palmera) con validación de librería
        if PILLOW_INSTALADO:
            try:
                logo_image = ctk.CTkImage(
                    light_image=Image.open("logo_palma.png"),
                    dark_image=Image.open("logo_palma.png"),
                    size=(130, 130) 
                )
                self.lbl_logo = ctk.CTkLabel(self.card, image=logo_image, text="")
            except Exception:
                self.lbl_logo = ctk.CTkLabel(self.card, text="🌴", font=("Arial", 70))
        else:
            self.lbl_logo = ctk.CTkLabel(self.card, text="🌴", font=("Arial", 70))
        self.lbl_logo.pack(pady=(45, 5))
        
        # Título del software
        ctk.CTkLabel(self.card, text="PALMA", text_color=VERDE_TEXTO, 
                     font=("Montserrat", 38, "bold")).pack(pady=(0, 30))

        # Inputs con bordes redondeados estilizados
        self.entry_user = ctk.CTkEntry(
            self.card, placeholder_text="Usuario",
            fg_color=VERDE_CLARO, border_width=0, text_color=VERDE_TEXTO,
            placeholder_text_color=VERDE_TEXTO, width=320, height=50, corner_radius=25,
            font=("Montserrat", 14)
        )
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(
            self.card, placeholder_text="Contraseña", show="*",
            fg_color=VERDE_CLARO, border_width=0, text_color=VERDE_TEXTO,
            placeholder_text_color=VERDE_TEXTO, width=320, height=50, corner_radius=25,
            font=("Montserrat", 14)
        )
        self.entry_pass.pack(pady=10)

        # Contenedor inferior para el botón y links
        self.bottom_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=45, pady=(30, 0))

        self.btn_entrar = ctk.CTkButton(
            self.bottom_frame, text="ENTRAR", fg_color=VERDE_TEXTO,
            hover_color="#005e28", corner_radius=18, width=130, height=48,
            font=("Montserrat", 15, "bold"),
            command=lambda: self.controller.procesar_login(self.entry_user.get(), self.entry_pass.get())
        )
        self.btn_entrar.pack(side="left")

        self.links_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.links_frame.pack(side="right")
        
        link_style = {"text_color": VERDE_TEXTO, "font": ("Montserrat", 10, "underline"), "cursor": "hand2"}
        ctk.CTkLabel(self.links_frame, text="¿Olvidaste el usuario?", **link_style).pack(anchor="e")
        ctk.CTkLabel(self.links_frame, text="¿Olvidaste la contraseña?", **link_style).pack(anchor="e")
        ctk.CTkLabel(self.links_frame, text="Ayuda", text_color=VERDE_TEXTO, font=("Montserrat", 10)).pack(anchor="e")

    def limpiar_campos(self):
        self.entry_user.delete(0, 'end')
        self.entry_pass.delete(0, 'end')


class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # --- BARRA SUPERIOR DE PRUEBAS (Alineación exacta a la derecha) ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=50, pady=(25, 0))
        
        # Estilos de botones superiores basados en la captura real
        btn_top_style = {
            "font": ("Montserrat", 11, "bold"), 
            "height": 32, 
            "corner_radius": 10
        }
        
        # Botón Cerrar Sesión en rojo suave con texto blanco
        ctk.CTkButton(
            self.top_bar, text="Cerrar Sesión", fg_color="#FF4D4D", text_color="white", 
            hover_color="#CC0000", width=120, command=lambda: controller.cambiar_pantalla("LoginFrame"), 
            **btn_top_style
        ).pack(side="right", padx=6)
        
        # Botón Ver Cajero (Blanco reactivo)
        ctk.CTkButton(
            self.top_bar, text="Ver Cajero", fg_color="white", text_color="#008F39", 
            hover_color="#E6E6E6", width=100, command=lambda: controller.cambiar_pantalla("UserDashboard"), 
            **btn_top_style
        ).pack(side="right", padx=6)
        
        # Botón Ver Admin (Indicador de vista activa del prototipo)
        ctk.CTkButton(
            self.top_bar, text="Ver Admin", fg_color="white", text_color="#008F39", 
            state="disabled", width=100, 
            **btn_top_style
        ).pack(side="right", padx=6)

        # --- GRID PRINCIPAL DE TARJETAS BLANCAS ---
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.place(relx=0.5, rely=0.49, anchor="center")

        # Configuración común para calcar las tarjetas blancas
        estilo_blanco = {
            "fg_color": "white",
            "text_color": "#008F39",
            "font": ("Montserrat", 24, "bold"), # Fuente idéntica en tamaño y grosor
            "corner_radius": 40,
            "hover_color": "#F4F4F4",
            "width": 270,
            "height": 255
        }

        # Fila 1: Ventas e Inventarios (Ambos idénticos en blanco)
        self.btn_ventas = ctk.CTkButton(self.grid_frame, text="VENTAS", **estilo_blanco)
        self.btn_ventas.grid(row=0, column=0, padx=16, pady=16)
        
        self.btn_inventarios = ctk.CTkButton(self.grid_frame, text="INVENTARIOS", **estilo_blanco)
        self.btn_inventarios.grid(row=0, column=1, padx=16, pady=16)
        
        # Fila 2: Finanzas y Personal
        self.btn_finanzas = ctk.CTkButton(self.grid_frame, text="FINANZAS", **estilo_blanco)
        self.btn_finanzas.grid(row=1, column=0, padx=16, pady=16)
        
        self.btn_personal = ctk.CTkButton(self.grid_frame, text="PERSONAL", **estilo_blanco)
        self.btn_personal.grid(row=1, column=1, padx=16, pady=16)

        # Módulo Lateral: CUENTA (Tarjeta alargada vertical que cubre ambas filas)
        self.btn_cuenta = ctk.CTkButton(
            self.grid_frame, text="CUENTA", fg_color="white", text_color="#008F39",
            font=("Montserrat", 24, "bold"), corner_radius=40, hover_color="#F4F4F4",
            width=270, height=542 # Altura simétrica perfecta sumando paddings
        )
        self.btn_cuenta.grid(row=0, column=2, rowspan=2, padx=16, pady=16)
        
        # --- FOOTER / PANEL INFERIOR (Usuario y Reloj digital) ---
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(side="bottom", fill="x", padx=60, pady=40)

        # Lado izquierdo: Identificación del Administrador en sesión
        self.user_panel = ctk.CTkFrame(self.footer, fg_color="transparent")
        self.user_panel.pack(side="left")
        
        self.avatar = ctk.CTkFrame(self.user_panel, width=60, height=60, corner_radius=30, fg_color="#E2E8F0")
        self.avatar.pack(side="left", padx=(0, 15))
        
        self.user_info = ctk.CTkFrame(self.user_panel, fg_color="transparent")
        self.user_info.pack(side="left")
        ctk.CTkLabel(self.user_info, text="Nicolas Herran", text_color="white", font=("Montserrat", 22, "bold")).pack(anchor="w")
        ctk.CTkLabel(self.user_info, text="Administrador", text_color="#D6EFE2", font=("Montserrat", 14)).pack(anchor="w")

        # Lado derecho: Reloj en formato gigante y Fecha del sistema
        self.time_panel = ctk.CTkFrame(self.footer, fg_color="transparent")
        self.time_panel.pack(side="right")
        
        self.lbl_hora = ctk.CTkLabel(self.time_panel, text="19:50", text_color="white", font=("Montserrat", 54, "bold"))
        self.lbl_hora.pack(anchor="e", pady=(0, 0))
        
        self.lbl_fecha = ctk.CTkLabel(self.time_panel, text="LUNES 25 MAYO, 2026", text_color="white", font=("Montserrat", 13, "bold"))
        self.lbl_fecha.pack(anchor="e")

    def actualizar_reloj(self):
        """Mantiene sincronizado el tiempo del sistema en mayúsculas de manera exacta."""
        ahora = datetime.datetime.now()
        self.lbl_hora.configure(text=ahora.strftime("%H:%M"))
        
        dias = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        
        fecha_text = f"{dias[ahora.weekday()]} {ahora.day} {meses[ahora.month - 1]}, {ahora.year}"
        self.lbl_fecha.configure(text=fecha_text)
        self.after(1000, self.actualizar_reloj)


class UserDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # --- BARRA SUPERIOR CAJERO ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=50, pady=(25, 0))
        
        ctk.CTkButton(
            self.top_bar, text="Cerrar sesión", fg_color="white", text_color="red", 
            hover_color="#F2F2F2", font=("Montserrat", 11, "bold"), width=110, height=30, corner_radius=8,
            command=lambda: controller.cambiar_pantalla("LoginFrame")
        ).pack(side="right")

        # --- GRID ADAPTADO A 4 MÓDULOS (DISEÑO CAJERO) ---
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.place(relx=0.5, rely=0.48, anchor="center")

        estilo_blanco_cajero = {
            "fg_color": "white",
            "text_color": "#008F39",
            "font": ("Montserrat", 20, "bold"),
            "corner_radius": 35,
            "hover_color": "#F2F2F2",
            "width": 250,
            "height": 250
        }

        # Fila Superior: Módulo VENTAS expandido cubriendo las 3 columnas de abajo
        self.btn_ventas = ctk.CTkButton(
            self.grid_frame, text="VENTAS", fg_color="white", text_color="#008F39", 
            hover_color="#F2F2F2", corner_radius=35, width=810, height=250, font=("Montserrat", 22, "bold")
        )
        self.btn_ventas.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Fila Inferior: Finanzas, Personal e Inventarios en tres columnas exactas
        ctk.CTkButton(self.grid_frame, text="FINANZAS", **estilo_blanco_cajero).grid(row=1, column=0, padx=15)
        ctk.CTkButton(self.grid_frame, text="PERSONAL", **estilo_blanco_cajero).grid(row=1, column=1, padx=15)
        ctk.CTkButton(self.grid_frame, text="INVENTARIOS", **estilo_blanco_cajero).grid(row=1, column=2, padx=15)

        # --- PANEL INFERIOR INFORMATIVO CAJERO ---
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(side="bottom", fill="x", padx=60, pady=35)

        # Datos del Cajero en sesión
        self.user_panel = ctk.CTkFrame(self.footer, fg_color="transparent")
        self.user_panel.pack(side="left")
        
        self.avatar = ctk.CTkFrame(self.user_panel, width=55, height=55, corner_radius=27, fg_color="#E0E0E0")
        self.avatar.pack(side="left", padx=(0, 15))
        
        self.user_info = ctk.CTkFrame(self.user_panel, fg_color="transparent")
        self.user_info.pack(side="left")
        ctk.CTkLabel(self.user_info, text="Edwin Acosta", text_color="white", font=("Montserrat", 20, "bold")).pack(anchor="w")
        ctk.CTkLabel(self.user_info, text="Cajero", text_color="#D6EFE2", font=("Montserrat", 13)).pack(anchor="w")

        # Sincronización del Reloj del Cajero
        self.time_panel = ctk.CTkFrame(self.footer, fg_color="transparent")
        self.time_panel.pack(side="right")
        
        self.lbl_hora = ctk.CTkLabel(self.time_panel, text="00:00", text_color="white", font=("Montserrat", 48, "bold"))
        self.lbl_hora.pack(anchor="e", pady=(0, 2))
        
        self.lbl_fecha = ctk.CTkLabel(self.time_panel, text="FECHA", text_color="white", font=("Montserrat", 13, "bold"))
        self.lbl_fecha.pack(anchor="e")

    def actualizar_reloj(self):
        """Mantiene sincronizado el tiempo del sistema en la vista de usuario."""
        ahora = datetime.datetime.now()
        self.lbl_hora.configure(text=ahora.strftime("%H:%M"))
        
        dias = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        
        fecha_text = f"{dias[ahora.weekday()]} {ahora.day} {meses[ahora.month - 1]}, {ahora.year}"
        self.lbl_fecha.configure(text=fecha_text)
        self.after(1000, self.actualizar_reloj)