"""
Controlador de Autenticación
Maneja toda la lógica de negocio relacionada con autenticación de usuarios
"""
from typing import Dict, Any, Optional
import logging

from config.mysql_db import connect_db, disconnect_db, login_user, register_user
from models import UserModel, User, EmailValidator, PasswordValidator, NameValidator

logger = logging.getLogger(__name__)


class AuthController:
    """
    Controlador que maneja la lógica de autenticación
    """
    
    def __init__(self):
        self.current_user: Optional[User] = None
        self.is_connected = False
    
    def login(self, correo: str, clave: str) -> Dict[str, Any]:
        """
        Procesa el login de un usuario
        
        Args:
            correo: Correo electrónico
            clave: Contraseña
            
        Returns:
            Dict con el resultado del login
        """
        try:
            # Validar datos de entrada
            validation = UserModel.validate_login_data(correo, clave)
            if not validation["is_valid"]:
                return {
                    "success": False,
                    "message": validation["errors"][0],
                    "user": None
                }
            
            # Conectar a la base de datos
            if not self._ensure_connection():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "user": None
                }
            
            # Limpiar datos
            clean_data = UserModel.clean_user_data("", correo, clave)
            
            # Intentar login
            resultado = login_user(clean_data["correo"], clean_data["clave"])
            
            if resultado["success"]:
                # Crear objeto User
                user_data = resultado["user"]
                self.current_user = User(
                    id=user_data["id"],
                    nombre=user_data["nombre"],
                    correo=user_data["correo"],
                    clave=""  # No almacenar la contraseña
                )
                
                logger.info(f"Login exitoso para usuario: {self.current_user.correo}")
                
                return {
                    "success": True,
                    "message": resultado["message"],
                    "user": self.current_user
                }
            else:
                return {
                    "success": False,
                    "message": resultado["message"],
                    "user": None
                }
                
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return {
                "success": False,
                "message": "Error inesperado durante el login",
                "user": None
            }
    
    def register(self, nombre: str, correo: str, clave: str) -> Dict[str, Any]:
        """
        Procesa el registro de un nuevo usuario
        
        Args:
            nombre: Nombre del usuario
            correo: Correo electrónico
            clave: Contraseña
            
        Returns:
            Dict con el resultado del registro
        """
        try:
            # Validar datos de entrada
            validation = UserModel.validate_user_data(nombre, correo, clave)
            if not validation["is_valid"]:
                return {
                    "success": False,
                    "message": validation["errors"][0]
                }
            
            # Validaciones adicionales más específicas
            name_validation = NameValidator.validate(nombre)
            if not name_validation["is_valid"]:
                return {
                    "success": False,
                    "message": name_validation["errors"][0]
                }
            
            email_validation = EmailValidator.validate(correo)
            if not email_validation["is_valid"]:
                return {
                    "success": False,
                    "message": email_validation["errors"][0]
                }
            
            password_validation = PasswordValidator.validate(clave)
            if not password_validation["is_valid"]:
                return {
                    "success": False,
                    "message": password_validation["errors"][0]
                }
            
            # Conectar a la base de datos
            if not self._ensure_connection():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos"
                }
            
            # Limpiar datos
            clean_data = UserModel.clean_user_data(nombre, correo, clave)
            
            # Intentar registro
            resultado = register_user(
                clean_data["nombre"],
                clean_data["correo"],
                clean_data["clave"]
            )
            
            if resultado["success"]:
                logger.info(f"Registro exitoso para usuario: {clean_data['correo']}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error en registro: {e}")
            return {
                "success": False,
                "message": "Error inesperado durante el registro"
            }
    
    def logout(self) -> Dict[str, Any]:
        """
        Cierra la sesión del usuario actual
        
        Returns:
            Dict con el resultado del logout
        """
        try:
            if self.current_user:
                logger.info(f"Logout para usuario: {self.current_user.correo}")
                self.current_user = None
            
            self._disconnect()
            
            return {
                "success": True,
                "message": "Sesión cerrada correctamente"
            }
            
        except Exception as e:
            logger.error(f"Error en logout: {e}")
            return {
                "success": False,
                "message": "Error al cerrar sesión"
            }
    
    def get_current_user(self) -> Optional[User]:
        """
        Obtiene el usuario actualmente autenticado
        
        Returns:
            Usuario actual o None si no hay sesión activa
        """
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """
        Verifica si hay un usuario autenticado
        
        Returns:
            True si hay un usuario autenticado
        """
        return self.current_user is not None
    
    def _ensure_connection(self) -> bool:
        """
        Asegura que haya conexión a la base de datos
        
        Returns:
            True si la conexión está activa
        """
        try:
            if not self.is_connected:
                self.is_connected = connect_db()
            return self.is_connected
        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            return False
    
    def _disconnect(self):
        """
        Desconecta de la base de datos
        """
        try:
            disconnect_db()
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error al desconectar: {e}")
    
    def validate_field(self, field_name: str, value: str) -> Dict[str, Any]:
        """
        Valida un campo específico
        
        Args:
            field_name: Nombre del campo (nombre, correo, clave)
            value: Valor a validar
            
        Returns:
            Dict con el resultado de la validación
        """
        if field_name == "nombre":
            return NameValidator.validate(value)
        elif field_name == "correo":
            return EmailValidator.validate(value)
        elif field_name == "clave":
            return PasswordValidator.validate(value)
        else:
            return {
                "is_valid": False,
                "errors": ["Campo no reconocido"]
            }
