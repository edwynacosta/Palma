import customtkinter as ctk
from modelos.usuario_modelo import UsuarioModelo
from vistas.login_vista import AppVista
from controladores.login_controlador import PalmaControlador

ctk.set_appearance_mode("light")

if __name__ == "__main__":
    # 1. Instanciamos el Modelo de datos
    modelo_sistema = UsuarioModelo()

    # 2. Instanciamos la Vista Gráfica Principal
    vista_sistema = AppVista()
    
    # 3. El Controlador une ambas partes
    controlador_sistema = PalmaControlador(vista_sistema, modelo_sistema)

    # 4. Arranca la aplicación de escritorio
    vista_sistema.mainloop()