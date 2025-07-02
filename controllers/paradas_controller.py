"""
Controlador de Paradas
Maneja la lógica de negocio relacionada con paradas de rutas
"""
import logging
from typing import List, Dict, Any, Optional
from models import Parada
from config.mysql_db import MySQL

logger = logging.getLogger(__name__)


class ParadasController:
    """
    Controlador para gestionar paradas de rutas
    """
    
    def __init__(self):
        """Inicializa el controlador de paradas"""
        self.db = MySQL()
    
    def get_route_stops(self, route_id: int, user_id: int) -> Dict[str, Any]:
        """
        Obtiene todas las paradas de una ruta específica
        
        Args:
            route_id: ID de la ruta
            user_id: ID del usuario (para verificar permisos)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar parámetros
            if not route_id or route_id <= 0:
                return {
                    "success": False,
                    "message": "ID de ruta inválido",
                    "paradas": []
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "paradas": []
                }
            
            # Verificar que la ruta existe y pertenece al usuario
            check_query = """
                SELECT COUNT(*) as count 
                FROM rutas 
                WHERE id = %s AND usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(check_query, (route_id, user_id))
            result = cursor.fetchone()
            
            if result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ruta no encontrada o no tienes permisos",
                    "paradas": []
                }
            
            # Consultar paradas de la ruta
            query = """
                SELECT id, ruta_id, nombre, descripcion, created_at
                FROM paradas 
                WHERE ruta_id = %s 
                ORDER BY created_at ASC
            """
            
            cursor.execute(query, (route_id,))
            paradas_data = cursor.fetchall()
            cursor.close()
            
            # Convertir a objetos Parada
            paradas = []
            for parada_data in paradas_data:
                parada = Parada.from_dict(parada_data)
                paradas.append(parada)
            
            logger.info(f"Paradas obtenidas para ruta {route_id}: {len(paradas)}")
            
            return {
                "success": True,
                "message": f"Se encontraron {len(paradas)} paradas",
                "paradas": paradas,
                "total": len(paradas)
            }
            
        except Exception as e:
            logger.error(f"Error al obtener paradas de la ruta {route_id}: {e}")
            return {
                "success": False,
                "message": "Error al obtener las paradas",
                "paradas": []
            }
        
        finally:
            self.db.disconnect()
    
    def create_stop(self, route_id: int, user_id: int, nombre: str, descripcion: Optional[str] = None) -> Dict[str, Any]:
        """
        Crea una nueva parada para una ruta
        
        Args:
            route_id: ID de la ruta
            user_id: ID del usuario (para verificar permisos)
            nombre: Nombre de la parada
            descripcion: Descripción de la parada (opcional)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Procesar la descripción
            descripcion_final = None
            if descripcion and descripcion.strip():
                descripcion_final = descripcion.strip()
            
            # Crear objeto parada
            nueva_parada = Parada(
                ruta_id=route_id,
                nombre=nombre,
                descripcion=descripcion_final
            )
            
            # Validar la parada
            if not nueva_parada.is_valid():
                errors = nueva_parada.get_validation_errors()
                return {
                    "success": False,
                    "message": "; ".join(errors),
                    "parada": None
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "parada": None
                }
            
            # Verificar que la ruta existe y pertenece al usuario
            check_query = """
                SELECT COUNT(*) as count 
                FROM rutas 
                WHERE id = %s AND usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(check_query, (route_id, user_id))
            result = cursor.fetchone()
            
            if result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ruta no encontrada o no tienes permisos",
                    "parada": None
                }
            
            # Verificar que no existe una parada con el mismo nombre en esta ruta
            duplicate_query = """
                SELECT COUNT(*) as count 
                FROM paradas 
                WHERE ruta_id = %s AND nombre = %s
            """
            cursor.execute(duplicate_query, (route_id, nombre.strip()))
            duplicate_result = cursor.fetchone()
            
            if duplicate_result['count'] > 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ya existe una parada con ese nombre en esta ruta",
                    "parada": None
                }
            
            # Insertar nueva parada
            insert_query = """
                INSERT INTO paradas (ruta_id, nombre, descripcion)
                VALUES (%s, %s, %s)
            """
            
            cursor.execute(insert_query, (route_id, nombre.strip(), descripcion_final))
            parada_id = cursor.lastrowid
            connection.commit()
            cursor.close()
            
            # Crear objeto parada con ID
            nueva_parada.id = parada_id
            
            logger.info(f"Parada creada exitosamente: ID {parada_id}, Ruta {route_id}")
            
            return {
                "success": True,
                "message": "Parada creada exitosamente",
                "parada": nueva_parada
            }
            
        except Exception as e:
            logger.error(f"Error al crear parada: {e}")
            return {
                "success": False,
                "message": "Error al crear la parada",
                "parada": None
            }
        
        finally:
            self.db.disconnect()
    
    def update_stop(self, stop_id: int, route_id: int, user_id: int, nombre: str, descripcion: Optional[str] = None) -> Dict[str, Any]:
        """
        Actualiza una parada existente
        
        Args:
            stop_id: ID de la parada a actualizar
            route_id: ID de la ruta (para verificar permisos)
            user_id: ID del usuario (para verificar permisos)
            nombre: Nuevo nombre de la parada
            descripcion: Nueva descripción de la parada (opcional)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar datos
            if not nombre or not nombre.strip():
                return {
                    "success": False,
                    "message": "El nombre de la parada es obligatorio"
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos"
                }
            
            # Verificar que la parada existe y pertenece a una ruta del usuario
            check_query = """
                SELECT COUNT(*) as count 
                FROM paradas p
                INNER JOIN rutas r ON p.ruta_id = r.id
                WHERE p.id = %s AND p.ruta_id = %s AND r.usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(check_query, (stop_id, route_id, user_id))
            result = cursor.fetchone()
            
            if result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Parada no encontrada o no tienes permisos"
                }
            
            # Verificar que no existe otra parada con el mismo nombre en esta ruta
            duplicate_query = """
                SELECT COUNT(*) as count 
                FROM paradas 
                WHERE ruta_id = %s AND nombre = %s AND id != %s
            """
            cursor.execute(duplicate_query, (route_id, nombre.strip(), stop_id))
            duplicate_result = cursor.fetchone()
            
            if duplicate_result['count'] > 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ya existe una parada con ese nombre en esta ruta"
                }
            
            # Actualizar la parada
            update_query = """
                UPDATE paradas 
                SET nombre = %s, descripcion = %s
                WHERE id = %s AND ruta_id = %s
            """
            
            cursor.execute(update_query, (nombre.strip(), descripcion, stop_id, route_id))
            connection.commit()
            cursor.close()
            
            logger.info(f"Parada actualizada: ID {stop_id} -> {nombre.strip()}")
            
            return {
                "success": True,
                "message": "Parada actualizada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error al actualizar parada {stop_id}: {e}")
            return {
                "success": False,
                "message": "Error al actualizar la parada"
            }
        
        finally:
            self.db.disconnect()
    
    def delete_stop(self, stop_id: int, route_id: int, user_id: int) -> Dict[str, Any]:
        """
        Elimina una parada
        
        Args:
            stop_id: ID de la parada a eliminar
            route_id: ID de la ruta (para verificar permisos)
            user_id: ID del usuario (para verificar permisos)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos"
                }
            
            # Verificar que la parada existe y pertenece a una ruta del usuario
            check_query = """
                SELECT COUNT(*) as count 
                FROM paradas p
                INNER JOIN rutas r ON p.ruta_id = r.id
                WHERE p.id = %s AND p.ruta_id = %s AND r.usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(check_query, (stop_id, route_id, user_id))
            result = cursor.fetchone()
            
            if result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Parada no encontrada o no tienes permisos"
                }
            
            # Eliminar parada (CASCADE eliminará vecinos automáticamente)
            delete_query = "DELETE FROM paradas WHERE id = %s AND ruta_id = %s"
            cursor.execute(delete_query, (stop_id, route_id))
            connection.commit()
            cursor.close()
            
            logger.info(f"Parada eliminada: ID {stop_id}, Ruta {route_id}")
            
            return {
                "success": True,
                "message": "Parada eliminada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error al eliminar parada {stop_id}: {e}")
            return {
                "success": False,
                "message": "Error al eliminar la parada"
            }
        
        finally:
            self.db.disconnect()
