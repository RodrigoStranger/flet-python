"""
Vista del Dashboard/Pantalla Principal
Maneja la interfaz de usuario para la pantalla principal después del login
Incluye la gestión de rutas directamente en el dashboard
"""
import flet as ft
from typing import Callable, Optional, List
from models import User, Ruta


class DashboardView:
    """
    Vista del dashboard principal
    """
    
    def __init__(self, on_logout: Callable, on_create_route: Callable):
        """
        Inicializa la vista del dashboard
        
        Args:
            on_logout: Callback para cuando se cierra sesión
            on_create_route: Callback para crear nueva ruta
        """
        self.on_logout = on_logout
        self.on_create_route = on_create_route
        self.user = None
        self.routes = []
        self.message_container = None
        self.routes_container = None
        
    def create(self, user: Optional[User] = None, routes: List[Ruta] = None) -> ft.Container:
        """
        Crea y retorna el contenido de la vista del dashboard
        
        Args:
            user: Usuario actual
            routes: Lista de rutas del usuario
            
        Returns:
            Container con la vista del dashboard
        """
        self.user = user
        self.routes = routes or []
        
        # Información del usuario
        nombre_usuario = user.nombre if user else "Usuario"
        correo_usuario = user.correo if user else ""
        
        # Crear contenedores que se actualizarán
        self.message_container = ft.Container()
        self.routes_container = ft.Container()
        
        # Actualizar contenido de rutas
        self._update_routes_content()
        
        # Contenido principal
        return ft.Container(
            content=ft.Column([
                # Header con información del usuario
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("🎉 ¡Bienvenido!", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Hola, {nombre_usuario}", size=18, color="blue"),
                            ft.Text(f"📧 {correo_usuario}", size=12, color="grey"),
                        ], spacing=5, expand=True),
                        ft.ElevatedButton(
                            "Cerrar Sesión",
                            on_click=self._on_logout_click,
                            bgcolor="red",
                            color="white",
                            width=120,
                            height=40
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=20,
                    border_radius=10,
                    bgcolor="blue50",
                    border=ft.border.all(1, "blue200")
                ),
                
                ft.Container(height=20),
                
                # Mensaje container
                self.message_container,
                
                # Título de rutas y botón crear
                ft.Container(
                    content=ft.Row([
                        ft.Text("🗺️ Mis Rutas", size=24, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Text("➕", size=16),
                                ft.Text("Nueva Ruta", size=14)
                            ], spacing=8),
                            on_click=self._on_create_route_click,
                            bgcolor="green",
                            color="white",
                            height=40
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=10)
                ),
                
                ft.Container(height=10),
                
                # Container de rutas
                self.routes_container,
                
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO
            ),
            padding=20,
            border_radius=15,
            bgcolor="white",
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color="grey400",
            ),
            expand=True
        )
    
    def _on_logout_click(self, e):
        """Maneja el click del botón de cerrar sesión"""
        self.on_logout()
    
    def _on_create_route_click(self, e):
        """Maneja el click del botón crear ruta"""
        self._show_create_route_dialog()
    
    def _update_routes_content(self):
        """Actualiza el contenido del contenedor de rutas"""
        if not self.routes:
            # Mostrar mensaje cuando no hay rutas
            self.routes_container.content = ft.Container(
                content=ft.Column([
                    ft.Text("🗺️", size=80),
                    ft.Text("No tienes rutas creadas", size=18, weight=ft.FontWeight.BOLD, color="grey"),
                    ft.Text("¡Crea tu primera ruta para comenzar!", size=14, color="grey"),
                    ft.Container(height=15),
                    ft.Text("💡 Una ruta te permite planificar un recorrido", size=12, color="grey"),
                    ft.Text("con múltiples paradas y conexiones entre ellas", size=12, color="grey"),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8),
                padding=30,
                border_radius=10,
                bgcolor="grey50",
                border=ft.border.all(1, "grey300"),
                alignment=ft.alignment.center
            )
        else:
            # Mostrar lista de rutas
            routes_list = []
            
            for i, ruta in enumerate(self.routes):
                route_card = self._create_route_card(ruta, i)
                routes_list.append(route_card)
            
            self.routes_container.content = ft.Column([
                ft.Text(f"📋 Total de rutas: {len(self.routes)}", size=14, weight=ft.FontWeight.BOLD, color="grey"),
                ft.Container(height=10),
                ft.Column(routes_list, spacing=10)
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5)
    
    def _create_route_card(self, ruta: Ruta, index: int) -> ft.Container:
        """
        Crea una tarjeta para mostrar una ruta
        
        Args:
            ruta: Objeto Ruta
            index: Índice en la lista
            
        Returns:
            Container con la tarjeta de la ruta
        """
        # Emojis para diferentes índices
        emojis = ["🗺️", "📍", "🚩", "🏁", "⭐", "🎯", "📌", "🔵", "🟢", "🟡"]
        emoji = emojis[index % len(emojis)]
        
        # Descripción truncada
        descripcion_text = ruta.descripcion if ruta.descripcion else "Sin descripción"
        if len(descripcion_text) > 80:
            descripcion_text = descripcion_text[:80] + "..."
        
        # Fecha de creación
        fecha_text = "Fecha no disponible"
        if ruta.created_at:
            try:
                fecha_text = ruta.created_at.strftime("%d/%m/%Y")
            except:
                fecha_text = str(ruta.created_at)
        
        return ft.Container(
            content=ft.Column([
                # Encabezado de la tarjeta
                ft.Row([
                    ft.Text(emoji, size=24),
                    ft.Column([
                        ft.Text(ruta.nombre, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"ID: {ruta.id}", size=10, color="grey"),
                    ], spacing=2, expand=True),
                    ft.Text("⋮", size=16, color="grey")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Descripción
                ft.Text(descripcion_text, size=12, color="grey700"),
                
                # Footer con fecha
                ft.Row([
                    ft.Text(f"📅 {fecha_text}", size=10, color="grey"),
                    ft.Row([
                        ft.Text("📋", size=12),
                        ft.Text("Ver paradas", size=10),
                    ], spacing=3)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=8),
            padding=15,
            border_radius=8,
            bgcolor="white",
            border=ft.border.all(1, "grey300"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=3,
                color="grey300",
            ),
            width=500
        )
    
    def _show_create_route_dialog(self):
        """Muestra el diálogo para crear una nueva ruta"""
        nombre_field = ft.TextField(
            label="Nombre de la ruta",
            hint_text="Ej: Ruta Centro Histórico",
            width=300
        )
        
        descripcion_field = ft.TextField(
            label="Descripción (opcional)",
            hint_text="Describe tu ruta...",
            multiline=True,
            max_lines=3,
            width=300
        )
        
        def crear_ruta(e):
            if not nombre_field.value or not nombre_field.value.strip():
                self.show_message("El nombre de la ruta es obligatorio", "error")
                return
            
            # Cerrar diálogo
            dialog.open = False
            if hasattr(e.page, 'update'):
                e.page.update()
            
            # Llamar al callback
            self.on_create_route(nombre_field.value.strip(), descripcion_field.value or "")
        
        def cancelar(e):
            dialog.open = False
            if hasattr(e.page, 'update'):
                e.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("🗺️ Crear Nueva Ruta"),
            content=ft.Column([
                nombre_field,
                ft.Container(height=10),
                descripcion_field,
            ], spacing=10, tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton("Crear Ruta", on_click=crear_ruta, bgcolor="green", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Mostrar diálogo
        if hasattr(self, '_page_ref'):
            self._page_ref.dialog = dialog
            dialog.open = True
            self._page_ref.update()
    
    def update_routes(self, routes: List[Ruta]):
        """
        Actualiza la lista de rutas mostrada
        
        Args:
            routes: Nueva lista de rutas
        """
        self.routes = routes
        self._update_routes_content()
        if hasattr(self, '_page_ref'):
            self._page_ref.update()
    
    def show_message(self, message: str, message_type: str = "info"):
        """
        Muestra un mensaje en la vista
        
        Args:
            message: Mensaje a mostrar
            message_type: Tipo de mensaje (info, success, warning, error)
        """
        color_map = {
            "info": "blue",
            "success": "green", 
            "warning": "orange",
            "error": "red"
        }
        
        bgcolor_map = {
            "info": "lightblue100",
            "success": "lightgreen100", 
            "warning": "lightyellow100",
            "error": "lightred100"
        }
        
        color = color_map.get(message_type, "blue")
        bgcolor = bgcolor_map.get(message_type, "lightblue100")
        
        icon_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        emoji = icon_map.get(message_type, "ℹ️")
        
        self.message_container.content = ft.Container(
            content=ft.Row([
                ft.Text(emoji, size=16),
                ft.Text(message, color=color, size=12),
            ], spacing=8),
            padding=12,
            border_radius=6,
            bgcolor=bgcolor,
            border=ft.border.all(1, color)
        )
        
        if hasattr(self, '_page_ref'):
            self._page_ref.update()
    
    def clear_message(self):
        """Limpia el mensaje mostrado"""
        self.message_container.content = None
        if hasattr(self, '_page_ref'):
            self._page_ref.update()
    
    def set_page_reference(self, page):
        """Establece referencia a la página para actualizaciones"""
        self._page_ref = page
    
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
