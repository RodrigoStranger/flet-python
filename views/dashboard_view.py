"""
Vista del Dashboard/Pantalla Principal
Maneja la interfaz de usuario para la pantalla principal después del login
"""
import flet as ft
from typing import Callable, Optional
from models import User


class DashboardView:
    """
    Vista del dashboard principal
    """
    
    def __init__(self, on_logout: Callable):
        """
        Inicializa la vista del dashboard
        
        Args:
            on_logout: Callback para cuando se cierra sesión
        """
        self.on_logout = on_logout
        self.user = None
        
    def create(self, user: Optional[User] = None) -> ft.Container:
        """
        Crea y retorna el contenido de la vista del dashboard
        
        Args:
            user: Usuario actual
            
        Returns:
            Container con la vista del dashboard
        """
        self.user = user
        
        # Información del usuario
        nombre_usuario = user.nombre if user else "Usuario"
        correo_usuario = user.correo if user else ""
        user_id = user.id if user else "N/A"
        
        # Información de conexión
        connection_info = ft.Container(
            content=ft.Column([
                ft.Text("✅ Sesión iniciada correctamente", size=16, color="green"),
                ft.Text("🔗 Conectado a la base de datos", size=16, color="green"),
                ft.Divider(height=20),
                ft.Text("Tours App está listo para usar", size=14, color="grey"),
                ft.Text(f"ID de usuario: {user_id}", size=12, color="grey"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor="lightgreen100",
            border_radius=10
        )
        
        # Contenido principal
        return ft.Container(
            content=ft.Column([
                ft.Text("🎉", size=60),
                ft.Text("¡Bienvenido!", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(f"Hola, {nombre_usuario}", size=20, color="blue"),
                ft.Text(f"📧 {correo_usuario}", size=14, color="grey"),
                ft.Divider(height=30),
                
                connection_info,
                
                ft.Container(height=30),
                
                # Botones de acción
                ft.Row([
                    ft.ElevatedButton(
                        "Ver Perfil",
                        on_click=self._on_profile_click,
                        bgcolor="blue",
                        color="white",
                        width=140,
                        height=40
                    ),
                    ft.ElevatedButton(
                        "Configuración",
                        on_click=self._on_settings_click,
                        bgcolor="orange",
                        color="white",
                        width=140,
                        height=40
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                
                ft.Container(height=20),
                
                ft.ElevatedButton(
                    "Cerrar Sesión",
                    on_click=self._on_logout_click,
                    bgcolor="red",
                    color="white",
                    width=300,
                    height=45
                ),
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
    
    def _on_logout_click(self, e):
        """Maneja el click del botón de cerrar sesión"""
        self.on_logout()
    
    def _on_profile_click(self, e):
        """Maneja el click del botón de perfil"""
        # Esta función se puede expandir para mostrar el perfil del usuario
        print(f"Ver perfil de: {self.user.nombre if self.user else 'Usuario'}")
    
    def _on_settings_click(self, e):
        """Maneja el click del botón de configuración"""
        # Esta función se puede expandir para mostrar configuraciones
        print("Abrir configuración")
    
    def update_user_info(self, user: User):
        """
        Actualiza la información del usuario en la vista
        
        Args:
            user: Usuario actualizado
        """
        self.user = user
        # Esta función se puede expandir para actualizar la vista en tiempo real
    
    def get_user_info(self) -> dict:
        """
        Obtiene la información del usuario actual
        
        Returns:
            Dict con la información del usuario
        """
        if not self.user:
            return {}
        
        return {
            "id": self.user.id,
            "nombre": self.user.nombre,
            "correo": self.user.correo
        }
    
    def show_notification(self, message: str, notification_type: str = "info"):
        """
        Muestra una notificación en el dashboard
        
        Args:
            message: Mensaje a mostrar
            notification_type: Tipo de notificación (info, success, warning, error)
        """
        # Esta función se puede expandir para mostrar notificaciones en el dashboard
        color_map = {
            "info": "blue",
            "success": "green", 
            "warning": "orange",
            "error": "red"
        }
        
        color = color_map.get(notification_type, "blue")
        print(f"Notificación ({color}): {message}")
    
    def add_quick_action(self, name: str, callback: Callable, icon: str = "STAR"):
        """
        Añade una acción rápida al dashboard
        
        Args:
            name: Nombre de la acción
            callback: Función a ejecutar
            icon: Icono de la acción
        """
        # Esta función se puede expandir para añadir acciones dinámicas
        print(f"Acción rápida añadida: {name}")
    
    def get_dashboard_stats(self) -> dict:
        """
        Obtiene estadísticas del dashboard
        
        Returns:
            Dict con estadísticas
        """
        # Esta función se puede expandir para mostrar estadísticas
        return {
            "session_start": "Ahora",
            "last_login": "Primera vez",
            "user_level": "Básico"
        }
