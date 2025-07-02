"""
Vista de Grafo de Ruta
Maneja la interfaz de usuario para visualizar el grafo de una ruta con sus paradas y conexiones
"""
import flet as ft
import math
from typing import Callable, Optional, List, Dict, Tuple
from models import User, Ruta, Parada, Conexion


class RutaGraphView:
    """
    Vista para visualizar el grafo de una ruta
    """
    
    def __init__(self, on_back: Callable):
        """
        Inicializa la vista del grafo de ruta
        
        Args:
            on_back: Callback para volver a la vista de paradas
        """
        self.on_back = on_back
        self.user = None
        self.ruta = None
        self.paradas = []
        self.conexiones = []
        self.message_container = None
        self.graph_container = None
        self._page_ref = None
        
        # Dimensiones del canvas
        self.canvas_width = 800
        self.canvas_height = 600
        self.node_radius = 20
        self.node_positions = {}  # Almacena las posiciones (x, y) de cada nodo (parada)
        
    def create(self, user: Optional[User] = None, ruta: Optional[Ruta] = None, 
               paradas: List[Parada] = None, conexiones: List[Conexion] = None, 
               page: Optional[ft.Page] = None) -> ft.Container:
        """
        Crea y retorna el contenido de la vista del grafo
        
        Args:
            user: Usuario actual
            ruta: Ruta seleccionada
            paradas: Lista de paradas de la ruta
            conexiones: Lista de conexiones entre paradas
            page: Referencia a la página
            
        Returns:
            Container con la vista del grafo
        """
        # Si nos pasan una página, la establecemos como referencia
        if page:
            self._page_ref = page
            
        self.user = user
        self.ruta = ruta
        self.paradas = paradas or []
        self.conexiones = conexiones or []
        
        # Calcular posiciones de los nodos
        self._calculate_node_positions()
        
        # Información de la ruta
        ruta_nombre = ruta.nombre if ruta else "Ruta"
        ruta_descripcion = ruta.descripcion if ruta and ruta.descripcion else "Sin descripción"
        
        # Crear contenedores que se actualizarán
        self.message_container = ft.Container()
        self.graph_container = ft.Container(
            content=self._create_graph_canvas(),
            border=ft.border.all(1, "grey400"),
            border_radius=10,
            width=self.canvas_width,
            height=self.canvas_height,
            alignment=ft.alignment.center
        )
        
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
                                tooltip="Volver a paradas",
                                on_click=self._on_back_click
                            ),
                            ft.Column([
                                ft.Text("🗺️ Visualización de Ruta", size=24, weight=ft.FontWeight.BOLD),
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
                
                # Información del grafo
                ft.Container(
                    content=ft.Row([
                        ft.Text("📊 Grafo de Ruta", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"({len(self.paradas)} paradas, {len(self.conexiones)} conexiones)", size=14, color="grey"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=10)
                ),
                
                ft.Container(height=10),
                
                # Contenedor del grafo
                ft.Container(
                    content=self.graph_container,
                    alignment=ft.alignment.center
                ),
                
                ft.Container(height=20),
                
                # Leyenda
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=15, height=15, bgcolor="blue", border_radius=50),
                                ft.Text("Parada", size=12),
                            ], spacing=5),
                            padding=5,
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=40, height=2, bgcolor="green"),
                                ft.Text("Conexión", size=12),
                            ], spacing=5),
                            padding=5,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ),
                
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
    
    def _calculate_node_positions(self):
        """Calcula las posiciones de los nodos (paradas) en el canvas"""
        if not self.paradas:
            return
            
        # Algoritmo de distribución circular
        num_nodes = len(self.paradas)
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        radius = min(center_x, center_y) * 0.8  # 80% del radio máximo posible
        
        self.node_positions = {}
        
        # Para pocas paradas, usar posiciones específicas
        if num_nodes == 1:
            # Una sola parada en el centro
            self.node_positions[self.paradas[0].id] = (center_x, center_y)
        elif num_nodes == 2:
            # Dos paradas horizontalmente
            self.node_positions[self.paradas[0].id] = (center_x - radius * 0.5, center_y)
            self.node_positions[self.paradas[1].id] = (center_x + radius * 0.5, center_y)
        else:
            # Distribución circular para 3 o más paradas
            angle_step = 2 * math.pi / num_nodes
            
            for i, parada in enumerate(self.paradas):
                angle = i * angle_step
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.node_positions[parada.id] = (x, y)
    
    def _create_graph_canvas(self) -> ft.Stack:
        """Crea el stack con el grafo de la ruta"""
        import math
        stack_controls = []

        # Primero dibujamos las aristas (conexiones)
        for conexion in self.conexiones:
            origen_pos = self.node_positions.get(conexion.parada_origen_id)
            destino_pos = self.node_positions.get(conexion.parada_destino_id)

            if origen_pos and destino_pos:
                x1, y1 = origen_pos
                x2, y2 = destino_pos
                dx = x2 - x1
                dy = y2 - y1
                length = math.sqrt(dx ** 2 + dy ** 2)
                angle = math.degrees(math.atan2(dy, dx))

                # Dibujar la línea (simulada con un Container rotado)
                line = ft.Container(
                    width=length - self.node_radius,  # Deja espacio para la flecha
                    height=2,
                    bgcolor="green",
                    left=x1,
                    top=y1,
                    rotate=angle,
                )
                stack_controls.append(line)

                # Dibujar la flecha (▶) cerca del nodo destino
                arrow_offset = 10  # Distancia de la flecha al borde del nodo destino
                arrow_x = x2 - self.node_radius * math.cos(angle * math.pi / 180) - arrow_offset * math.cos(angle * math.pi / 180)
                arrow_y = y2 - self.node_radius * math.sin(angle * math.pi / 180) - arrow_offset * math.sin(angle * math.pi / 180)
                arrow = ft.Text(
                    "▶",
                    size=18,
                    color="green",
                    left=arrow_x - 9,  # Ajuste visual
                    top=arrow_y - 9,   # Ajuste visual
                    rotate=angle,
                )
                stack_controls.append(arrow)

                # Calcular punto medio para mostrar la distancia
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                # Texto con la distancia
                distance_text = ft.Text(
                    f"{conexion.distancia} km",
                    size=10,
                    color="black",
                    bgcolor="white",
                    left=mid_x,
                    top=mid_y,
                )
                stack_controls.append(distance_text)

        # Luego dibujamos los nodos (paradas)
        for parada in self.paradas:
            pos = self.node_positions.get(parada.id)
            if pos:
                x, y = pos

                # Dibujar círculo (nodo)
                circle = ft.Container(
                    width=self.node_radius * 2,
                    height=self.node_radius * 2,
                    border_radius=self.node_radius,
                    bgcolor="blue",
                    alignment=ft.alignment.center,
                    content=ft.Text(str(parada.id), color="white", size=10),
                    left=x - self.node_radius,
                    top=y - self.node_radius,
                )
                stack_controls.append(circle)

                # Texto con nombre de la parada
                name_text = ft.Text(
                    parada.nombre,
                    size=12,
                    color="black",
                    left=x - self.node_radius,
                    top=y + self.node_radius * 1.2,
                )
                stack_controls.append(name_text)

        return ft.Stack(
            controls=stack_controls,
            width=self.canvas_width,
            height=self.canvas_height
        )
    
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
                ft.Text(message, color=color, size=14),
            ], spacing=8),
            padding=12,
            border_radius=6,
            bgcolor=bgcolor,
            border=ft.border.all(1, color)
        )
        
        if self._page_ref:
            self._page_ref.update()
    
    def clear_message(self):
        """Limpia el mensaje mostrado"""
        self.message_container.content = None
        if self._page_ref:
            self._page_ref.update()
