"""
Controlador de Rutas
Maneja la lógica de negocio relacionada con rutas
"""
import logging
from typing import List, Dict, Any, Optional
from models import Ruta
from config.mysql_db import MySQL

logger = logging.getLogger(__name__)


class RoutesController:
    """
    Controlador para gestionar rutas del usuario
    """
    
    def __init__(self):
        """Inicializa el controlador de rutas"""
        self.db = MySQL()
    
    def get_user_routes(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene todas las rutas de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar user_id
            if not user_id or user_id <= 0:
                return {
                    "success": False,
                    "message": "ID de usuario inválido",
                    "routes": []
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "routes": []
                }
            
            # Consultar rutas del usuario
            query = """
                SELECT id, usuario_id, nombre, descripcion, created_at
                FROM rutas 
                WHERE usuario_id = %s 
                ORDER BY created_at DESC
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            routes_data = cursor.fetchall()
            cursor.close()
            
            # Convertir a objetos Ruta
            routes = []
            for route_data in routes_data:
                ruta = Ruta.from_dict(route_data)
                routes.append(ruta)
            
            logger.info(f"Rutas obtenidas para usuario {user_id}: {len(routes)}")
            
            return {
                "success": True,
                "message": f"Se encontraron {len(routes)} rutas",
                "routes": routes,
                "total": len(routes)
            }
            
        except Exception as e:
            logger.error(f"Error al obtener rutas del usuario {user_id}: {e}")
            return {
                "success": False,
                "message": "Error al obtener las rutas",
                "routes": []
            }
        
        finally:
            self.db.disconnect()
    
    def create_route(self, user_id: int, nombre: str, descripcion: str = "") -> Dict[str, Any]:
        """
        Crea una nueva ruta para el usuario
        
        Args:
            user_id: ID del usuario
            nombre: Nombre de la ruta
            descripcion: Descripción de la ruta
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Crear objeto ruta
            nueva_ruta = Ruta(
                usuario_id=user_id,
                nombre=nombre,
                descripcion=descripcion
            )
            
            # Validar la ruta
            if not nueva_ruta.is_valid():
                errors = nueva_ruta.get_validation_errors()
                return {
                    "success": False,
                    "message": "; ".join(errors),
                    "route": None
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "route": None
                }
            
            # Verificar que no existe una ruta con el mismo nombre para este usuario
            check_query = """
                SELECT COUNT(*) as count 
                FROM rutas 
                WHERE usuario_id = %s AND nombre = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(check_query, (user_id, nombre.strip()))
            result = cursor.fetchone()
            
            if result['count'] > 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ya existe una ruta con ese nombre",
                    "route": None
                }
            
            # Insertar nueva ruta
            insert_query = """
                INSERT INTO rutas (usuario_id, nombre, descripcion)
                VALUES (%s, %s, %s)
            """
            
            cursor.execute(insert_query, (user_id, nombre.strip(), descripcion.strip()))
            ruta_id = cursor.lastrowid
            connection.commit()
            cursor.close()
            
            # Crear objeto ruta con ID
            nueva_ruta.id = ruta_id
            
            logger.info(f"Ruta creada exitosamente: ID {ruta_id}, Usuario {user_id}")
            
            return {
                "success": True,
                "message": "Ruta creada exitosamente",
                "route": nueva_ruta
            }
            
        except Exception as e:
            logger.error(f"Error al crear ruta: {e}")
            return {
                "success": False,
                "message": "Error al crear la ruta",
                "route": None
            }
        
        finally:
            self.db.disconnect()
    
    def get_route_by_id(self, route_id: int, user_id: int) -> Dict[str, Any]:
        """
        Obtiene una ruta específica por ID
        
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
                    "route": None
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "route": None
                }
            
            # Consultar ruta
            query = """
                SELECT id, usuario_id, nombre, descripcion, created_at
                FROM rutas 
                WHERE id = %s AND usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (route_id, user_id))
            route_data = cursor.fetchone()
            cursor.close()
            
            if not route_data:
                return {
                    "success": False,
                    "message": "Ruta no encontrada",
                    "route": None
                }
            
            # Convertir a objeto Ruta
            ruta = Ruta.from_dict(route_data)
            
            return {
                "success": True,
                "message": "Ruta encontrada",
                "route": ruta
            }
            
        except Exception as e:
            logger.error(f"Error al obtener ruta {route_id}: {e}")
            return {
                "success": False,
                "message": "Error al obtener la ruta",
                "route": None
            }
        
        finally:
            self.db.disconnect()
    
    def delete_route(self, route_id: int, user_id: int) -> Dict[str, Any]:
        """
        Elimina una ruta
        
        Args:
            route_id: ID de la ruta
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
                    "message": "Ruta no encontrada o no tienes permisos"
                }
            
            # Eliminar ruta (CASCADE eliminará paradas y vecinos automáticamente)
            delete_query = "DELETE FROM rutas WHERE id = %s AND usuario_id = %s"
            cursor.execute(delete_query, (route_id, user_id))
            connection.commit()
            cursor.close()
            
            logger.info(f"Ruta eliminada: ID {route_id}, Usuario {user_id}")
            
            return {
                "success": True,
                "message": "Ruta eliminada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error al eliminar ruta {route_id}: {e}")
            return {
                "success": False,
                "message": "Error al eliminar la ruta"
            }
        
        finally:
            self.db.disconnect()
    
    def get_routes_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de rutas del usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con estadísticas
        """
        try:
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "stats": {}
                }
            
            # Consultar estadísticas
            query = """
                SELECT 
                    COUNT(*) as total_rutas,
                    COUNT(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as rutas_esta_semana,
                    COUNT(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as rutas_este_mes
                FROM rutas 
                WHERE usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            stats = cursor.fetchone()
            cursor.close()
            
            return {
                "success": True,
                "message": "Estadísticas obtenidas",
                "stats": stats or {}
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {
                "success": False,
                "message": "Error al obtener estadísticas",
                "stats": {}
            }
        
        finally:
            self.db.disconnect()
