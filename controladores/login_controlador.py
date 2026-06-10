from PySide6.QtWidgets import QMessageBox

class PalmaControlador:
    def __init__(self, vista, modelo, navegador):
        self.vista = vista
        self.modelo = modelo
        self.navegador = navegador

        self.vista.btn_entrar.clicked.connect(self.procesar_login)
        self.vista.txt_usuario.returnPressed.connect(self.procesar_login)
        self.vista.txt_password.returnPressed.connect(self.procesar_login)

    def procesar_login(self):
        usuario = self.vista.txt_usuario.text().strip()
        contrasena = self.vista.txt_password.text().strip()

        if not usuario or not contrasena:
            QMessageBox.warning(self.vista, "Campos vacíos", "Por favor, llene todos los campos.")
            return

        # Consultar credenciales usando el modelo
        datos_usuario = self.modelo.verificar_credenciales(usuario, contrasena)
        
        if datos_usuario:
            id_rol = datos_usuario.get("id_rol")
            username_log = datos_usuario.get("username_log")
            
            rol_texto = "administrador" if id_rol == 1 else "cajero"
            
            datos_sesion = {
                "id_usuario": datos_usuario.get("id_usuario"),
                "username_log": username_log,
                "nombre": username_log,
                "rol": rol_texto,
                "id_rol": id_rol,
            }
            
            print(f"¡Acceso concedido! Usuario: {username_log}, Rol: {rol_texto}")
            
            # Navegar según el rol
            if id_rol == 1:  # Administrador
                self.navegador.cambiar_pantalla("AdminDashboard", datos_usuario=datos_sesion)
            elif id_rol == 2:  # Cajero
                self.navegador.cambiar_pantalla("CajeroDashboard", datos_usuario=datos_sesion)
            else:
                print(f"Rol desconocido: {id_rol}")
        else:
            QMessageBox.warning(self.vista, "Acceso denegado", "Usuario o contraseña incorrectos.")