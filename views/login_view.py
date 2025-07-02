"""
Vista de Login
Maneja la interfaz de usuario para el inicio de sesión
"""
import flet as ft
from typing import Callable, Optional


class LoginView:
    """
    Vista del formulario de login
    """
    
    def __init__(self, on_login: Callable, on_go_to_register: Callable):
        """
        Inicializa la vista de login
        
        Args:
            on_login: Callback para cuando se intenta hacer login
            on_go_to_register: Callback para ir a la vista de registro
        """
        self.on_login = on_login
        self.on_go_to_register = on_go_to_register
        
        # Controles de la vista
        self.txt_correo = None
        self.txt_clave = None
        self.msg_status = None
        
    def create(self) -> ft.Container:
        """
        Crea y retorna el contenido de la vista de login
        
        Returns:
            Container con la vista de login
        """
        # Campos de entrada
        self.txt_correo = ft.TextField(
            label="Correo electrónico",
            width=300,
            prefix_icon=ft.Icons.EMAIL,
            keyboard_type=ft.KeyboardType.EMAIL,
            on_change=self._on_field_change
        )
        
        self.txt_clave = ft.TextField(
            label="Contraseña",
            width=300,
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            on_change=self._on_field_change,
            on_submit=self._on_login_click
        )
        
        # Mensaje de estado
        self.msg_status = ft.Text(
            "",
            color="red",
            size=14,
            text_align=ft.TextAlign.CENTER,
            width=300
        )
        
        # Contenido principal
        return ft.Container(
            content=ft.Column([
                ft.Text("🏢", size=60),
                ft.Text("Tours App", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Iniciar Sesión", size=18, color="grey"),
                ft.Divider(height=30),
                
                self.txt_correo,
                self.txt_clave,
                
                ft.Container(height=20),
                self.msg_status,
                ft.Container(height=20),
                
                ft.ElevatedButton(
                    "Iniciar Sesión",
                    on_click=self._on_login_click,
                    bgcolor="blue",
                    color="white",
                    width=300,
                    height=45
                ),
                
                ft.Container(height=20),
                
                ft.Row([
                    ft.Text("¿No tienes cuenta?"),
                    ft.TextButton(
                        "Registrarse",
                        on_click=self._on_register_click
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
            ),
            padding=40,
            border_radius=15,
            bgcolor="white",
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color="grey400",
            )
        )
    
    def _on_login_click(self, e):
        """Maneja el click del botón de login"""
        correo = self.txt_correo.value if self.txt_correo.value else ""
        clave = self.txt_clave.value if self.txt_clave.value else ""
        
        self.on_login(correo, clave)
    
    def _on_register_click(self, e):
        """Maneja el click del botón de ir a registro"""
        self.on_go_to_register()
    
    def _on_field_change(self, e):
        """Maneja cambios en los campos para limpiar mensajes"""
        if self.msg_status and self.msg_status.value:
            self.msg_status.value = ""
            self.msg_status.update()
    
    def show_message(self, message: str, color: str = "red"):
        """
        Muestra un mensaje en la vista
        
        Args:
            message: Mensaje a mostrar
            color: Color del mensaje
        """
        if self.msg_status:
            self.msg_status.value = message
            self.msg_status.color = color
            self.msg_status.update()
    
    def clear_fields(self):
        """Limpia los campos del formulario"""
        if self.txt_correo:
            self.txt_correo.value = ""
            self.txt_correo.update()
        
        if self.txt_clave:
            self.txt_clave.value = ""
            self.txt_clave.update()
        
        if self.msg_status:
            self.msg_status.value = ""
            self.msg_status.update()
    
    def get_data(self) -> dict:
        """
        Obtiene los datos del formulario
        
        Returns:
            Dict con los datos del formulario
        """
        return {
            "correo": self.txt_correo.value if self.txt_correo.value else "",
            "clave": self.txt_clave.value if self.txt_clave.value else ""
        }
    
    def set_focus_email(self):
        """Establece el foco en el campo de correo"""
        if self.txt_correo:
            self.txt_correo.focus()
    
    def set_loading_state(self, is_loading: bool):
        """
        Establece el estado de carga
        
        Args:
            is_loading: True si está cargando
        """
        # Esta función se puede expandir para deshabilitar campos durante la carga
        pass
