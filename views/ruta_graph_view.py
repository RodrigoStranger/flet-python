"""
Vista de Grafo de Ruta Mejorada
Utiliza NetworkX y Matplotlib para una mejor visualización del grafo
"""
import flet as ft
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import io
import base64
from typing import Callable, Optional, List, Dict, Tuple
from models import User, Ruta, Parada, Conexion


class RutaGraphView:
    """
    Vista para visualizar el grafo de una ruta usando NetworkX y Matplotlib
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
        
        # Configuración del grafo
        self.graph = nx.DiGraph()  # Grafo dirigido
        self.figure_size = (12, 8)
        self.current_layout = "spring"
        self.shortest_path = None
        self.start_node = None
        self.end_node = None
        
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
        if page:
            self._page_ref = page
            
        self.user = user
        self.ruta = ruta
        self.paradas = paradas or []
        self.conexiones = conexiones or []
        
        # Construir el grafo
        self._build_graph()
        
        # Información de la ruta
        ruta_nombre = ruta.nombre if ruta else "Ruta"
        ruta_descripcion = ruta.descripcion if ruta and ruta.descripcion else "Sin descripción"
        
        # Crear contenedores
        self.message_container = ft.Container()
        self.route_info_container = ft.Ref[ft.Container]()
        self.start_dropdown = ft.Ref[ft.Dropdown]()
        self.end_dropdown = ft.Ref[ft.Dropdown]()
        self.calculate_button = ft.Ref[ft.ElevatedButton]()
        
        self.graph_container = ft.Container(
            content=self._create_graph_visualization(),
            border=ft.border.all(1, "grey400"),
            border_radius=10,
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
                
                # Información del grafo y controles
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("📊 Grafo de Ruta", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"({len(self.paradas)} paradas, {len(self.conexiones)} conexiones)", 
                                   size=14, color="grey"),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        # Estadísticas del grafo (eliminadas: nodos, aristas, densidad)
                        #
                        # Controles de layout (eliminar botón análisis)
                        ft.Row([
                            ft.Dropdown(
                                label="Layout del Grafo",
                                value=self.current_layout,
                                options=[
                                    ft.dropdown.Option("spring", "Spring Layout"),
                                    ft.dropdown.Option("circular", "Circular Layout"),
                                    ft.dropdown.Option("kamada_kawai", "Kamada-Kawai"),
                                    ft.dropdown.Option("planar", "Planar Layout"),
                                    ft.dropdown.Option("shell", "Shell Layout"),
                                ],
                                width=180,
                                on_change=self._on_layout_change
                            ),
                            ft.ElevatedButton(
                                "🔄 Regenerar",
                                on_click=self._regenerate_graph,
                                icon=ft.Icons.REFRESH
                            ),
                            # Botón de análisis eliminado
                        ], spacing=10),
                        
                        # Controles de Dijkstra
                        ft.Container(
                            content=ft.Column([
                                ft.Text("🛣️ Ruta Más Corta (Dijkstra)", size=16, weight=ft.FontWeight.BOLD),
                                ft.Row([
                                    ft.Dropdown(
                                        label="Parada de Origen",
                                        hint_text="Seleccionar origen",
                                        options=[ft.dropdown.Option(str(p.id), f"{p.id} - {p.nombre}") for p in self.paradas],
                                        width=200,
                                        on_change=self._on_start_node_change,
                                        ref=self.start_dropdown
                                    ),
                                    ft.Dropdown(
                                        label="Parada de Destino",
                                        hint_text="Seleccionar destino",
                                        options=[ft.dropdown.Option(str(p.id), f"{p.id} - {p.nombre}") for p in self.paradas],
                                        width=200,
                                        on_change=self._on_end_node_change,
                                        ref=self.end_dropdown
                                    ),
                                    ft.ElevatedButton(
                                        "🚀 Calcular Ruta Óptima",
                                        on_click=self._calculate_shortest_path,
                                        icon=ft.Icons.ROUTE,
                                        disabled=True,
                                        tooltip="Selecciona origen y destino",
                                        ref=self.calculate_button
                                    ),
                                ], spacing=10),
                                
                                # Información de la ruta calculada
                                ft.Container(
                                    content=ft.Row([
                                        ft.Text("Ruta: No calculada", size=12, color="grey"),
                                        ft.Text("Distancia: --", size=12, color="grey"),
                                    ], spacing=20),
                                    visible=False,
                                    ref=self.route_info_container
                                )
                            ], spacing=10),
                            padding=15,
                            border=ft.border.all(1, "orange300"),
                            border_radius=8,
                            bgcolor="orange50"
                        ),
                        
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=10)
                ),
                
                ft.Container(height=10),
                
                # Contenedor del grafo
                ft.Container(
                    content=self.graph_container,
                    alignment=ft.alignment.center
                ),
                
                ft.Container(height=20),
                
                # Leyenda mejorada
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=15, height=15, bgcolor="lightblue", border_radius=50, border=ft.border.all(2, "blue")),
                                ft.Text("Parada", size=12),
                            ], spacing=5),
                            padding=5,
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=30, height=3, bgcolor="red"),
                                ft.Text("→", size=14, color="red"),
                                ft.Text("Conexión", size=12),
                            ], spacing=5),
                            padding=5,
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=30, height=4, bgcolor="gold"),
                                ft.Text("→", size=14, color="gold"),
                                ft.Text("Ruta óptima", size=12),
                            ], spacing=5),
                            padding=5,
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=15, height=15, bgcolor="lightgreen", border_radius=50, border=ft.border.all(2, "green")),
                                ft.Text("Origen", size=12),
                            ], spacing=5),
                            padding=5,
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=15, height=15, bgcolor="lightcoral", border_radius=50, border=ft.border.all(2, "red")),
                                ft.Text("Destino", size=12),
                            ], spacing=5),
                            padding=5,
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=15, height=15, bgcolor="lightyellow", border_radius=50, border=ft.border.all(2, "orange")),
                                ft.Text("En ruta óptima", size=12),
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
    
    def _build_graph(self):
        """Construye el grafo NetworkX a partir de las paradas y conexiones"""
        self.graph.clear()
        
        # Agregar nodos (paradas)
        for parada in self.paradas:
            self.graph.add_node(parada.id, 
                              nombre=parada.nombre,
                              descripcion=getattr(parada, 'descripcion', ''),
                              latitud=getattr(parada, 'latitud', None),
                              longitud=getattr(parada, 'longitud', None))
        
        # Agregar aristas (conexiones)
        for conexion in self.conexiones:
            self.graph.add_edge(conexion.parada_origen_id, 
                              conexion.parada_destino_id,
                              distancia=conexion.distancia,
                              tiempo=getattr(conexion, 'tiempo', None))
    
    def _create_graph_visualization(self) -> ft.Image:
        """Crea la visualización del grafo usando matplotlib y la convierte a imagen"""
        if not self.graph.nodes():
            return ft.Container(
                content=ft.Text("No hay datos para mostrar el grafo", size=16, color="grey"),
                alignment=ft.alignment.center,
                height=400
            )
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=100)
        fig.patch.set_facecolor('white')

        # Si hay ruta óptima, mostrar solo subgrafo de la ruta
        if self.shortest_path and len(self.shortest_path) > 1:
            sub_nodes = set(self.shortest_path)
            sub_edges = set()
            for i in range(len(self.shortest_path)-1):
                sub_edges.add((self.shortest_path[i], self.shortest_path[i+1]))
            G = nx.DiGraph()
            for n in sub_nodes:
                parada = next((p for p in self.paradas if p.id == n), None)
                G.add_node(n, nombre=parada.nombre if parada else str(n))
            for u, v in sub_edges:
                data = self.graph.get_edge_data(u, v, default={})
                G.add_edge(u, v, **data)
            graph_to_draw = G
        else:
            graph_to_draw = self.graph

        # Layout
        try:
            if self.current_layout == "spring":
                pos = nx.spring_layout(graph_to_draw, k=2, iterations=50)
            elif self.current_layout == "circular":
                pos = nx.circular_layout(graph_to_draw)
            elif self.current_layout == "kamada_kawai":
                pos = nx.kamada_kawai_layout(graph_to_draw)
            elif self.current_layout == "planar":
                if nx.is_planar(graph_to_draw):
                    pos = nx.planar_layout(graph_to_draw)
                else:
                    pos = nx.spring_layout(graph_to_draw, k=2, iterations=50)
            elif self.current_layout == "shell":
                pos = nx.shell_layout(graph_to_draw)
            else:
                pos = nx.spring_layout(graph_to_draw, k=2, iterations=50)
        except:
            pos = nx.spring_layout(graph_to_draw, k=2, iterations=50)

        # Aristas y colores
        edge_labels = {}
        edge_colors = []
        edge_widths = []
        for edge in graph_to_draw.edges(data=True):
            u, v, data = edge
            distancia = data.get('distancia', '')
            edge_labels[(u, v)] = f"{distancia} km"
            if self.shortest_path and (u, v) in zip(self.shortest_path, self.shortest_path[1:]):
                edge_colors.append('gold')
                edge_widths.append(4)
            else:
                edge_colors.append('red')
                edge_widths.append(2)
        nx.draw_networkx_edges(graph_to_draw, pos, 
                             edge_color=edge_colors,
                             width=edge_widths,
                             arrows=True,
                             arrowsize=20,
                             arrowstyle='->',
                             alpha=0.7,
                             ax=ax)
        # Nodos
        node_colors = []
        node_sizes = []
        for node in graph_to_draw.nodes():
            if self.shortest_path and node == self.start_node:
                node_colors.append('lightgreen')
                node_sizes.append(1000)
            elif self.shortest_path and node == self.end_node:
                node_colors.append('lightcoral')
                node_sizes.append(1000)
            elif self.shortest_path and node in self.shortest_path:
                node_colors.append('lightyellow')
                node_sizes.append(900)
            else:
                node_colors.append('lightblue')
                node_sizes.append(800)
        nx.draw_networkx_nodes(graph_to_draw, pos,
                             node_color=node_colors,
                             node_size=node_sizes,
                             edgecolors='blue',
                             linewidths=2,
                             ax=ax)
        # Etiquetas de nodos (IDs)
        nx.draw_networkx_labels(graph_to_draw, pos,
                              font_size=10,
                              font_weight='bold',
                              font_color='black',
                              ax=ax)
        # Etiquetas de aristas (distancias)
        nx.draw_networkx_edge_labels(graph_to_draw, pos, edge_labels,
                                   font_size=8,
                                   font_color='red',
                                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8),
                                   ax=ax)
        # Nombres de paradas
        for node, (x, y) in pos.items():
            parada = next((p for p in self.paradas if p.id == node), None)
            if parada:
                ax.text(x, y-0.15, parada.nombre, 
                       horizontalalignment='center',
                       verticalalignment='top',
                       fontsize=9,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        # Título
        title = f'Grafo de Ruta: {self.ruta.nombre if self.ruta else "Sin nombre"}'
        if self.shortest_path:
            path_str = " → ".join(str(node) for node in self.shortest_path)
            title += f'\nRuta Óptima: {path_str}'
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        plt.tight_layout()
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100, facecolor='white')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return ft.Image(
            src_base64=img_base64,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10
        )

    def _on_back_click(self, e):
        """Maneja el click del botón de volver"""
        self.on_back()
    
    def _on_start_node_change(self, e):
        """Maneja el cambio de nodo de inicio"""
        self.start_node = int(e.control.value) if e.control.value else None
        self._update_calculate_button()
    
    def _on_end_node_change(self, e):
        """Maneja el cambio de nodo de fin"""
        self.end_node = int(e.control.value) if e.control.value else None
        self._update_calculate_button()
    
    def _update_calculate_button(self):
        """Actualiza el estado del botón de calcular"""
        if hasattr(self, 'calculate_button') and self.calculate_button.current:
            can_calculate = (self.start_node is not None and 
                           self.end_node is not None and 
                           self.start_node != self.end_node)
            
            self.calculate_button.current.disabled = not can_calculate
            
            if can_calculate:
                self.calculate_button.current.tooltip = "Calcular ruta más corta"
            else:
                self.calculate_button.current.tooltip = "Selecciona origen y destino diferentes"
            
            if self._page_ref:
                self._page_ref.update()
    
    def _calculate_shortest_path(self, e):
        """Calcula la ruta más corta usando Dijkstra"""
        if not self.start_node or not self.end_node:
            self.show_message("Selecciona paradas de origen y destino", "warning")
            return
        
        if self.start_node == self.end_node:
            self.show_message("El origen y destino deben ser diferentes", "warning")
            return
        
        try:
            self.show_message("Calculando ruta más corta...", "info")
            
            # Calcular camino más corto con Dijkstra
            try:
                path = nx.shortest_path(self.graph, 
                                      source=self.start_node, 
                                      target=self.end_node, 
                                      weight='distancia',
                                      method='dijkstra')
                
                path_length = nx.shortest_path_length(self.graph, 
                                                    source=self.start_node, 
                                                    target=self.end_node, 
                                                    weight='distancia',
                                                    method='dijkstra')
                
                self.shortest_path = path
                
                # Actualizar información de la ruta
                self._update_route_info(path, path_length)
                
                # Regenerar grafo con la ruta resaltada
                self.graph_container.content = self._create_graph_visualization()
                
                if self._page_ref:
                    self._page_ref.update()
                
                self.show_message(f"Ruta óptima calculada: {path_length:.2f} km", "success")
                
            except nx.NetworkXNoPath:
                self.show_message("No existe una ruta entre las paradas seleccionadas", "error")
            except nx.NodeNotFound:
                self.show_message("Una de las paradas seleccionadas no existe en el grafo", "error")
                
        except Exception as ex:
            self.show_message(f"Error al calcular ruta: {str(ex)}", "error")
    
    def _update_route_info(self, path, distance):
        """Actualiza la información de la ruta calculada"""
        if hasattr(self, 'route_info_container') and self.route_info_container.current:
            path_names = []
            for node_id in path:
                parada = next((p for p in self.paradas if p.id == node_id), None)
                if parada:
                    path_names.append(f"{parada.id}-{parada.nombre}")
                else:
                    path_names.append(str(node_id))
            
            path_str = " → ".join(path_names)
            
            self.route_info_container.current.content = ft.Column([
                ft.Text(f"🛣️ Ruta: {path_str}", size=12, color="green", weight=ft.FontWeight.BOLD),
                ft.Text(f"📏 Distancia Total: {distance:.2f} km", size=12, color="blue"),
                ft.Text(f"🔢 Paradas: {len(path)} ({len(path)-1} conexiones)", size=12, color="orange"),
            ], spacing=2)
            
            self.route_info_container.current.visible = True
            
            if self._page_ref:
                self._page_ref.update()
    
    def _on_layout_change(self, e):
        """Maneja el cambio de layout del grafo"""
        self.current_layout = e.control.value
        self._regenerate_graph(e)
    
    def _regenerate_graph(self, e):
        """Regenera la visualización del grafo y vuelve al estado original"""
        self.shortest_path = None
        self.start_node = None
        self.end_node = None
        if hasattr(self, 'start_dropdown') and self.start_dropdown.current:
            self.start_dropdown.current.value = None
        if hasattr(self, 'end_dropdown') and self.end_dropdown.current:
            self.end_dropdown.current.value = None
        self._update_calculate_button()
        self.graph_container.content = self._create_graph_visualization()
        if self._page_ref:
            self._page_ref.update()
        self.show_message("Grafo regenerado exitosamente", "success")
    
    def _show_connectivity_analysis(self, e):
        """Muestra análisis de conectividad del grafo"""
        if not self.graph.nodes():
            self.show_message("No hay datos para analizar", "warning")
            return
        
        try:
            analysis = []
            
            # Análisis básico
            analysis.append(f"Nodos: {self.graph.number_of_nodes()}")
            analysis.append(f"Aristas: {self.graph.number_of_edges()}")
            
            if self.graph.number_of_nodes() > 1:
                analysis.append(f"Densidad: {nx.density(self.graph):.3f}")
                
                # Componentes conexas
                if self.graph.is_directed():
                    weak_components = list(nx.weakly_connected_components(self.graph))
                    strong_components = list(nx.strongly_connected_components(self.graph))
                    analysis.append(f"Componentes débilmente conexas: {len(weak_components)}")
                    analysis.append(f"Componentes fuertemente conexas: {len(strong_components)}")
                else:
                    components = list(nx.connected_components(self.graph))
                    analysis.append(f"Componentes conexas: {len(components)}")
                
                # Grado de nodos
                if self.graph.is_directed():
                    in_degrees = dict(self.graph.in_degree())
                    out_degrees = dict(self.graph.out_degree())
                    max_in = max(in_degrees.values()) if in_degrees else 0
                    max_out = max(out_degrees.values()) if out_degrees else 0
                    analysis.append(f"Grado de entrada máximo: {max_in}")
                    analysis.append(f"Grado de salida máximo: {max_out}")
                else:
                    degrees = dict(self.graph.degree())
                    max_degree = max(degrees.values()) if degrees else 0
                    analysis.append(f"Grado máximo: {max_degree}")
                
                # Camino más corto promedio
                try:
                    if nx.is_connected(self.graph.to_undirected()):
                        avg_path = nx.average_shortest_path_length(self.graph)
                        analysis.append(f"Camino más corto promedio: {avg_path:.2f}")
                except:
                    analysis.append("Camino más corto promedio: N/A (grafo no conexo)")
            
            message = "Análisis de conectividad:\\n" + "\\n".join(analysis)
            self.show_message(message, "info")
            
        except Exception as ex:
            self.show_message(f"Error en análisis: {str(ex)}", "error")
    
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
        
        # Procesar saltos de línea en el mensaje
        message_lines = message.split('\\n')
        
        if len(message_lines) > 1:
            # Mensaje multilínea
            content = ft.Column([
                ft.Row([
                    ft.Text(emoji, size=16),
                    ft.Text(message_lines[0], color=color, size=14, weight=ft.FontWeight.BOLD),
                ], spacing=8)
            ] + [
                ft.Text(line, color=color, size=12) for line in message_lines[1:]
            ], spacing=2)
        else:
            # Mensaje de una línea
            content = ft.Row([
                ft.Text(emoji, size=16),
                ft.Text(message, color=color, size=14),
            ], spacing=8)
        
        self.message_container.content = ft.Container(
            content=content,
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