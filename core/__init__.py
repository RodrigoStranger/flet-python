"""
Módulo core de la aplicación Tours App
Contiene la configuración y componentes centrales
"""

from .config import AppConfig
from .events import EventManager, Event, event_manager, emit_event, register_event_handler

__all__ = [
    'AppConfig',
    'EventManager', 
    'Event',
    'event_manager',
    'emit_event',
    'register_event_handler'
]
