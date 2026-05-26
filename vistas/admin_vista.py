# vistas/admin_vista.py
import tkinter as tk
import customtkinter as ctk
from datetime import datetime

try:
    from PIL import Image
    PILLOW_INSTALADO = True
except ImportError:
    PILLOW_INSTALADO = False

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#008F39") # Verde corporativo de fondo
        self.controller = controller

        # --- PALETA DE COLORES CALCADA ---
        BLANCO_TARJETA = "#FFFFFF"
        VERDE_TEXTO_TARJETA = "#008037"
        VERDE_NAV_ACTIVO = "#1E4620"  # Verde oscuro para 'Ver Admin' o tarjetas seleccionadas
        VERDE_NAV_HOVER = "#0D6E36"
        GRIS_AVATAR = "#E0E0E0"
        BLANCO_TEXTO_SECUNDARIO = "#D6EFE2"

        # ==============================================================================
        # BARRA SUPERIOR DE NAVEGACIÓN (BOTONES DE VISTA)
        # ==============================================================================
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=60, pady=(40, 10))

        # Botón "Ver Admin" (Activo por defecto)
        self.btn_ver_admin = ctk.CTkButton(
            self.nav_frame,
            text="Ver Admin",
            font=("Montserrat", 13, "bold"),
            fg_color=BLANCO_TARJETA,
            text_color=VERDE_TEXTO_TARJETA,
            width=110,
            height=35,
            corner_radius=8,
            command=self.ir_a_admin
        )
        self.btn_ver_admin.pack(side="right", padx=5)

        # Botón "Ver Cajero"
        self.btn_ver_cajero = ctk.CTkButton(
            self.nav_frame,
            text="Ver Cajero",
            font=("Montserrat", 13, "bold"),
            fg_color=VERDE_NAV_ACTIVO,
            text_color=BLANCO_TARJETA,
            hover_color=VERDE_NAV_HOVER,
            width=110,
            height=35,
            corner_radius=8,
            command=self.ir_a_cajero
        )
        self.btn_ver_cajero.pack(side="right", padx=5)


        # ==============================================================================
        # CUADRÍCULA CENTRAL DE MÓDULOS (DASHBOARD GRID)
        # ==============================================================================
        # Contenedor principal de la cuadrícula
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(expand=True, fill="both", padx=60, pady=(10, 20))

        # Configuramos los pesos de la grilla (3 columnas, 2 filas)
        self.grid_container.grid_columnconfigure(0, weight=1, uniform="grilla_admin")
        self.grid_container.grid_columnconfigure(1, weight=1, uniform="grilla_admin")
        self.grid_container.grid_columnconfigure(2, weight=1, uniform="grilla_admin")
        self.grid_container.grid_rowconfigure(0, weight=1, uniform="grilla_admin")
        self.grid_container.grid_rowconfigure(1, weight=1, uniform="grilla_admin")

        # --- TARJETA 1: VENTAS (Destacada / Verde Oscuro) ---
        self.card_ventas = ctk.CTkFrame(self.grid_container, corner_radius=35, fg_color=VERDE_NAV_ACTIVO)
        self.card_ventas.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Contenido de Ventas (Logo/Emoji + Texto)
        if PILLOW_INSTALADO:
            try:
                img_logo = ctk.CTkImage(Image.open("vistas/logo_palma.png"), size=(80, 80))
                lbl_img = ctk.CTkLabel(self.card_ventas, image=img_logo, text="")
                lbl_img.pack(expand=True, pady=(20, 0))
            except Exception:
                ctk.CTkLabel(self.card_ventas, text="🌴", font=("Arial", 50)).pack(expand=True, pady=(20, 0))
        else:
            ctk.CTkLabel(self.card_ventas, text="🌴", font=("Arial", 50)).pack(expand=True, pady=(20, 0))

        ctk.CTkLabel(
            self.card_ventas, 
            text="VENTAS", 
            font=("Montserrat", 24, "bold"), 
            text_color=BLANCO_TARJETA
        ).pack(expand=True, pady=(0, 20))

        # --- TARJETA 2: INVENTARIOS ---
        self.card_inventarios = ctk.CTkButton(
            self.grid_container,
            text="INVENTARIOS",
            font=("Montserrat", 24, "bold"),
            fg_color=BLANCO_TARJETA,
            text_color=VERDE_TEXTO_TARJETA,
            hover_color=BLANCO_TEXTO_SECUNDARIO,
            corner_radius=35,
            command=lambda: print("Módulo de Inventarios seleccionado")
        )
        self.card_inventarios.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        # --- TARJETA 3: CUENTA (Ocupa dos filas hacia abajo) ---
        self.card_cuenta = ctk.CTkButton(
            self.grid_container,
            text="CUENTA",
            font=("Montserrat", 24, "bold"),
            fg_color=BLANCO_TARJETA,
            text_color=VERDE_TEXTO_TARJETA,
            hover_color=BLANCO_TEXTO_SECUNDARIO,
            corner_radius=35,
            command=lambda: print("Módulo de Cuenta seleccionado")
        )
        self.card_cuenta.grid(row=0, column=2, rowspan=2, padx=15, pady=15, sticky="nsew")

        # --- TARJETA 4: FINANZAS ---
        self.card_finanzas = ctk.CTkButton(
            self.grid_container,
            text="FINANZAS",
            font=("Montserrat", 24, "bold"),
            fg_color=BLANCO_TARJETA,
            text_color=VERDE_TEXTO_TARJETA,
            hover_color=BLANCO_TEXTO_SECUNDARIO,
            corner_radius=35,
            command=lambda: print("Módulo de Finanzas seleccionado")
        )
        self.card_finanzas.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        # --- TARJETA 5: PERSONAL ---
        self.card_personal = ctk.CTkButton(
            self.grid_container,
            text="PERSONAL",
            font=("Montserrat", 24, "bold"),
            fg_color=BLANCO_TARJETA,
            text_color=VERDE_TEXTO_TARJETA,
            hover_color=BLANCO_TEXTO_SECUNDARIO,
            corner_radius=35,
            command=lambda: print("Módulo de Personal seleccionado")
        )
        self.grid_personal = self.card_personal.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")


        # ==============================================================================
        # BARRA INFERIOR (INFORMACIÓN DE USUARIO Y RELOJ)
        # ==============================================================================
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(fill="x", padx=60, pady=(10, 40), side="bottom")

        # Bloque Izquierdo: Info del Usuario Logueado
        self.user_info_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.user_info_frame.pack(side="left", align="center")

        # Círculo del Avatar (Simulado con una tarjeta redondeada pequeña)
        self.avatar_mock = ctk.CTkFrame(self.user_info_frame, width=54, height=54, corner_radius=27, fg_color=GRIS_AVATAR)
        self.avatar_mock.pack(side="left", padx=(0, 15))
        self.avatar_mock.pack_propagate(False)

        # Textos de usuario
        self.user_labels_frame = ctk.CTkFrame(self.user_info_frame, fg_color="transparent")
        self.user_labels_frame.pack(side="left")

        self.lbl_nombre_usuario = ctk.CTkLabel(
            self.user_labels_frame, 
            text="Nicolás Herrán", # Cambiable dinámicamente desde base de datos
            font=("Montserrat", 20, "bold"), 
            text_color=BLANCO_TARJETA
        )
        self.lbl_nombre_usuario.pack(anchor="w")

        self.lbl_rol_usuario = ctk.CTkLabel(
            self.user_labels_frame, 
            text="Administrador", 
            font=("Montserrat", 13), 
            text_color=BLANCO_TEXTO_SECUNDARIO
        )
        self.lbl_rol_usuario.pack(anchor="w")

        # Bloque Derecho: Reloj Dinámico Exacto
        self.time_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.time_frame.pack(side="right")

        self.lbl_hora = ctk.CTkLabel(
            self.time_frame, 
            text="00:00", 
            font=("Montserrat", 54, "bold"), 
            text_color=BLANCO_TARJETA,
            height=54
        )
        self.lbl_hora.pack(anchor="e")

        self.lbl_fecha = ctk.CTkLabel(
            self.time_frame, 
            text="LUNES 1 ENERO, 2026", 
            font=("Montserrat", 12, "bold"), 
            text_color=BLANCO_TARJETA
        )
        self.lbl_fecha.pack(anchor="e", pady=(5, 0))

        # Iniciamos el ciclo del reloj dinámico
        self.actualizar_reloj()

    # ==============================================================================
    # LÓGICA DINÁMICA DE LA INTERFAZ
    # ==============================================================================
    def actualizar_reloj(self):
        """Actualiza la hora y la fecha de la barra inferior de forma constante."""
        ahora = datetime.now()
        # Formato de hora: 08:09
        string_hora = ahora.strftime("%H:%M")
        
        # Formato de fecha localizado manual (Evita dependencias del OS)
        dias_semana = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
        meses_ano = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        
        dia_sem = dias_semana[ahora.weekday()]
        dia_num = ahora.day
        mes_nom = meses_ano[ahora.month - 1]
        ano_num = ahora.year
        
        string_fecha = f"{dia_sem} {dia_num} {mes_nom}, {ano_num}"

        # Seteamos los widgets de manera segura si la ventana sigue abierta
        try:
            self.lbl_hora.configure(text=string_hora)
            self.lbl_fecha.configure(text=string_fecha)
            # Re-ejecuta el método cada segundo (1000 ms)
            self.after(1000, self.actualizar_reloj)
        except Exception:
            pass

    def ir_a_admin(self):
        print("Ya estás visualizando la interfaz de Administrador.")

    def ir_a_cajero(self):
        # Aquí puedes llamar al controlador global para cambiar al Frame del cajero
        print("Cambiando a la vista del Cajero...")
        # self.controller.cambiar_vista("UserDashboard")