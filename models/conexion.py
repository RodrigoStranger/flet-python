"""
Modelo de Conexión/Vecino
Representa una conexión entre dos paradas con su distancia
"""
from typing import Optional, Dict, Any, List
from datetime import datetime


class Conexion:
    """
    Modelo para representar una conexión entre paradas
    """
    
    def __init__(self, parada_origen_id: int, parada_destino_id: int, distancia: float, 
                 parada_origen_nombre: str = None, parada_destino_nombre: str = None):
        """
        Inicializa una conexión
        
        Args:
            parada_origen_id: ID de la parada origen
            parada_destino_id: ID de la parada destino
            distancia: Distancia entre las paradas
            parada_origen_nombre: Nombre de la parada origen (opcional)
            parada_destino_nombre: Nombre de la parada destino (opcional)
        """
        self.parada_origen_id = parada_origen_id
        self.parada_destino_id = parada_destino_id
        self.distancia = distancia
        self.parada_origen_nombre = parada_origen_nombre
        self.parada_destino_nombre = parada_destino_nombre
    
    def is_valid(self) -> bool:
        """
        Valida si la conexión es válida
        
        Returns:
            True si es válida, False en caso contrario
        """
        try:
            # Validar IDs
            if not self.parada_origen_id or self.parada_origen_id <= 0:
                return False
            
            if not self.parada_destino_id or self.parada_destino_id <= 0:
                return False
            
            # No puede conectarse a sí misma (validación crítica)
            if self.parada_origen_id == self.parada_destino_id:
                return False
            
            # Validar distancia
            if self.distancia is None or self.distancia < 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_validation_errors(self) -> List[str]:
        """
        Obtiene lista de errores de validación
        
        Returns:
            Lista de strings con errores
        """
        errors = []
        
        try:
            if not self.parada_origen_id or self.parada_origen_id <= 0:
                errors.append("ID de parada origen inválido")
            
            if not self.parada_destino_id or self.parada_destino_id <= 0:
                errors.append("ID de parada destino inválido")
            
            if self.parada_origen_id == self.parada_destino_id:
                errors.append("⚠️ Error: La parada no puede conectarse a sí misma")
            
            if self.distancia is None or self.distancia < 0:
                errors.append("La distancia debe ser mayor o igual a 0")
                
        except Exception as e:
            errors.append(f"Error en validación: {str(e)}")
        
        return errors
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conexion':
        """
        Crea una conexión desde un diccionario
        
        Args:
            data: Diccionario con datos de la conexión
            
        Returns:
            Instancia de Conexion
        """
        return cls(
            parada_origen_id=data.get('parada_origen_id'),
            parada_destino_id=data.get('parada_destino_id'),
            distancia=float(data.get('distancia', 0)),
            parada_origen_nombre=data.get('parada_origen_nombre'),
            parada_destino_nombre=data.get('parada_destino_nombre')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la conexión a diccionario
        
        Returns:
            Diccionario con datos de la conexión
        """
        return {
            'parada_origen_id': self.parada_origen_id,
            'parada_destino_id': self.parada_destino_id,
            'distancia': self.distancia,
            'parada_origen_nombre': self.parada_origen_nombre,
            'parada_destino_nombre': self.parada_destino_nombre
        }
    
    def __str__(self) -> str:
        """Representación string de la conexión"""
        origen = self.parada_origen_nombre or f"ID {self.parada_origen_id}"
        destino = self.parada_destino_nombre or f"ID {self.parada_destino_id}"
        return f"{origen} → {destino} ({self.distancia}km)"
    
    def __repr__(self) -> str:
        """Representación para debug"""
        return f"Conexion(origen={self.parada_origen_id}, destino={self.parada_destino_id}, distancia={self.distancia})"
