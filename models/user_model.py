"""
Modelo de Usuario
Maneja la lógica de datos del usuario y validaciones básicas
"""
import re
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class User:
    """Clase de datos para representar un usuario"""
    id: Optional[int] = None
    nombre: str = ""
    correo: str = ""
    clave: str = ""


class UserModel:
    """
    Modelo de Usuario que maneja la lógica de datos
    """
    
    @staticmethod
    def validate_user_data(nombre: str, correo: str, clave: str) -> Dict[str, Any]:
        """
        Valida los datos de usuario para registro
        
        Args:
            nombre: Nombre del usuario
            correo: Correo electrónico
            clave: Contraseña
            
        Returns:
            Dict con el resultado de la validación
        """
        errors = []
        
        # Validar nombre
        if not nombre or not nombre.strip():
            errors.append("El nombre no debe estar vacío")
        
        # Validar correo
        if not correo:
            errors.append("El correo es obligatorio")
        elif not UserModel.is_valid_email(correo):
            errors.append("Formato de correo inválido")
        
        # Validar contraseña
        if not clave:
            errors.append("La contraseña es obligatoria")
        elif len(clave) < 4:
            errors.append("La contraseña debe tener al menos 4 caracteres")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_login_data(correo: str, clave: str) -> Dict[str, Any]:
        """
        Valida los datos de login
        
        Args:
            correo: Correo electrónico
            clave: Contraseña
            
        Returns:
            Dict con el resultado de la validación
        """
        errors = []
        
        # Validar correo
        if not correo:
            errors.append("El correo es obligatorio")
        elif not UserModel.is_valid_email(correo):
            errors.append("Formato de correo inválido")
        
        # Validar contraseña
        if not clave:
            errors.append("La contraseña es obligatoria")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Valida el formato de un correo electrónico
        
        Args:
            email: Correo a validar
            
        Returns:
            True si el formato es válido, False en caso contrario
        """
        if not email:
            return False
            
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def create_user_object(nombre: str, correo: str, clave: str) -> User:
        """
        Crea un objeto User con los datos proporcionados
        
        Args:
            nombre: Nombre del usuario
            correo: Correo electrónico
            clave: Contraseña
            
        Returns:
            Objeto User
        """
        return User(
            nombre=nombre.strip(),
            correo=correo.lower().strip(),
            clave=clave
        )
    
    @staticmethod
    def clean_user_data(nombre: str, correo: str, clave: str) -> Dict[str, str]:
        """
        Limpia y normaliza los datos del usuario
        
        Args:
            nombre: Nombre del usuario
            correo: Correo electrónico
            clave: Contraseña
            
        Returns:
            Dict con los datos limpios
        """
        return {
            "nombre": nombre.strip(),
            "correo": correo.lower().strip(),
            "clave": clave
        }
