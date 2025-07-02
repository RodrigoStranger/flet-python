"""
Validadores para diferentes tipos de datos
"""
import re
from typing import List, Dict, Any


class EmailValidator:
    """Validador de correos electrónicos"""
    
    @staticmethod
    def validate(email: str) -> Dict[str, Any]:
        """
        Valida un correo electrónico
        
        Args:
            email: Correo a validar
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        
        if not email:
            errors.append("El correo es obligatorio")
        elif not EmailValidator.is_valid_format(email):
            errors.append("Formato de correo inválido")
        elif len(email) > 100:
            errors.append("El correo es demasiado largo (máximo 100 caracteres)")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "cleaned_value": email.lower().strip() if email else ""
        }
    
    @staticmethod
    def is_valid_format(email: str) -> bool:
        """
        Verifica el formato del correo
        
        Args:
            email: Correo a verificar
            
        Returns:
            True si el formato es válido
        """
        if not email:
            return False
            
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


class PasswordValidator:
    """Validador de contraseñas"""
    
    MIN_LENGTH = 4
    MAX_LENGTH = 255
    
    @staticmethod
    def validate(password: str) -> Dict[str, Any]:
        """
        Valida una contraseña
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        
        if not password:
            errors.append("La contraseña es obligatoria")
        elif len(password) < PasswordValidator.MIN_LENGTH:
            errors.append(f"La contraseña debe tener al menos {PasswordValidator.MIN_LENGTH} caracteres")
        elif len(password) > PasswordValidator.MAX_LENGTH:
            errors.append(f"La contraseña es demasiado larga (máximo {PasswordValidator.MAX_LENGTH} caracteres)")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength": PasswordValidator.get_strength(password) if password else "weak"
        }
    
    @staticmethod
    def get_strength(password: str) -> str:
        """
        Evalúa la fortaleza de la contraseña
        
        Args:
            password: Contraseña a evaluar
            
        Returns:
            Nivel de fortaleza: weak, medium, strong
        """
        if len(password) < 4:
            return "weak"
        elif len(password) < 8:
            return "medium"
        else:
            # Verificar si tiene mayúsculas, minúsculas, números y símbolos
            has_upper = bool(re.search(r'[A-Z]', password))
            has_lower = bool(re.search(r'[a-z]', password))
            has_digit = bool(re.search(r'\d', password))
            has_symbol = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
            
            complexity_score = sum([has_upper, has_lower, has_digit, has_symbol])
            
            if complexity_score >= 3:
                return "strong"
            elif complexity_score >= 2:
                return "medium"
            else:
                return "weak"


class NameValidator:
    """Validador de nombres"""
    
    MIN_LENGTH = 2
    MAX_LENGTH = 100
    
    @staticmethod
    def validate(name: str) -> Dict[str, Any]:
        """
        Valida un nombre
        
        Args:
            name: Nombre a validar
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        
        if not name or not name.strip():
            errors.append("El nombre no debe estar vacío")
        elif len(name.strip()) > NameValidator.MAX_LENGTH:
            errors.append(f"El nombre es demasiado largo (máximo {NameValidator.MAX_LENGTH} caracteres)")
        elif not NameValidator.is_valid_format(name):
            errors.append("El nombre contiene caracteres no válidos")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "cleaned_value": name.strip().title() if name else ""
        }
    
    @staticmethod
    def is_valid_format(name: str) -> bool:
        """
        Verifica que el nombre contenga solo caracteres válidos
        
        Args:
            name: Nombre a verificar
            
        Returns:
            True si el formato es válido
        """
        if not name:
            return False
            
        # Permitir letras, espacios, guiones y apostrofes
        pattern = r"^[a-zA-ZÀ-ÿñÑ\s\-']+$"
        return re.match(pattern, name.strip()) is not None
