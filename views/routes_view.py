"""
Vista de Gestión de Rutas
Maneja la interfaz para ver y gestionar rutas del usuario
"""
import flet as ft
from typing import Callable, List, Optional
from models import User, Ruta


class RoutesView:
    """
    Vista para gestionar rutas del usuario
    """
    
    def __init__(self, on_create_route: Callable, on_back_to_dashboard: Callable):
        """
        Inicializa la vista de rutas
        
        Args:
            on_create_route: Callback para crear nueva ruta
            on_back_to_dashboard: Callback para volver al dashboard
        """
        self.on_create_route = on_create_route
        self.on_back_to_dashboard = on_back_to_dashboard
        self.user = None
        self.routes = []
        self.message_container = None
        self.routes_container = None
        
    def create(self, user: User, routes: List[Ruta]) -> ft.Container:
        """
        Crea y retorna el contenido de la vista de rutas
        
        Args:
            user: Usuario actual
            routes: Lista de rutas del usuario
            
        Returns:
            Container con la vista de rutas
        """
        self.user = user
        self.routes = routes
        
        # Crear contenedores que se actualizarán
        self.message_container = ft.Container()
        self.routes_container = ft.Container()
        
        # Título y información del usuario
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton(
                        content=ft.Row([
                            ft.Text("⬅️", size=16),
                            ft.Text("Volver", size=14)
                        ], spacing=5),
                        on_click=self._on_back_click
                    ),
                    ft.Text("🗺️ Mis Rutas", size=28, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Text(f"Usuario: {user.nombre}", size=16, color="grey"),
                ft.Divider(height=20),
            ], spacing=10),
            padding=ft.padding.only(bottom=20)
        )
        
        # Botón para crear nueva ruta
        create_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row([
                    ft.Text("➕", size=20),  # Emoji más
                    ft.Text("Crear Nueva Ruta", size=16)
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                on_click=self._on_create_route_click,
                bgcolor="green",
                color="white",
                width=300,
                height=50
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.only(bottom=20)
        )
        
        # Actualizar contenido de rutas
        self._update_routes_content()
        
        # Contenido principal
        return ft.Container(
            content=ft.Column([
                header,
                self.message_container,
                create_button,
                self.routes_container,
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
            ),
            expand=True
        )
    
    def _update_routes_content(self):
        """Actualiza el contenido del contenedor de rutas"""
        if not self.routes:
            # Mostrar mensaje cuando no hay rutas
            self.routes_container.content = ft.Container(
                content=ft.Column([
                    ft.Text("🗺️", size=100),  # Emoji grande de mapa
                    ft.Text("No tienes rutas creadas", size=20, weight=ft.FontWeight.BOLD, color="grey"),
                    ft.Text("¡Crea tu primera ruta para comenzar!", size=16, color="grey"),
                    ft.Container(height=20),
                    ft.Text("💡 Una ruta te permite planificar un recorrido", size=14, color="grey"),
                    ft.Text("con múltiples paradas y conexiones entre ellas", size=14, color="grey"),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10),
                padding=40,
                border_radius=10,
                bgcolor="grey50",
                border=ft.border.all(2, "grey300")
            )
        else:
            # Mostrar lista de rutas
            routes_list = []
            
            for i, ruta in enumerate(self.routes):
                route_card = self._create_route_card(ruta, i)
                routes_list.append(route_card)
            
            self.routes_container.content = ft.Column([
                ft.Text(f"📋 Total de rutas: {len(self.routes)}", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Column(routes_list, spacing=10)
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10)
    
    def _create_route_card(self, ruta: Ruta, index: int) -> ft.Container:
        """
        Crea una tarjeta para mostrar una ruta
        
        Args:
            ruta: Objeto Ruta
            index: Índice en la lista
            
        Returns:
            Container con la tarjeta de la ruta
        """
        # Iconos para diferentes índices (usando emojis)
        emojis = ["🗺️", "📍", "🚩", "🏁", "⭐", "🎯", "📌", "🔵", "🟢", "🟡"]
        emoji = emojis[index % len(emojis)]
        
        # Descripción truncada
        descripcion_text = ruta.descripcion if ruta.descripcion else "Sin descripción"
        if len(descripcion_text) > 100:
            descripcion_text = descripcion_text[:100] + "..."
        
        # Fecha de creación
        fecha_text = "Fecha no disponible"
        if ruta.created_at:
            try:
                fecha_text = ruta.created_at.strftime("%d/%m/%Y %H:%M")
            except:
                fecha_text = str(ruta.created_at)
        
        return ft.Container(
            content=ft.Column([
                # Encabezado de la tarjeta
                ft.Row([
                    ft.Text(emoji, size=30),  # Usar emoji en lugar de ícono
                    ft.Column([
                        ft.Text(ruta.nombre, size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"ID: {ruta.id}", size=12, color="grey"),
                    ], spacing=2, expand=True),
                    ft.Text("⋮", size=20, color="grey")  # Menú de tres puntos como emoji
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Descripción
                ft.Text(descripcion_text, size=14, color="grey700"),
                
                # Footer con fecha y acciones
                ft.Row([
                    ft.Text(f"📅 {fecha_text}", size=12, color="grey"),
                    ft.Row([
                        ft.TextButton(
                            content=ft.Row([
                                ft.Text("📋", size=14),
                                ft.Text("Ver paradas", size=12)
                            ], spacing=5),
                            on_click=lambda e, r=ruta: self._on_view_stops(r)
                        ),
                        ft.TextButton(
                            content=ft.Row([
                                ft.Text("⚙️", size=14),
                                ft.Text("Gestionar", size=12)
                            ], spacing=5),
                            on_click=lambda e, r=ruta: self._on_manage_route(r)
                        ),
                    ], spacing=10)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=10),
            padding=20,
            border_radius=10,
            bgcolor="white",
            border=ft.border.all(1, "grey300"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color="grey400",
            ),
            width=600
        )
    
    def _on_back_click(self, e):
        """Maneja el click del botón volver"""
        self.on_back_to_dashboard()
    
    def _on_create_route_click(self, e):
        """Maneja el click del botón crear ruta"""
        # Por ahora, mostrar un diálogo simple
        self._show_create_route_dialog()
    
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
    
    def _on_view_details(self, ruta: Ruta):
        """Maneja ver detalles de una ruta"""
        print(f"Ver detalles de ruta: {ruta.nombre}")
        # Implementar más tarde
    
    def _on_edit_route(self, ruta: Ruta):
        """Maneja editar una ruta"""
        print(f"Editar ruta: {ruta.nombre}")
        # Implementar más tarde
    
    def _on_delete_route(self, ruta: Ruta):
        """Maneja eliminar una ruta"""
        print(f"Eliminar ruta: {ruta.nombre}")
        # Implementar más tarde
    
    def _on_view_stops(self, ruta: Ruta):
        """Maneja ver paradas de una ruta"""
        print(f"Ver paradas de ruta: {ruta.nombre}")
        # Implementar más tarde
    
    def _on_manage_route(self, ruta: Ruta):
        """Maneja gestionar una ruta"""
        print(f"Gestionar ruta: {ruta.nombre}")
        # Implementar más tarde
    
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
            "success": "",
            "warning": "⚠️",
            "error": "❌"
        }
        
        emoji = icon_map.get(message_type, "ℹ️")
        
        self.message_container.content = ft.Container(
            content=ft.Row([
                ft.Text(emoji, size=20),
                ft.Text(message, color=color, size=14),
            ], spacing=10),
            padding=15,
            border_radius=8,
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
