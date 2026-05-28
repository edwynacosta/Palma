# controladores/login_controlador.py

class PalmaControlador:
    def __init__(self, vista, modelo, navegador):
        self.vista = vista
        self.modelo = modelo
        self.navegador = navegador  # El QStackedWidget de main.py

        # Conectar señales nativas de PySide6 (Click y Enter)
        self.vista.btn_entrar.clicked.connect(self.procesar_login)
        self.vista.txt_usuario.returnPressed.connect(self.procesar_login)
        self.vista.txt_password.returnPressed.connect(self.procesar_login)

    def procesar_login(self):
        usuario = self.vista.txt_usuario.text().strip()
        contrasena = self.vista.txt_password.text().strip()

        if not usuario or not contrasena:
            print("⚠️ Por favor, llene todos los campos.")
            return

        # Consultar las credenciales en la nube de Aiven (Devuelve el string del rol)
        rol_usuario = self.modelo.verificar_credenciales(usuario, contrasena)
        
        if rol_usuario:
            rol_limpio = rol_usuario.lower().strip()
            print(f"✅ ¡Acceso concedido! Rol detectado: {rol_limpio}")
            
            # Redirección dinámica basada en roles mediante el Stack de Qt
            if rol_limpio == "administrador":
                self.navegador.cambiar_pantalla("AdminDashboard")
            elif rol_limpio == "cajero":
                self.navegador.cambiar_pantalla("CajeroDashboard")
            else:
                print(f"⚠️ Rol desconocido '{rol_limpio}'. No hay interfaz asignada.")
        else:
            print("❌ Usuario o contraseña incorrectos.")