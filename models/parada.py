"""
Modelo de Parada
Representa una parada dentro de una ruta
"""
from datetime import datetime
from typing import Optional


class Parada:
    """
    Modelo para representar una parada en una ruta
    """
    
    def __init__(self, id: Optional[int] = None, ruta_id: int = None, nombre: str = "", 
                 descripcion: Optional[str] = None, created_at: Optional[datetime] = None):
        """
        Inicializa una nueva parada
        
        Args:
            id: ID único de la parada
            ruta_id: ID de la ruta a la que pertenece
            nombre: Nombre de la parada
            descripcion: Descripción de la parada
            created_at: Fecha de creación
        """
        self.id = id
        self.ruta_id = ruta_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.created_at = created_at
    
    def is_valid(self) -> bool:
        """
        Valida si la parada es válida
        
        Returns:
            True si es válida, False si no
        """
        return bool(self.nombre and self.nombre.strip() and self.ruta_id)
    
    def get_validation_errors(self) -> list:
        """
        Obtiene errores de validación
        
        Returns:
            Lista de errores
        """
        errors = []
        
        if not self.nombre or not self.nombre.strip():
            errors.append("El nombre de la parada es obligatorio")
        
        if not self.ruta_id:
            errors.append("La parada debe pertenecer a una ruta")
        
        return errors
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Parada':
        """
        Crea una parada desde un diccionario
        
        Args:
            data: Diccionario con datos de la parada
            
        Returns:
            Instancia de Parada
        """
        return cls(
            id=data.get('id'),
            ruta_id=data.get('ruta_id'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> dict:
        """
        Convierte la parada a diccionario
        
        Returns:
            Diccionario con datos de la parada
        """
        return {
            'id': self.id,
            'ruta_id': self.ruta_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'created_at': self.created_at
        }
    
    def __str__(self) -> str:
        """Representación en string de la parada"""
        return f"Parada(id={self.id}, nombre='{self.nombre}', ruta_id={self.ruta_id})"
    
    def __repr__(self) -> str:
        """Representación detallada de la parada"""
        return self.__str__()
