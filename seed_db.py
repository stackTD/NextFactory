#!/usr/bin/env python3
"""
NextFactory ERP+MES Exhibition Demo - Database Seeding Script
============================================================

This script populates the NextFactory database with mock data for exhibition
purposes. It creates default roles, demo users with various access levels,
and sample inventory items to demonstrate system functionality.

The script is designed to be idempotent - it can be run multiple times safely
and will only create data that doesn't already exist.

Features:
    - Creates all system roles with appropriate permissions
    - Generates demo users for each role type
    - Populates inventory with realistic sample data
    - Prevents duplicate data creation
    - Provides detailed logging and status reporting

Usage:
    python seed_db.py [--force]
    
    --force: Force re-creation of existing data (use with caution)

Author: NextFactory Development Team
Created: 2024
"""

import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from database import get_db_session, setup_exhibition_database
from models import (
    Role, RoleEnum, User, InventoryItem, InventoryCategory, StatusEnum,
    get_role_by_name, get_user_by_username
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSeeder:
    """
    Data seeding class for populating the NextFactory database.
    
    This class handles the creation of roles, users, and inventory items
    for the exhibition demo, ensuring data consistency and preventing
    duplicate entries.
    """
    
    def __init__(self, force_recreate: bool = False):
        """
        Initialize data seeder.
        
        Args:
            force_recreate (bool): If True, recreate existing data
        """
        self.force_recreate = force_recreate
        self.stats = {
            'roles_created': 0,
            'users_created': 0,
            'inventory_created': 0,
            'errors': 0
        }
    
    def create_roles(self) -> bool:
        """
        Create system roles with appropriate permissions.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Creating system roles...")
        
        # Define roles with their permissions
        roles_data = [
            {
                'name': RoleEnum.ADMIN,
                'display_name': 'Administrator',
                'description': 'Full system access including user management, configuration, and all modules',
                'can_edit_users': True,
                'can_view_reports': True,
                'can_manage_inventory': True,
                'can_access_mes': True,
                'can_access_erp': True,
                'can_create_orders': True,
                'can_modify_schedule': True,
            },
            {
                'name': RoleEnum.MANAGER,
                'display_name': 'Manager',
                'description': 'Management oversight with access to reporting, scheduling, and high-level operations',
                'can_edit_users': False,
                'can_view_reports': True,
                'can_manage_inventory': True,
                'can_access_mes': True,
                'can_access_erp': True,
                'can_create_orders': True,
                'can_modify_schedule': True,
            },
            {
                'name': RoleEnum.OPERATOR,
                'display_name': 'Operator',
                'description': 'Production floor operations including data entry and basic monitoring',
                'can_edit_users': False,
                'can_view_reports': True,
                'can_manage_inventory': False,
                'can_access_mes': True,
                'can_access_erp': False,
                'can_create_orders': False,
                'can_modify_schedule': False,
            },
            {
                'name': RoleEnum.GUEST,
                'display_name': 'Guest',
                'description': 'Read-only access for demonstrations and tours',
                'can_edit_users': False,
                'can_view_reports': True,
                'can_manage_inventory': False,
                'can_access_mes': False,
                'can_access_erp': False,
                'can_create_orders': False,
                'can_modify_schedule': False,
            },
            {
                'name': RoleEnum.ANALYST,
                'display_name': 'Analyst',
                'description': 'Reporting and analytics focus with data analysis capabilities',
                'can_edit_users': False,
                'can_view_reports': True,
                'can_manage_inventory': False,
                'can_access_mes': True,
                'can_access_erp': True,
                'can_create_orders': False,
                'can_modify_schedule': False,
            },
        ]
        
        try:
            with get_db_session() as session:
                for role_data in roles_data:
                    existing_role = get_role_by_name(session, role_data['name'].value)
                    
                    if existing_role and not self.force_recreate:
                        logger.info(f"Role '{role_data['display_name']}' already exists, skipping")
                        continue
                    
                    if existing_role and self.force_recreate:
                        session.delete(existing_role)
                        logger.info(f"Removed existing role '{role_data['display_name']}'")
                    
                    # Create new role
                    role = Role(**role_data)
                    session.add(role)
                    self.stats['roles_created'] += 1
                    logger.info(f"Created role: {role_data['display_name']}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error creating roles: {e}")
            self.stats['errors'] += 1
            return False
    
    def create_users(self) -> bool:
        """
        Create demo users for each role type.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Creating demo users...")
        
        # Define demo users with credentials
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@nextfactory.com',
                'password': 'admin123',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role_name': 'admin',
            },
            {
                'username': 'manager',
                'email': 'manager@nextfactory.com',
                'password': 'manager123',
                'first_name': 'John',
                'last_name': 'Manager',
                'role_name': 'manager',
            },
            {
                'username': 'operator',
                'email': 'operator@nextfactory.com',
                'password': 'operator123',
                'first_name': 'Alice',
                'last_name': 'Operator',
                'role_name': 'operator',
            },
            {
                'username': 'guest',
                'email': 'guest@nextfactory.com',
                'password': 'guest123',
                'first_name': 'Demo',
                'last_name': 'Guest',
                'role_name': 'guest',
            },
            {
                'username': 'analyst',
                'email': 'analyst@nextfactory.com',
                'password': 'analyst123',
                'first_name': 'Sarah',
                'last_name': 'Analyst',
                'role_name': 'analyst',
            },
        ]
        
        try:
            with get_db_session() as session:
                for user_data in users_data:
                    existing_user = get_user_by_username(session, user_data['username'])
                    
                    if existing_user and not self.force_recreate:
                        logger.info(f"User '{user_data['username']}' already exists, skipping")
                        continue
                    
                    if existing_user and self.force_recreate:
                        session.delete(existing_user)
                        logger.info(f"Removed existing user '{user_data['username']}'")
                    
                    # Get role for user
                    role = get_role_by_name(session, user_data['role_name'])
                    if not role:
                        logger.error(f"Role '{user_data['role_name']}' not found for user '{user_data['username']}'")
                        continue
                    
                    # Create new user
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        role_id=role.id,
                    )
                    user.set_password(user_data['password'])
                    
                    session.add(user)
                    self.stats['users_created'] += 1
                    logger.info(f"Created user: {user_data['username']} ({user_data['role_name']})")
                
            return True
            
        except Exception as e:
            logger.error(f"Error creating users: {e}")
            self.stats['errors'] += 1
            return False
    
    def create_inventory_items(self) -> bool:
        """
        Create sample inventory items for demonstration.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Creating sample inventory items...")
        
        # Define sample inventory items
        inventory_data = [
            # Raw Materials
            {
                'item_code': 'RM001',
                'item_name': 'Steel Sheets',
                'description': 'Cold-rolled steel sheets for manufacturing',
                'category': InventoryCategory.RAW_MATERIALS,
                'quantity': 150.0,
                'unit_of_measure': 'sheets',
                'unit_cost': 25.50,
                'reorder_point': 20.0,
                'supplier': 'MetalWorks Inc.',
                'location': 'Warehouse A1',
            },
            {
                'item_code': 'RM002',
                'item_name': 'Aluminum Rods',
                'description': '6061-T6 aluminum rods, 1-inch diameter',
                'category': InventoryCategory.RAW_MATERIALS,
                'quantity': 200.0,
                'unit_of_measure': 'pieces',
                'unit_cost': 12.75,
                'reorder_point': 30.0,
                'supplier': 'Aluminum Supply Co.',
                'location': 'Warehouse A2',
            },
            {
                'item_code': 'RM003',
                'item_name': 'Industrial Lubricant',
                'description': 'High-performance machinery lubricant',
                'category': InventoryCategory.RAW_MATERIALS,
                'quantity': 85.5,
                'unit_of_measure': 'liters',
                'unit_cost': 8.90,
                'reorder_point': 15.0,
                'supplier': 'LubeTech Solutions',
                'location': 'Chemical Storage',
            },
            
            # Work in Progress
            {
                'item_code': 'WIP001',
                'item_name': 'Machined Components A',
                'description': 'Partially machined components for Product Line A',
                'category': InventoryCategory.WORK_IN_PROGRESS,
                'quantity': 45.0,
                'unit_of_measure': 'pieces',
                'unit_cost': 35.20,
                'reorder_point': 10.0,
                'supplier': 'Internal Production',
                'location': 'Production Floor B',
            },
            {
                'item_code': 'WIP002',
                'item_name': 'Assembly Subunit B',
                'description': 'Assembled subunits awaiting final assembly',
                'category': InventoryCategory.WORK_IN_PROGRESS,
                'quantity': 28.0,
                'unit_of_measure': 'units',
                'unit_cost': 125.75,
                'reorder_point': 5.0,
                'supplier': 'Internal Production',
                'location': 'Assembly Area 2',
            },
            
            # Finished Goods
            {
                'item_code': 'FG001',
                'item_name': 'Industrial Pump Model X1',
                'description': 'High-efficiency industrial pump, 500 GPM capacity',
                'category': InventoryCategory.FINISHED_GOODS,
                'quantity': 12.0,
                'unit_of_measure': 'units',
                'unit_cost': 1250.00,
                'reorder_point': 3.0,
                'supplier': 'Internal Production',
                'location': 'Finished Goods A',
            },
            {
                'item_code': 'FG002',
                'item_name': 'Control Panel Series C',
                'description': 'Programmable control panel with HMI interface',
                'category': InventoryCategory.FINISHED_GOODS,
                'quantity': 8.0,
                'unit_of_measure': 'units',
                'unit_cost': 850.00,
                'reorder_point': 2.0,
                'supplier': 'Internal Production',
                'location': 'Finished Goods B',
            },
            
            # Tools
            {
                'item_code': 'TL001',
                'item_name': 'CNC End Mills',
                'description': '1/2 inch carbide end mills for CNC machining',
                'category': InventoryCategory.TOOLS,
                'quantity': 24.0,
                'unit_of_measure': 'pieces',
                'unit_cost': 45.60,
                'reorder_point': 8.0,
                'supplier': 'Tool Supply Corp',
                'location': 'Tool Crib',
            },
            {
                'item_code': 'TL002',
                'item_name': 'Precision Measuring Set',
                'description': 'Digital calipers and measurement tools',
                'category': InventoryCategory.TOOLS,
                'quantity': 6.0,
                'unit_of_measure': 'sets',
                'unit_cost': 125.00,
                'reorder_point': 2.0,
                'supplier': 'Precision Tools Ltd',
                'location': 'Tool Crib',
            },
            
            # Consumables
            {
                'item_code': 'CS001',
                'item_name': 'Safety Gloves',
                'description': 'Cut-resistant safety gloves, size L',
                'category': InventoryCategory.CONSUMABLES,
                'quantity': 150.0,
                'unit_of_measure': 'pairs',
                'unit_cost': 3.25,
                'reorder_point': 30.0,
                'supplier': 'Safety Supply Inc',
                'location': 'Safety Storage',
            },
            {
                'item_code': 'CS002',
                'item_name': 'Cleaning Rags',
                'description': 'Industrial cleaning rags for maintenance',
                'category': InventoryCategory.CONSUMABLES,
                'quantity': 500.0,
                'unit_of_measure': 'pieces',
                'unit_cost': 0.50,
                'reorder_point': 100.0,
                'supplier': 'Maintenance Supply Co',
                'location': 'Maintenance Storage',
            },
            
            # Low stock items for demonstration
            {
                'item_code': 'RM004',
                'item_name': 'Copper Wire',
                'description': '14 AWG copper wire for electrical connections',
                'category': InventoryCategory.RAW_MATERIALS,
                'quantity': 8.0,  # Below reorder point
                'unit_of_measure': 'meters',
                'unit_cost': 2.15,
                'reorder_point': 50.0,
                'supplier': 'ElectroWire Ltd',
                'location': 'Electrical Storage',
            },
        ]
        
        try:
            with get_db_session() as session:
                for item_data in inventory_data:
                    # Check if item already exists
                    existing_item = session.query(InventoryItem).filter_by(
                        item_code=item_data['item_code']
                    ).first()
                    
                    if existing_item and not self.force_recreate:
                        logger.info(f"Inventory item '{item_data['item_code']}' already exists, skipping")
                        continue
                    
                    if existing_item and self.force_recreate:
                        session.delete(existing_item)
                        logger.info(f"Removed existing inventory item '{item_data['item_code']}'")
                    
                    # Create new inventory item
                    item = InventoryItem(**item_data)
                    session.add(item)
                    self.stats['inventory_created'] += 1
                    logger.info(f"Created inventory item: {item_data['item_code']} - {item_data['item_name']}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error creating inventory items: {e}")
            self.stats['errors'] += 1
            return False
    
    def seed_all_data(self) -> bool:
        """
        Seed all demonstration data.
        
        Returns:
            bool: True if all seeding successful, False otherwise
        """
        logger.info("Starting NextFactory database seeding...")
        
        success = True
        
        # Create roles first (required for users)
        if not self.create_roles():
            success = False
        
        # Create users (requires roles)
        if not self.create_users():
            success = False
        
        # Create inventory items
        if not self.create_inventory_items():
            success = False
        
        # Log final statistics
        logger.info("Database seeding completed")
        logger.info(f"Statistics:")
        logger.info(f"  Roles created: {self.stats['roles_created']}")
        logger.info(f"  Users created: {self.stats['users_created']}")
        logger.info(f"  Inventory items created: {self.stats['inventory_created']}")
        logger.info(f"  Errors encountered: {self.stats['errors']}")
        
        return success and self.stats['errors'] == 0


def print_demo_credentials():
    """Print demo user credentials for exhibition use."""
    print("\n" + "=" * 60)
    print("NextFactory Exhibition Demo - User Credentials")
    print("=" * 60)
    print()
    print("Role        | Username | Password   | Capabilities")
    print("-" * 60)
    print("Admin       | admin    | admin123   | Full system access")
    print("Manager     | manager  | manager123 | Management oversight")
    print("Operator    | operator | operator123| Production operations")
    print("Guest       | guest    | guest123   | Read-only demonstration")
    print("Analyst     | analyst  | analyst123 | Reporting and analytics")
    print()
    print("Note: These are demonstration credentials for exhibition use only.")
    print("In production, use strong passwords and proper authentication.")
    print("=" * 60)


def main():
    """Main function for script execution."""
    parser = argparse.ArgumentParser(description='Seed NextFactory database with demo data')
    parser.add_argument('--force', action='store_true', 
                       help='Force recreation of existing data')
    args = parser.parse_args()
    
    print("NextFactory Database Seeding Utility")
    print("=" * 40)
    
    # Ensure database is set up
    if not setup_exhibition_database():
        logger.error("Database setup failed, cannot proceed with seeding")
        return False
    
    # Create seeder and populate data
    seeder = DataSeeder(force_recreate=args.force)
    
    if seeder.seed_all_data():
        print("\n✓ Database seeding completed successfully")
        print("✓ NextFactory is ready for exhibition demo")
        print_demo_credentials()
        return True
    else:
        print("\n✗ Database seeding failed")
        print("Please check the logs for error details")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)