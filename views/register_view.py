"""
Vista de Registro
Maneja la interfaz de usuario para el registro de nuevos usuarios
"""
import flet as ft
from typing import Callable


class RegisterView:
    """
    Vista del formulario de registro
    """
    
    def __init__(self, on_register: Callable, on_go_to_login: Callable):
        """
        Inicializa la vista de registro
        
        Args:
            on_register: Callback para cuando se intenta registrar
            on_go_to_login: Callback para ir a la vista de login
        """
        self.on_register = on_register
        self.on_go_to_login = on_go_to_login
        
        # Controles de la vista
        self.txt_nombre = None
        self.txt_correo = None
        self.txt_clave = None
        self.msg_status = None
        
    def create(self) -> ft.Container:
        """
        Crea y retorna el contenido de la vista de registro
        
        Returns:
            Container con la vista de registro
        """
        # Campos de entrada
        self.txt_nombre = ft.TextField(
            label="Nombre completo",
            width=300,
            prefix_icon=ft.Icons.PERSON,
            on_change=self._on_field_change
        )
        
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
            on_submit=self._on_register_click
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
                ft.Text("👤", size=60),
                ft.Text("Crear Cuenta", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Registrar nuevo usuario", size=18, color="grey"),
                ft.Divider(height=30),
                
                self.txt_nombre,
                self.txt_correo,
                self.txt_clave,
                
                ft.Container(height=20),
                self.msg_status,
                ft.Container(height=20),
                
                ft.ElevatedButton(
                    "Registrarse",
                    on_click=self._on_register_click,
                    bgcolor="green",
                    color="white",
                    width=300,
                    height=45
                ),
                
                ft.Container(height=20),
                
                ft.Row([
                    ft.Text("¿Ya tienes cuenta?"),
                    ft.TextButton(
                        "Iniciar Sesión",
                        on_click=self._on_login_click
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
    
    def _on_register_click(self, e):
        """Maneja el click del botón de registro"""
        nombre = self.txt_nombre.value if self.txt_nombre.value else ""
        correo = self.txt_correo.value if self.txt_correo.value else ""
        clave = self.txt_clave.value if self.txt_clave.value else ""
        
        self.on_register(nombre, correo, clave)
    
    def _on_login_click(self, e):
        """Maneja el click del botón de ir a login"""
        self.on_go_to_login()
    
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
        if self.txt_nombre:
            self.txt_nombre.value = ""
            self.txt_nombre.update()
        
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
            "nombre": self.txt_nombre.value if self.txt_nombre.value else "",
            "correo": self.txt_correo.value if self.txt_correo.value else "",
            "clave": self.txt_clave.value if self.txt_clave.value else ""
        }
    
    def set_focus_name(self):
        """Establece el foco en el campo de nombre"""
        if self.txt_nombre:
            self.txt_nombre.focus()
    
    def set_loading_state(self, is_loading: bool):
        """
        Establece el estado de carga
        
        Args:
            is_loading: True si está cargando
        """
        # Esta función se puede expandir para deshabilitar campos durante la carga
        pass
    
    def show_field_error(self, field_name: str, error_message: str):
        """
        Muestra un error específico de un campo
        
        Args:
            field_name: Nombre del campo (nombre, correo, clave)
            error_message: Mensaje de error
        """
        # Esta función se puede expandir para mostrar errores específicos por campo
        self.show_message(f"❌ {error_message}", "red")
    
    def highlight_field(self, field_name: str, is_error: bool = True):
        """
        Resalta un campo específico
        
        Args:
            field_name: Nombre del campo
            is_error: True si es un error, False si es éxito
        """
        # Esta función se puede expandir para resaltar campos específicos
        color = "red" if is_error else "green"
        
        if field_name == "nombre" and self.txt_nombre:
            self.txt_nombre.border_color = color
            self.txt_nombre.update()
        elif field_name == "correo" and self.txt_correo:
            self.txt_correo.border_color = color
            self.txt_correo.update()
        elif field_name == "clave" and self.txt_clave:
            self.txt_clave.border_color = color
            self.txt_clave.update()
