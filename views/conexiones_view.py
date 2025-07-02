"""
Vista de Conexiones
Maneja la interfaz de usuario para mostrar y gestionar conexiones entre paradas
"""
import flet as ft
from typing import Callable, Optional, List
from models import User, Ruta, Parada, Conexion


class ConexionesView:
    """
    Vista para gestionar conexiones entre paradas
    """
    
    def __init__(self, on_back: Callable, on_create_connection: Callable, on_delete_connection: Callable = None):
        """
        Inicializa la vista de conexiones
        
        Args:
            on_back: Callback para volver a la vista de paradas
            on_create_connection: Callback para crear nueva conexión
            on_delete_connection: Callback para eliminar conexión
        """
        self.on_back = on_back
        self.on_create_connection = on_create_connection
        self.on_delete_connection = on_delete_connection
        self.user = None
        self.ruta = None
        self.parada = None
        self.conexiones = []
        self.paradas_disponibles = []
        self.message_container = None
        self.connections_container = None
        self._page_ref = None
        self.page = None  # Referencia a la página (será igual a _page_ref)
        
    def create(self, user: Optional[User] = None, ruta: Optional[Ruta] = None, 
               parada: Optional[Parada] = None, conexiones: List[Conexion] = None,
               paradas_disponibles: List[dict] = None, page: Optional[ft.Page] = None) -> ft.Container:
        """
        Si se proporciona una página, la usaremos para actualizaciones
        """
        # Si nos pasan una página, la establecemos como referencia
        if page:
            self.set_page_reference(page)
        """
        Crea y retorna el contenido de la vista de conexiones
        
        Args:
            user: Usuario actual
            ruta: Ruta seleccionada
            parada: Parada seleccionada
            conexiones: Lista de conexiones de la parada
            paradas_disponibles: Lista de paradas disponibles para conectar
            
        Returns:
            Container con la vista de conexiones
        """
        self.user = user
        self.ruta = ruta
        self.parada = parada
        self.conexiones = conexiones or []
        self.paradas_disponibles = paradas_disponibles or []
        
        # Información de la parada
        parada_nombre = parada.nombre if parada else "Parada"
        ruta_nombre = ruta.nombre if ruta else "Ruta"
        
        # Crear contenedores que se actualizarán
        self.message_container = ft.Container()
        self.connections_container = ft.Container()
        
        # Actualizar contenido de conexiones
        self._update_connections_content()
        
        # Contenido principal
        return ft.Container(
            content=ft.Column([
                # Header con información de la parada
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_size=24,
                                tooltip="Volver a paradas",
                                on_click=self._on_back_click
                            ),
                            ft.Column([
                                ft.Text("🔗 Conexiones de Parada", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text(f"🚏 {parada_nombre}", size=18, color="blue"),
                                ft.Text(f"📍 Ruta: {ruta_nombre}", size=12, color="grey"),
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
                
                # Título de conexiones y botón crear
                ft.Container(
                    content=ft.Row([
                        ft.Text("🔗 Conexiones", size=24, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Text("➕", size=16),
                                ft.Text("Nueva Conexión", size=14)
                            ], spacing=8),
                            on_click=self._on_create_connection_click,
                            bgcolor="green",
                            color="white",
                            height=40,
                            data=self.page if hasattr(self, "page") else None  # Almacenar referencia a la página si existe
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=10)
                ),
                
                ft.Container(height=10),
                
                # Container de conexiones
                self.connections_container,
                
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
    
    def _on_create_connection_click(self, e):
        """Maneja el click del botón crear conexión"""
        print("DEBUG: Botón 'Nueva Conexión' clicado")
        
        # Si la página no está establecida pero podemos obtenerla del evento
        if not self._page_ref and e and hasattr(e, "page") and e.page:
            print("DEBUG: Estableciendo referencia a la página desde el evento del botón")
            self.set_page_reference(e.page)
            
        # Si no tenemos la referencia, buscar desde el control
        if not self._page_ref and e and hasattr(e, "control") and hasattr(e.control, "page") and e.control.page:
            print("DEBUG: Estableciendo referencia a la página desde el control del botón")
            self.set_page_reference(e.control.page)
            
        self._open_create_connection_form()
    
    def _open_create_connection_form(self):
        """Abre el formulario para crear nueva conexión"""
        
        # Verificar si tenemos referencia a la página
        if not self._page_ref:
            print("ERROR: No hay referencia a la página (self._page_ref es None)")
            return
        
        if not self.paradas_disponibles:
            # Mostrar mensaje si no hay paradas disponibles
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("⚠️ Sin paradas disponibles"),
                content=ft.Text("No hay paradas disponibles para crear conexiones. Todas las paradas de esta ruta ya están conectadas.", size=14),
                actions=[
                    ft.TextButton("Entendido", on_click=lambda e: self._close_dialog(dlg)),
                ],
            )
            self._page_ref.open(dlg)
            return
        
        # Crear selector de parada destino
        parada_options = []
        for parada_data in self.paradas_disponibles:
            parada_options.append(
                ft.dropdown.Option(
                    key=str(parada_data["id"]),
                    text=parada_data["nombre"]
                )
            )
        
        parada_dropdown = ft.Dropdown(
            label="Parada destino",
            hint_text="Selecciona una parada",
            options=parada_options,
            width=300
        )
        
        # Campo de distancia
        distancia_field = ft.TextField(
            label="Distancia (km)", 
            hint_text="Ej: 2.5",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER
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
            if e.control.text == "Crear Conexión":
                # Limpiar errores previos
                clear_error()
                
                # Validar parada destino
                if not parada_dropdown.value:
                    show_error("❌ Debes seleccionar una parada destino")
                    return
                
                # Validar distancia
                distancia_str = distancia_field.value
                if not distancia_str or not distancia_str.strip():
                    show_error("❌ La distancia es obligatoria")
                    return
                
                try:
                    distancia = float(distancia_str.strip())
                    if distancia < 0:
                        show_error("❌ La distancia debe ser mayor o igual a 0")
                        return
                except ValueError:
                    show_error("❌ La distancia debe ser un número válido")
                    return
                
                # Cerrar diálogo y crear conexión
                dlg.open = False
                self._page_ref.update()
                
                parada_destino_id = int(parada_dropdown.value)
                print(f"Creando conexión: {self.parada.id} -> {parada_destino_id}, Distancia: {distancia}")
                if self.on_create_connection and self.parada and self.ruta:
                    self.on_create_connection(self.parada.id, parada_destino_id, distancia, self.ruta.id)
            else:
                # Cancelar
                dlg.open = False
                self._page_ref.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("🔗 Crear Nueva Conexión"),
            content=ft.Column([
                ft.Text("Complete los datos:", size=14),
                ft.Container(height=10),
                ft.Text(f"Desde: {self.parada.nombre}", size=12, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                parada_dropdown,
                ft.Container(height=10),
                distancia_field,
                ft.Container(height=15),
                error_container,  # Contenedor para errores
            ], tight=True, height=320),
            actions=[
                ft.TextButton("Cancelar", on_click=handle_close),
                ft.ElevatedButton("Crear Conexión", on_click=handle_close, bgcolor="green", color="white"),
            ],
        )
        
        self._page_ref.open(dlg)
    
    def _update_connections_content(self):
        """Actualiza el contenido del contenedor de conexiones"""
        if not self.conexiones:
            # Mostrar mensaje cuando no hay conexiones
            self.connections_container.content = ft.Container(
                content=ft.Column([
                    ft.Text("🔗", size=80),
                    ft.Text("No hay conexiones desde esta parada", size=18, weight=ft.FontWeight.BOLD, color="grey"),
                    ft.Text("¡Crea la primera conexión para comenzar!", size=14, color="grey"),
                    ft.Container(height=15),
                    ft.Text("💡 Las conexiones definen cómo se puede", size=12, color="grey"),
                    ft.Text("navegar entre paradas de tu ruta", size=12, color="grey"),
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
            # Mostrar lista de conexiones
            connections_list = []
            
            for i, conexion in enumerate(self.conexiones):
                connection_card = self._create_connection_card(conexion, i)
                connections_list.append(connection_card)
            
            self.connections_container.content = ft.Column([
                ft.Text(f"📋 Total de conexiones: {len(self.conexiones)}", size=14, weight=ft.FontWeight.BOLD, color="grey"),
                ft.Container(height=10),
                ft.Column(connections_list, spacing=10)
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5)
    
    def _create_connection_card(self, conexion: Conexion, index: int) -> ft.Container:
        """
        Crea una tarjeta para mostrar una conexión
        
        Args:
            conexion: Objeto Conexion
            index: Índice en la lista
            
        Returns:
            Container con la tarjeta de la conexión
        """
        # Determinar dirección de la conexión
        if conexion.parada_origen_id == self.parada.id:
            # Esta parada es el origen
            direccion_emoji = "➡️"
            parada_destino = conexion.parada_destino_nombre or f"Parada {conexion.parada_destino_id}"
            titulo = f"Hacia: {parada_destino}"
        else:
            # Esta parada es el destino
            direccion_emoji = "⬅️"
            parada_origen = conexion.parada_origen_nombre or f"Parada {conexion.parada_origen_id}"
            titulo = f"Desde: {parada_origen}"
        
        return ft.Container(
            content=ft.Column([
                # Encabezado de la tarjeta
                ft.Row([
                    ft.Text(direccion_emoji, size=24),
                    ft.Column([
                        ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Distancia: {conexion.distancia} km", size=12, color="blue"),
                    ], spacing=2, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color="red",
                        icon_size=20,
                        tooltip="Eliminar conexión",
                        on_click=lambda e, conn=conexion: self._confirm_delete_connection(conn)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
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
    
    def _confirm_delete_connection(self, conexion: Conexion):
        """
        Muestra el modal de confirmación para eliminar una conexión
        
        Args:
            conexion: La conexión a eliminar
        """
        # Verificar si tenemos referencia a la página
        if not self._page_ref:
            print("ERROR: No hay referencia a la página (self._page_ref es None)")
            return
            
        # Determinar nombres para mostrar
        if conexion.parada_origen_id == self.parada.id:
            destino_nombre = conexion.parada_destino_nombre or f"Parada {conexion.parada_destino_id}"
            descripcion = f"Conexión hacia: {destino_nombre}"
        else:
            origen_nombre = conexion.parada_origen_nombre or f"Parada {conexion.parada_origen_id}"
            descripcion = f"Conexión desde: {origen_nombre}"
        
        def handle_delete(e):
            if e.control.text == "Sí, eliminar":
                dlg.open = False
                self._page_ref.update()
                
                print(f"Eliminando conexión: {conexion.parada_origen_id} -> {conexion.parada_destino_id}")
                if self.on_delete_connection and self.ruta:
                    self.on_delete_connection(conexion.parada_origen_id, conexion.parada_destino_id, self.ruta.id)
            else:
                # Cancelar
                dlg.open = False
                self._page_ref.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Confirmar Eliminación"),
            content=ft.Column([
                ft.Text("¿Estás seguro de que quieres eliminar esta conexión?", size=14),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("🔗", size=16),
                            ft.Text(descripcion, size=16, weight=ft.FontWeight.BOLD),
                        ], spacing=8),
                        ft.Text(f"Distancia: {conexion.distancia} km", size=12, color="grey"),
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
        if self._page_ref:
            self._page_ref.update()
        else:
            print("ERROR: No hay referencia a la página (self._page_ref es None) al intentar cerrar diálogo")
    
    def update_connections(self, conexiones: List[Conexion], paradas_disponibles: List[dict] = None):
        """
        Actualiza la lista de conexiones y paradas disponibles
        
        Args:
            conexiones: Nueva lista de conexiones
            paradas_disponibles: Nueva lista de paradas disponibles
        """
        self.conexiones = conexiones
        if paradas_disponibles is not None:
            self.paradas_disponibles = paradas_disponibles
        self._update_connections_content()
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
        self.page = page  # También actualizamos la propiedad page
        print(f"DEBUG: Referencia de página establecida en ConexionesView: {page is not None}")
