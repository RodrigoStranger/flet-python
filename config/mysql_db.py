import os
import logging
from typing import Optional
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MySQL:
    """
    Clase simple para manejar la base de datos MySQL
    """
    
    def __init__(self):
        self._connection: Optional[mysql.connector.MySQLConnection] = None
        self._cursor: Optional[mysql.connector.cursor.MySQLCursor] = None
        
        # Obtener configuración del .env
        self._host = os.getenv("MYSQL_HOST")
        self._port = int(os.getenv("MYSQL_PORT"))
        self._user = os.getenv("MYSQL_USER")
        self._password = os.getenv("MYSQL_PASSWORD")
        self._database = os.getenv("MYSQL_DATABASE")
        
        # Validar que las variables requeridas estén configuradas
        if not all([self._user, self._password, self._database]):
            logger.error("❌ Variables de entorno MySQL no configuradas")
            raise ValueError("MYSQL_USER, MYSQL_PASSWORD y MYSQL_DATABASE deben estar configuradas en el archivo .env")
    
    def connect(self) -> bool:
        """
        Conecta a MySQL de forma simple
        """
        try:
            logger.info(f"🔗 Conectando a base de datos MySQL: {self._database}")
            
            # Crear conexión
            self._connection = mysql.connector.connect(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                database=self._database
            )
            
            if self._connection.is_connected():
                self._cursor = self._connection.cursor()
                logger.info(f"✅ Conectado exitosamente a: {self._database}")
                return True
            else:
                logger.error("❌ No se pudo establecer la conexión")
                return False
            
        except Error as e:
            logger.error(f"❌ Error al conectar a MySQL: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return False
    
    def disconnect(self):
        """
        Desconecta de MySQL
        """
        try:
            if self._cursor:
                self._cursor.close()
            if self._connection and self._connection.is_connected():
                self._connection.close()
                logger.info("🔌 Desconectado de MySQL")
        except Exception as e:
            logger.error(f"❌ Error al desconectar: {e}")
        finally:
            self._cursor = None
            self._connection = None
    
    def is_connected(self) -> bool:
        """
        Verifica si está conectado
        """
        try:
            if self._connection:
                return self._connection.is_connected()
        except Exception:
            pass
        return False
    
    def get_connection(self) -> Optional[mysql.connector.MySQLConnection]:
        """
        Retorna la conexión
        """
        return self._connection
    
    def get_cursor(self) -> Optional[mysql.connector.cursor.MySQLCursor]:
        """
        Retorna el cursor
        """
        return self._cursor
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """
        Ejecuta una consulta SQL
        """
        try:
            if not self._cursor:
                logger.error("❌ No hay cursor disponible")
                return False
            
            if params:
                self._cursor.execute(query, params)
            else:
                self._cursor.execute(query)
            
            self._connection.commit()
            return True
            
        except Error as e:
            logger.error(f"❌ Error ejecutando consulta: {e}")
            return False

# Instancia global
db_manager = MySQL()

# Funciones principales
def connect_db() -> bool:
    """Conecta a la base de datos"""
    return db_manager.connect()

def disconnect_db():
    """Desconecta de la base de datos"""
    db_manager.disconnect()

def is_db_connected() -> bool:
    """Verifica si está conectado"""
    return db_manager.is_connected()

def get_connection() -> Optional[mysql.connector.MySQLConnection]:
    """Obtiene la conexión"""
    return db_manager.get_connection()

def get_cursor() -> Optional[mysql.connector.cursor.MySQLCursor]:
    """Obtiene el cursor"""
    return db_manager.get_cursor()

def execute_query(query: str, params: tuple = None) -> bool:
    """Ejecuta una consulta SQL"""
    return db_manager.execute_query(query, params)

# Funciones de autenticación
def login_user(correo: str, clave: str) -> dict:
    """
    Intenta hacer login de un usuario
    Retorna dict con resultado del login
    """
    try:
        if not is_db_connected():
            return {"success": False, "message": "No hay conexión a la base de datos"}
        
        cursor = get_cursor()
        if not cursor:
            return {"success": False, "message": "No se pudo obtener cursor"}
        
        # Buscar usuario por correo y clave
        query = "SELECT id, nombre, correo FROM usuarios WHERE correo = %s AND clave = %s"
        cursor.execute(query, (correo, clave))
        result = cursor.fetchone()
        
        if result:
            user_data = {
                "id": result[0],
                "nombre": result[1], 
                "correo": result[2]
            }
            logger.info(f"✅ Login exitoso para: {correo}")
            return {"success": True, "message": "Inicio de sesión exitoso", "user": user_data}
        else:
            logger.warning(f"⚠️ Login fallido para: {correo}")
            return {"success": False, "message": "Correo o contraseña incorrectos"}
    
    except Error as e:
        logger.error(f"❌ Error en login: {e}")
        return {"success": False, "message": f"Error en la base de datos: {str(e)}"}
    except Exception as e:
        logger.error(f"❌ Error inesperado en login: {e}")
        return {"success": False, "message": "Error inesperado"}

def register_user(nombre: str, correo: str, clave: str) -> dict:
    """
    Registra un nuevo usuario
    Retorna dict con resultado del registro
    """
    try:
        if not is_db_connected():
            return {"success": False, "message": "No hay conexión a la base de datos"}
        
        # Validar formato de correo (básico)
        if not validate_email(correo):
            return {"success": False, "message": "Formato de correo inválido"}
        
        cursor = get_cursor()
        if not cursor:
            return {"success": False, "message": "No se pudo obtener cursor"}
        
        # Verificar si el correo ya existe
        check_query = "SELECT id FROM usuarios WHERE correo = %s"
        cursor.execute(check_query, (correo,))
        if cursor.fetchone():
            return {"success": False, "message": "El correo ya está registrado"}
        
        # Insertar nuevo usuario
        insert_query = "INSERT INTO usuarios (nombre, correo, clave) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (nombre, correo, clave))
        get_connection().commit()
        
        logger.info(f"✅ Usuario registrado exitosamente: {correo}")
        return {"success": True, "message": "Usuario registrado exitosamente"}
    
    except Error as e:
        logger.error(f"❌ Error en registro: {e}")
        return {"success": False, "message": f"Error en la base de datos: {str(e)}"}
    except Exception as e:
        logger.error(f"❌ Error inesperado en registro: {e}")
        return {"success": False, "message": "Error inesperado"}

def validate_email(email: str) -> bool:
    """
    Validación básica de formato de correo electrónico
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
