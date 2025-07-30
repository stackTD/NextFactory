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


class PriorityEnum(enum.Enum):
    """Priority levels for various entities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class OrderStatusEnum(enum.Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class TaskStatusEnum(enum.Enum):
    """Task status enumeration for production."""
    PLANNED = "planned"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


# ERP Module Models

class Supplier(Base):
    """
    Supplier model for supply chain management.
    
    Attributes:
        id (int): Primary key
        supplier_code (str): Unique supplier identifier
        name (str): Supplier company name
        contact_person (str): Primary contact person
        email (str): Contact email
        phone (str): Contact phone
        address (str): Supplier address
        rating (float): Supplier performance rating (1-5)
        status (StatusEnum): Supplier status
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    rating = Column(Float, default=3.0)  # 1-5 scale
    status = Column(Enum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    
    def __repr__(self) -> str:
        return f"<Supplier(code='{self.supplier_code}', name='{self.name}')>"


class PurchaseOrder(Base):
    """
    Purchase order model for supply chain management.
    
    Attributes:
        id (int): Primary key
        order_number (str): Unique order number
        supplier_id (int): Foreign key to Supplier
        total_amount (float): Order total amount
        status (OrderStatusEnum): Order status
        priority (PriorityEnum): Order priority
        requested_date (datetime): Requested delivery date
        expected_date (datetime): Expected delivery date
        actual_date (datetime): Actual delivery date
        notes (str): Order notes
        created_by_id (int): User who created the order
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = 'purchase_orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(100), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    total_amount = Column(Float, default=0.0)
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.PENDING, nullable=False)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM, nullable=False)
    
    # Dates
    requested_date = Column(DateTime)
    expected_date = Column(DateTime)
    actual_date = Column(DateTime)
    
    notes = Column(Text)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    created_by = relationship("User")
    order_items = relationship("PurchaseOrderItem", back_populates="purchase_order")
    
    def __repr__(self) -> str:
        return f"<PurchaseOrder(number='{self.order_number}', status='{self.status.value}')>"


class PurchaseOrderItem(Base):
    """
    Purchase order line items.
    
    Attributes:
        id (int): Primary key
        purchase_order_id (int): Foreign key to PurchaseOrder
        inventory_item_id (int): Foreign key to InventoryItem
        quantity (float): Ordered quantity
        unit_price (float): Price per unit
        total_price (float): Line total (quantity * unit_price)
    """
    __tablename__ = 'purchase_order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_order_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="order_items")
    inventory_item = relationship("InventoryItem")
    
    def __repr__(self) -> str:
        return f"<PurchaseOrderItem(order_id={self.purchase_order_id}, qty={self.quantity})>"


# MES Module Models

class ProductionTask(Base):
    """
    Production task model for scheduling and dispatching.
    
    Attributes:
        id (int): Primary key
        task_number (str): Unique task identifier
        title (str): Task title/description
        description (str): Detailed task description
        priority (PriorityEnum): Task priority
        status (TaskStatusEnum): Current task status
        assigned_to_id (int): Assigned user ID
        planned_start (datetime): Planned start time
        planned_end (datetime): Planned end time
        actual_start (datetime): Actual start time
        actual_end (datetime): Actual end time
        estimated_hours (float): Estimated completion time
        actual_hours (float): Actual completion time
        created_by_id (int): User who created the task
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = 'production_tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_number = Column(String(100), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM, nullable=False)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.PLANNED, nullable=False)
    
    # Assignment and scheduling
    assigned_to_id = Column(Integer, ForeignKey('users.id'))
    planned_start = Column(DateTime)
    planned_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    estimated_hours = Column(Float, default=0.0)
    actual_hours = Column(Float, default=0.0)
    
    # Metadata
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self) -> str:
        return f"<ProductionTask(number='{self.task_number}', status='{self.status.value}')>"


class SensorDataType(enum.Enum):
    """Types of sensor data collected."""
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    VIBRATION = "vibration"
    SPEED = "speed"
    POWER = "power"
    COUNT = "count"
    OTHER = "other"


class SensorData(Base):
    """
    Real-time sensor data collection model.
    
    Attributes:
        id (int): Primary key
        sensor_name (str): Sensor identifier
        data_type (SensorDataType): Type of data
        value (float): Sensor reading value
        unit (str): Unit of measurement
        equipment_id (str): Equipment identifier
        location (str): Sensor location
        is_anomaly (bool): Whether reading is anomalous
        threshold_min (float): Minimum threshold value
        threshold_max (float): Maximum threshold value
        recorded_at (datetime): When data was recorded
        created_at (datetime): Database entry timestamp
    """
    __tablename__ = 'sensor_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_name = Column(String(100), nullable=False)
    data_type = Column(Enum(SensorDataType), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    equipment_id = Column(String(100))
    location = Column(String(100))
    
    # Anomaly detection
    is_anomaly = Column(Boolean, default=False)
    threshold_min = Column(Float)
    threshold_max = Column(Float)
    
    # Timestamps
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<SensorData(sensor='{self.sensor_name}', value={self.value}, type='{self.data_type.value}')>"


class QualityCheck(Base):
    """
    Quality management check model.
    
    Attributes:
        id (int): Primary key
        check_number (str): Unique check identifier
        task_id (int): Associated production task
        inspector_id (int): Inspector user ID
        check_type (str): Type of quality check
        result (str): Pass/Fail/Review
        defects_found (int): Number of defects found
        defect_description (str): Description of defects
        corrective_action (str): Required corrective action
        inspection_date (datetime): When inspection was performed
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = 'quality_checks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    check_number = Column(String(100), unique=True, nullable=False)
    task_id = Column(Integer, ForeignKey('production_tasks.id'))
    inspector_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Check details
    check_type = Column(String(100), nullable=False)
    result = Column(String(50), nullable=False)  # Pass, Fail, Review
    defects_found = Column(Integer, default=0)
    defect_description = Column(Text)
    corrective_action = Column(Text)
    
    # Timestamps
    inspection_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    task = relationship("ProductionTask")
    inspector = relationship("User")
    
    def __repr__(self) -> str:
        return f"<QualityCheck(number='{self.check_number}', result='{self.result}')>"


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


# ERP Module Database Functions

def get_suppliers(session: Session, active_only: bool = True) -> List[Supplier]:
    """
    Get suppliers with optional filtering.
    
    Args:
        session (Session): Database session
        active_only (bool): Filter to show only active suppliers
        
    Returns:
        List[Supplier]: List of suppliers
    """
    query = session.query(Supplier)
    if active_only:
        query = query.filter_by(status=StatusEnum.ACTIVE)
    return query.all()


def get_purchase_orders(session: Session, status: Optional[str] = None) -> List[PurchaseOrder]:
    """
    Get purchase orders with optional status filtering.
    
    Args:
        session (Session): Database session
        status (Optional[str]): Filter by order status
        
    Returns:
        List[PurchaseOrder]: List of purchase orders
    """
    query = session.query(PurchaseOrder)
    if status:
        try:
            status_enum = OrderStatusEnum(status.lower())
            query = query.filter_by(status=status_enum)
        except ValueError:
            pass
    return query.order_by(PurchaseOrder.created_at.desc()).all()


# MES Module Database Functions

def get_production_tasks(session: Session, status: Optional[str] = None, 
                        assigned_to: Optional[int] = None) -> List[ProductionTask]:
    """
    Get production tasks with optional filtering.
    
    Args:
        session (Session): Database session
        status (Optional[str]): Filter by task status
        assigned_to (Optional[int]): Filter by assigned user ID
        
    Returns:
        List[ProductionTask]: List of production tasks
    """
    query = session.query(ProductionTask)
    
    if status:
        try:
            status_enum = TaskStatusEnum(status.lower())
            query = query.filter_by(status=status_enum)
        except ValueError:
            pass
    
    if assigned_to:
        query = query.filter_by(assigned_to_id=assigned_to)
    
    return query.order_by(ProductionTask.planned_start.desc()).all()


def get_recent_sensor_data(session: Session, hours: int = 24, 
                          sensor_name: Optional[str] = None) -> List[SensorData]:
    """
    Get recent sensor data.
    
    Args:
        session (Session): Database session
        hours (int): Number of hours to look back
        sensor_name (Optional[str]): Filter by sensor name
        
    Returns:
        List[SensorData]: List of sensor data entries
    """
    from datetime import timedelta
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = session.query(SensorData).filter(SensorData.recorded_at >= cutoff_time)
    
    if sensor_name:
        query = query.filter_by(sensor_name=sensor_name)
    
    return query.order_by(SensorData.recorded_at.desc()).all()


def get_anomalous_sensor_data(session: Session, hours: int = 24) -> List[SensorData]:
    """
    Get anomalous sensor readings.
    
    Args:
        session (Session): Database session
        hours (int): Number of hours to look back
        
    Returns:
        List[SensorData]: List of anomalous sensor data entries
    """
    from datetime import timedelta
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    return session.query(SensorData).filter(
        SensorData.recorded_at >= cutoff_time,
        SensorData.is_anomaly == True
    ).order_by(SensorData.recorded_at.desc()).all()


def get_quality_checks(session: Session, task_id: Optional[int] = None, 
                      result: Optional[str] = None) -> List[QualityCheck]:
    """
    Get quality checks with optional filtering.
    
    Args:
        session (Session): Database session
        task_id (Optional[int]): Filter by production task ID
        result (Optional[str]): Filter by check result
        
    Returns:
        List[QualityCheck]: List of quality checks
    """
    query = session.query(QualityCheck)
    
    if task_id:
        query = query.filter_by(task_id=task_id)
    
    if result:
        query = query.filter_by(result=result)
    
    return query.order_by(QualityCheck.inspection_date.desc()).all()