# vistas/login_vista.py
import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

try:
    from PIL import Image
    PILLOW_INSTALADO = True
except ImportError:
    PILLOW_INSTALADO = False

# ==============================================================================
# SCRIPT DE CARGA AUTOMÁTICA DE FUENTES LOCALES (Equivalente a Google Fonts)
# ==============================================================================
def cargar_fuentes_locales():
    """
    Busca los archivos TTF de Montserrat en la carpeta 'fuentes' y los 
    registra de forma privada en el sistema operativo para que Tkinter los use.
    """
    try:
        # Si estás en Windows, usamos la API nativa de gdi32
        if os.name == 'nt':
            import ctypes
            from ctypes import wintypes
            
            # Directorio donde deben estar tus fuentes descargadas de Google Fonts
            dir_fuentes = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fuentes")
            
            if os.path.exists(dir_fuentes):
                for archivo in os.listdir(dir_fuentes):
                    if archivo.endswith(".ttf"):
                        ruta_fuente = os.path.join(dir_fuentes, archivo)
                        # Carga la fuente en la sesión actual de Windows
                        ctypes.windll.gdi32.AddFontResourceExW(
                            ctypes.byref(ctypes.create_unicode_buffer(ruta_fuente)), 
                            0x10, # FR_PRIVATE: Solo disponible para este proceso
                            0
                        )
    except Exception as e:
        print(f"Nota: No se pudo cargar la fuente Montserrat dinámicamente ({e}). Se usará la de defecto.")

# Ejecutamos la carga al importar el módulo
cargar_fuentes_locales()


class AppVista(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PALMA")
        
        # Geometría corregida panorámica 1200x800
        self.geometry("1200x800")  
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
        # Lista iterable con corchetes corregida para evitar errores
        for F in [LoginFrame]:
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

        # --- PALETA DE COLORES EXACTA DE LAS IMÁGENES ---
        VERDE_FONDO_INPUT = "#DCEFE3"   # Tono pastel de fondo para las cajas
        VERDE_TEXTO_INPUT = "#5C8D70"   # Color del texto de placeholders en reposo
        VERDE_CORPORATIVO = "#008037"   # El verde oscuro de "PALMA" y del botón ENTRAR
        VERDE_BORDE_FOCUS = "#0D6E36"   # Borde oscuro para resaltar
        VERDE_HOVER_BOTON = "#005E28"   # Tono al pasar el mouse por encima del botón
        VERDE_GLOW_BOTON  = "#A1D9B7"   # Brillo exterior/sombra que rodea al botón ENTRAR

        # Tarjeta Central Blanca Redondeada
        self.card = ctk.CTkFrame(self, corner_radius=35, fg_color="white", width=420, height=580)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # Logotipo (Validación de imagen buscando en la carpeta 'vistas')
        if PILLOW_INSTALADO:
            try:
                logo_image = ctk.CTkImage(
                    light_image=Image.open("vistas/logo_palma.png"),
                    dark_image=Image.open("vistas/logo_palma.png"),
                    size=(130, 130) 
                )
                self.lbl_logo = ctk.CTkLabel(self.card, image=logo_image, text="")
            except Exception:
                self.lbl_logo = ctk.CTkLabel(self.card, text="🌴", font=("Arial", 70))
        else:
            self.lbl_logo = ctk.CTkLabel(self.card, text="🌴", font=("Arial", 70))
        self.lbl_logo.pack(pady=(45, 5))
        
        # Título del Software
        ctk.CTkLabel(
            self.card, 
            text="PALMA", 
            text_color=VERDE_CORPORATIVO, 
            font=("Montserrat", 38, "bold")
        ).pack(pady=(0, 30))

        # --- INPUTS ESTILIZADOS SEGUROS Y COMPATIBLES ---
        self.entry_user = ctk.CTkEntry(
            self.card, 
            placeholder_text="Usuario",
            fg_color=VERDE_FONDO_INPUT, 
            border_width=1,                  
            border_color=VERDE_FONDO_INPUT,  
            text_color=VERDE_BORDE_FOCUS,
            placeholder_text_color=VERDE_TEXTO_INPUT, 
            width=320, 
            height=50, 
            corner_radius=25,
            font=("Montserrat", 14)
        )
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(
            self.card, 
            placeholder_text="Contraseña", 
            show="*",
            fg_color=VERDE_FONDO_INPUT, 
            border_width=1,
            border_color=VERDE_FONDO_INPUT,
            text_color=VERDE_BORDE_FOCUS,
            placeholder_text_color=VERDE_TEXTO_INPUT, 
            width=320, 
            height=50, 
            corner_radius=25,
            font=("Montserrat", 14)
        )
        self.entry_pass.pack(pady=10)

        # Contenedor inferior para el botón y links
        self.bottom_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=45, pady=(30, 0))

        # --- BOTÓN ENTRAR ---
        self.btn_entrar = ctk.CTkButton(
            self.bottom_frame, 
            text="ENTRAR", 
            fg_color=VERDE_CORPORATIVO,
            hover_color=VERDE_HOVER_BOTON, 
            corner_radius=18, 
            width=130, 
            height=48,
            font=("Montserrat", 15, "bold"), 
            border_width=4,                
            border_color=VERDE_GLOW_BOTON,  
            command=lambda: self.controller.procesar_login(self.entry_user.get(), self.entry_pass.get())
        )
        self.btn_entrar.pack(side="left")

        # Contenedor derecho para los hipervínculos de ayuda
        self.links_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.links_frame.pack(side="right")
        
        link_style = {
            "text_color": VERDE_BORDE_FOCUS, 
            "font": ("Montserrat", 10, "bold"), 
            "cursor": "hand2"
        }
        
        ctk.CTkLabel(self.links_frame, text="¿Olvidaste el usuario?", **link_style).pack(anchor="e")
        ctk.CTkLabel(self.links_frame, text="¿Olvidaste la contraseña?", **link_style).pack(anchor="e")
        ctk.CTkLabel(self.links_frame, text="Ayuda", text_color=VERDE_BORDE_FOCUS, font=("Montserrat", 10, "bold"), cursor="hand2").pack(anchor="e")

    def limpiar_campos(self):
        """Limpia los inputs de forma segura tras una sesión."""
        self.entry_user.delete(0, 'end')
        self.entry_pass.delete(0, 'end')