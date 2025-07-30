#!/usr/bin/env python3
"""
NextFactory ERP+MES Exhibition Demo - Database Configuration and Utilities
=========================================================================

This module provides database configuration, connection management, and utility
functions for the NextFactory application. It handles PostgreSQL connection
setup, session management, and database initialization.

Features:
    - Database connection configuration
    - Session management with context managers
    - Database initialization and table creation
    - Error handling and logging

Author: NextFactory Development Team
Created: 2024
"""

import os
import logging
from typing import Optional, Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

from models import Base, create_tables

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Database configuration class for PostgreSQL connection settings.
    
    This class manages database connection parameters, supporting both
    environment variables and default values for exhibition deployment.
    """
    
    def __init__(self):
        """Initialize database configuration from environment variables."""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'nextfactory')
        self.username = os.getenv('DB_USER', 'nextfactory')
        self.password = os.getenv('DB_PASSWORD', 'nextfactory123')
        self.echo = os.getenv('DB_ECHO', 'False').lower() == 'true'
        
    @property
    def connection_string(self) -> str:
        """
        Generate PostgreSQL connection string.
        
        Returns:
            str: PostgreSQL connection URL
        """
        return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def __repr__(self) -> str:
        """Return string representation without password."""
        return f"DatabaseConfig(host='{self.host}', port='{self.port}', database='{self.database}', user='{self.username}')"


class DatabaseManager:
    """
    Database manager class for handling connections and sessions.
    
    This class provides centralized database connection management,
    session handling, and database operations for the NextFactory application.
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database manager.
        
        Args:
            config (Optional[DatabaseConfig]): Database configuration instance
        """
        self.config = config or DatabaseConfig()
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        
    @property
    def engine(self) -> Engine:
        """
        Get or create SQLAlchemy engine.
        
        Returns:
            Engine: SQLAlchemy engine instance
        """
        if self._engine is None:
            self._engine = create_engine(
                self.config.connection_string,
                echo=self.config.echo,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Validate connections before use
                pool_recycle=3600,   # Recycle connections every hour
            )
            logger.info(f"Database engine created: {self.config}")
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """
        Get or create session factory.
        
        Returns:
            sessionmaker: SQLAlchemy session factory
        """
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory
    
    def create_database_if_not_exists(self) -> bool:
        """
        Create database if it doesn't exist.
        
        This method connects to PostgreSQL server and creates the NextFactory
        database if it doesn't already exist.
        
        Returns:
            bool: True if database was created or already exists, False on error
        """
        try:
            # Connect to postgres database to create our database
            admin_config = DatabaseConfig()
            admin_config.database = 'postgres'  # Connect to default postgres db
            admin_engine = create_engine(admin_config.connection_string)
            
            with admin_engine.connect() as conn:
                # Check if database exists
                result = conn.execute(text(
                    "SELECT 1 FROM pg_database WHERE datname = :dbname"
                ), {"dbname": self.config.database})
                
                if not result.fetchone():
                    # Database doesn't exist, create it
                    conn.execute(text("COMMIT"))  # End any open transaction
                    conn.execute(text(f'CREATE DATABASE "{self.config.database}"'))
                    logger.info(f"Database '{self.config.database}' created successfully")
                else:
                    logger.info(f"Database '{self.config.database}' already exists")
                    
            admin_engine.dispose()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def initialize_database(self) -> bool:
        """
        Initialize database schema and tables.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            create_tables(self.engine)
            logger.info("Database tables created successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.fetchone() is not None
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        
        Provides automatic session management with commit/rollback handling.
        
        Yields:
            Session: SQLAlchemy session instance
            
        Example:
            with db_manager.get_session() as session:
                user = session.query(User).first()
                # Session is automatically committed and closed
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def create_session(self) -> Session:
        """
        Create a new database session.
        
        Note: Manual session management - remember to close the session.
        Use get_session() context manager for automatic management.
        
        Returns:
            Session: SQLAlchemy session instance
        """
        return self.session_factory()
    
    def close(self) -> None:
        """Close database engine and clean up connections."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database engine closed")


# Global database manager instance
db_manager = DatabaseManager()


def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager: Global database manager
    """
    return db_manager


def initialize_application_database() -> bool:
    """
    Initialize the application database.
    
    This function performs complete database setup including:
    1. Creating database if it doesn't exist
    2. Creating tables and schema
    3. Testing connection
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        # Create database if it doesn't exist
        if not db_manager.create_database_if_not_exists():
            logger.error("Failed to create database")
            return False
        
        # Test connection
        if not db_manager.test_connection():
            logger.error("Database connection test failed")
            return False
        
        # Initialize tables
        if not db_manager.initialize_database():
            logger.error("Failed to initialize database tables")
            return False
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


# Convenience functions for common operations

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Convenience function to get database session.
    
    Yields:
        Session: SQLAlchemy session instance
    """
    with db_manager.get_session() as session:
        yield session


def test_database_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    return db_manager.test_connection()


# Exhibition-specific database functions

def setup_exhibition_database() -> bool:
    """
    Set up database for exhibition demo.
    
    This function performs all necessary database setup for the exhibition,
    including database creation, table initialization, and connection testing.
    
    Returns:
        bool: True if setup successful, False otherwise
    """
    logger.info("Setting up NextFactory exhibition database...")
    
    success = initialize_application_database()
    
    if success:
        logger.info("Exhibition database setup completed successfully")
        logger.info("Ready to seed initial data with seed_db.py")
    else:
        logger.error("Exhibition database setup failed")
        
    return success


if __name__ == "__main__":
    """
    Direct execution for database setup and testing.
    """
    print("NextFactory Database Setup Utility")
    print("=" * 40)
    
    # Setup exhibition database
    if setup_exhibition_database():
        print("✓ Database setup successful")
        print("✓ Ready for NextFactory exhibition demo")
        
        # Display connection info
        config = DatabaseConfig()
        print(f"\nDatabase Configuration:")
        print(f"  Host: {config.host}")
        print(f"  Port: {config.port}")
        print(f"  Database: {config.database}")
        print(f"  Username: {config.username}")
        
        print(f"\nNext steps:")
        print(f"  1. Run 'python seed_db.py' to populate demo data")
        print(f"  2. Run 'python main.py' to start the application")
    else:
        print("✗ Database setup failed")
        print("Please check your PostgreSQL installation and configuration")