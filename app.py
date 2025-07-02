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
from views.login_view import LoginView
from views.register_view import RegisterView  
from views.dashboard_view import DashboardView
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
            on_logout=self.handle_logout
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
        """Muestra la vista del dashboard"""
        if not self.current_user:
            logger.warning("Intento de acceder al dashboard sin autenticación")
            self.show_login()
            return
        
        self._clear_and_show(self.dashboard_view.create(user=self.current_user))
        logger.debug(f"Dashboard mostrado para: {self.current_user.nombre}")
    
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
