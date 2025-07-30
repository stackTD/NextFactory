#!/usr/bin/env python3
"""
NextFactory ERP+MES Exhibition Demo - Main Application
====================================================

This is the main application entry point for the NextFactory ERP+MES demonstration.
It provides a professional PyQt6 interface with role-based access control, modular
design for easy expansion, and comprehensive exhibition-ready features.

Features:
    - Professional login dialog with role-based authentication
    - Modular tabbed interface for ERP and MES modules
    - Dynamic UI element enabling/disabling based on user roles
    - Real-time dashboard with periodic data updates
    - Central module framework for future expansion
    - Exhibition-ready styling and user experience

Author: NextFactory Development Team
Created: 2024
"""

import sys
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QComboBox, QTextEdit, QFrame,
    QSplitter, QStatusBar, QMenuBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGroupBox, QGridLayout
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QThread, pyqtSlot
)
from PyQt6.QtGui import (
    QFont, QIcon, QPalette, QColor, QPixmap, QAction
)

from database import get_db_session, test_database_connection
from models import User, authenticate_user, get_inventory_items, InventoryItem, joinedload
from ui_components import BaseModuleWidget

# Import new ERP and MES modules
try:
    from erp_modules import (
        EnhancedInventoryModule, SupplyChainModule, ReportingModule,
        SalesCRMModule, AssetManagementModule
    )
    from mes_modules import (
        ProductionSchedulingModule, RealTimeDataModule, 
        QualityManagementModule, PerformanceAnalysisModule,
        ResourceAllocationModule, ProductTrackingModule, 
        MaintenanceManagementModule, LaborManagementModule
    )
    ERP_MES_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ERP/MES modules not available: {e}")
    ERP_MES_MODULES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """
    Professional login dialog with role-based authentication.
    
    This dialog provides secure user authentication with support for
    multiple user roles and comprehensive error handling. It features
    a clean, professional interface suitable for exhibition use.
    """
    
    # Signal emitted when user successfully logs in
    user_authenticated = pyqtSignal(object)  # User object
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize login dialog.
        
        Args:
            parent (Optional[QWidget]): Parent widget
        """
        super().__init__(parent)
        self.current_user: Optional[User] = None
        self.setup_ui()
        self.setup_styling()
        
    def setup_ui(self):
        """Set up the user interface for the login dialog."""
        self.setWindowTitle("NextFactory - User Authentication")
        self.setFixedSize(800, 600)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel("NextFactory ERP+MES")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        subtitle_label = QLabel("Exhibition Demo Login")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)
        layout.addWidget(subtitle_label)
        
        # Login form
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Username field
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        self.username_edit.setMinimumHeight(30)
        form_layout.addRow("Username:", self.username_edit)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(30)
        form_layout.addRow("Password:", self.password_edit)
        
        # Quick select combo for demo purposes
        self.quick_select = QComboBox()
        self.quick_select.addItems([
            "Select Demo User...",
            "admin (Administrator)",
            "manager (Manager)",
            "operator (Operator)",
            "guest (Guest)",
            "analyst (Analyst)"
        ])
        self.quick_select.currentTextChanged.connect(self.on_quick_select_changed)
        form_layout.addRow("Quick Select:", self.quick_select)
        
        layout.addWidget(form_frame)
        
        # Status/error message area
        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setMinimumHeight(40)
        layout.addWidget(self.message_label)
        
        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Login")
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Exit")
        self.button_box.accepted.connect(self.authenticate_user)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        # Connect Enter key to login
        self.username_edit.returnPressed.connect(self.authenticate_user)
        self.password_edit.returnPressed.connect(self.authenticate_user)
        
        # Set initial focus to username field
        self.username_edit.setFocus()
        
        # Set focus to username field
        self.username_edit.setFocus()
    
    def setup_styling(self):
        """Apply professional styling to the dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
            QComboBox {
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005c99;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)
    
    @pyqtSlot(str)
    def on_quick_select_changed(self, text: str):
        """
        Handle quick select combo box changes.
        
        Args:
            text (str): Selected combo box text
        """
        if text.startswith("Select Demo"):
            return
        
        # Extract username from selection
        username = text.split(" (")[0]
        self.username_edit.setText(username)
        
        # Set corresponding demo password
        demo_passwords = {
            'admin': 'admin123',
            'manager': 'manager123',
            'operator': 'operator123',
            'guest': 'guest123',
            'analyst': 'analyst123'
        }
        
        if username in demo_passwords:
            self.password_edit.setText(demo_passwords[username])
            self.show_message("Demo credentials auto-filled", "info")
    
    def show_message(self, message: str, message_type: str = "error"):
        """
        Display a message to the user.
        
        Args:
            message (str): Message to display
            message_type (str): Type of message ("error", "info", "success")
        """
        colors = {
            "error": "#d32f2f",
            "info": "#1976d2",
            "success": "#388e3c"
        }
        
        color = colors.get(message_type, colors["error"])
        self.message_label.setText(message)
        self.message_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def authenticate_user(self):
        """Authenticate user credentials and emit signal on success."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            self.show_message("Please enter both username and password")
            return
        
        # Test database connection first
        if not test_database_connection():
            self.show_message("Database connection failed. Please check configuration.")
            return
        
        try:
            with get_db_session() as session:
                user = authenticate_user(session, username, password)
                
                if user:
                    self.current_user = user
                    self.show_message(f"Welcome, {user.get_full_name()}!", "success")
                    self.user_authenticated.emit(user)
                    self.accept()
                else:
                    self.show_message("Invalid username or password")
                    self.password_edit.clear()
                    self.password_edit.setFocus()
                    
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            self.show_message("Authentication failed. Please try again.")


class DashboardWidget(BaseModuleWidget):
    """
    Central dashboard widget providing system overview and quick access.
    
    This widget serves as the main landing page for users, displaying
    key metrics, recent activity, and providing quick access to major
    system functions based on user role permissions.
    """
    
    def __init__(self, user: User, parent: Optional[QWidget] = None):
        """
        Initialize dashboard widget.
        
        Args:
            user (User): Current logged-in user
            parent (Optional[QWidget]): Parent widget
        """
        super().__init__("Dashboard", user, parent=parent)
        self.setup_ui()
        self.setup_refresh_timer()
        
    def setup_ui(self):
        """Set up the dashboard user interface."""
        layout = self.get_content_layout()
        layout.setSpacing(20)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Quick actions
        left_panel = self.create_quick_actions_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - System status and metrics
        right_panel = self.create_status_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
    def create_quick_actions_panel(self) -> QWidget:
        """
        Create quick actions panel based on user permissions.
        
        Returns:
            QWidget: Quick actions panel widget
        """
        panel = QGroupBox("Quick Actions")
        layout = QVBoxLayout(panel)
        
        # Get user permissions
        permissions = self.user.role.to_dict()['permissions']
        
        # Add action buttons based on permissions
        if permissions.get('can_access_erp', False):
            erp_btn = QPushButton("Open ERP Module")
            erp_btn.clicked.connect(lambda: self.open_module('erp'))
            layout.addWidget(erp_btn)
        
        if permissions.get('can_access_mes', False):
            mes_btn = QPushButton("Open MES Module")
            mes_btn.clicked.connect(lambda: self.open_module('mes'))
            layout.addWidget(mes_btn)
        
        if permissions.get('can_view_reports', False):
            reports_btn = QPushButton("View Reports")
            reports_btn.clicked.connect(lambda: self.open_module('reports'))
            layout.addWidget(reports_btn)
        
        if permissions.get('can_manage_inventory', False):
            inventory_btn = QPushButton("Manage Inventory")
            inventory_btn.clicked.connect(lambda: self.open_module('inventory'))
            layout.addWidget(inventory_btn)
        
        # Always available actions
        help_btn = QPushButton("System Help")
        help_btn.clicked.connect(self.show_help)
        help_btn.setToolTip("View system help and user permissions")
        layout.addWidget(help_btn)
        
        layout.addStretch()
        return panel
    
    def create_status_panel(self) -> QWidget:
        """
        Create system status and metrics panel.
        
        Returns:
            QWidget: Status panel widget
        """
        panel = QGroupBox("System Status")
        layout = QVBoxLayout(panel)
        
        # Current time
        self.time_label = QLabel()
        self.update_time()
        layout.addWidget(self.time_label)
        
        # System metrics
        self.metrics_label = QLabel("Loading system metrics...")
        layout.addWidget(self.metrics_label)
        
        # Inventory summary (if user can view)
        if self.user.role.can_view_reports:
            self.inventory_summary = QLabel("Loading inventory summary...")
            layout.addWidget(self.inventory_summary)
            self.update_inventory_summary()
        
        layout.addStretch()
        return panel
    
    def setup_refresh_timer(self):
        """Set up timer for periodic dashboard updates."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(30000)  # Update every 30 seconds
        
        # Time update timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # Update every second
    
    def update_time(self):
        """Update the current time display."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"Current Time: {current_time}")
    
    def refresh_dashboard(self):
        """Refresh dashboard data."""
        if hasattr(self, 'inventory_summary'):
            self.update_inventory_summary()
        
        # Update metrics
        self.metrics_label.setText(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    def update_inventory_summary(self):
        """Update inventory summary information."""
        try:
            with get_db_session() as session:
                all_items = get_inventory_items(session)
                low_stock_items = get_inventory_items(session, low_stock_only=True)
                
                total_items = len(all_items)
                low_stock_count = len(low_stock_items)
                total_value = sum(item.total_value() for item in all_items)
                
                summary_text = f"""Inventory Summary:
• Total Items: {total_items}
• Low Stock Items: {low_stock_count}
• Total Value: ${total_value:,.2f}"""
                
                self.inventory_summary.setText(summary_text)
                
        except Exception as e:
            logger.error(f"Error updating inventory summary: {e}")
            self.inventory_summary.setText("Error loading inventory data")
    
    def open_module(self, module_name: str):
        """
        Open a specific module (placeholder for future implementation).
        
        Args:
            module_name (str): Name of module to open
        """
        QMessageBox.information(
            self,
            "Module Access",
            f"Opening {module_name.upper()} module...\n\n"
            f"This will be implemented in Phase 2 of the NextFactory development."
        )
    
    def show_help(self):
        """Display system help information."""
        try:
            # Ensure we have access to user data by refreshing it from the database
            with get_db_session() as session:
                # Get the current user with role information
                current_user = session.query(User).options(joinedload(User.role)).filter_by(id=self.user.id).first()
                if not current_user:
                    QMessageBox.warning(self, "Error", "User session has expired. Please restart the application.")
                    return
                
                help_text = f"""NextFactory ERP+MES System Help

Current User: {current_user.get_full_name()}
Role: {current_user.role.display_name}

Role Permissions:
"""
                permissions = current_user.role.to_dict()['permissions']
                for perm, value in permissions.items():
                    status = "✓" if value else "✗"
                    perm_name = perm.replace('_', ' ').title()
                    help_text += f"• {status} {perm_name}\n"
                
                help_text += """
Navigation:
• Use the tabs to access different modules
• Dashboard provides system overview
• Quick actions are based on your role permissions

For technical support during the exhibition,
please contact the NextFactory team."""
                
                QMessageBox.information(self, "System Help", help_text)
                
        except Exception as e:
            logger.error(f"Error displaying help: {e}")
            QMessageBox.warning(self, "Error", "Unable to display help information. Please try again.")


class InventoryModule(BaseModuleWidget):
    """
    Basic inventory management module for demonstration.
    
    This module provides a simple inventory view with basic functionality
    for displaying and managing inventory items based on user permissions.
    """
    
    def __init__(self, user: User, parent: Optional[QWidget] = None):
        """
        Initialize inventory module.
        
        Args:
            user (User): Current logged-in user
            parent (Optional[QWidget]): Parent widget
        """
        super().__init__("Inventory Management", user, parent=parent)
        self.setup_ui()
        self.load_inventory_data()
        
    def setup_ui(self):
        """Set up the inventory module user interface."""
        layout = self.get_content_layout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_inventory_data)
        controls_layout.addWidget(refresh_btn)
        
        if self.user.role.can_manage_inventory:
            add_btn = QPushButton("Add Item")
            add_btn.clicked.connect(self.add_item)
            controls_layout.addWidget(add_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(8)
        self.inventory_table.setHorizontalHeaderLabels([
            "Item Code", "Name", "Category", "Quantity", "Unit", "Unit Cost", "Total Value", "Status"
        ])
        
        # Configure table
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setSortingEnabled(True)
        
        layout.addWidget(self.inventory_table)
        
    def load_inventory_data(self):
        """Load and display inventory data."""
        try:
            with get_db_session() as session:
                items = get_inventory_items(session)
                
                self.inventory_table.setRowCount(len(items))
                
                for row, item in enumerate(items):
                    self.inventory_table.setItem(row, 0, QTableWidgetItem(item.item_code))
                    self.inventory_table.setItem(row, 1, QTableWidgetItem(item.item_name))
                    self.inventory_table.setItem(row, 2, QTableWidgetItem(item.category.value))
                    self.inventory_table.setItem(row, 3, QTableWidgetItem(str(item.quantity)))
                    self.inventory_table.setItem(row, 4, QTableWidgetItem(item.unit_of_measure))
                    self.inventory_table.setItem(row, 5, QTableWidgetItem(f"${item.unit_cost:.2f}"))
                    self.inventory_table.setItem(row, 6, QTableWidgetItem(f"${item.total_value():.2f}"))
                    
                    # Status with color coding
                    status_item = QTableWidgetItem(item.status.value)
                    if item.is_low_stock():
                        status_item.setBackground(QColor("#ffebee"))  # Light red
                        status_item.setText("LOW STOCK")
                    self.inventory_table.setItem(row, 7, status_item)
                
        except Exception as e:
            logger.error(f"Error loading inventory data: {e}")
            QMessageBox.warning(self, "Error", "Failed to load inventory data")
    
    def add_item(self):
        """Add new inventory item (placeholder)."""
        QMessageBox.information(
            self,
            "Add Inventory Item",
            "Add item functionality will be implemented in Phase 2.\n\n"
            "This would open a dialog for entering new item details."
        )


class NextFactoryMainWindow(QMainWindow):
    """
    Main application window for NextFactory ERP+MES system.
    
    This is the primary application window that provides the main user interface,
    manages user sessions, and coordinates between different modules based on
    user roles and permissions.
    """
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        self.current_user: Optional[User] = None
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.show_login_dialog()
        
    def setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle("NextFactory ERP+MES Exhibition Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget with tab layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(False)  # Don't allow closing tabs
        self.tab_widget.setMovable(False)       # Don't allow moving tabs
        self.tab_widget.setUsesScrollButtons(True)  # Use scroll buttons if many tabs
        self.main_layout.addWidget(self.tab_widget)
        
        # Apply professional styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007acc;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                min-width: 120px;
            }
            QComboBox:focus {
                border: 2px solid #007acc;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
    def setup_menu_bar(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        logout_action = QAction("Logout", self)
        logout_action.setShortcut("Ctrl+Q")
        logout_action.setStatusTip("Logout from the current session")
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        help_action = QAction("System Help", self)
        help_action.setShortcut("F1")
        help_action.setStatusTip("Show system help and user information")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About NextFactory", self)
        about_action.setShortcut("Ctrl+I")
        about_action.setStatusTip("About NextFactory ERP+MES system")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Set up the application status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def show_login_dialog(self):
        """Display the login dialog."""
        dialog = LoginDialog(self)
        dialog.user_authenticated.connect(self.on_user_authenticated)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            # User cancelled login, exit application
            self.close()
            
    @pyqtSlot(object)
    def on_user_authenticated(self, user: User):
        """
        Handle successful user authentication.
        
        Args:
            user (User): Authenticated user object
        """
        self.current_user = user
        self.setup_user_interface()
        self.update_window_title()
        
        try:
            # Safely access user information
            self.status_bar.showMessage(f"Logged in as: {user.get_full_name()} ({user.role.display_name})")
        except Exception as e:
            logger.error(f"Error updating status bar: {e}")
            self.status_bar.showMessage(f"Logged in as: {user.username}")
        
    def setup_user_interface(self):
        """Set up user interface based on current user's role and permissions."""
        if not self.current_user:
            return
        
        # Clear existing tabs
        self.tab_widget.clear()
        
        # Always add dashboard
        dashboard = DashboardWidget(self.current_user)
        self.tab_widget.addTab(dashboard, "Dashboard")
        
        # Add tabs based on user permissions
        permissions = self.current_user.role.to_dict()['permissions']
        
        # Enhanced Inventory Management
        if permissions.get('can_view_reports', False) or permissions.get('can_manage_inventory', False):
            if ERP_MES_MODULES_AVAILABLE:
                enhanced_inventory = EnhancedInventoryModule(self.current_user)
                self.tab_widget.addTab(enhanced_inventory, "Inventory Management")
            else:
                # Fallback to basic inventory
                inventory_widget = InventoryModule(self.current_user)
                self.tab_widget.addTab(inventory_widget, "Inventory")
        
        # ERP modules
        if permissions.get('can_access_erp', False) and ERP_MES_MODULES_AVAILABLE:
            # Supply Chain Management
            supply_chain = SupplyChainModule(self.current_user)
            self.tab_widget.addTab(supply_chain, "Supply Chain")
            
            # Sales & CRM (Phase 3)
            sales_crm = SalesCRMModule(self.current_user)
            self.tab_widget.addTab(sales_crm, "Sales & CRM")
            
            # Asset Management (Phase 3)
            asset_management = AssetManagementModule(self.current_user)
            self.tab_widget.addTab(asset_management, "Asset Management")
            
            # Reporting & Analytics
            if permissions.get('can_view_reports', False):
                reporting = ReportingModule(self.current_user)
                self.tab_widget.addTab(reporting, "Reporting & Analytics")
        elif permissions.get('can_access_erp', False):
            # Placeholder if modules not available
            erp_placeholder = QLabel("ERP modules loading...")
            erp_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tab_widget.addTab(erp_placeholder, "ERP")
        
        # MES modules
        if permissions.get('can_access_mes', False) and ERP_MES_MODULES_AVAILABLE:
            # Production Scheduling
            production_scheduling = ProductionSchedulingModule(self.current_user)
            self.tab_widget.addTab(production_scheduling, "Production Scheduling")
            
            # Real-Time Data Collection
            real_time_data = RealTimeDataModule(self.current_user)
            self.tab_widget.addTab(real_time_data, "Real-Time Data")
            
            # Quality Management
            quality_management = QualityManagementModule(self.current_user)
            self.tab_widget.addTab(quality_management, "Quality Management")
            
            # Performance Analysis
            performance_analysis = PerformanceAnalysisModule(self.current_user)
            self.tab_widget.addTab(performance_analysis, "Performance Analysis")
            
            # Resource Allocation (Phase 3)
            resource_allocation = ResourceAllocationModule(self.current_user)
            self.tab_widget.addTab(resource_allocation, "Resource Allocation")
            
            # Product Tracking & Traceability (Phase 3)
            product_tracking = ProductTrackingModule(self.current_user)
            self.tab_widget.addTab(product_tracking, "Product Tracking")
            
            # Maintenance Management (Phase 3)
            maintenance_mgmt = MaintenanceManagementModule(self.current_user)
            self.tab_widget.addTab(maintenance_mgmt, "Maintenance")
            
            # Labor Management (Phase 3)
            labor_mgmt = LaborManagementModule(self.current_user)
            self.tab_widget.addTab(labor_mgmt, "Labor Management")
        elif permissions.get('can_access_mes', False):
            # Placeholder if modules not available
            mes_placeholder = QLabel("MES modules loading...")
            mes_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tab_widget.addTab(mes_placeholder, "MES")
        
        # Basic Reports tab (for users who can't access full ERP but can view reports)
        if permissions.get('can_view_reports', False) and not permissions.get('can_access_erp', False):
            if ERP_MES_MODULES_AVAILABLE:
                reporting = ReportingModule(self.current_user)
                self.tab_widget.addTab(reporting, "Reports")
            else:
                reports_placeholder = QLabel("Advanced reporting will be available soon")
                reports_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tab_widget.addTab(reports_placeholder, "Reports")
        
    def update_window_title(self):
        """Update window title with user information."""
        if self.current_user:
            title = f"NextFactory ERP+MES - {self.current_user.get_full_name()} ({self.current_user.role.display_name})"
            self.setWindowTitle(title)
        
    def logout(self):
        """Log out current user and show login dialog."""
        self.current_user = None
        self.tab_widget.clear()
        self.setWindowTitle("NextFactory ERP+MES Exhibition Demo")
        self.status_bar.showMessage("Logged out")
        self.show_login_dialog()
    
    def show_help(self):
        """Display system help from main window."""
        if self.current_user:
            # Find the dashboard tab and call its help method
            for i in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(i)
                if hasattr(widget, 'show_help'):
                    widget.show_help()
                    return
        
        # Fallback help if no dashboard found
        QMessageBox.information(
            self,
            "System Help",
            "NextFactory ERP+MES System Help\n\n"
            "Use F1 to access context-sensitive help\n"
            "Navigate using tabs or keyboard shortcuts\n\n"
            "Keyboard Shortcuts:\n"
            "• F1: Help\n"
            "• Ctrl+Q: Logout\n"
            "• Alt+F4: Exit\n"
            "• Ctrl+I: About"
        )
        
    def show_about(self):
        """Display about dialog."""
        about_text = """NextFactory ERP+MES Exhibition Demo

Version: 1.0 (Phase 1)
Built with PyQt6 and SQLAlchemy

This demonstration showcases an integrated ERP and MES solution
designed for modern manufacturing environments.

Features:
• Role-based access control
• Modular architecture
• Real-time data integration
• Professional user interface

Development Team: NextFactory
Created: 2024"""
        
        QMessageBox.about(self, "About NextFactory", about_text)
        
    def closeEvent(self, event):
        """Handle application close event."""
        reply = QMessageBox.question(
            self,
            "Exit NextFactory",
            "Are you sure you want to exit the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """Main application entry point."""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("NextFactory")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("NextFactory Development Team")
    
    # Set application icon (if available)
    # app.setWindowIcon(QIcon("icon.png"))
    
    # Test database connection before starting
    if not test_database_connection():
        QMessageBox.critical(
            None,
            "Database Connection Error",
            "Cannot connect to the database.\n\n"
            "Please ensure PostgreSQL is running and the database is configured.\n"
            "Run 'python database.py' to set up the database.\n"
            "Run 'python seed_db.py' to populate demo data."
        )
        sys.exit(1)
    
    # Create and show main window
    window = NextFactoryMainWindow()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()