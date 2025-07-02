"""
Configuración y constantes de la aplicación Tours App
"""
import logging
from typing import Dict, Any


class AppConfig:
    """
    Configuración central de la aplicación
    """
    
    # Configuración de la ventana
    WINDOW_CONFIG = {
        "width": 900,
        "height": 1000,
        "resizable": True,
        "maximizable": True,
        "minimizable": True,
        "title": "Tours App - Sistema de Autenticación",
        "icon": "assets/logo.jpeg"
    }
    
    # Configuración de logging
    LOGGING_CONFIG = {
        "level": logging.INFO,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
    
    # Configuración de UI
    UI_CONFIG = {
        "theme_mode": "light",
        "primary_color": "blue",
        "success_color": "green",
        "error_color": "red",
        "warning_color": "orange",
        "info_color": "grey"
    }
    
    # Configuración de campos
    FIELD_CONFIG = {
        "width": 300,
        "min_name_length": 2,
        "min_password_length": 4
    }
    
    # Mensajes de la aplicación
    MESSAGES = {
        "login": {
            "loading": "🔄 Iniciando sesión...",
            "success": "Inicio de sesión exitoso",
            "error_empty": "❌ Todos los campos son obligatorios",
            "error_email": "❌ Formato de correo inválido",
            "error_credentials": "❌ Correo o contraseña incorrectos",
            "error_connection": "❌ Error de conexión a la base de datos"
        },
        "register": {
            "loading": "🔄 Registrando usuario...",
            "success": "Usuario registrado exitosamente",
            "error_empty": "❌ Todos los campos son obligatorios",
            "error_name": "❌ El nombre no debe estar vacío",
            "error_email": "❌ Formato de correo inválido",
            "error_password": "❌ La contraseña debe tener al menos 4 caracteres",
            "error_email_exists": "❌ El correo ya está registrado",
            "error_connection": "❌ Error de conexión a la base de datos"
        },
        "general": {
            "welcome": "🎉 ¡Bienvenido!",
            "goodbye": "👋 Hasta luego",
            "error": "❌ Ha ocurrido un error",
            "success": "Operación exitosa"
        }
    }
    
    # Configuración de navegación
    NAVIGATION_CONFIG = {
        "login_delay": 1,  # segundos
        "register_delay": 2,  # segundos
        "default_view": "login"
    }
    
    @classmethod
    def get_window_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración de ventana"""
        return cls.WINDOW_CONFIG.copy()
    
    @classmethod
    def get_ui_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración de UI"""
        return cls.UI_CONFIG.copy()
    
    @classmethod
    def get_field_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración de campos"""
        return cls.FIELD_CONFIG.copy()
    
    @classmethod
    def get_message(cls, category: str, key: str) -> str:
        """
        Obtiene un mensaje específico
        
        Args:
            category: Categoría del mensaje (login, register, general)
            key: Clave del mensaje
            
        Returns:
            Mensaje correspondiente o mensaje de error si no existe
        """
        try:
            return cls.MESSAGES[category][key]
        except KeyError:
            return f"❌ Mensaje no encontrado: {category}.{key}"
    
    @classmethod
    def get_navigation_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración de navegación"""
        return cls.NAVIGATION_CONFIG.copy()
    
    @classmethod
    def setup_logging(cls):
        """Configura el sistema de logging"""
        logging.basicConfig(**cls.LOGGING_CONFIG)


def configure_page(page):
    """
    Configura las propiedades básicas de la página
    
    Args:
        page: Página de Flet a configurar
    """
    import flet as ft
    
    config = AppConfig.get_window_config()
    ui_config = AppConfig.get_ui_config()
    
    page.title = config["title"]
    page.theme_mode = ft.ThemeMode.LIGHT if ui_config["theme_mode"] == "light" else ft.ThemeMode.DARK
    page.window.width = config["width"]
    page.window.height = config["height"]
    page.window.resizable = config["resizable"]
    page.window.maximizable = config["maximizable"]
    page.window.minimizable = config["minimizable"]
    page.window.icon = config["icon"]
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
