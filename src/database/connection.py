"""
Database connection handler for MySQL with connection pooling.
"""
import os
import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Singleton database connection manager with pooling."""
    
    _instance: Optional['DatabaseConnection'] = None
    _connection_pool: List[pymysql.connections.Connection] = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.database = os.getenv('MYSQL_DATABASE', 'gst_db')
        self.user = os.getenv('MYSQL_USER', 'gst_user')
        self.password = os.getenv('MYSQL_PASSWORD', 'gstpassword123')
        self._initialized = True
        
        logger.info(f"Database connection initialized: {self.user}@{self.host}:{self.port}/{self.database}")
    
    def get_connection(self) -> pymysql.connections.Connection:
        """
        Get a database connection from the pool or create a new one.
        
        Returns:
            pymysql.connections.Connection: Database connection object
        """
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=DictCursor,
                autocommit=False
            )
            logger.debug("Database connection established")
            return connection
        except pymysql.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL SELECT query string
            params: Optional tuple of parameters for query
            
        Returns:
            List of dictionaries representing rows
        """
        connection = None
        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                # Only pass params if they're actually provided and non-empty
                # This prevents % in DATE_FORMAT from being interpreted as placeholders
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                results = cursor.fetchall()
                logger.debug(f"Query executed successfully. Rows returned: {len(results)}")
                return results
        except pymysql.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            bool: True if connection is successful
        """
        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                connection.close()
                return result is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global instance
db = DatabaseConnection()
