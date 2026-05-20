# modelos/usuario_modelo.py

class UsuarioModelo:
    def __init__(self):
        # Simulamos temporalmente la base de datos sin ensuciar la estructura de la clase
        self._datos_temporales = {
            "nicolas": {"password": "456", "rol": "admin", "nombre": "Nicolás Herrán"},
            "edwin": {"password": "123", "rol": "usuario", "nombre": "Edwin Acosta"},
            "alejandro": {"password": "789", "rol": "usuario", "nombre": "Alejandro Hernández"},
            "juandavid": {"password": "000", "rol": "usuario", "nombre": "Juan David"}
        }

    def verificar_credenciales(self, usuario, password):
        user_lower = usuario.lower()
        
        # Simula la verificación lógica antes de migrar a base de datos real
        if user_lower in self._datos_temporales:
            if self._datos_temporales[user_lower]["password"] == password:
                return self._datos_temporales[user_lower]
                
        return None