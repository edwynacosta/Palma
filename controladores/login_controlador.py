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

        datos_usuario = self.modelo.verificar_credenciales(usuario, password)

        if datos_usuario:
            # Convertimos a string y limpiamos espacios
            rol = str(datos_usuario.get("rol", "")).lower().strip()
            
            # CORREGIDO: Ahora acepta el "1" que viene de tu base de datos
            if rol in ["1", "admin", "administrador"]:
                self.vista.mostrar_frame("AdminDashboard")
            else:
                messagebox.showinfo(
                    "Acceso Exitoso", 
                    f"Bienvenido/a. El rol '{rol.upper()}' está activo, pero su interfaz está en desarrollo."
                )
            
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