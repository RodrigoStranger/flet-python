import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    """
    Clase simple para manejar la base de datos MongoDB
    """
    
    def __init__(self):
        self._client: Optional[MongoClient] = None
        self._database: Optional[Database] = None
        self._uri = os.getenv("MONGODB_URI")
        
        if not self._uri:
            logger.error("❌ Variable de entorno MONGODB_URI no configurada")
            raise ValueError("MONGODB_URI debe estar configurada en el archivo .env")
        
        self._db_name = self._extract_db_name(self._uri)
    
    def connect(self) -> bool:
        """
        Conecta a MongoDB de forma simple
        """
        try:
            logger.info(f"🔗 Conectando a base de datos: {self._db_name}")
            
            # Crear cliente simple
            self._client = MongoClient(self._uri)
            
            # Verificar la conexión
            self._client.admin.command('ping')
            
            # Obtener la base de datos
            self._database = self._client[self._db_name]
            
            logger.info(f"✅ Conectado exitosamente a: {self._db_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al conectar: {e}")
            return False
    
    def disconnect(self):
        """
        Desconecta de MongoDB
        """
        try:
            if self._client:
                self._client.close()
                logger.info("🔌 Desconectado de MongoDB")
        except Exception as e:
            logger.error(f"❌ Error al desconectar: {e}")
        finally:
            self._client = None
            self._database = None

# Instancia global
db_manager = MongoDB()

# Funciones principales
def connect_db() -> bool:
    """Conecta a la base de datos"""
    return db_manager.connect()

def disconnect_db():
    """Desconecta de la base de datos"""
    db_manager.disconnect()