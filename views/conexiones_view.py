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
    
    def __init__(self, on_back: Callable, on_create_connection: Callable, on_delete_connection: Callable = None, on_update_connection: Callable = None):
        """
        Inicializa la vista de conexiones
        
        Args:
            on_back: Callback para volver a la vista de paradas
            on_create_connection: Callback para crear nueva conexión
            on_delete_connection: Callback para eliminar conexión
            on_update_connection: Callback para actualizar conexión
        """
        self.on_back = on_back
        self.on_create_connection = on_create_connection
        self.on_delete_connection = on_delete_connection
        self.on_update_connection = on_update_connection
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
        
        # Filtrar paradas disponibles usando la función auxiliar
        filtered_paradas = self._filter_valid_destinations(self.paradas_disponibles)
        
        if not filtered_paradas:
            # Mostrar mensaje si no hay paradas disponibles después del filtrado
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("⚠️ Sin paradas disponibles"),
                content=ft.Text("No hay paradas disponibles para crear conexiones. Todas las paradas de esta ruta ya están conectadas o no son válidas como destino.", size=14),
                actions=[
                    ft.TextButton("Entendido", on_click=lambda e: self._close_dialog(dlg)),
                ],
            )
            self._page_ref.open(dlg)
            return
        
        # Filtrar paradas para mostrar solo destinos válidos (sin la parada actual y sin las ya conectadas)
        filtered_paradas = self._filter_valid_destinations(self.paradas_disponibles)
        
        # Crear selector de parada destino
        parada_options = []
        for parada_data in filtered_paradas:
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
                
                # Validar que la parada destino no sea la misma que la parada origen
                parada_destino_id = int(parada_dropdown.value)
                if parada_destino_id == self.parada.id:
                    show_error("❌ Error: No puedes conectar una parada consigo misma")
                    return
                    
                # Verificar si ya existe una conexión con este destino
                for conexion in self.conexiones:
                    if (conexion.parada_origen_id == self.parada.id and 
                        conexion.parada_destino_id == parada_destino_id):
                        show_error("❌ Error: Ya existe una conexión con esta parada")
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
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        icon_color="orange",
                        icon_size=20,
                        tooltip="Editar conexión",
                        on_click=lambda e, conn=conexion: self._open_edit_connection_form(conn)
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
    
    def _open_edit_connection_form(self, conexion: Conexion):
        """Abre el formulario para editar una conexión existente"""
        
        # Verificar si tenemos referencia a la página
        if not self._page_ref:
            print("ERROR: No hay referencia a la página (self._page_ref es None)")
            return
        
        # Para editar, permitiremos cambiar tanto la parada destino como la distancia
        parada_actual_id = conexion.parada_destino_id
        parada_actual_nombre = conexion.parada_destino_nombre or f"Parada {parada_actual_id}"
        
        # Verificación crítica: asegurarse de que no se está editando una conexión a sí misma
        if parada_actual_id == self.parada.id:
            self.show_message("⚠️ Error: No se puede editar una conexión a la misma parada", "error")
            return
            
        # Obtener todas las paradas disponibles para la edición
        # Incluiremos tanto las disponibles como la parada destino actual
        filtered_paradas = self._filter_valid_destinations(self.paradas_disponibles)
        
        # Crear opciones para el dropdown incluyendo todas las paradas disponibles
        parada_options = []
        
        # Asegurarse de incluir siempre la parada actual como opción
        parada_actual_incluida = False
        
        # Agregar todas las paradas disponibles
        for parada_data in filtered_paradas:
            parada_options.append(
                ft.dropdown.Option(
                    key=str(parada_data["id"]),
                    text=parada_data["nombre"]
                )
            )
            if parada_data["id"] == parada_actual_id:
                parada_actual_incluida = True
        
        # Si la parada actual no está en las filtradas, agregarla manualmente
        if not parada_actual_incluida:
            parada_options.append(
                ft.dropdown.Option(
                    key=str(parada_actual_id),
                    text=parada_actual_nombre
                )
            )
        
        # Usar la distancia actual como valor por defecto
        distancia_default = conexion.distancia
        
        parada_dropdown = ft.Dropdown(
            label="Parada destino",
            hint_text="Selecciona una parada destino",
            options=parada_options,
            value=str(parada_actual_id),  # Valor por defecto (la parada destino actual)
            width=300
        )
        
        # Campo de distancia
        distancia_field = ft.TextField(
            label="Distancia (km)", 
            hint_text="Ej: 2.5",
            value=str(distancia_default),  # Valor por defecto
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
            if e.control.text == "Guardar Cambios":
                # Limpiar errores previos
                clear_error()
                
                # Validar parada destino seleccionada
                if not parada_dropdown.value:
                    show_error("❌ Debes seleccionar una parada destino")
                    return
                
                # Validar que la parada destino no sea la misma que la parada origen
                parada_destino_id = int(parada_dropdown.value)
                if parada_destino_id == self.parada.id:
                    show_error("❌ Error: No puedes conectar una parada consigo misma")
                    return
                
                # Verificar si ya existe una conexión con este destino (excepto la que estamos editando)
                for con in self.conexiones:
                    if (con.parada_origen_id == self.parada.id and 
                        con.parada_destino_id == parada_destino_id and
                        # Permitir el destino actual
                        con.parada_destino_id != parada_actual_id):
                        show_error("❌ Error: Ya existe una conexión con esta parada")
                        return
                
                # Validar distancia (campo obligatorio)
                distancia_str = distancia_field.value
                if not distancia_str or not distancia_str.strip():
                    show_error("❌ Error: La distancia es obligatoria")
                    return
                
                try:
                    distancia = float(distancia_str.strip())
                    if distancia < 0:
                        show_error("❌ Error: La distancia debe ser mayor o igual a 0")
                        return
                    if distancia == 0:
                        # Mostrar una advertencia, pero permitir continuar
                        show_error("⚠️ Advertencia: Has ingresado una distancia de 0 km")
                        # No hacemos return para permitir continuar
                except ValueError:
                    show_error("❌ Error: La distancia debe ser un número válido")
                    return
                
                # Cerrar diálogo y guardar cambios
                dlg.open = False
                self._page_ref.update()
                
                parada_destino_id = int(parada_dropdown.value)
                
                # Verificar si el destino ha cambiado
                if parada_destino_id != parada_actual_id:
                    print(f"Actualizando conexión: {self.parada.id} -> {parada_destino_id} (antes era {parada_actual_id}), Nueva distancia: {distancia}")
                else:
                    print(f"Actualizando solo distancia de conexión: {self.parada.id} -> {parada_destino_id}, Nueva distancia: {distancia}")
                    
                if self.on_update_connection and self.parada and self.ruta:
                    # Pasamos el ID de la parada destino anterior para que el controlador sepa si está cambiando
                    self.on_update_connection(self.parada.id, parada_destino_id, distancia, self.ruta.id, parada_actual_id)
            else:
                # Cancelar
                dlg.open = False
                self._page_ref.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("✏️ Editar Distancia de Conexión"),
            content=ft.Column([
                ft.Text("Modifica la distancia de la conexión:", size=14),
                ft.Container(height=10),
                ft.Text(f"Desde: {self.parada.nombre}", size=12, weight=ft.FontWeight.BOLD),
                ft.Text(f"Hacia: {parada_actual_nombre}", size=12, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                parada_dropdown,
                ft.Container(height=10),
                distancia_field,
                ft.Container(height=15),
                error_container,  # Contenedor para errores
            ], tight=True, height=320),
            actions=[
                ft.TextButton("Cancelar", on_click=handle_close),
                ft.ElevatedButton("Guardar Cambios", on_click=handle_close, bgcolor="green", color="white"),
            ],
        )
        
        self._page_ref.open(dlg)
    
    def update_connections(self, conexiones: List[Conexion], paradas_disponibles: List[dict] = None):
        """
        Actualiza la lista de conexiones y paradas disponibles
        
        Args:
            conexiones: Nueva lista de conexiones
            paradas_disponibles: Nueva lista de paradas disponibles (se filtrarán automáticamente)
        """
        self.conexiones = conexiones
        if paradas_disponibles is not None:
            self.paradas_disponibles = paradas_disponibles
            # Filtrar paradas para eliminar las que ya tienen conexión y la actual
            filtered_paradas = self._filter_valid_destinations(paradas_disponibles)
            # Imprimir un mensaje de depuración
            print(f"Paradas disponibles filtradas: {len(filtered_paradas)} de {len(paradas_disponibles)}")
            
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
    
    def _close_dialog(self, dlg):
        """Cierra un diálogo modal"""
        if dlg and hasattr(dlg, "open"):
            dlg.open = False
            if self._page_ref:
                self._page_ref.update()
    
    def _filter_valid_destinations(self, paradas_list):
        """
        Filtra las paradas para mostrar solo destinos válidos (excluye la actual y las ya conectadas)
        
        Args:
            paradas_list: Lista de paradas para filtrar
            
        Returns:
            Lista de paradas filtradas
        """
        if not paradas_list or not self.parada:
            return []
            
        # Crear una lista de IDs de paradas ya conectadas desde la actual
        connected_ids = []
        for conexion in self.conexiones:
            if conexion.parada_origen_id == self.parada.id:
                connected_ids.append(conexion.parada_destino_id)
        
        # Filtrar paradas (excluir la actual y las ya conectadas)
        filtered_list = []
        for parada_data in paradas_list:
            if (parada_data["id"] != self.parada.id and 
                parada_data["id"] not in connected_ids):
                filtered_list.append(parada_data)
                
        return filtered_list
    
    def set_page_reference(self, page):
        """Establece referencia a la página para actualizaciones"""
        self._page_ref = page
        self.page = page  # También actualizamos la propiedad page
        print(f"DEBUG: Referencia de página establecida en ConexionesView: {page is not None}")
