"""
Controlador principal de la aplicación Tours App
Maneja la lógica de alto nivel y coordinación entre componentes
"""
import logging
import time
import threading
from typing import Optional

from models import User
from controllers import AuthController, UIController
from views import LoginView, RegisterView, DashboardView

logger = logging.getLogger(__name__)


class AppController:
    """
    Controlador principal que coordina toda la aplicación
    """
    
    def __init__(self, page):
        """
        Inicializa el controlador de aplicación
        
        Args:
            page: Página de Flet
        """
        self.page = page
        
        # Inicializar controladores
        self.auth_controller = AuthController()
        self.ui_controller = UIController(page)
        
        # Inicializar vistas
        self.login_view = None
        self.register_view = None
        self.dashboard_view = None
        
        # Estado de la aplicación
        self.current_user: Optional[User] = None
        
        logger.info("AppController inicializado")
    
    def initialize(self):
        """Inicializa la aplicación completa"""
        try:
            # Configurar la aplicación
            self._setup_app()
            
            # Registrar vistas y callbacks
            self._register_views()
            self._register_callbacks()
            
            # Mostrar vista inicial
            self.show_login()
            
            logger.info("Aplicación inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar la aplicación: {e}")
            raise
    
    def _setup_app(self):
        """Configura la aplicación"""
        logger.debug("Configurando aplicación...")
        self.ui_controller.set_page_title("Tours App - Sistema de Autenticación")
    
    def _register_views(self):
        """Registra todas las vistas"""
        # Registrar vista de login
        self.ui_controller.register_view("login", self._create_login_view)
        
        # Registrar vista de registro
        self.ui_controller.register_view("register", self._create_register_view)
        
        # Registrar vista de dashboard
        self.ui_controller.register_view("dashboard", self._create_dashboard_view)
        
        logger.debug("Vistas registradas correctamente")
    
    def _register_callbacks(self):
        """Registra todos los callbacks"""
        # Callbacks de autenticación
        self.ui_controller.register_callback("login", self._handle_login)
        self.ui_controller.register_callback("register", self._handle_register)
        self.ui_controller.register_callback("logout", self._handle_logout)
        
        # Callbacks de navegación
        self.ui_controller.register_callback("go_to_login", self.show_login)
        self.ui_controller.register_callback("go_to_register", self.show_register)
        self.ui_controller.register_callback("go_to_dashboard", self.show_dashboard)
        
        logger.debug("Callbacks registrados correctamente")
    
    def _create_login_view(self):
        """Crea la vista de login"""
        self.login_view = LoginView(
            on_login=self._handle_login,
            on_go_to_register=self.show_register
        )
        return self.login_view.create()
    
    def _create_register_view(self):
        """Crea la vista de registro"""
        self.register_view = RegisterView(
            on_register=self._handle_register,
            on_go_to_login=self.show_login
        )
        return self.register_view.create()
    
    def _create_dashboard_view(self):
        """Crea la vista del dashboard"""
        self.dashboard_view = DashboardView(
            on_logout=self._handle_logout
        )
        return self.dashboard_view.create(user=self.current_user)
    
    def _handle_login(self, correo: str, clave: str):
        """Maneja el proceso de login"""
        if not self.login_view:
            logger.error("Vista de login no inicializada")
            return
        
        # Mostrar mensaje de carga
        self.login_view.show_message("🔄 Iniciando sesión...", "orange")
        
        # Procesar login
        resultado = self.auth_controller.login(correo, clave)
        
        if resultado["success"]:
            # Login exitoso
            self.current_user = resultado["user"]
            self.login_view.show_message(f"{resultado['message']}", "green")
            
            # Esperar un momento y cambiar a dashboard
            self._delayed_navigation(self.show_dashboard, 1)
            
            logger.info(f"Login exitoso para: {correo}")
        else:
            # Login fallido
            self.login_view.show_message(f"❌ {resultado['message']}", "red")
            logger.warning(f"Login fallido para: {correo} - {resultado['message']}")
    
    def _handle_register(self, nombre: str, correo: str, clave: str):
        """Maneja el proceso de registro"""
        if not self.register_view:
            logger.error("Vista de registro no inicializada")
            return
        
        # Mostrar mensaje de carga
        self.register_view.show_message("🔄 Registrando usuario...", "orange")
        
        # Procesar registro
        resultado = self.auth_controller.register(nombre, correo, clave)
        
        if resultado["success"]:
            # Registro exitoso
            self.register_view.show_message(f"{resultado['message']}", "green")
            
            # Limpiar campos
            self.register_view.clear_fields()
            
            # Esperar un momento y volver al login
            self._delayed_navigation(self.show_login, 2)
            
            logger.info(f"Registro exitoso para: {correo}")
        else:
            # Registro fallido
            self.register_view.show_message(f"❌ {resultado['message']}", "red")
            logger.warning(f"Registro fallido para: {correo} - {resultado['message']}")
    
    def _handle_logout(self):
        """Maneja el proceso de logout"""
        logger.info("Iniciando proceso de logout...")
        
        # Procesar logout
        resultado = self.auth_controller.logout()
        
        if resultado["success"]:
            self.current_user = None
            logger.info("Logout exitoso")
        else:
            logger.warning(f"Error en logout: {resultado['message']}")
        
        # Ir al login independientemente del resultado
        self.show_login()
    
    def _delayed_navigation(self, target_func, delay_seconds: int):
        """Ejecuta una navegación después de un delay"""
        def delayed_call():
            time.sleep(delay_seconds)
            target_func()
        
        thread = threading.Thread(target=delayed_call)
        thread.daemon = True
        thread.start()
    
    def show_login(self):
        """Muestra la vista de login"""
        logger.debug("Mostrando vista de login")
        self.ui_controller.show_view("login")
    
    def show_register(self):
        """Muestra la vista de registro"""
        logger.debug("Mostrando vista de registro")
        self.ui_controller.show_view("register")
    
    def show_dashboard(self):
        """Muestra la vista del dashboard"""
        if not self.current_user:
            logger.warning("Intento de acceder al dashboard sin usuario autenticado")
            self.show_login()
            return
        
        logger.debug(f"Mostrando dashboard para: {self.current_user.nombre}")
        self.ui_controller.show_view("dashboard")
    
    def get_current_user(self) -> Optional[User]:
        """Obtiene el usuario actual"""
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado"""
        return self.current_user is not None
    
    def cleanup(self):
        """Limpia recursos de la aplicación"""
        logger.info("Limpiando recursos de la aplicación...")
        
        try:
            # Logout si hay usuario autenticado
            if self.is_authenticated():
                self.auth_controller.logout()
            
            # Limpiar controladores
            self.ui_controller.cleanup()
            
            logger.info("Limpieza completada")
        except Exception as e:
            logger.error(f"Error durante la limpieza: {e}")
