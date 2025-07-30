#!/usr/bin/env python3
"""
NextFactory ERP+MES Exhibition Demo - Database Models
=====================================================

This module defines the SQLAlchemy database models for the NextFactory application.
The models support the core functionality including user management, role-based access
control, and basic inventory management for the exhibition demo.

Models:
    - Role: User roles (Admin, Manager, Operator, Guest, Analyst)
    - User: Application users with role assignments
    - InventoryItem: Basic inventory management for demonstration

Author: NextFactory Development Team
Created: 2024
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean, 
    Text, ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.engine import Engine
import enum
import bcrypt

# SQLAlchemy declarative base
Base = declarative_base()


class RoleEnum(enum.Enum):
    """
    Enumeration of user roles in the NextFactory system.
    
    Each role has specific permissions and access levels:
    - ADMIN: Full system access, user management, configuration
    - MANAGER: Management oversight, reporting, high-level operations
    - OPERATOR: Production floor operations, data entry, basic monitoring
    - GUEST: Read-only access for demonstrations and tours
    - ANALYST: Reporting and analytics focus, data analysis capabilities
    """
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    GUEST = "guest"
    ANALYST = "analyst"


class StatusEnum(enum.Enum):
    """
    General status enumeration for various entities.
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"


class Role(Base):
    """
    Role model defining access levels and permissions in the system.
    
    This model stores role definitions with their permissions and capabilities.
    Roles are used for dynamic UI element enabling/disabling and access control.
    
    Attributes:
        id (int): Primary key
        name (RoleEnum): Role name from enumeration
        display_name (str): Human-readable role name
        description (str): Detailed role description
        permissions (str): JSON string of permissions (can be expanded to separate table)
        can_edit_users (bool): Permission to manage users
        can_view_reports (bool): Permission to access reporting modules
        can_manage_inventory (bool): Permission to modify inventory
        can_access_mes (bool): Permission to access MES modules
        can_access_erp (bool): Permission to access ERP modules
        created_at (datetime): Role creation timestamp
        updated_at (datetime): Last modification timestamp
    """
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum(RoleEnum), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Permission flags for role-based access control
    can_edit_users = Column(Boolean, default=False, nullable=False)
    can_view_reports = Column(Boolean, default=True, nullable=False)
    can_manage_inventory = Column(Boolean, default=False, nullable=False)
    can_access_mes = Column(Boolean, default=False, nullable=False)
    can_access_erp = Column(Boolean, default=False, nullable=False)
    can_create_orders = Column(Boolean, default=False, nullable=False)
    can_modify_schedule = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="role")
    
    def __repr__(self) -> str:
        return f"<Role(name='{self.name.value}', display_name='{self.display_name}')>"
    
    def to_dict(self) -> dict:
        """Convert role to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name.value,
            'display_name': self.display_name,
            'description': self.description,
            'permissions': {
                'can_edit_users': self.can_edit_users,
                'can_view_reports': self.can_view_reports,
                'can_manage_inventory': self.can_manage_inventory,
                'can_access_mes': self.can_access_mes,
                'can_access_erp': self.can_access_erp,
                'can_create_orders': self.can_create_orders,
                'can_modify_schedule': self.can_modify_schedule,
            }
        }


class User(Base):
    """
    User model for authentication and role assignment.
    
    This model stores user credentials and associates users with roles for
    access control. Passwords are hashed using bcrypt for security.
    
    Attributes:
        id (int): Primary key
        username (str): Unique username for login
        email (str): User email address
        password_hash (str): Bcrypt hashed password
        first_name (str): User's first name
        last_name (str): User's last name
        role_id (int): Foreign key to Role table
        is_active (bool): Account active status
        last_login (datetime): Last login timestamp
        created_at (datetime): Account creation timestamp
        updated_at (datetime): Last modification timestamp
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Role assignment
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    
    # Account status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    
    # Ensure username and email uniqueness
    __table_args__ = (
        UniqueConstraint('username', name='uq_user_username'),
        UniqueConstraint('email', name='uq_user_email'),
    )
    
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', role='{self.role.name.value if self.role else None}')>"
    
    def set_password(self, password: str) -> None:
        """
        Set user password with bcrypt hashing.
        
        Args:
            password (str): Plain text password to hash and store
        """
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def get_full_name(self) -> str:
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for JSON serialization (without password)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'role': self.role.to_dict() if self.role else None,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
        }


class InventoryCategory(enum.Enum):
    """
    Inventory item categories for classification and filtering.
    """
    RAW_MATERIALS = "raw_materials"
    WORK_IN_PROGRESS = "work_in_progress"
    FINISHED_GOODS = "finished_goods"
    TOOLS = "tools"
    CONSUMABLES = "consumables"


class InventoryItem(Base):
    """
    Inventory item model for basic stock management.
    
    This model provides the foundation for inventory tracking, supporting
    stock levels, categorization, and basic inventory operations for the
    exhibition demo.
    
    Attributes:
        id (int): Primary key
        item_code (str): Unique item identifier
        item_name (str): Human-readable item name
        description (str): Detailed item description
        category (InventoryCategory): Item category
        quantity (float): Current stock quantity
        unit_of_measure (str): Unit of measurement (kg, pcs, liters, etc.)
        unit_cost (float): Cost per unit
        reorder_point (float): Minimum stock level for reorder alerts
        supplier (str): Primary supplier name
        location (str): Storage location
        status (StatusEnum): Item status
        created_at (datetime): Item creation timestamp
        updated_at (datetime): Last modification timestamp
    """
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_code = Column(String(50), unique=True, nullable=False)
    item_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(InventoryCategory), nullable=False)
    
    # Quantity and measurement
    quantity = Column(Float, default=0.0, nullable=False)
    unit_of_measure = Column(String(20), nullable=False)  # kg, pcs, liters, etc.
    unit_cost = Column(Float, default=0.0)
    
    # Inventory management
    reorder_point = Column(Float, default=0.0)
    supplier = Column(String(200))
    location = Column(String(100))
    status = Column(Enum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Ensure item code uniqueness
    __table_args__ = (
        UniqueConstraint('item_code', name='uq_inventory_item_code'),
    )
    
    def __repr__(self) -> str:
        return f"<InventoryItem(code='{self.item_code}', name='{self.item_name}', qty={self.quantity})>"
    
    def is_low_stock(self) -> bool:
        """Check if item is below reorder point."""
        return self.quantity <= self.reorder_point
    
    def total_value(self) -> float:
        """Calculate total value of current stock."""
        return self.quantity * self.unit_cost
    
    def to_dict(self) -> dict:
        """Convert inventory item to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'item_code': self.item_code,
            'item_name': self.item_name,
            'description': self.description,
            'category': self.category.value,
            'quantity': self.quantity,
            'unit_of_measure': self.unit_of_measure,
            'unit_cost': self.unit_cost,
            'total_value': self.total_value(),
            'reorder_point': self.reorder_point,
            'is_low_stock': self.is_low_stock(),
            'supplier': self.supplier,
            'location': self.location,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


# Database utility functions

def create_tables(engine: Engine) -> None:
    """
    Create all database tables.
    
    Args:
        engine (Engine): SQLAlchemy engine instance
    """
    Base.metadata.create_all(bind=engine)


def get_role_by_name(session: Session, role_name: str) -> Optional[Role]:
    """
    Get role by name.
    
    Args:
        session (Session): Database session
        role_name (str): Role name to search for
        
    Returns:
        Optional[Role]: Role object if found, None otherwise
    """
    try:
        role_enum = RoleEnum(role_name.lower())
        return session.query(Role).filter_by(name=role_enum).first()
    except ValueError:
        return None


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """
    Get user by username.
    
    Args:
        session (Session): Database session
        username (str): Username to search for
        
    Returns:
        Optional[User]: User object if found, None otherwise
    """
    return session.query(User).filter_by(username=username).first()


def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username and password.
    
    Args:
        session (Session): Database session
        username (str): Username for authentication
        password (str): Password for authentication
        
    Returns:
        Optional[User]: User object if authentication successful, None otherwise
    """
    user = get_user_by_username(session, username)
    if user and user.is_active and user.check_password(password):
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        session.commit()
        return user
    return None


def get_inventory_items(session: Session, category: Optional[str] = None, 
                       low_stock_only: bool = False) -> List[InventoryItem]:
    """
    Get inventory items with optional filtering.
    
    Args:
        session (Session): Database session
        category (Optional[str]): Filter by category
        low_stock_only (bool): Filter to show only low stock items
        
    Returns:
        List[InventoryItem]: List of inventory items
    """
    query = session.query(InventoryItem)
    
    if category:
        try:
            category_enum = InventoryCategory(category.lower())
            query = query.filter_by(category=category_enum)
        except ValueError:
            pass  # Invalid category, return empty result
    
    items = query.filter_by(status=StatusEnum.ACTIVE).all()
    
    if low_stock_only:
        items = [item for item in items if item.is_low_stock()]
    
    return items