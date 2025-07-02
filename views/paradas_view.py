"""
Vista de Paradas
Maneja la interfaz de usuario para mostrar y gestionar paradas de una ruta
"""
import flet as ft
from typing import Callable, Optional, List
from models import User, Ruta, Parada


class ParadasView:
    """
    Vista para gestionar paradas de una ruta
    """
    
    def __init__(self, on_back: Callable, on_create_stop: Callable, on_edit_stop: Callable = None, 
                 on_delete_stop: Callable = None, on_view_connections: Callable = None,
                 on_visualize_route: Callable = None):
        """
        Inicializa la vista de paradas
        
        Args:
            on_back: Callback para volver al dashboard
            on_create_stop: Callback para crear nueva parada
            on_edit_stop: Callback para editar parada existente
            on_delete_stop: Callback para eliminar parada
            on_view_connections: Callback para ver conexiones de una parada
            on_visualize_route: Callback para visualizar el grafo de la ruta
        """
        self.on_back = on_back
        self.on_create_stop = on_create_stop
        self.on_edit_stop = on_edit_stop
        self.on_delete_stop = on_delete_stop
        self.on_view_connections = on_view_connections
        self.on_visualize_route = on_visualize_route
        self.user = None
        self.ruta = None
        self.paradas = []
        self.message_container = None
        self.stops_container = None
        self._page_ref = None
        
    def create(self, user: Optional[User] = None, ruta: Optional[Ruta] = None, paradas: List[Parada] = None) -> ft.Container:
        """
        Crea y retorna el contenido de la vista de paradas
        
        Args:
            user: Usuario actual
            ruta: Ruta seleccionada
            paradas: Lista de paradas de la ruta
            
        Returns:
            Container con la vista de paradas
        """
        self.user = user
        self.ruta = ruta
        self.paradas = paradas or []
        
        # Información de la ruta
        ruta_nombre = ruta.nombre if ruta else "Ruta"
        ruta_descripcion = ruta.descripcion if ruta and ruta.descripcion else "Sin descripción"
        
        # Crear contenedores que se actualizarán
        self.message_container = ft.Container()
        self.stops_container = ft.Container()
        
        # Actualizar contenido de paradas
        self._update_stops_content()
        
        # Contenido principal
        return ft.Container(
            content=ft.Column([
                # Header con información de la ruta
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_size=24,
                                tooltip="Volver al dashboard",
                                on_click=self._on_back_click
                            ),
                            ft.Column([
                                ft.Text("🗺️ Paradas de Ruta", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text(f"📍 {ruta_nombre}", size=18, color="blue"),
                                ft.Text(ruta_descripcion, size=12, color="grey"),
                            ], spacing=5, expand=True),
                        ], alignment=ft.MainAxisAlignment.START),
                    ], spacing=10),
                    padding=20,
                    border_radius=10,
                    bgcolor="blue50",
                    border=ft.border.all(1, "blue200")
                ),
                
                ft.Container(height=20),
                
                # Mensaje container
                self.message_container,
                
                # Título de paradas y botones
                ft.Container(
                    content=ft.Row([
                        ft.Text("🚏 Paradas", size=24, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Text("🔍", size=16),
                                    ft.Text("Visualizar Ruta", size=14)
                                ], spacing=8),
                                on_click=self._on_visualize_route_click,
                                bgcolor="blue",
                                color="white",
                                height=40,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                )
                            ),
                            ft.Container(width=10),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Text("➕", size=16),
                                    ft.Text("Nueva Parada", size=14)
                                ], spacing=8),
                                on_click=self._on_create_stop_click,
                                bgcolor="green",
                                color="white",
                                height=40
                            ),
                        ], spacing=10)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=10)
                ),
                
                ft.Container(height=10),
                
                # Container de paradas
                self.stops_container,
                
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
    
    def _on_back_click(self, e):
        """Maneja el click del botón de volver"""
        self.on_back()
    
    def _on_visualize_route_click(self, e):
        """Maneja el click del botón visualizar ruta"""
        if hasattr(self, 'on_visualize_route') and self.on_visualize_route:
            if self.ruta:
                self.on_visualize_route(self.ruta)
            else:
                self.show_message("No hay una ruta seleccionada para visualizar", "warning")
        else:
            self.show_message("Función de visualización de ruta no configurada", "warning")
    
    def _on_create_stop_click(self, e):
        """Maneja el click del botón crear parada"""
        print("DEBUG: Botón 'Nueva Parada' clicado")
        self._open_create_stop_form()
    
    def _open_create_stop_form(self):
        """Abre el formulario para crear nueva parada"""
        
        # Crear campos del formulario
        nombre_field = ft.TextField(
            label="Nombre de la parada", 
            hint_text="Ej: Plaza Central",
            width=300
        )
        
        descripcion_field = ft.TextField(
            label="Descripción (opcional)", 
            multiline=True, 
            max_lines=2,
            width=300
        )
        
        # Contenedor para mensajes de error
        error_container = ft.Container()
        
        def show_error(message):
            """Muestra un mensaje de error en el formulario"""
            error_container.content = ft.Container(
                content=ft.Text(
                    message, 
                    color="red", 
                    size=12,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=5,
                border_radius=5,
                bgcolor="red100",
                border=ft.border.all(1, "red")
            )
            self._page_ref.update()
        
        def clear_error():
            """Limpia el mensaje de error"""
            error_container.content = None
            self._page_ref.update()
        
        def handle_close(e):
            if e.control.text == "Crear Parada":
                # Limpiar errores previos
                clear_error()
                
                # Validar nombre
                nombre = nombre_field.value
                if not nombre or not nombre.strip():
                    show_error("❌ El nombre de la parada es obligatorio")
                    return
                
                # Verificar duplicados
                if self._check_stop_name_exists(nombre.strip()):
                    show_error("❌ Ya existe una parada con ese nombre en esta ruta")
                    return
                
                # Procesar descripción
                descripcion = descripcion_field.value
                descripcion_final = None
                if descripcion and descripcion.strip():
                    descripcion_final = descripcion.strip()
                
                # Cerrar diálogo y crear parada
                dlg.open = False
                self._page_ref.update()
                
                print(f"Creando parada: {nombre.strip()}, Descripción: {descripcion_final}")
                if self.on_create_stop and self.ruta:
                    self.on_create_stop(self.ruta.id, nombre.strip(), descripcion_final)
            else:
                # Cancelar
                dlg.open = False
                self._page_ref.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("🚏 Crear Nueva Parada"),
            content=ft.Column([
                ft.Text("Complete los datos:", size=14),
                ft.Container(height=10),
                nombre_field,
                ft.Container(height=10),
                descripcion_field,
                ft.Container(height=15),
                error_container,  # Contenedor para errores
            ], tight=True, height=280),
            actions=[
                ft.TextButton("Cancelar", on_click=handle_close),
                ft.ElevatedButton("Crear Parada", on_click=handle_close, bgcolor="green", color="white"),
            ],
        )
        
        self._page_ref.open(dlg)
    
    def _check_stop_name_exists(self, nombre: str) -> bool:
        """
        Verifica si ya existe una parada con el mismo nombre en esta ruta
        
        Args:
            nombre: Nombre de la parada a verificar
            
        Returns:
            True si existe, False si no existe
        """
        try:
            # Obtener todas las paradas de la ruta
            for parada in self.paradas:
                if parada.nombre.lower().strip() == nombre.lower().strip():
                    return True
            return False
        except Exception as e:
            print(f"Error al verificar nombre de parada: {e}")
            return False
    
    def _update_stops_content(self):
        """Actualiza el contenido del contenedor de paradas"""
        if not self.paradas:
            # Mostrar mensaje cuando no hay paradas
            self.stops_container.content = ft.Container(
                content=ft.Column([
                    ft.Text("🚏", size=80),
                    ft.Text("No hay paradas en esta ruta", size=18, weight=ft.FontWeight.BOLD, color="grey"),
                    ft.Text("¡Crea la primera parada para comenzar!", size=14, color="grey"),
                    ft.Container(height=15),
                    ft.Text("💡 Las paradas son los puntos de interés", size=12, color="grey"),
                    ft.Text("que visitarás en tu recorrido", size=12, color="grey"),
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
            # Mostrar lista de paradas
            stops_list = []
            
            for i, parada in enumerate(self.paradas):
                stop_card = self._create_stop_card(parada, i)
                stops_list.append(stop_card)
            
            self.stops_container.content = ft.Column([
                ft.Text(f"📋 Total de paradas: {len(self.paradas)}", size=14, weight=ft.FontWeight.BOLD, color="grey"),
                ft.Container(height=10),
                ft.Column(stops_list, spacing=10)
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5)
    
    def _create_stop_card(self, parada: Parada, index: int) -> ft.Container:
        """
        Crea una tarjeta para mostrar una parada
        
        Args:
            parada: Objeto Parada
            index: Índice en la lista
            
        Returns:
            Container con la tarjeta de la parada
        """
        # Emojis para diferentes índices
        emojis = ["🚏", "📍", "🏪", "🏛️", "🏞️", "🏢", "🎯", "⭐", "🔵", "🟢"]
        emoji = emojis[index % len(emojis)]
        
        # Descripción truncada
        descripcion_text = parada.descripcion if parada.descripcion else "Sin descripción"
        if len(descripcion_text) > 80:
            descripcion_text = descripcion_text[:80] + "..."
        
        # Fecha de creación
        fecha_text = "Fecha no disponible"
        if parada.created_at:
            try:
                fecha_text = parada.created_at.strftime("%d/%m/%Y")
            except:
                fecha_text = str(parada.created_at)
        
        return ft.Container(
            content=ft.Column([
                # Encabezado de la tarjeta
                ft.Row([
                    ft.Text(emoji, size=24),
                    ft.Column([
                        ft.Text(parada.nombre, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"ID: {parada.id}", size=10, color="grey"),
                    ], spacing=2, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.MORE_VERT,
                        icon_size=20,
                        tooltip="Opciones",
                        on_click=lambda e, stop=parada: self._show_stop_options(stop)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Descripción
                ft.Text(descripcion_text, size=12, color="grey700"),
                
                # Footer con fecha
                ft.Row([
                    ft.Text(f"📅 {fecha_text}", size=10, color="grey"),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Text("🔗", size=12),
                            ft.Text("Conexiones", size=10),
                        ], spacing=3),
                        on_click=lambda e, stop=parada: self._on_view_connections_click(stop)
                    )
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
    
    def _show_stop_options(self, parada: Parada):
        """
        Muestra las opciones para una parada específica
        
        Args:
            parada: La parada seleccionada
        """
        def handle_option(e):
            dlg.open = False
            self._page_ref.update()
            
            # Identificar la opción por el texto del ListTile
            if hasattr(e.control, 'title') and hasattr(e.control.title, 'value'):
                option_text = e.control.title.value
                if option_text == "Editar parada":
                    self._edit_stop(parada)
                elif option_text == "Eliminar parada":
                    self._confirm_delete_stop(parada)
        
        def handle_edit(e):
            dlg.open = False
            self._page_ref.update()
            self._edit_stop(parada)
            
        def handle_delete(e):
            dlg.open = False
            self._page_ref.update()
            self._confirm_delete_stop(parada)
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Opciones para: {parada.nombre}"),
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.EDIT, color="blue"),
                    title=ft.Text("Editar parada"),
                    on_click=handle_edit
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DELETE, color="red"),
                    title=ft.Text("Eliminar parada"),
                    on_click=handle_delete
                ),
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._close_dialog(dlg)),
            ],
        )
        
        self._page_ref.open(dlg)
    
    def _edit_stop(self, parada: Parada):
        """
        Abre el formulario de edición para una parada existente
        
        Args:
            parada: La parada a editar
        """
        # Crear campos del formulario pre-llenados
        nombre_field = ft.TextField(
            label="Nombre de la parada", 
            hint_text="Ej: Plaza Central",
            width=300,
            value=parada.nombre
        )
        
        descripcion_field = ft.TextField(
            label="Descripción (opcional)", 
            multiline=True, 
            max_lines=2,
            width=300,
            value=parada.descripcion or ""
        )
        
        # Contenedor para mensajes de error
        error_container = ft.Container()
        
        def show_error(message):
            """Muestra un mensaje de error en el formulario"""
            error_container.content = ft.Container(
                content=ft.Text(
                    message, 
                    color="red", 
                    size=12,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=5,
                border_radius=5,
                bgcolor="red100",
                border=ft.border.all(1, "red")
            )
            self._page_ref.update()
        
        def clear_error():
            """Limpia el mensaje de error"""
            error_container.content = None
            self._page_ref.update()
        
        def handle_close(e):
            if e.control.text == "Guardar Cambios":
                # Limpiar errores previos
                clear_error()
                
                # Validar nombre
                nombre = nombre_field.value
                if not nombre or not nombre.strip():
                    show_error("❌ El nombre de la parada es obligatorio")
                    return
                
                # Verificar duplicados (solo si el nombre cambió)
                nombre_nuevo = nombre.strip()
                if nombre_nuevo.lower() != parada.nombre.lower():
                    if self._check_stop_name_exists(nombre_nuevo):
                        show_error("❌ Ya existe una parada con ese nombre en esta ruta")
                        return
                
                # Procesar descripción
                descripcion = descripcion_field.value
                descripcion_final = None
                if descripcion and descripcion.strip():
                    descripcion_final = descripcion.strip()
                
                # Cerrar diálogo y editar parada
                dlg.open = False
                self._page_ref.update()
                
                print(f"Editando parada ID {parada.id}: {nombre_nuevo}, Descripción: {descripcion_final}")
                if self.on_edit_stop and self.ruta:
                    self.on_edit_stop(parada.id, self.ruta.id, nombre_nuevo, descripcion_final)
            else:
                # Cancelar
                dlg.open = False
                self._page_ref.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("✏️ Editar Parada"),
            content=ft.Column([
                ft.Text("Modifica los datos de la parada:", size=14),
                ft.Container(height=10),
                nombre_field,
                ft.Container(height=10),
                descripcion_field,
                ft.Container(height=15),
                error_container,  # Contenedor para errores
            ], tight=True, height=280),
            actions=[
                ft.TextButton("Cancelar", on_click=handle_close),
                ft.ElevatedButton("Guardar Cambios", on_click=handle_close, bgcolor="blue", color="white"),
            ],
        )
        
        self._page_ref.open(dlg)
    
    def _confirm_delete_stop(self, parada: Parada):
        """
        Muestra el modal de confirmación para eliminar una parada
        
        Args:
            parada: La parada a eliminar
        """
        def handle_delete(e):
            if e.control.text == "Sí, eliminar":
                dlg.open = False
                self._page_ref.update()
                
                print(f"Eliminando parada ID {parada.id}: {parada.nombre}")
                if self.on_delete_stop and self.ruta:
                    self.on_delete_stop(parada.id, self.ruta.id, parada.nombre)
            else:
                # Cancelar
                dlg.open = False
                self._page_ref.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Confirmar Eliminación"),
            content=ft.Column([
                ft.Text("¿Estás seguro de que quieres eliminar esta parada?", size=14),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("🚏", size=16),
                            ft.Text(parada.nombre, size=16, weight=ft.FontWeight.BOLD),
                        ], spacing=8),
                        ft.Text(parada.descripcion or "Sin descripción", size=12, color="grey"),
                    ], spacing=5),
                    padding=10,
                    border_radius=5,
                    bgcolor="red50",
                    border=ft.border.all(1, "red200")
                ),
                ft.Container(height=15),
                ft.Text("⚠️ Esta acción no se puede deshacer", size=12, color="red", weight=ft.FontWeight.BOLD),
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=handle_delete),
                ft.ElevatedButton("Sí, eliminar", on_click=handle_delete, bgcolor="red", color="white"),
            ],
        )
        
        self._page_ref.open(dlg)
    
    def _close_dialog(self, dialog):
        """Cierra un diálogo"""
        dialog.open = False
        self._page_ref.update()
    
    def update_stops(self, paradas: List[Parada]):
        """
        Actualiza la lista de paradas mostrada
        
        Args:
            paradas: Nueva lista de paradas
        """
        self.paradas = paradas
        self._update_stops_content()
        if self._page_ref:
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
                ft.Text(emoji, size=16),
                ft.Text(message, color=color, size=12),
            ], spacing=8),
            padding=12,
            border_radius=6,
            bgcolor=bgcolor,
            border=ft.border.all(1, color)
        )
        
        if self._page_ref:
            self._page_ref.update()
        
        # Auto-ocultar mensajes de éxito después de 2 segundos
        if message_type == "success":
            import threading
            import time
            
            def auto_hide():
                time.sleep(2)
                self.clear_message()
            
            thread = threading.Thread(target=auto_hide)
            thread.daemon = True
            thread.start()
    
    def clear_message(self):
        """Limpia el mensaje mostrado"""
        self.message_container.content = None
        if self._page_ref:
            self._page_ref.update()
    
    def set_page_reference(self, page):
        """Establece referencia a la página para actualizaciones"""
        self._page_ref = page
        print(f"DEBUG: Referencia de página establecida en ParadasView: {page is not None}")
    
    def _on_view_connections_click(self, parada: Parada):
        """
        Maneja el click del botón Ver conexiones
        
        Args:
            parada: La parada seleccionada
        """
        print(f"DEBUG: Ver conexiones clicado para parada: {parada.nombre}")
        if self.on_view_connections:
            self.on_view_connections(parada)
