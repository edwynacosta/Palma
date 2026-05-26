# controladores/login_controlador.py
from tkinter import messagebox

class PalmaControlador:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        
        # Inicializa las pantallas secundarias incrustadas
        self.vista.inicializar_frames(self)

    def procesar_login(self, usuario, password):
        if not usuario or not password:
            messagebox.showerror("Error", "Por favor, llena todos los campos")
            return

        # Le pide al modelo que valide las credenciales en la base de datos
        datos_usuario = self.modelo.verificar_credenciales(usuario, password)

        if datos_usuario:
            # Convertimos a minúsculas para evitar problemas con mayúsculas/minúsculas
            rol = str(datos_usuario.get("rol", "")).lower().strip()
            
            # 1. Primero realizamos la redirección inteligente según el rol
            if rol == "admin" or rol == "administrador":
                self.vista.mostrar_frame("AdminDashboard")
            else:
                self.vista.mostrar_frame("UserDashboard")
            
            # 2. Después de cambiar la pantalla, limpiamos los campos de forma segura
            try:
                self.vista.frames["LoginFrame"].limpiar_campos()
            except Exception:
                pass
                
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def cambiar_pantalla(self, nombre_pantalla):
        # Al cerrar sesión o volver, limpiamos primero el formulario
        if nombre_pantalla == "LoginFrame":
            try:
                self.vista.frames["LoginFrame"].limpiar_campos()
            except Exception:
                pass
            
        self.vista.mostrar_frame(nombre_pantalla)