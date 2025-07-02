"""
Controlador de Conexiones
Maneja la lógica de negocio relacionada con conexiones entre paradas
"""
import logging
from typing import List, Dict, Any, Optional
from models import Conexion
from config.mysql_db import MySQL

logger = logging.getLogger(__name__)


class ConexionesController:
    """
    Controlador para gestionar conexiones entre paradas
    """
    
    def __init__(self):
        """Inicializa el controlador de conexiones"""
        self.db = MySQL()
    
    def get_route_connections(self, route_id: int, user_id: int) -> Dict[str, Any]:
        """
        Obtiene todas las conexiones de una ruta específica
        
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
                    "conexiones": []
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "conexiones": []
                }
            
            # Verificar que la ruta pertenece al usuario
            route_check_query = """
                SELECT COUNT(*) as count
                FROM rutas 
                WHERE id = %s AND usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(route_check_query, (route_id, user_id))
            route_result = cursor.fetchone()
            
            if route_result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ruta no encontrada o no tienes permisos",
                    "conexiones": []
                }
            
            # Consultar conexiones de la ruta con nombres de paradas
            query = """
                SELECT 
                    v.parada_origen_id,
                    v.parada_destino_id,
                    v.distancia,
                    po.nombre as parada_origen_nombre,
                    pd.nombre as parada_destino_nombre
                FROM vecinos v
                INNER JOIN paradas po ON v.parada_origen_id = po.id
                INNER JOIN paradas pd ON v.parada_destino_id = pd.id
                WHERE po.ruta_id = %s AND pd.ruta_id = %s
                ORDER BY po.nombre, pd.nombre
            """
            
            cursor.execute(query, (route_id, route_id))
            connections_data = cursor.fetchall()
            cursor.close()
            
            # Convertir a objetos Conexion
            conexiones = []
            for conn_data in connections_data:
                conexion = Conexion.from_dict(conn_data)
                conexiones.append(conexion)
            
            logger.info(f"Conexiones obtenidas para ruta {route_id}: {len(conexiones)}")
            
            return {
                "success": True,
                "message": f"Se encontraron {len(conexiones)} conexiones",
                "conexiones": conexiones,
                "total": len(conexiones)
            }
            
        except Exception as e:
            logger.error(f"Error al obtener conexiones de la ruta {route_id}: {e}")
            return {
                "success": False,
                "message": "Error al obtener las conexiones",
                "conexiones": []
            }
        
        finally:
            self.db.disconnect()
    
    def create_connection(self, route_id: int, user_id: int, parada_origen_id: int, 
                         parada_destino_id: int, distancia: float) -> Dict[str, Any]:
        """
        Crea una nueva conexión entre paradas
        
        Args:
            route_id: ID de la ruta
            user_id: ID del usuario (para verificar permisos)
            parada_origen_id: ID de la parada origen
            parada_destino_id: ID de la parada destino
            distancia: Distancia entre las paradas
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Crear objeto conexión
            nueva_conexion = Conexion(
                parada_origen_id=parada_origen_id,
                parada_destino_id=parada_destino_id,
                distancia=distancia
            )
            
            # Validar la conexión
            if not nueva_conexion.is_valid():
                errors = nueva_conexion.get_validation_errors()
                return {
                    "success": False,
                    "message": "; ".join(errors),
                    "conexion": None
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "conexion": None
                }
            
            # Verificar que la ruta pertenece al usuario
            route_check_query = """
                SELECT COUNT(*) as count
                FROM rutas 
                WHERE id = %s AND usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(route_check_query, (route_id, user_id))
            route_result = cursor.fetchone()
            
            if route_result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ruta no encontrada o no tienes permisos",
                    "conexion": None
                }
            
            # Verificar que ambas paradas pertenecen a la ruta
            stops_check_query = """
                SELECT COUNT(*) as count
                FROM paradas 
                WHERE ruta_id = %s AND id IN (%s, %s)
            """
            
            cursor.execute(stops_check_query, (route_id, parada_origen_id, parada_destino_id))
            stops_result = cursor.fetchone()
            
            if stops_result['count'] != 2:
                cursor.close()
                return {
                    "success": False,
                    "message": "Una o ambas paradas no pertenecen a esta ruta",
                    "conexion": None
                }
            
            # Verificar que la parada origen y destino son diferentes
            if parada_origen_id == parada_destino_id:
                cursor.close()
                return {
                    "success": False,
                    "message": "⚠️ Error: No se puede crear una conexión de una parada a sí misma",
                    "conexion": None
                }
                
            # Verificar que no existe ya esta conexión
            existing_check_query = """
                SELECT COUNT(*) as count
                FROM vecinos 
                WHERE parada_origen_id = %s AND parada_destino_id = %s
            """
            
            cursor.execute(existing_check_query, (parada_origen_id, parada_destino_id))
            existing_result = cursor.fetchone()
            
            if existing_result['count'] > 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ya existe una conexión entre estas paradas",
                    "conexion": None
                }
            
            # Insertar nueva conexión
            insert_query = """
                INSERT INTO vecinos (parada_origen_id, parada_destino_id, distancia)
                VALUES (%s, %s, %s)
            """
            
            cursor.execute(insert_query, (parada_origen_id, parada_destino_id, distancia))
            connection.commit()
            cursor.close()
            
            logger.info(f"Conexión creada: {parada_origen_id} → {parada_destino_id} ({distancia}km)")
            
            return {
                "success": True,
                "message": "Conexión creada exitosamente",
                "conexion": nueva_conexion
            }
            
        except Exception as e:
            logger.error(f"Error al crear conexión: {e}")
            return {
                "success": False,
                "message": "Error al crear la conexión",
                "conexion": None
            }
        
        finally:
            self.db.disconnect()
    
    def delete_connection(self, route_id: int, user_id: int, parada_origen_id: int, 
                         parada_destino_id: int) -> Dict[str, Any]:
        """
        Elimina una conexión entre paradas
        
        Args:
            route_id: ID de la ruta
            user_id: ID del usuario (para verificar permisos)
            parada_origen_id: ID de la parada origen
            parada_destino_id: ID de la parada destino
            
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
            
            # Verificar que la ruta pertenece al usuario
            route_check_query = """
                SELECT COUNT(*) as count
                FROM rutas 
                WHERE id = %s AND usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(route_check_query, (route_id, user_id))
            route_result = cursor.fetchone()
            
            if route_result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ruta no encontrada o no tienes permisos"
                }
            
            # Verificar que la conexión existe
            check_query = """
                SELECT COUNT(*) as count
                FROM vecinos v
                INNER JOIN paradas po ON v.parada_origen_id = po.id
                INNER JOIN paradas pd ON v.parada_destino_id = pd.id
                WHERE v.parada_origen_id = %s AND v.parada_destino_id = %s
                AND po.ruta_id = %s AND pd.ruta_id = %s
            """
            
            cursor.execute(check_query, (parada_origen_id, parada_destino_id, route_id, route_id))
            result = cursor.fetchone()
            
            if result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Conexión no encontrada"
                }
            
            # Eliminar conexión
            delete_query = """
                DELETE FROM vecinos 
                WHERE parada_origen_id = %s AND parada_destino_id = %s
            """
            
            cursor.execute(delete_query, (parada_origen_id, parada_destino_id))
            connection.commit()
            cursor.close()
            
            logger.info(f"Conexión eliminada: {parada_origen_id} → {parada_destino_id}")
            
            return {
                "success": True,
                "message": "Conexión eliminada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error al eliminar conexión: {e}")
            return {
                "success": False,
                "message": "Error al eliminar la conexión"
            }
        
        finally:
            self.db.disconnect()
    
    def get_stop_connections(self, stop_id: int, route_id: int, user_id: int) -> Dict[str, Any]:
        """
        Obtiene todas las conexiones de una parada específica
        
        Args:
            stop_id: ID de la parada
            route_id: ID de la ruta
            user_id: ID del usuario (para verificar permisos)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar parámetros
            if not stop_id or stop_id <= 0 or not route_id or route_id <= 0:
                return {
                    "success": False,
                    "message": "ID de parada o ruta inválido",
                    "conexiones": []
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "conexiones": []
                }
            
            # Verificar que la ruta pertenece al usuario
            route_check_query = """
                SELECT COUNT(*) as count
                FROM rutas 
                WHERE id = %s AND usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(route_check_query, (route_id, user_id))
            route_result = cursor.fetchone()
            
            if route_result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ruta no encontrada o no tienes permisos",
                    "conexiones": []
                }
            
            # Verificar que la parada pertenece a la ruta
            stop_check_query = """
                SELECT COUNT(*) as count
                FROM paradas 
                WHERE id = %s AND ruta_id = %s
            """
            
            cursor.execute(stop_check_query, (stop_id, route_id))
            stop_result = cursor.fetchone()
            
            if stop_result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Parada no encontrada en esta ruta",
                    "conexiones": []
                }
            
            # Consultar conexiones de la parada (como origen o destino)
            query = """
                SELECT 
                    v.parada_origen_id,
                    v.parada_destino_id,
                    v.distancia,
                    po.nombre as parada_origen_nombre,
                    pd.nombre as parada_destino_nombre
                FROM vecinos v
                INNER JOIN paradas po ON v.parada_origen_id = po.id
                INNER JOIN paradas pd ON v.parada_destino_id = pd.id
                WHERE (v.parada_origen_id = %s OR v.parada_destino_id = %s)
                AND po.ruta_id = %s AND pd.ruta_id = %s
                ORDER BY po.nombre, pd.nombre
            """
            
            cursor.execute(query, (stop_id, stop_id, route_id, route_id))
            connections_data = cursor.fetchall()
            cursor.close()
            
            # Convertir a objetos Conexion
            conexiones = []
            for conn_data in connections_data:
                conexion = Conexion.from_dict(conn_data)
                conexiones.append(conexion)
            
            logger.info(f"Conexiones obtenidas para parada {stop_id}: {len(conexiones)}")
            
            return {
                "success": True,
                "message": f"Se encontraron {len(conexiones)} conexiones",
                "conexiones": conexiones
            }
            
        except Exception as e:
            logger.error(f"Error al obtener conexiones de la parada {stop_id}: {e}")
            return {
                "success": False,
                "message": "Error al obtener las conexiones",
                "conexiones": []
            }
        
        finally:
            self.db.disconnect()
    
    def get_available_stops_for_connection(self, stop_id: int, route_id: int, user_id: int) -> Dict[str, Any]:
        """
        Obtiene las paradas de una ruta que están disponibles para crear conexiones
        desde una parada específica (excluye las paradas ya conectadas y la parada origen)
        
        Args:
            stop_id: ID de la parada origen
            route_id: ID de la ruta
            user_id: ID del usuario (para verificar permisos)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar parámetros
            if not stop_id or stop_id <= 0 or not route_id or route_id <= 0:
                return {
                    "success": False,
                    "message": "ID de parada o ruta inválido",
                    "paradas": []
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos",
                    "paradas": []
                }
            
            # Verificar que la ruta pertenece al usuario
            route_check_query = """
                SELECT COUNT(*) as count
                FROM rutas 
                WHERE id = %s AND usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(route_check_query, (route_id, user_id))
            route_result = cursor.fetchone()
            
            if route_result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ruta no encontrada o no tienes permisos",
                    "paradas": []
                }
            
            # Obtener todas las paradas disponibles (excluyendo la parada origen y las que ya tienen conexión saliente)
            query = """
                SELECT p.id, p.nombre, p.descripcion
                FROM paradas p
                WHERE p.ruta_id = %s 
                AND p.id != %s  -- Excluir la parada origen (importante para evitar conexiones a sí misma)
                AND p.id NOT IN (
                    -- Excluir las paradas que ya tienen conexión saliente desde la parada origen
                    SELECT parada_destino_id FROM vecinos WHERE parada_origen_id = %s
                )
                ORDER BY p.nombre
            """
            
            cursor.execute(query, (route_id, stop_id, stop_id))
            paradas_data = cursor.fetchall()
            
            # Imprimir información de depuración
            logger.info(f"SQL para paradas disponibles: {query}")
            logger.info(f"Parámetros: route_id={route_id}, stop_id={stop_id}")
            logger.info(f"Total de paradas en la ruta: {len(paradas_data)}")
            
            # Si no hay paradas disponibles, hacer un diagnóstico detallado
            if len(paradas_data) == 0:
                total_query = """
                    SELECT COUNT(*) as total FROM paradas WHERE ruta_id = %s
                """
                cursor.execute(total_query, (route_id,))
                total_result = cursor.fetchone()
                total_paradas = total_result['total'] if total_result else 0
                
                logger.info(f"Total de paradas en la ruta {route_id}: {total_paradas}")
                
                # Si hay más de una parada en la ruta, investigar por qué no hay disponibles
                if total_paradas > 1:
                    # Contar conexiones salientes de esta parada
                    out_conn_query = """
                        SELECT COUNT(*) as total FROM vecinos WHERE parada_origen_id = %s
                    """
                    cursor.execute(out_conn_query, (stop_id,))
                    out_conn_result = cursor.fetchone()
                    conexiones_salientes = out_conn_result['total'] if out_conn_result else 0
                    
                    # Listar los IDs de las paradas conectadas
                    connected_query = """
                        SELECT parada_destino_id FROM vecinos WHERE parada_origen_id = %s
                    """
                    cursor.execute(connected_query, (stop_id,))
                    connected_stops = [row['parada_destino_id'] for row in cursor.fetchall()]
                    
                    # Listar todas las paradas (excepto la origen) para ver qué está pasando
                    all_stops_query = """
                        SELECT id, nombre FROM paradas 
                        WHERE ruta_id = %s AND id != %s
                    """
                    cursor.execute(all_stops_query, (route_id, stop_id))
                    all_stops = cursor.fetchall()
                    
                    logger.warning(
                        f"Diagnóstico para parada {stop_id}: "
                        f"Total paradas en ruta: {total_paradas}, "
                        f"Conexiones salientes: {conexiones_salientes}, "
                        f"Paradas conectadas: {connected_stops}, "
                        f"Todas las paradas (excepto origen): {[s['id'] for s in all_stops]}"
                    )
            
            cursor.close()
            
            logger.info(f"Paradas disponibles para conectar desde parada {stop_id}: {len(paradas_data)}")
            
            # Si no hay paradas disponibles, simplemente retornar lista vacía
            if len(paradas_data) == 0:
                return {
                    "success": True,
                    "message": f"No se encontraron paradas disponibles para conectar",
                    "paradas": []
                }
            
            return {
                "success": True,
                "message": f"Se encontraron {len(paradas_data)} paradas disponibles",
                "paradas": paradas_data
            }
            
        except Exception as e:
            logger.error(f"Error al obtener paradas disponibles para conexión: {e}")
            return {
                "success": False,
                "message": "Error al obtener las paradas disponibles",
                "paradas": []
            }
        
        finally:
            self.db.disconnect()

    def get_route_stops_for_connections(self, route_id: int, user_id: int) -> Dict[str, Any]:
        """
        Obtiene todas las paradas de una ruta para usar en selectores de conexiones
        
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
                    "message": "Error de conexión a la base de datos",
                    "paradas": []
                }
            
            # Verificar que la ruta pertenece al usuario
            route_check_query = """
                SELECT COUNT(*) as count
                FROM rutas 
                WHERE id = %s AND usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(route_check_query, (route_id, user_id))
            route_result = cursor.fetchone()
            
            if route_result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ruta no encontrada o no tienes permisos",
                    "paradas": []
                }
            
            # Consultar paradas de la ruta
            query = """
                SELECT id, nombre, descripcion
                FROM paradas 
                WHERE ruta_id = %s 
                ORDER BY nombre
            """
            
            cursor.execute(query, (route_id,))
            paradas_data = cursor.fetchall()
            cursor.close()
            
            return {
                "success": True,
                "message": f"Se encontraron {len(paradas_data)} paradas",
                "paradas": paradas_data
            }
            
        except Exception as e:
            logger.error(f"Error al obtener paradas para conexiones: {e}")
            return {
                "success": False,
                "message": "Error al obtener las paradas",
                "paradas": []
            }
        
        finally:
            self.db.disconnect()
    
    def update_connection(self, route_id: int, user_id: int, parada_origen_id: int, 
                         parada_destino_id: int, distancia: float, 
                         parada_destino_anterior_id: int = None) -> Dict[str, Any]:
        """
        Actualiza una conexión existente entre paradas
        
        Args:
            route_id: ID de la ruta
            user_id: ID del usuario (para verificar permisos)
            parada_origen_id: ID de la parada origen
            parada_destino_id: ID de la nueva parada destino
            distancia: Nueva distancia entre las paradas
            parada_destino_anterior_id: ID de la parada destino anterior (si se está cambiando)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar que la parada origen y destino son diferentes
            if parada_origen_id == parada_destino_id:
                return {
                    "success": False,
                    "message": "⚠️ Error: No se puede conectar una parada consigo misma",
                }
                
            # Validar la distancia
            if distancia < 0:
                return {
                    "success": False,
                    "message": "La distancia no puede ser negativa",
                }
            
            # Conectar a la base de datos
            if not self.db.connect():
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos"
                }
            
            # Verificar que la ruta pertenece al usuario
            route_check_query = """
                SELECT COUNT(*) as count
                FROM rutas 
                WHERE id = %s AND usuario_id = %s
            """
            
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(route_check_query, (route_id, user_id))
            route_result = cursor.fetchone()
            
            if route_result['count'] == 0:
                cursor.close()
                return {
                    "success": False,
                    "message": "Ruta no encontrada o no tienes permisos"
                }
            
            # Verificar que ambas paradas pertenecen a la ruta
            stops_check_query = """
                SELECT COUNT(*) as count
                FROM paradas 
                WHERE ruta_id = %s AND id IN (%s, %s)
            """
            
            cursor.execute(stops_check_query, (route_id, parada_origen_id, parada_destino_id))
            stops_result = cursor.fetchone()
            
            if stops_result['count'] != 2:
                cursor.close()
                return {
                    "success": False,
                    "message": "Una o ambas paradas no pertenecen a esta ruta"
                }
            
            # Verificar si estamos modificando el destino o solo la distancia
            if parada_destino_anterior_id and parada_destino_id != parada_destino_anterior_id:
                # Estamos cambiando la parada destino, así que necesitamos verificar:
                
                # 1. Que la conexión original existe
                existing_check_query = """
                    SELECT COUNT(*) as count
                    FROM vecinos 
                    WHERE parada_origen_id = %s AND parada_destino_id = %s
                """
                cursor.execute(existing_check_query, (parada_origen_id, parada_destino_anterior_id))
                existing_result = cursor.fetchone()
                
                if existing_result['count'] == 0:
                    # La conexión original no existe
                    cursor.close()
                    return {
                        "success": False,
                        "message": "No existe la conexión original que intentas modificar"
                    }
                
                # 2. Que no exista una conexión con el nuevo destino
                cursor.execute(existing_check_query, (parada_origen_id, parada_destino_id))
                existing_new_result = cursor.fetchone()
                
                if existing_new_result['count'] > 0:
                    # Ya existe una conexión hacia el nuevo destino
                    cursor.close()
                    return {
                        "success": False,
                        "message": "Ya existe una conexión hacia la nueva parada destino"
                    }
                
                # Todo está bien, eliminar la conexión anterior y crear la nueva
                delete_query = """
                    DELETE FROM vecinos 
                    WHERE parada_origen_id = %s AND parada_destino_id = %s
                """
                cursor.execute(delete_query, (parada_origen_id, parada_destino_anterior_id))
                
                # Crear la nueva conexión
                insert_query = """
                    INSERT INTO vecinos (parada_origen_id, parada_destino_id, distancia)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (parada_origen_id, parada_destino_id, distancia))
                
                action_text = "actualizada (cambiado destino)"
            else:
                # Solo estamos actualizando la distancia
                # Verificar que existe la conexión
                existing_check_query = """
                    SELECT COUNT(*) as count
                    FROM vecinos 
                    WHERE parada_origen_id = %s AND parada_destino_id = %s
                """
                
                cursor.execute(existing_check_query, (parada_origen_id, parada_destino_id))
                existing_result = cursor.fetchone()
                
                if existing_result['count'] == 0:
                    # La conexión no existe, devolver error
                    cursor.close()
                    return {
                        "success": False,
                        "message": "No existe una conexión entre estas paradas para actualizar"
                    }
                    
                # Actualizar la conexión existente
                update_query = """
                    UPDATE vecinos 
                    SET distancia = %s
                    WHERE parada_origen_id = %s AND parada_destino_id = %s
                """
                
                cursor.execute(update_query, (distancia, parada_origen_id, parada_destino_id))
                action_text = "actualizada (solo distancia)"
            connection.commit()
            logger.info(f"Conexión actualizada: {parada_origen_id} → {parada_destino_id} (nueva distancia: {distancia}km)")
            
            action_text = "actualizada"
            
            cursor.close()
            
            return {
                "success": True,
                "message": "Conexión actualizada exitosamente",
                "message": "Conexión actualizada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error al actualizar conexión: {e}")
            return {
                "success": False,
                "message": "Error al actualizar la conexión"
            }
        
        finally:
            self.db.disconnect()
