"""
Modelo de Ruta
Representa una ruta del sistema
"""
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Ruta:
    """
    Clase que representa una ruta en el sistema
    """
    id: Optional[int] = None
    usuario_id: Optional[int] = None
    nombre: str = ""
    descripcion: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones post-inicialización"""
        if self.nombre:
            self.nombre = self.nombre.strip()
        if self.descripcion:
            self.descripcion = self.descripcion.strip()
    
    def to_dict(self) -> dict:
        """
        Convierte la ruta a diccionario
        
        Returns:
            Dict con los datos de la ruta
        """
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Ruta':
        """
        Crea una ruta desde un diccionario
        
        Args:
            data: Diccionario con los datos
            
        Returns:
            Instancia de Ruta
        """
        return cls(
            id=data.get('id'),
            usuario_id=data.get('usuario_id'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', ''),
            created_at=data.get('created_at')
        )
    
    def is_valid(self) -> bool:
        """
        Valida si la ruta tiene datos válidos
        
        Returns:
            True si es válida, False en caso contrario
        """
        return bool(self.nombre and self.nombre.strip())
    
    def get_validation_errors(self) -> List[str]:
        """
        Obtiene una lista de errores de validación
        
        Returns:
            Lista de errores
        """
        errors = []
        
        if not self.nombre or not self.nombre.strip():
            errors.append("El nombre de la ruta es obligatorio")
        elif len(self.nombre.strip()) < 2:
            errors.append("El nombre debe tener al menos 2 caracteres")
        elif len(self.nombre.strip()) > 100:
            errors.append("El nombre no puede tener más de 100 caracteres")
            
        if self.descripcion and len(self.descripcion) > 1000:
            errors.append("La descripción no puede tener más de 1000 caracteres")
            
        return errors
    
    def __str__(self) -> str:
        """Representación en string de la ruta"""
        return f"Ruta(id={self.id}, nombre='{self.nombre}', usuario_id={self.usuario_id})"
    
    def __repr__(self) -> str:
        """Representación técnica de la ruta"""
        return self.__str__()
