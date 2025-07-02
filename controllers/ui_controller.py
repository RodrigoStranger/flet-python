"""
Controlador de UI
Maneja la lógica de la interfaz de usuario y navegación
"""
from typing import Callable, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class UIController:
    """
    Controlador que maneja la lógica de la interfaz de usuario
    """
    
    def __init__(self, page):
        self.page = page
        self.current_view = None
        self.views = {}
        self.callbacks = {}
        
        # Configurar la página
        self._setup_page()
    
    def _setup_page(self):
        """Configura las propiedades básicas de la página"""
        self.page.title = "Tours App - Sistema de Autenticación"
        self.page.theme_mode = "light"
        self.page.window.width = 450
        self.page.window.height = 600
        self.page.window.resizable = True
        self.page.window.maximizable = True
        self.page.window.minimizable = True
        self.page.horizontal_alignment = "center"
        self.page.vertical_alignment = "center"
    
    def register_view(self, view_name: str, view_creator: Callable) -> None:
        """
        Registra una vista con su función creadora
        
        Args:
            view_name: Nombre de la vista
            view_creator: Función que crea la vista
        """
        self.views[view_name] = view_creator
        logger.debug(f"Vista registrada: {view_name}")
    
    def register_callback(self, callback_name: str, callback_func: Callable) -> None:
        """
        Registra un callback para eventos
        
        Args:
            callback_name: Nombre del callback
            callback_func: Función callback
        """
        self.callbacks[callback_name] = callback_func
        logger.debug(f"Callback registrado: {callback_name}")
    
    def show_view(self, view_name: str, **kwargs) -> bool:
        """
        Muestra una vista específica
        
        Args:
            view_name: Nombre de la vista a mostrar
            **kwargs: Argumentos adicionales para la vista
            
        Returns:
            True si la vista se mostró correctamente
        """
        try:
            if view_name not in self.views:
                logger.error(f"Vista no encontrada: {view_name}")
                return False
            
            # Limpiar la página
            self.page.clean()
            
            # Crear y mostrar la nueva vista
            view_creator = self.views[view_name]
            view_content = view_creator(**kwargs)
            
            self.page.add(view_content)
            self.page.update()
            
            self.current_view = view_name
            logger.info(f"Vista mostrada: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error al mostrar vista {view_name}: {e}")
            return False
    
    def get_current_view(self) -> Optional[str]:
        """
        Obtiene el nombre de la vista actual
        
        Returns:
            Nombre de la vista actual o None
        """
        return self.current_view
    
    def execute_callback(self, callback_name: str, *args, **kwargs) -> Any:
        """
        Ejecuta un callback registrado
        
        Args:
            callback_name: Nombre del callback
            *args: Argumentos posicionales
            **kwargs: Argumentos de palabra clave
            
        Returns:
            Resultado del callback
        """
        try:
            if callback_name not in self.callbacks:
                logger.error(f"Callback no encontrado: {callback_name}")
                return None
            
            callback_func = self.callbacks[callback_name]
            result = callback_func(*args, **kwargs)
            
            logger.debug(f"Callback ejecutado: {callback_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error al ejecutar callback {callback_name}: {e}")
            return None
    
    def update_page(self):
        """Actualiza la página"""
        try:
            self.page.update()
        except Exception as e:
            logger.error(f"Error al actualizar página: {e}")
    
    def show_message(self, message: str, color: str = "red", duration: int = 3) -> None:
        """
        Muestra un mensaje temporal (placeholder para futuras implementaciones)
        
        Args:
            message: Mensaje a mostrar
            color: Color del mensaje
            duration: Duración en segundos
        """
        # Esta función se puede expandir para mostrar mensajes toast o snackbar
        logger.info(f"Mensaje UI: {message}")
    
    def get_page_size(self) -> Dict[str, int]:
        """
        Obtiene el tamaño de la página
        
        Returns:
            Dict con width y height
        """
        return {
            "width": self.page.window.width,
            "height": self.page.window.height
        }
    
    def set_page_size(self, width: int, height: int):
        """
        Establece el tamaño de la página
        
        Args:
            width: Ancho
            height: Alto
        """
        try:
            self.page.window.width = width
            self.page.window.height = height
            self.page.update()
            logger.debug(f"Tamaño de página cambiado a: {width}x{height}")
        except Exception as e:
            logger.error(f"Error al cambiar tamaño de página: {e}")
    
    def set_page_title(self, title: str):
        """
        Establece el título de la página
        
        Args:
            title: Nuevo título
        """
        try:
            self.page.title = title
            self.page.update()
            logger.debug(f"Título cambiado a: {title}")
        except Exception as e:
            logger.error(f"Error al cambiar título: {e}")
    
    def cleanup(self):
        """Limpia recursos del controlador"""
        try:
            self.views.clear()
            self.callbacks.clear()
            self.current_view = None
            logger.info("UI Controller limpiado")
        except Exception as e:
            logger.error(f"Error al limpiar UI Controller: {e}")
