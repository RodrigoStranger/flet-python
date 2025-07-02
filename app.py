"""
Tours App - Aplicación Principal Modularizada
Sistema de autenticación con arquitectura MVC simplificada
"""
import flet as ft
import logging
from typing import Optional, Dict, Any

# Importar módulos propios
from core.config import AppConfig, configure_page
from controllers.auth_controller import AuthController
from controllers.routes_controller import RoutesController
from controllers.paradas_controller import ParadasController
from views.login_view import LoginView
from views.register_view import RegisterView  
from views.dashboard_view import DashboardView
from views.paradas_view import ParadasView
from models import User

# Configurar logging
logging.basicConfig(
    level=AppConfig.LOGGING_CONFIG["level"],
    format=AppConfig.LOGGING_CONFIG["format"]
)
logger = logging.getLogger(__name__)


class ToursApp:
    """
    Clase principal de la aplicación Tours App
    Maneja la navegación y coordinación entre vistas
    """
    
    def __init__(self, page: ft.Page):
        """
        Inicializa la aplicación
        
        Args:
            page: Página de Flet
        """
        self.page = page
        self.current_user: Optional[User] = None
        
        # Configurar página
        configure_page(page)
        
        # Inicializar controladores
        self.auth_controller = AuthController()
        self.routes_controller = RoutesController()
        self.paradas_controller = ParadasController()
        
        # Inicializar vistas
        self._init_views()
        
        # Mostrar vista inicial
        self.show_login()
        
        logger.info("Tours App inicializada correctamente")
    
    def _init_views(self):
        """Inicializa todas las vistas"""
        self.login_view = LoginView(
            on_login=self.handle_login,
            on_go_to_register=self.show_register
        )
        
        self.register_view = RegisterView(
            on_register=self.handle_register,
            on_go_to_login=self.show_login
        )
        
        self.dashboard_view = DashboardView(
            on_logout=self.handle_logout,
            on_create_route=self.handle_create_route,
            on_edit_route=self.handle_edit_route,
            on_delete_route=self.handle_delete_route,
            on_view_stops=self.handle_view_stops
        )
        
        self.paradas_view = ParadasView(
            on_back=self.show_dashboard,
            on_create_stop=self.handle_create_stop,
            on_edit_stop=self.handle_edit_stop,
            on_delete_stop=self.handle_delete_stop
        )
    
    # =============== MANEJADORES DE EVENTOS ===============
    
    def handle_login(self, correo: str, clave: str):
        """
        Maneja el proceso de login
        
        Args:
            correo: Correo electrónico
            clave: Contraseña
        """
        try:
            # Mostrar estado de carga
            self.login_view.show_message(
                AppConfig.MESSAGES["login"]["loading"], 
                AppConfig.UI_CONFIG["warning_color"]
            )
            
            # Procesar login
            resultado = self.auth_controller.login(correo, clave)
            
            if resultado["success"]:
                self.current_user = resultado["user"]
                self.login_view.show_message(
                    resultado["message"], 
                    AppConfig.UI_CONFIG["success_color"]
                )
                
                # Navegar al dashboard después de un momento
                self._delayed_action(self.show_dashboard, 1)
                logger.info(f"Login exitoso para: {correo}")
                
            else:
                self.login_view.show_message(
                    resultado["message"], 
                    AppConfig.UI_CONFIG["error_color"]
                )
                logger.warning(f"Login fallido para: {correo}")
                
        except Exception as e:
            error_msg = "Error inesperado durante el login"
            self.login_view.show_message(error_msg, AppConfig.UI_CONFIG["error_color"])
            logger.error(f"Error en login: {e}")
    
    def handle_register(self, nombre: str, correo: str, clave: str):
        """
        Maneja el proceso de registro
        
        Args:
            nombre: Nombre del usuario
            correo: Correo electrónico
            clave: Contraseña
        """
        try:
            # Mostrar estado de carga
            self.register_view.show_message(
                AppConfig.MESSAGES["register"]["loading"],
                AppConfig.UI_CONFIG["warning_color"]
            )
            
            # Procesar registro
            resultado = self.auth_controller.register(nombre, correo, clave)
            
            if resultado["success"]:
                self.register_view.show_message(
                    resultado["message"],
                    AppConfig.UI_CONFIG["success_color"]
                )
                
                # Limpiar campos y volver al login
                self.register_view.clear_fields()
                self._delayed_action(self.show_login, 2)
                logger.info(f"Registro exitoso para: {correo}")
                
            else:
                self.register_view.show_message(
                    resultado["message"],
                    AppConfig.UI_CONFIG["error_color"]
                )
                logger.warning(f"Registro fallido para: {correo}")
                
        except Exception as e:
            error_msg = "Error inesperado durante el registro"
            self.register_view.show_message(error_msg, AppConfig.UI_CONFIG["error_color"])
            logger.error(f"Error en registro: {e}")
    
    def handle_logout(self):
        """Maneja el proceso de logout"""
        try:
            logger.info("Iniciando logout...")
            
            # Procesar logout
            self.auth_controller.logout()
            self.current_user = None
            
            # Volver al login
            self.show_login()
            logger.info("Logout completado")
            
        except Exception as e:
            logger.error(f"Error en logout: {e}")
            # Ir al login de todas formas
            self.show_login()
    
    def handle_create_route(self, nombre: str, descripcion: Optional[str]):
        """
        Maneja la creación de una nueva ruta
        
        Args:
            nombre: Nombre de la ruta
            descripcion: Descripción de la ruta (puede ser None)
        """
        try:
            if not self.current_user:
                logger.warning("Intento de crear ruta sin autenticación")
                self.show_login()
                return
            
            # Mostrar mensaje de carga
            self.dashboard_view.show_message("🔄 Creando ruta...", "info")
            
            # Crear la ruta
            resultado = self.routes_controller.create_route(
                user_id=self.current_user.id,
                nombre=nombre,
                descripcion=descripcion
            )
            
            if resultado["success"]:
                # Mostrar mensaje de éxito
                self.dashboard_view.show_message(
                    f"Ruta '{nombre}' creada exitosamente", 
                    "success"
                )
                
                # Actualizar la lista de rutas en el dashboard
                self._refresh_routes_in_dashboard()
                logger.info(f"Ruta creada: {nombre} (Usuario: {self.current_user.id})")
                
            else:
                # Mostrar error
                self.dashboard_view.show_message(
                    resultado["message"], 
                    "error"
                )
                logger.warning(f"Error al crear ruta: {resultado['message']}")
                
        except Exception as e:
            error_msg = "Error inesperado al crear la ruta"
            self.dashboard_view.show_message(error_msg, "error")
            logger.error(f"Error en crear ruta: {e}")
    
    def handle_edit_route(self, route_id: int, nombre: str, descripcion: Optional[str]):
        """
        Maneja la edición de una ruta existente
        
        Args:
            route_id: ID de la ruta a editar
            nombre: Nuevo nombre de la ruta
            descripcion: Nueva descripción de la ruta (puede ser None)
        """
        try:
            if not self.current_user:
                logger.warning("Intento de editar ruta sin autenticación")
                self.show_login()
                return
            
            # Mostrar mensaje de carga
            self.dashboard_view.show_message("🔄 Guardando cambios...", "info")
            
            # Editar la ruta usando el controlador
            resultado = self.routes_controller.update_route(
                route_id=route_id,
                user_id=self.current_user.id,
                nombre=nombre,
                descripcion=descripcion
            )
            
            if resultado["success"]:
                # Mostrar mensaje de éxito
                self.dashboard_view.show_message(
                    f"Ruta '{nombre}' actualizada exitosamente", 
                    "success"
                )
                
                # Actualizar la lista de rutas en el dashboard
                self._refresh_routes_in_dashboard()
                logger.info(f"Ruta editada: ID {route_id} -> {nombre} (Usuario: {self.current_user.id})")
                
            else:
                # Mostrar error
                self.dashboard_view.show_message(
                    resultado["message"], 
                    "error"
                )
                logger.warning(f"Error al editar ruta: {resultado['message']}")
                
        except Exception as e:
            error_msg = f"Error inesperado al editar ruta: {str(e)}"
            self.dashboard_view.show_message(error_msg, "error")
            logger.error(error_msg)
    
    def handle_delete_route(self, route_id: int, nombre: str):
        """
        Maneja la eliminación de una ruta
        
        Args:
            route_id: ID de la ruta a eliminar
            nombre: Nombre de la ruta (para logging y mensajes)
        """
        try:
            if not self.current_user:
                logger.warning("Intento de eliminar ruta sin autenticación")
                self.show_login()
                return
            
            # Mostrar mensaje de carga
            self.dashboard_view.show_message("🔄 Eliminando ruta...", "info")
            
            # Eliminar la ruta usando el controlador
            resultado = self.routes_controller.delete_route(
                route_id=route_id,
                user_id=self.current_user.id
            )
            
            if resultado["success"]:
                # Mostrar mensaje de éxito
                self.dashboard_view.show_message(
                    f"Ruta '{nombre}' eliminada exitosamente", 
                    "success"
                )
                
                # Actualizar la lista de rutas en el dashboard
                self._refresh_routes_in_dashboard()
                logger.info(f"Ruta eliminada: ID {route_id} - {nombre} (Usuario: {self.current_user.id})")
                
            else:
                # Mostrar error
                self.dashboard_view.show_message(
                    resultado["message"], 
                    "error"
                )
                logger.warning(f"Error al eliminar ruta: {resultado['message']}")
                
        except Exception as e:
            error_msg = f"Error inesperado al eliminar ruta: {str(e)}"
            self.dashboard_view.show_message(error_msg, "error")
            logger.error(error_msg)

    def handle_view_stops(self, ruta):
        """
        Maneja la visualización de paradas de una ruta
        
        Args:
            ruta: Ruta seleccionada
        """
        try:
            if not self.current_user:
                logger.warning("Intento de ver paradas sin autenticación")
                self.show_login()
                return
            
            # Obtener paradas de la ruta
            resultado = self.paradas_controller.get_route_stops(ruta.id, self.current_user.id)
            
            if resultado["success"]:
                paradas = resultado["paradas"]
                logger.info(f"Mostrando {len(paradas)} paradas para ruta {ruta.nombre}")
            else:
                paradas = []
                logger.warning(f"No se pudieron cargar paradas: {resultado['message']}")
            
            # Crear y mostrar la vista de paradas
            content = self.paradas_view.create(user=self.current_user, ruta=ruta, paradas=paradas)
            self.paradas_view.set_page_reference(self.page)
            self._clear_and_show(content)
            
            # Mostrar mensaje si hubo error al cargar
            if not resultado["success"]:
                self.paradas_view.show_message(
                    f"⚠️ {resultado['message']}", 
                    "warning"
                )
            
            logger.debug(f"Vista de paradas mostrada para ruta: {ruta.nombre}")
            
        except Exception as e:
            logger.error(f"Error al mostrar paradas: {e}")
            # Mostrar vista de paradas básica en caso de error
            content = self.paradas_view.create(user=self.current_user, ruta=ruta, paradas=[])
            self._clear_and_show(content)
    
    def handle_create_stop(self, route_id: int, nombre: str, descripcion: Optional[str]):
        """
        Maneja la creación de una nueva parada
        
        Args:
            route_id: ID de la ruta
            nombre: Nombre de la parada
            descripcion: Descripción de la parada (puede ser None)
        """
        try:
            if not self.current_user:
                logger.warning("Intento de crear parada sin autenticación")
                self.show_login()
                return
            
            # Mostrar mensaje de carga
            self.paradas_view.show_message("🔄 Creando parada...", "info")
            
            # Crear la parada
            resultado = self.paradas_controller.create_stop(
                route_id=route_id,
                user_id=self.current_user.id,
                nombre=nombre,
                descripcion=descripcion
            )
            
            if resultado["success"]:
                # Mostrar mensaje de éxito
                self.paradas_view.show_message(
                    f"Parada '{nombre}' creada exitosamente", 
                    "success"
                )
                
                # Actualizar la lista de paradas
                self._refresh_stops_in_view(route_id)
                logger.info(f"Parada creada: {nombre} (Ruta: {route_id})")
                
            else:
                # Mostrar error
                self.paradas_view.show_message(
                    resultado["message"], 
                    "error"
                )
                logger.warning(f"Error al crear parada: {resultado['message']}")
                
        except Exception as e:
            error_msg = "Error inesperado al crear la parada"
            self.paradas_view.show_message(error_msg, "error")
            logger.error(f"Error en crear parada: {e}")
    
    def handle_edit_stop(self, stop_id: int, route_id: int, nombre: str, descripcion: Optional[str]):
        """
        Maneja la edición de una parada existente
        
        Args:
            stop_id: ID de la parada a editar
            route_id: ID de la ruta
            nombre: Nuevo nombre de la parada
            descripcion: Nueva descripción de la parada (puede ser None)
        """
        try:
            if not self.current_user:
                logger.warning("Intento de editar parada sin autenticación")
                self.show_login()
                return
            
            # Mostrar mensaje de carga
            self.paradas_view.show_message("🔄 Guardando cambios...", "info")
            
            # Editar la parada
            resultado = self.paradas_controller.update_stop(
                stop_id=stop_id,
                route_id=route_id,
                user_id=self.current_user.id,
                nombre=nombre,
                descripcion=descripcion
            )
            
            if resultado["success"]:
                # Mostrar mensaje de éxito
                self.paradas_view.show_message(
                    f"Parada '{nombre}' actualizada exitosamente", 
                    "success"
                )
                
                # Actualizar la lista de paradas
                self._refresh_stops_in_view(route_id)
                logger.info(f"Parada editada: ID {stop_id} -> {nombre}")
                
            else:
                # Mostrar error
                self.paradas_view.show_message(
                    resultado["message"], 
                    "error"
                )
                logger.warning(f"Error al editar parada: {resultado['message']}")
                
        except Exception as e:
            error_msg = f"Error inesperado al editar parada: {str(e)}"
            self.paradas_view.show_message(error_msg, "error")
            logger.error(error_msg)
    
    def handle_delete_stop(self, stop_id: int, route_id: int, nombre: str):
        """
        Maneja la eliminación de una parada
        
        Args:
            stop_id: ID de la parada a eliminar
            route_id: ID de la ruta
            nombre: Nombre de la parada (para logging y mensajes)
        """
        try:
            if not self.current_user:
                logger.warning("Intento de eliminar parada sin autenticación")
                self.show_login()
                return
            
            # Mostrar mensaje de carga
            self.paradas_view.show_message("🔄 Eliminando parada...", "info")
            
            # Eliminar la parada
            resultado = self.paradas_controller.delete_stop(
                stop_id=stop_id,
                route_id=route_id,
                user_id=self.current_user.id
            )
            
            if resultado["success"]:
                # Mostrar mensaje de éxito
                self.paradas_view.show_message(
                    f"Parada '{nombre}' eliminada exitosamente", 
                    "success"
                )
                
                # Actualizar la lista de paradas
                self._refresh_stops_in_view(route_id)
                logger.info(f"Parada eliminada: ID {stop_id} - {nombre}")
                
            else:
                # Mostrar error
                self.paradas_view.show_message(
                    resultado["message"], 
                    "error"
                )
                logger.warning(f"Error al eliminar parada: {resultado['message']}")
                
        except Exception as e:
            error_msg = f"Error inesperado al eliminar parada: {str(e)}"
            self.paradas_view.show_message(error_msg, "error")
            logger.error(error_msg)
    
    def _refresh_routes_in_dashboard(self):
        """
        Actualiza las rutas en el dashboard actual sin recargar toda la vista
        """
        if not self.current_user:
            logger.warning("Intento de actualizar rutas sin autenticación")
            return
        
        try:
            # Obtener rutas del usuario
            resultado = self.routes_controller.get_user_routes(self.current_user.id)
            
            if resultado["success"]:
                routes = resultado["routes"]
                # Actualizar las rutas en el dashboard view
                self.dashboard_view.update_routes(routes)
                logger.info(f"Rutas actualizadas en dashboard: {len(routes)} rutas")
            else:
                logger.warning(f"Error al actualizar rutas: {resultado['message']}")
                # En caso de error, mostrar lista vacía
                self.dashboard_view.update_routes([])
                
        except Exception as e:
            logger.error(f"Error al actualizar rutas en dashboard: {e}")
            # En caso de error, mostrar lista vacía
            self.dashboard_view.update_routes([])
    
    def _refresh_stops_in_view(self, route_id: int):
        """
        Actualiza las paradas en la vista actual sin recargar toda la vista
        
        Args:
            route_id: ID de la ruta
        """
        if not self.current_user:
            logger.warning("Intento de actualizar paradas sin autenticación")
            return
        
        try:
            # Obtener paradas de la ruta
            resultado = self.paradas_controller.get_route_stops(route_id, self.current_user.id)
            
            if resultado["success"]:
                paradas = resultado["paradas"]
                # Actualizar las paradas en la vista
                self.paradas_view.update_stops(paradas)
                logger.info(f"Paradas actualizadas en vista: {len(paradas)} paradas")
            else:
                logger.warning(f"Error al actualizar paradas: {resultado['message']}")
                # En caso de error, mostrar lista vacía
                self.paradas_view.update_stops([])
                
        except Exception as e:
            logger.error(f"Error al actualizar paradas en vista: {e}")
            # En caso de error, mostrar lista vacía
            self.paradas_view.update_stops([])

    # =============== NAVEGACIÓN ===============
    
    def show_login(self):
        """Muestra la vista de login"""
        self._clear_and_show(self.login_view.create())
        logger.debug("Vista de login mostrada")
    
    def show_register(self):
        """Muestra la vista de registro"""
        self._clear_and_show(self.register_view.create())
        logger.debug("Vista de registro mostrada")
    
    def show_dashboard(self):
        """Muestra la vista del dashboard con rutas integradas"""
        if not self.current_user:
            logger.warning("Intento de acceder al dashboard sin autenticación")
            self.show_login()
            return
        
        try:
            # Obtener rutas del usuario
            resultado = self.routes_controller.get_user_routes(self.current_user.id)
            
            if resultado["success"]:
                routes = resultado["routes"]
                logger.info(f"Mostrando dashboard con {len(routes)} rutas para usuario {self.current_user.nombre}")
            else:
                routes = []
                logger.warning(f"No se pudieron cargar rutas: {resultado['message']}")
            
            # Crear y mostrar el dashboard con rutas
            content = self.dashboard_view.create(user=self.current_user, routes=routes)
            self.dashboard_view.set_page_reference(self.page)
            self._clear_and_show(content)
            
            # Mostrar mensaje si hubo error al cargar
            if not resultado["success"]:
                self.dashboard_view.show_message(
                    f"⚠️ {resultado['message']}", 
                    "warning"
                )
            
            logger.debug(f"Dashboard mostrado para: {self.current_user.nombre}")
            
        except Exception as e:
            logger.error(f"Error al mostrar dashboard: {e}")
            # Mostrar dashboard básico en caso de error
            content = self.dashboard_view.create(user=self.current_user, routes=[])
            self._clear_and_show(content)
    
    def _clear_and_show(self, content):
        """
        Limpia la página y muestra nuevo contenido
        
        Args:
            content: Contenido a mostrar
        """
        self.page.clean()
        self.page.add(content)
        self.page.update()
    
    # =============== UTILIDADES ===============
    
    def _delayed_action(self, action_func, delay_seconds: int):
        """
        Ejecuta una acción después de un delay
        
        Args:
            action_func: Función a ejecutar
            delay_seconds: Segundos de delay
        """
        import threading
        import time
        
        def delayed_call():
            time.sleep(delay_seconds)
            action_func()
        
        thread = threading.Thread(target=delayed_call)
        thread.daemon = True
        thread.start()
    
    def get_current_user(self) -> Optional[User]:
        """Obtiene el usuario actual"""
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado"""
        return self.current_user is not None
    
    def cleanup(self):
        """Limpia recursos de la aplicación"""
        try:
            if self.is_authenticated():
                self.auth_controller.logout()
            logger.info("Limpieza de la aplicación completada")
        except Exception as e:
            logger.error(f"Error durante la limpieza: {e}")
    
def main(page: ft.Page):
    """
    Función principal de la aplicación
    
    Args:
        page: Página de Flet
    """
    try:
        # Crear la aplicación
        app = ToursApp(page)
        
        # Manejar eventos de ventana
        def on_window_event(e):
            if e.data == "close":
                app.cleanup()
        
        page.window.on_event = on_window_event
        
    except Exception as e:
        logger.error(f"Error crítico al inicializar la aplicación: {e}")
        
        # Mostrar pantalla de error
        error_content = ft.Container(
            content=ft.Column([
                ft.Text("❌ Error de Inicialización", size=24, color="red", weight=ft.FontWeight.BOLD),
                ft.Text(f"Error: {str(e)}", size=14, color="grey"),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Cerrar Aplicación",
                    on_click=lambda _: page.window.close(),
                    bgcolor="red",
                    color="white"
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20),
            padding=40,
            border_radius=15,
            bgcolor="white"
        )
        
        page.add(error_content)
        page.update()


if __name__ == "__main__":
    logger.info("🚀 Iniciando Tours App...")
    ft.app(target=main)
