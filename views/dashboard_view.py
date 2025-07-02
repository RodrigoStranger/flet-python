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
    
    def __init__(self, on_logout: Callable, on_create_route: Callable, on_edit_route: Callable = None, on_delete_route: Callable = None):
        """
        Inicializa la vista del dashboard
        
        Args:
            on_logout: Callback para cuando se cierra sesión
            on_create_route: Callback para crear nueva ruta
            on_edit_route: Callback para editar ruta existente
            on_delete_route: Callback para eliminar ruta
        """
        self.on_logout = on_logout
        self.on_create_route = on_create_route
        self.on_edit_route = on_edit_route
        self.on_delete_route = on_delete_route
        self.user = None
        self.routes = []
        self.message_container = None
        self.routes_container = None
        self._page_ref = None
        
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
        print("DEBUG: Botón 'Nueva Ruta' clicado")
        
        # SOLUCIÓN SIMPLE: Usar page.open()
        self._open_simple_form()
    
    def _open_simple_form(self):
        """Abre un formulario simple que SÍ funciona"""
        
        # Crear campos del formulario
        nombre_field = ft.TextField(
            label="Nombre de la ruta", 
            hint_text="Ej: Ruta Centro",
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
            if e.control.text == "Crear Ruta":
                # Limpiar errores previos
                clear_error()
                
                # Validar nombre
                nombre = nombre_field.value
                if not nombre or not nombre.strip():
                    show_error("❌ El nombre de la ruta es obligatorio")
                    return
                
                # Verificar duplicados
                if self._check_route_name_exists(nombre.strip()):
                    show_error("❌ Ya existe una ruta con ese nombre")
                    return
                
                # Procesar descripción
                descripcion = descripcion_field.value
                descripcion_final = None
                if descripcion and descripcion.strip():
                    descripcion_final = descripcion.strip()
                
                # Cerrar diálogo y crear ruta
                dlg.open = False
                self._page_ref.update()
                
                print(f"Creando ruta: {nombre.strip()}, Descripción: {descripcion_final}")
                self._handle_route_creation(nombre.strip(), descripcion_final)
            else:
                # Cancelar
                dlg.open = False
                self._page_ref.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("🗺️ Crear Nueva Ruta"),
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
                ft.ElevatedButton("Crear Ruta", on_click=handle_close, bgcolor="green", color="white"),
            ],
        )
        
        self._page_ref.open(dlg)
    
    def _check_route_name_exists(self, nombre: str) -> bool:
        """
        Verifica si ya existe una ruta con el mismo nombre para el usuario actual
        
        Args:
            nombre: Nombre de la ruta a verificar
            
        Returns:
            True si existe, False si no existe
        """
        if not self.user:
            return False
        
        try:
            # Obtener todas las rutas del usuario
            for ruta in self.routes:
                if ruta.nombre.lower().strip() == nombre.lower().strip():
                    return True
            return False
        except Exception as e:
            print(f"Error al verificar nombre de ruta: {e}")
            return False
    
    def _show_create_route_dialog_direct(self):
        """Muestra el formulario para crear ruta usando BottomSheet"""
        print("DEBUG: Iniciando creación de BottomSheet...")
        
        nombre_field = ft.TextField(
            label="Nombre de la ruta",
            hint_text="Ej: Ruta Centro Histórico",
            width=350,
            autofocus=True
        )
        
        descripcion_field = ft.TextField(
            label="Descripción (opcional)",
            hint_text="Describe tu ruta...",
            multiline=True,
            max_lines=3,
            width=350
        )
        
        def crear_ruta(e):
            print("DEBUG: Botón Crear Ruta presionado")
            if not nombre_field.value or not nombre_field.value.strip():
                print("Error: El nombre es obligatorio")
                nombre_field.error_text = "El nombre es obligatorio"
                self._page_ref.update()
                return
            
            print(f"DEBUG: Cerrando BottomSheet y creando ruta: {nombre_field.value}")
            # Cerrar BottomSheet
            self._page_ref.bottom_sheet.open = False
            self._page_ref.update()
            
            # Crear la ruta
            self._handle_route_creation(nombre_field.value.strip(), descripcion_field.value or "")
        
        def cancelar(e):
            print("DEBUG: Cancelando BottomSheet")
            self._page_ref.bottom_sheet.open = False
            self._page_ref.update()
        
        # Crear BottomSheet
        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    # Título
                    ft.Row([
                        ft.Icon(ft.Icons.ADD_LOCATION, color="green"),
                        ft.Text("Crear Nueva Ruta", size=20, weight=ft.FontWeight.BOLD),
                    ], spacing=10),
                    
                    ft.Divider(),
                    
                    # Campos del formulario
                    nombre_field,
                    ft.Container(height=10),
                    descripcion_field,
                    ft.Container(height=20),
                    
                    # Botones
                    ft.Row([
                        ft.ElevatedButton(
                            "Cancelar", 
                            on_click=cancelar,
                            bgcolor="grey",
                            color="white",
                            width=150
                        ),
                        ft.ElevatedButton(
                            "Crear Ruta", 
                            on_click=crear_ruta, 
                            bgcolor="green", 
                            color="white",
                            width=150
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    
                    ft.Container(height=20),
                    
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30,
                width=400
            ),
            open=True
        )
        
        print("DEBUG: Configurando BottomSheet en página...")
        # Mostrar BottomSheet
        if self._page_ref:
            self._page_ref.bottom_sheet = bottom_sheet
            self._page_ref.update()
            print("DEBUG: ¡BottomSheet configurado y mostrado!")
        else:
            print("ERROR: No hay referencia a la página")
    
    def _handle_route_creation(self, nombre: str, descripcion: Optional[str]):
        """
        Maneja la creación de ruta desde el formulario
        
        Args:
            nombre: Nombre de la ruta
            descripcion: Descripción de la ruta (puede ser None)
        """
        print(f"DEBUG: Creando ruta - Nombre: {nombre}, Descripción: {descripcion}")
        # Llamar al callback principal
        if self.on_create_route:
            self.on_create_route(nombre, descripcion)
    
    def _handle_form_cancel(self):
        """Maneja la cancelación del formulario"""
        print("DEBUG: Formulario de crear ruta cancelado")
    
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
                    ft.IconButton(
                        icon=ft.Icons.MORE_VERT,
                        icon_size=20,
                        tooltip="Opciones",
                        on_click=lambda e, route=ruta: self._show_route_options(route)
                    )
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
    
    def update_routes(self, routes: List[Ruta]):
        """
        Actualiza la lista de rutas mostrada
        
        Args:
            routes: Nueva lista de rutas
        """
        self.routes = routes
        self._update_routes_content()
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
        print(f"DEBUG: Referencia de página establecida: {page is not None}")
    
    def update_user_info(self, user: User):
        """
        Actualiza la información del usuario en la vista
        
        Args:
            user: Usuario actualizado
        """
        self.user = user
    
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
        print(f"Acción rápida añadida: {name}")
    
    def get_dashboard_stats(self) -> dict:
        """
        Obtiene estadísticas del dashboard
        
        Returns:
            Dict con estadísticas
        """
        return {
            "session_start": "Ahora",
            "last_login": "Primera vez",
            "user_level": "Básico"
        }
    
    def _show_route_options(self, ruta: Ruta):
        """
        Muestra las opciones para una ruta específica
        
        Args:
            ruta: La ruta seleccionada
        """
        def handle_option(e):
            dlg.open = False
            self._page_ref.update()
            
            # Usar el título del ListTile para identificar la acción
            if e.control.title.value == "Editar ruta":
                self._edit_route(ruta)
            elif e.control.title.value == "Eliminar ruta":
                self._confirm_delete_route(ruta)
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Opciones para: {ruta.nombre}"),
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.EDIT, color="blue"),
                    title=ft.Text("Editar ruta"),
                    on_click=handle_option
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DELETE, color="red"),
                    title=ft.Text("Eliminar ruta"),
                    on_click=handle_option
                ),
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._close_dialog(dlg)),
            ],
        )
        
        self._page_ref.open(dlg)
    
    def _edit_route(self, ruta: Ruta):
        """
        Abre el formulario de edición para una ruta existente
        
        Args:
            ruta: La ruta a editar
        """
        # Crear campos del formulario pre-llenados
        nombre_field = ft.TextField(
            label="Nombre de la ruta", 
            hint_text="Ej: Ruta Centro",
            width=300,
            value=ruta.nombre
        )
        
        descripcion_field = ft.TextField(
            label="Descripción (opcional)", 
            multiline=True, 
            max_lines=2,
            width=300,
            value=ruta.descripcion or ""
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
                    show_error("❌ El nombre de la ruta es obligatorio")
                    return
                
                # Verificar duplicados (solo si el nombre cambió)
                nombre_nuevo = nombre.strip()
                if nombre_nuevo.lower() != ruta.nombre.lower() and self._check_route_name_exists(nombre_nuevo):
                    show_error("❌ Ya existe una ruta con ese nombre")
                    return
                
                # Procesar descripción
                descripcion = descripcion_field.value
                descripcion_final = None
                if descripcion and descripcion.strip():
                    descripcion_final = descripcion.strip()
                
                # Cerrar diálogo y editar ruta
                dlg.open = False
                self._page_ref.update()
                
                print(f"Editando ruta ID {ruta.id}: {nombre_nuevo}, Descripción: {descripcion_final}")
                if self.on_edit_route:
                    self.on_edit_route(ruta.id, nombre_nuevo, descripcion_final)
            else:
                # Cancelar
                dlg.open = False
                self._page_ref.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("✏️ Editar Ruta"),
            content=ft.Column([
                ft.Text("Modifica los datos de la ruta:", size=14),
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
    
    def _confirm_delete_route(self, ruta: Ruta):
        """
        Muestra el modal de confirmación para eliminar una ruta
        
        Args:
            ruta: La ruta a eliminar
        """
        def handle_delete(e):
            if e.control.text == "Sí, eliminar":
                dlg.open = False
                self._page_ref.update()
                
                print(f"Eliminando ruta ID {ruta.id}: {ruta.nombre}")
                if self.on_delete_route:
                    self.on_delete_route(ruta.id, ruta.nombre)
            else:
                # Cancelar
                dlg.open = False
                self._page_ref.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Confirmar Eliminación"),
            content=ft.Column([
                ft.Text("¿Estás seguro de que quieres eliminar esta ruta?", size=14),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("📛", size=16),
                            ft.Text(ruta.nombre, size=16, weight=ft.FontWeight.BOLD),
                        ], spacing=8),
                        ft.Text(ruta.descripcion or "Sin descripción", size=12, color="grey"),
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
