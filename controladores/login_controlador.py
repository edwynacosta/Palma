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

        # Le pide al modelo que valide las credenciales
        datos_usuario = self.modelo.verificar_credenciales(usuario, password)

        if datos_usuario:
            rol = datos_usuario.get("rol", "").lower()
            
            # Redirección inteligente según el rol que retorne el modelo
            if rol == "admin" or rol == "administrador":
                self.vista.mostrar_frame("AdminDashboard")
            else:
                self.vista.mostrar_frame("UserDashboard")
            
            self.vista.frames["LoginFrame"].limpiar_campos()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def cambiar_pantalla(self, nombre_pantalla):
        if nombre_pantalla == "LoginFrame":
            self.vista.frames["LoginFrame"].limpiar_campos()
            
        self.vista.mostrar_frame(nombre_pantalla)