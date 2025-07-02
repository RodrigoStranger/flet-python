"""
Manejador de eventos de la aplicación
"""
import logging
from typing import Dict, Callable, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Event:
    """
    Clase que representa un evento en la aplicación
    """
    
    def __init__(self, name: str, data: Dict[str, Any] = None):
        """
        Inicializa un evento
        
        Args:
            name: Nombre del evento
            data: Datos del evento
        """
        self.name = name
        self.data = data or {}
        self.timestamp = None
        
    def __repr__(self):
        return f"Event(name='{self.name}', data={self.data})"


class EventHandler(ABC):
    """
    Interfaz para manejadores de eventos
    """
    
    @abstractmethod
    def handle(self, event: Event) -> bool:
        """
        Maneja un evento
        
        Args:
            event: Evento a manejar
            
        Returns:
            True si el evento fue manejado correctamente
        """
        pass


class EventManager:
    """
    Manejador central de eventos de la aplicación
    """
    
    def __init__(self):
        """Inicializa el manejador de eventos"""
        self._handlers: Dict[str, list] = {}
        self._middleware: list = []
        logger.debug("EventManager inicializado")
    
    def register_handler(self, event_name: str, handler: Callable):
        """
        Registra un manejador para un evento específico
        
        Args:
            event_name: Nombre del evento
            handler: Función manejadora
        """
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        
        self._handlers[event_name].append(handler)
        logger.debug(f"Handler registrado para evento: {event_name}")
    
    def unregister_handler(self, event_name: str, handler: Callable):
        """
        Desregistra un manejador de evento
        
        Args:
            event_name: Nombre del evento
            handler: Función manejadora a remover
        """
        if event_name in self._handlers:
            try:
                self._handlers[event_name].remove(handler)
                logger.debug(f"Handler desregistrado para evento: {event_name}")
            except ValueError:
                logger.warning(f"Handler no encontrado para evento: {event_name}")
    
    def add_middleware(self, middleware: Callable):
        """
        Añade middleware que se ejecuta antes de cada evento
        
        Args:
            middleware: Función middleware
        """
        self._middleware.append(middleware)
        logger.debug("Middleware añadido")
    
    def emit(self, event_name: str, data: Dict[str, Any] = None) -> bool:
        """
        Emite un evento
        
        Args:
            event_name: Nombre del evento
            data: Datos del evento
            
        Returns:
            True si el evento fue procesado correctamente
        """
        event = Event(event_name, data)
        
        try:
            # Ejecutar middleware
            for middleware in self._middleware:
                if not middleware(event):
                    logger.warning(f"Middleware bloqueó evento: {event_name}")
                    return False
            
            # Ejecutar handlers
            if event_name in self._handlers:
                for handler in self._handlers[event_name]:
                    try:
                        handler(event)
                        logger.debug(f"Handler ejecutado para evento: {event_name}")
                    except Exception as e:
                        logger.error(f"Error en handler para evento {event_name}: {e}")
                        return False
            else:
                logger.debug(f"No hay handlers para evento: {event_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al emitir evento {event_name}: {e}")
            return False
    
    def get_registered_events(self) -> list:
        """
        Obtiene la lista de eventos registrados
        
        Returns:
            Lista de nombres de eventos
        """
        return list(self._handlers.keys())
    
    def clear_handlers(self, event_name: str = None):
        """
        Limpia los handlers de un evento específico o todos
        
        Args:
            event_name: Nombre del evento a limpiar (None para todos)
        """
        if event_name:
            if event_name in self._handlers:
                self._handlers[event_name].clear()
                logger.debug(f"Handlers limpiados para evento: {event_name}")
        else:
            self._handlers.clear()
            logger.debug("Todos los handlers limpiados")


# Instancia global del manejador de eventos
event_manager = EventManager()


# Decorador para registrar manejadores de eventos
def event_handler(event_name: str):
    """
    Decorador para registrar automáticamente un manejador de eventos
    
    Args:
        event_name: Nombre del evento
    """
    def decorator(func):
        event_manager.register_handler(event_name, func)
        return func
    return decorator


# Funciones utilitarias
def emit_event(event_name: str, data: Dict[str, Any] = None) -> bool:
    """
    Función utilitaria para emitir eventos
    
    Args:
        event_name: Nombre del evento
        data: Datos del evento
        
    Returns:
        True si el evento fue procesado correctamente
    """
    return event_manager.emit(event_name, data)


def register_event_handler(event_name: str, handler: Callable):
    """
    Función utilitaria para registrar manejadores de eventos
    
    Args:
        event_name: Nombre del evento
        handler: Función manejadora
    """
    event_manager.register_handler(event_name, handler)
