#!/usr/bin/env python3
"""
NextFactory ERP Modules - Phase 2 Implementation
=================================================

This module implements the ERP (Enterprise Resource Planning) modules for
the NextFactory exhibition demo, including enhanced inventory management,
supply chain management, and reporting/analytics capabilities.

Modules:
    - EnhancedInventoryModule: Advanced inventory management with filtering and alerts
    - SupplyChainModule: Supplier management and procurement
    - ReportingModule: Analytics and data visualization

Author: NextFactory Development Team
Created: 2024
"""

import sys
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateTimeEdit,
    QCheckBox, QGroupBox, QFrame, QMessageBox, QHeaderView,
    QTabWidget, QSplitter, QProgressBar, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QDateTime
from PyQt6.QtGui import QFont, QColor, QPalette

# Import matplotlib for charts
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

from database import get_db_session
from models import (
    User, InventoryItem, InventoryCategory, StatusEnum,
    Supplier, PurchaseOrder, PurchaseOrderItem, OrderStatusEnum, PriorityEnum,
    get_inventory_items, get_suppliers, get_purchase_orders
)

logger = logging.getLogger(__name__)


class InventoryAlertWidget(QWidget):
    """Widget for displaying inventory alerts and low stock notifications."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
        self.update_alerts()
        
        # Set up timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_alerts)
        self.timer.start(60000)  # Update every minute
        
    def setup_ui(self):
        """Set up the alert widget UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Inventory Alerts")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Alert list
        self.alert_list = QTableWidget()
        self.alert_list.setColumnCount(4)
        self.alert_list.setHorizontalHeaderLabels(["Item", "Current Stock", "Reorder Point", "Status"])
        
        header = self.alert_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.alert_list)
        
    def update_alerts(self):
        """Update the alert display with current low stock items."""
        try:
            with get_db_session() as session:
                low_stock_items = get_inventory_items(session, low_stock_only=True)
                
                self.alert_list.setRowCount(len(low_stock_items))
                
                for row, item in enumerate(low_stock_items):
                    # Item name
                    name_item = QTableWidgetItem(f"{item.item_code} - {item.item_name}")
                    self.alert_list.setItem(row, 0, name_item)
                    
                    # Current stock
                    stock_item = QTableWidgetItem(f"{item.quantity:.1f} {item.unit_of_measure}")
                    self.alert_list.setItem(row, 1, stock_item)
                    
                    # Reorder point
                    reorder_item = QTableWidgetItem(f"{item.reorder_point:.1f}")
                    self.alert_list.setItem(row, 2, reorder_item)
                    
                    # Status (color-coded)
                    status_item = QTableWidgetItem("LOW STOCK")
                    status_item.setBackground(QColor("#ffebee"))  # Light red
                    status_item.setForeground(QColor("#d32f2f"))   # Dark red
                    self.alert_list.setItem(row, 3, status_item)
                    
        except Exception as e:
            logger.error(f"Error updating inventory alerts: {e}")


class EnhancedInventoryModule(QWidget):
    """
    Enhanced inventory management module with advanced features.
    
    Features:
    - Advanced filtering and search
    - Low stock alerts
    - Category-based views
    - Stock level management
    - Export capabilities
    """
    
    def __init__(self, user: User, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()
        self.load_inventory_data()
        
    def setup_ui(self):
        """Set up the enhanced inventory management UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Enhanced Inventory Management")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Filters and alerts
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Inventory table
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
        
    def create_left_panel(self) -> QWidget:
        """Create the left panel with filters and alerts."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Filters group
        filters_group = QGroupBox("Filters")
        filters_layout = QFormLayout(filters_group)
        
        # Category filter
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        for category in InventoryCategory:
            self.category_combo.addItem(category.value.replace('_', ' ').title())
        self.category_combo.currentTextChanged.connect(self.apply_filters)
        self.category_combo.setToolTip("Filter inventory items by category")
        filters_layout.addRow("Category:", self.category_combo)
        
        # Search filter
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.textChanged.connect(self.apply_filters)
        self.search_input.setToolTip("Search by item name or code")
        filters_layout.addRow("Search:", self.search_input)
        
        # Low stock filter
        self.low_stock_checkbox = QCheckBox("Show only low stock")
        self.low_stock_checkbox.toggled.connect(self.apply_filters)
        self.low_stock_checkbox.setToolTip("Show only items below reorder point")
        filters_layout.addRow(self.low_stock_checkbox)
        
        layout.addWidget(filters_group)
        
        # Alert widget
        self.alert_widget = InventoryAlertWidget()
        layout.addWidget(self.alert_widget)
        
        layout.addStretch()
        return panel
        
    def create_right_panel(self) -> QWidget:
        """Create the right panel with inventory table and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_inventory_data)
        controls_layout.addWidget(refresh_btn)
        
        if self.user.role.can_manage_inventory:
            add_btn = QPushButton("Add Item")
            add_btn.clicked.connect(self.add_inventory_item)
            controls_layout.addWidget(add_btn)
            
            update_btn = QPushButton("Update Stock")
            update_btn.clicked.connect(self.update_stock)
            controls_layout.addWidget(update_btn)
        
        export_btn = QPushButton("Export Data")
        export_btn.clicked.connect(self.export_inventory_data)
        controls_layout.addWidget(export_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(9)
        self.inventory_table.setHorizontalHeaderLabels([
            "Item Code", "Name", "Category", "Quantity", "Unit", 
            "Unit Cost", "Total Value", "Reorder Point", "Status"
        ])
        
        # Configure table
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setSortingEnabled(True)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.inventory_table)
        
        return panel
        
    def load_inventory_data(self):
        """Load and display inventory data."""
        try:
            with get_db_session() as session:
                items = get_inventory_items(session)
                self.all_items = items  # Store for filtering
                self.display_items(items)
                
        except Exception as e:
            logger.error(f"Error loading inventory data: {e}")
            QMessageBox.warning(self, "Error", "Failed to load inventory data")
            
    def display_items(self, items: List[InventoryItem]):
        """Display inventory items in the table."""
        self.inventory_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # Item code
            self.inventory_table.setItem(row, 0, QTableWidgetItem(item.item_code))
            
            # Name
            self.inventory_table.setItem(row, 1, QTableWidgetItem(item.item_name))
            
            # Category
            category_text = item.category.value.replace('_', ' ').title()
            self.inventory_table.setItem(row, 2, QTableWidgetItem(category_text))
            
            # Quantity
            self.inventory_table.setItem(row, 3, QTableWidgetItem(f"{item.quantity:.1f}"))
            
            # Unit
            self.inventory_table.setItem(row, 4, QTableWidgetItem(item.unit_of_measure))
            
            # Unit cost
            self.inventory_table.setItem(row, 5, QTableWidgetItem(f"${item.unit_cost:.2f}"))
            
            # Total value
            self.inventory_table.setItem(row, 6, QTableWidgetItem(f"${item.total_value():.2f}"))
            
            # Reorder point
            self.inventory_table.setItem(row, 7, QTableWidgetItem(f"{item.reorder_point:.1f}"))
            
            # Status with color coding
            status_text = "LOW STOCK" if item.is_low_stock() else item.status.value.upper()
            status_item = QTableWidgetItem(status_text)
            
            if item.is_low_stock():
                status_item.setBackground(QColor("#ffebee"))
                status_item.setForeground(QColor("#d32f2f"))
            
            self.inventory_table.setItem(row, 8, status_item)
            
    def apply_filters(self):
        """Apply current filter settings to inventory display."""
        if not hasattr(self, 'all_items'):
            return
        
        try:
            filtered_items = self.all_items.copy()
            
            # Category filter
            category_text = self.category_combo.currentText()
            if category_text != "All Categories":
                category_value = category_text.lower().replace(' ', '_')
                try:
                    filtered_items = [item for item in filtered_items 
                                    if item.category.value == category_value]
                except Exception as e:
                    logger.error(f"Error filtering by category: {e}")
                    # If we can't access category, reload data
                    self.show_message("Reloading data due to session issue...")
                    self.load_inventory_data()
                    return
            
            # Search filter
            search_text = self.search_input.text().lower()
            if search_text:
                try:
                    filtered_items = [item for item in filtered_items
                                    if search_text in item.item_name.lower() or 
                                       search_text in item.item_code.lower()]
                except Exception as e:
                    logger.error(f"Error in search filter: {e}")
                    self.show_message("Search failed due to session issue. Reloading data...")
                    self.load_inventory_data()
                    return
            
            # Low stock filter
            if self.low_stock_checkbox.isChecked():
                try:
                    filtered_items = [item for item in filtered_items if item.is_low_stock()]
                except Exception as e:
                    logger.error(f"Error in low stock filter: {e}")
                    self.show_message("Low stock filter failed. Reloading data...")
                    self.load_inventory_data()
                    return
            
            self.display_items(filtered_items)
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            self.show_message("Filtering failed. Please try again.")
    
    def show_message(self, message: str):
        """Show a user-friendly message."""
        QMessageBox.information(self, "Information", message)
        
    def add_inventory_item(self):
        """Add a new inventory item (placeholder for Phase 2)."""
        QMessageBox.information(
            self,
            "Add Inventory Item",
            "Add item functionality will be fully implemented in the next phase.\n\n"
            "This would open a detailed form for entering:\n"
            "• Item details and specifications\n"
            "• Initial stock quantities\n"
            "• Supplier information\n"
            "• Reorder points and thresholds"
        )
        
    def update_stock(self):
        """Update stock levels (placeholder for Phase 2)."""
        QMessageBox.information(
            self,
            "Update Stock",
            "Stock update functionality will be fully implemented in the next phase.\n\n"
            "This would allow:\n"
            "• Adjusting quantities for received materials\n"
            "• Recording material usage\n"
            "• Batch updates from production\n"
            "• Inventory audit adjustments"
        )
        
    def export_inventory_data(self):
        """Export inventory data to CSV."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Inventory Data", "inventory_export.csv", "CSV Files (*.csv)"
            )
            if filename:
                # Create DataFrame from current table data
                data = []
                headers = []
                for col in range(self.inventory_table.columnCount()):
                    headers.append(self.inventory_table.horizontalHeaderItem(col).text())
                
                for row in range(self.inventory_table.rowCount()):
                    row_data = []
                    for col in range(self.inventory_table.columnCount()):
                        item = self.inventory_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                df = pd.DataFrame(data, columns=headers)
                df.to_csv(filename, index=False)
                
                QMessageBox.information(self, "Export Complete", f"Data exported to {filename}")
                
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            QMessageBox.warning(self, "Export Error", "Failed to export data")


class SupplyChainModule(QWidget):
    """
    Supply chain management module with supplier management and procurement.
    
    Features:
    - Supplier management
    - Purchase order creation
    - Delivery simulation
    - Auto-order based on inventory thresholds
    """
    
    def __init__(self, user: User, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Set up the supply chain management UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Supply Chain Management")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Suppliers tab
        self.suppliers_tab = self.create_suppliers_tab()
        self.tab_widget.addTab(self.suppliers_tab, "Suppliers")
        
        # Purchase Orders tab
        self.orders_tab = self.create_orders_tab()
        self.tab_widget.addTab(self.orders_tab, "Purchase Orders")
        
        # Auto-Order tab
        self.auto_order_tab = self.create_auto_order_tab()
        self.tab_widget.addTab(self.auto_order_tab, "Auto-Order System")
        
        layout.addWidget(self.tab_widget)
        
    def create_suppliers_tab(self) -> QWidget:
        """Create the suppliers management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_suppliers)
        controls_layout.addWidget(refresh_btn)
        
        if self.user.role.can_access_erp:
            add_supplier_btn = QPushButton("Add Supplier")
            add_supplier_btn.clicked.connect(self.add_supplier)
            controls_layout.addWidget(add_supplier_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(6)
        self.suppliers_table.setHorizontalHeaderLabels([
            "Code", "Name", "Contact", "Email", "Rating", "Status"
        ])
        
        header = self.suppliers_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.suppliers_table.setAlternatingRowColors(True)
        self.suppliers_table.setSortingEnabled(True)
        
        layout.addWidget(self.suppliers_table)
        
        return widget
        
    def create_orders_tab(self) -> QWidget:
        """Create the purchase orders tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_orders)
        controls_layout.addWidget(refresh_btn)
        
        if self.user.role.can_create_orders:
            create_order_btn = QPushButton("Create Order")
            create_order_btn.clicked.connect(self.create_purchase_order)
            controls_layout.addWidget(create_order_btn)
        
        simulate_delivery_btn = QPushButton("Simulate Delivery")
        simulate_delivery_btn.clicked.connect(self.simulate_delivery)
        controls_layout.addWidget(simulate_delivery_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            "Order Number", "Supplier", "Total Amount", "Status", 
            "Priority", "Expected Date", "Created"
        ])
        
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setSortingEnabled(True)
        
        layout.addWidget(self.orders_table)
        
        return widget
        
    def create_auto_order_tab(self) -> QWidget:
        """Create the auto-order system tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Info label
        info_label = QLabel("Automatic ordering based on inventory thresholds")
        info_label.setFont(QFont("Arial", 10))
        layout.addWidget(info_label)
        
        # Auto-order controls
        controls_group = QGroupBox("Auto-Order Settings")
        controls_layout = QFormLayout(controls_group)
        
        self.auto_order_enabled = QCheckBox("Enable automatic ordering")
        controls_layout.addRow(self.auto_order_enabled)
        
        self.check_interval = QSpinBox()
        self.check_interval.setRange(1, 60)
        self.check_interval.setValue(5)
        self.check_interval.setSuffix(" minutes")
        controls_layout.addRow("Check interval:", self.check_interval)
        
        layout.addWidget(controls_group)
        
        # Trigger analysis button
        analyze_btn = QPushButton("Analyze Reorder Needs")
        analyze_btn.clicked.connect(self.analyze_reorder_needs)
        layout.addWidget(analyze_btn)
        
        # Results area
        self.auto_order_results = QTextEdit()
        self.auto_order_results.setReadOnly(True)
        layout.addWidget(self.auto_order_results)
        
        return widget
        
    def load_data(self):
        """Load all supply chain data."""
        self.load_suppliers()
        self.load_orders()
        
    def load_suppliers(self):
        """Load suppliers data."""
        try:
            with get_db_session() as session:
                suppliers = get_suppliers(session)
                self.display_suppliers(suppliers)
        except Exception as e:
            logger.error(f"Error loading suppliers: {e}")
            
    def display_suppliers(self, suppliers: List[Supplier]):
        """Display suppliers in the table."""
        self.suppliers_table.setRowCount(len(suppliers))
        
        for row, supplier in enumerate(suppliers):
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(supplier.supplier_code))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier.name))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier.contact_person or ""))
            self.suppliers_table.setItem(row, 3, QTableWidgetItem(supplier.email or ""))
            self.suppliers_table.setItem(row, 4, QTableWidgetItem(f"{supplier.rating:.1f}/5.0"))
            self.suppliers_table.setItem(row, 5, QTableWidgetItem(supplier.status.value.upper()))
            
    def load_orders(self):
        """Load purchase orders data."""
        try:
            with get_db_session() as session:
                orders = get_purchase_orders(session)
                self.display_orders(orders)
        except Exception as e:
            logger.error(f"Error loading orders: {e}")
            
    def display_orders(self, orders: List[PurchaseOrder]):
        """Display purchase orders in the table."""
        self.orders_table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(order.order_number))
            self.orders_table.setItem(row, 1, QTableWidgetItem(order.supplier.name))
            self.orders_table.setItem(row, 2, QTableWidgetItem(f"${order.total_amount:.2f}"))
            self.orders_table.setItem(row, 3, QTableWidgetItem(order.status.value.upper()))
            self.orders_table.setItem(row, 4, QTableWidgetItem(order.priority.value.upper()))
            
            expected_date = order.expected_date.strftime("%Y-%m-%d") if order.expected_date else "TBD"
            self.orders_table.setItem(row, 5, QTableWidgetItem(expected_date))
            
            created_date = order.created_at.strftime("%Y-%m-%d")
            self.orders_table.setItem(row, 6, QTableWidgetItem(created_date))
            
    def add_supplier(self):
        """Add a new supplier (placeholder)."""
        QMessageBox.information(
            self,
            "Add Supplier",
            "Add supplier functionality will be fully implemented in the next phase.\n\n"
            "This would include:\n"
            "• Supplier registration form\n"
            "• Contact information management\n"
            "• Performance rating system\n"
            "• Document management"
        )
        
    def create_purchase_order(self):
        """Create a new purchase order (placeholder)."""
        QMessageBox.information(
            self,
            "Create Purchase Order",
            "Purchase order creation will be fully implemented in the next phase.\n\n"
            "This would include:\n"
            "• Item selection and quantities\n"
            "• Supplier selection\n"
            "• Pricing and terms\n"
            "• Approval workflow"
        )
        
    def simulate_delivery(self):
        """Simulate delivery of purchase orders."""
        QMessageBox.information(
            self,
            "Delivery Simulation",
            "Simulating delivery process...\n\n"
            "In a real system, this would:\n"
            "• Update order status to 'Delivered'\n"
            "• Increase inventory quantities\n"
            "• Generate receiving reports\n"
            "• Trigger quality inspections"
        )
        
    def analyze_reorder_needs(self):
        """Analyze inventory for reorder needs."""
        try:
            with get_db_session() as session:
                low_stock_items = get_inventory_items(session, low_stock_only=True)
                
                if not low_stock_items:
                    self.auto_order_results.setText("No items below reorder point. All inventory levels are adequate.")
                    return
                
                results = "REORDER ANALYSIS RESULTS\n"
                results += "=" * 50 + "\n\n"
                
                total_reorder_value = 0.0
                
                for item in low_stock_items:
                    shortage = item.reorder_point - item.quantity
                    reorder_qty = max(shortage, item.reorder_point * 1.5)  # Order 1.5x reorder point
                    estimated_cost = reorder_qty * item.unit_cost
                    total_reorder_value += estimated_cost
                    
                    results += f"Item: {item.item_name} ({item.item_code})\n"
                    results += f"  Current Stock: {item.quantity:.1f} {item.unit_of_measure}\n"
                    results += f"  Reorder Point: {item.reorder_point:.1f}\n"
                    results += f"  Suggested Order: {reorder_qty:.1f} {item.unit_of_measure}\n"
                    results += f"  Estimated Cost: ${estimated_cost:.2f}\n"
                    results += f"  Primary Supplier: {item.supplier or 'Not specified'}\n\n"
                
                results += f"SUMMARY:\n"
                results += f"Items needing reorder: {len(low_stock_items)}\n"
                results += f"Total estimated cost: ${total_reorder_value:.2f}\n"
                
                self.auto_order_results.setText(results)
                
        except Exception as e:
            logger.error(f"Error analyzing reorder needs: {e}")
            self.auto_order_results.setText("Error analyzing reorder needs.")


class ChartWidget(QWidget):
    """Custom widget for displaying matplotlib charts."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        
    def clear(self):
        """Clear the chart."""
        self.figure.clear()
        self.canvas.draw()
        
    def plot_inventory_by_category(self):
        """Plot inventory distribution by category."""
        try:
            with get_db_session() as session:
                items = get_inventory_items(session)
                
                # Group by category
                category_data = {}
                for item in items:
                    category = item.category.value.replace('_', ' ').title()
                    if category not in category_data:
                        category_data[category] = {'count': 0, 'value': 0.0}
                    category_data[category]['count'] += 1
                    category_data[category]['value'] += item.total_value()
                
                if not category_data:
                    return
                
                self.figure.clear()
                
                # Create subplots
                ax1 = self.figure.add_subplot(2, 1, 1)
                ax2 = self.figure.add_subplot(2, 1, 2)
                
                categories = list(category_data.keys())
                counts = [category_data[cat]['count'] for cat in categories]
                values = [category_data[cat]['value'] for cat in categories]
                
                # Item count by category
                ax1.bar(categories, counts, color='skyblue')
                ax1.set_title('Inventory Items by Category')
                ax1.set_ylabel('Number of Items')
                ax1.tick_params(axis='x', rotation=45)
                
                # Value by category
                ax2.bar(categories, values, color='lightgreen')
                ax2.set_title('Inventory Value by Category')
                ax2.set_ylabel('Total Value ($)')
                ax2.tick_params(axis='x', rotation=45)
                
                self.figure.tight_layout()
                self.canvas.draw()
                
        except Exception as e:
            logger.error(f"Error plotting inventory chart: {e}")
            
    def plot_low_stock_trends(self):
        """Plot low stock trends over time (simulated data)."""
        try:
            # Generate sample trend data
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            low_stock_counts = [random.randint(3, 12) for _ in range(30)]
            
            self.figure.clear()
            ax = self.figure.add_subplot(1, 1, 1)
            
            ax.plot(dates, low_stock_counts, marker='o', linestyle='-', color='red')
            ax.set_title('Low Stock Items Trend (Last 30 Days)')
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Low Stock Items')
            ax.grid(True, alpha=0.3)
            
            # Format x-axis dates
            self.figure.autofmt_xdate()
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error plotting trend chart: {e}")


class ReportingModule(QWidget):
    """
    Reporting and analytics module with data visualization and export capabilities.
    
    Features:
    - Interactive charts and graphs
    - KPI dashboards
    - Data export (PDF/CSV)
    - Customizable reports
    """
    
    def __init__(self, user: User, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()
        self.load_default_charts()
        
    def setup_ui(self):
        """Set up the reporting and analytics UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Reporting & Analytics")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Create splitter for layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Controls and KPIs
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Charts
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
    def create_left_panel(self) -> QWidget:
        """Create the left panel with controls and KPIs."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Chart controls
        controls_group = QGroupBox("Chart Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.chart_selector = QComboBox()
        self.chart_selector.addItems([
            "Inventory by Category",
            "Low Stock Trends",
            "Supplier Performance",
            "Cost Analysis"
        ])
        self.chart_selector.currentTextChanged.connect(self.update_chart)
        controls_layout.addWidget(QLabel("Select Chart:"))
        controls_layout.addWidget(self.chart_selector)
        
        refresh_btn = QPushButton("Refresh Chart")
        refresh_btn.clicked.connect(self.refresh_current_chart)
        controls_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("Export Chart")
        export_btn.clicked.connect(self.export_chart)
        controls_layout.addWidget(export_btn)
        
        layout.addWidget(controls_group)
        
        # KPI Dashboard
        kpi_group = QGroupBox("Key Performance Indicators")
        kpi_layout = QGridLayout(kpi_group)
        
        # KPI widgets
        self.total_items_label = QLabel("0")
        self.total_items_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        kpi_layout.addWidget(QLabel("Total Items:"), 0, 0)
        kpi_layout.addWidget(self.total_items_label, 0, 1)
        
        self.total_value_label = QLabel("$0.00")
        self.total_value_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        kpi_layout.addWidget(QLabel("Total Value:"), 1, 0)
        kpi_layout.addWidget(self.total_value_label, 1, 1)
        
        self.low_stock_label = QLabel("0")
        self.low_stock_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.low_stock_label.setStyleSheet("color: red;")
        kpi_layout.addWidget(QLabel("Low Stock:"), 2, 0)
        kpi_layout.addWidget(self.low_stock_label, 2, 1)
        
        layout.addWidget(kpi_group)
        
        # Update KPIs
        self.update_kpis()
        
        layout.addStretch()
        return panel
        
    def create_right_panel(self) -> QWidget:
        """Create the right panel with chart display."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Chart widget
        self.chart_widget = ChartWidget()
        layout.addWidget(self.chart_widget)
        
        return panel
        
    def load_default_charts(self):
        """Load the default chart."""
        self.update_chart("Inventory by Category")
        
    def update_chart(self, chart_name: str):
        """Update the chart based on selection."""
        if chart_name == "Inventory by Category":
            self.chart_widget.plot_inventory_by_category()
        elif chart_name == "Low Stock Trends":
            self.chart_widget.plot_low_stock_trends()
        else:
            # Placeholder for other charts
            self.chart_widget.clear()
            QMessageBox.information(
                self,
                "Chart Coming Soon",
                f"The '{chart_name}' chart will be implemented in the next phase."
            )
            
    def refresh_current_chart(self):
        """Refresh the currently selected chart."""
        current_chart = self.chart_selector.currentText()
        self.update_chart(current_chart)
        self.update_kpis()
        
    def update_kpis(self):
        """Update KPI values."""
        try:
            with get_db_session() as session:
                items = get_inventory_items(session)
                low_stock_items = get_inventory_items(session, low_stock_only=True)
                
                total_items = len(items)
                total_value = sum(item.total_value() for item in items)
                low_stock_count = len(low_stock_items)
                
                self.total_items_label.setText(str(total_items))
                self.total_value_label.setText(f"${total_value:,.2f}")
                self.low_stock_label.setText(str(low_stock_count))
                
        except Exception as e:
            logger.error(f"Error updating KPIs: {e}")
            
    def export_chart(self):
        """Export the current chart."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Chart", "chart_export.png", "PNG Files (*.png)"
            )
            if filename:
                self.chart_widget.figure.savefig(filename, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Export Complete", f"Chart exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting chart: {e}")
            QMessageBox.warning(self, "Export Error", "Failed to export chart")


# Phase 3 Optional ERP Modules

class SalesCRMModule(QWidget):
    """
    Sales & CRM module for customer relationship management.
    
    Features:
    - Customer management with contact information
    - Sales order creation and tracking
    - Order history and relationship tracking
    - Customer analytics and performance metrics
    """
    
    def __init__(self, user, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()
        self.load_data()
        
        # Set up timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # Update every 30 seconds
        
    def setup_ui(self):
        """Set up the Sales & CRM module UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Sales & CRM Management")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Customer Management Tab
        self.setup_customer_tab()
        
        # Sales Orders Tab
        self.setup_orders_tab()
        
        # Customer Analytics Tab
        self.setup_analytics_tab()
        
    def setup_customer_tab(self):
        """Set up customer management tab."""
        customer_widget = QWidget()
        layout = QVBoxLayout(customer_widget)
        
        # Customer controls
        controls_layout = QHBoxLayout()
        
        add_customer_btn = QPushButton("Add Customer")
        add_customer_btn.clicked.connect(self.add_customer)
        controls_layout.addWidget(add_customer_btn)
        
        edit_customer_btn = QPushButton("Edit Customer")
        edit_customer_btn.clicked.connect(self.edit_customer)
        controls_layout.addWidget(edit_customer_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Customer table
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(7)
        self.customer_table.setHorizontalHeaderLabels([
            "Customer Code", "Company Name", "Contact Person", 
            "Email", "Phone", "Credit Limit", "Status"
        ])
        
        header = self.customer_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.customer_table)
        
        self.tab_widget.addTab(customer_widget, "Customers")
        
    def setup_orders_tab(self):
        """Set up sales orders tab."""
        orders_widget = QWidget()
        layout = QVBoxLayout(orders_widget)
        
        # Order controls
        controls_layout = QHBoxLayout()
        
        add_order_btn = QPushButton("New Order")
        add_order_btn.clicked.connect(self.add_sales_order)
        controls_layout.addWidget(add_order_btn)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Orders", "Pending", "Confirmed", "In Progress", "Shipped", "Delivered"])
        self.status_filter.currentTextChanged.connect(self.filter_orders)
        controls_layout.addWidget(QLabel("Filter:"))
        controls_layout.addWidget(self.status_filter)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(8)
        self.orders_table.setHorizontalHeaderLabels([
            "Order #", "Customer", "Order Date", "Total Amount", 
            "Status", "Priority", "Requested Delivery", "Notes"
        ])
        
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.orders_table)
        
        self.tab_widget.addTab(orders_widget, "Sales Orders")
        
    def setup_analytics_tab(self):
        """Set up customer analytics tab."""
        analytics_widget = QWidget()
        layout = QVBoxLayout(analytics_widget)
        
        # Analytics header
        analytics_header = QLabel("Customer Analytics & Performance")
        analytics_header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(analytics_header)
        
        # KPI cards
        kpi_layout = QHBoxLayout()
        
        # Total customers
        self.total_customers_card = self.create_kpi_card("Total Customers", "0")
        kpi_layout.addWidget(self.total_customers_card)
        
        # Active orders
        self.active_orders_card = self.create_kpi_card("Active Orders", "0")
        kpi_layout.addWidget(self.active_orders_card)
        
        # Monthly revenue
        self.monthly_revenue_card = self.create_kpi_card("Monthly Revenue", "$0")
        kpi_layout.addWidget(self.monthly_revenue_card)
        
        # Average order value
        self.avg_order_card = self.create_kpi_card("Avg Order Value", "$0")
        kpi_layout.addWidget(self.avg_order_card)
        
        layout.addLayout(kpi_layout)
        
        # Top customers table
        top_customers_label = QLabel("Top Customers by Order Value")
        top_customers_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(top_customers_label)
        
        self.top_customers_table = QTableWidget()
        self.top_customers_table.setColumnCount(4)
        self.top_customers_table.setHorizontalHeaderLabels([
            "Customer", "Total Orders", "Total Value", "Last Order"
        ])
        self.top_customers_table.setMaximumHeight(200)
        layout.addWidget(self.top_customers_table)
        
        self.tab_widget.addTab(analytics_widget, "Analytics")
        
    def create_kpi_card(self, title: str, value: str) -> QGroupBox:
        """Create a KPI card widget."""
        card = QGroupBox(title)
        layout = QVBoxLayout(card)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: #2E86AB; padding: 10px;")
        
        layout.addWidget(value_label)
        card.value_label = value_label  # Store reference for updates
        
        return card
        
    def load_data(self):
        """Load customer and order data."""
        self.load_customers()
        self.load_sales_orders()
        self.update_analytics()
        
    def load_customers(self):
        """Load customer data into table."""
        try:
            from models import get_customers
            with get_db_session() as session:
                customers = get_customers(session)
                
                self.customer_table.setRowCount(len(customers))
                
                for row, customer in enumerate(customers):
                    self.customer_table.setItem(row, 0, QTableWidgetItem(customer.customer_code))
                    self.customer_table.setItem(row, 1, QTableWidgetItem(customer.company_name))
                    self.customer_table.setItem(row, 2, QTableWidgetItem(customer.contact_person or ""))
                    self.customer_table.setItem(row, 3, QTableWidgetItem(customer.email or ""))
                    self.customer_table.setItem(row, 4, QTableWidgetItem(customer.phone or ""))
                    self.customer_table.setItem(row, 5, QTableWidgetItem(f"${customer.credit_limit:,.2f}"))
                    self.customer_table.setItem(row, 6, QTableWidgetItem(customer.status.value))
                    
        except Exception as e:
            logger.error(f"Error loading customers: {e}")
            
    def load_sales_orders(self):
        """Load sales orders data into table."""
        try:
            from models import get_sales_orders
            with get_db_session() as session:
                orders = get_sales_orders(session)
                
                self.orders_table.setRowCount(len(orders))
                
                for row, order in enumerate(orders):
                    self.orders_table.setItem(row, 0, QTableWidgetItem(order.order_number))
                    self.orders_table.setItem(row, 1, QTableWidgetItem(order.customer.company_name))
                    self.orders_table.setItem(row, 2, QTableWidgetItem(order.order_date.strftime("%Y-%m-%d")))
                    self.orders_table.setItem(row, 3, QTableWidgetItem(f"${order.total_amount:,.2f}"))
                    self.orders_table.setItem(row, 4, QTableWidgetItem(order.status.value))
                    self.orders_table.setItem(row, 5, QTableWidgetItem(order.priority.value))
                    
                    req_delivery = order.requested_delivery.strftime("%Y-%m-%d") if order.requested_delivery else "TBD"
                    self.orders_table.setItem(row, 6, QTableWidgetItem(req_delivery))
                    self.orders_table.setItem(row, 7, QTableWidgetItem(order.notes or ""))
                    
        except Exception as e:
            logger.error(f"Error loading sales orders: {e}")
            
    def update_analytics(self):
        """Update analytics and KPIs."""
        try:
            from models import get_customers, get_sales_orders
            with get_db_session() as session:
                customers = get_customers(session)
                orders = get_sales_orders(session)
                
                # Update KPI cards
                self.total_customers_card.value_label.setText(str(len(customers)))
                
                active_orders = [o for o in orders if o.status.value in ['pending', 'confirmed', 'in_progress']]
                self.active_orders_card.value_label.setText(str(len(active_orders)))
                
                # Calculate monthly revenue (demo: sum of all orders)
                total_revenue = sum(order.total_amount for order in orders)
                self.monthly_revenue_card.value_label.setText(f"${total_revenue:,.2f}")
                
                # Average order value
                avg_order = total_revenue / len(orders) if orders else 0
                self.avg_order_card.value_label.setText(f"${avg_order:,.2f}")
                
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
            
    def filter_orders(self):
        """Filter orders by status."""
        filter_text = self.status_filter.currentText()
        if filter_text == "All Orders":
            self.load_sales_orders()
            return
            
        # Filter table rows based on status
        for row in range(self.orders_table.rowCount()):
            status_item = self.orders_table.item(row, 4)
            if status_item:
                should_show = filter_text.lower() in status_item.text().lower()
                self.orders_table.setRowHidden(row, not should_show)
                
    def add_customer(self):
        """Add new customer dialog."""
        QMessageBox.information(self, "Coming Soon", 
                              "Customer creation dialog will be implemented in the next phase.")
        
    def edit_customer(self):
        """Edit selected customer."""
        current_row = self.customer_table.currentRow()
        if current_row >= 0:
            QMessageBox.information(self, "Coming Soon", 
                                  "Customer editing dialog will be implemented in the next phase.")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a customer to edit.")
            
    def add_sales_order(self):
        """Add new sales order dialog."""
        QMessageBox.information(self, "Coming Soon", 
                              "Sales order creation dialog will be implemented in the next phase.")
        
    def refresh_data(self):
        """Refresh all data."""
        self.load_data()


class AssetManagementModule(QWidget):
    """
    Asset Management module for tracking machines, tools, and equipment.
    
    Features:
    - Asset registry with detailed information
    - Asset condition and status tracking
    - Maintenance history integration
    - Asset performance metrics
    """
    
    def __init__(self, user, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
        self.user = user
        self.load_data()
        
        # Set up timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(60000)  # Update every minute
        
    def setup_ui(self):
        """Set up the Asset Management module UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Asset Management")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_asset_btn = QPushButton("Add Asset")
        add_asset_btn.clicked.connect(self.add_asset)
        controls_layout.addWidget(add_asset_btn)
        
        self.asset_type_filter = QComboBox()
        self.asset_type_filter.addItems(["All Types", "Machine", "Tool", "Equipment", "Vehicle", "Computer", "Facility"])
        self.asset_type_filter.currentTextChanged.connect(self.filter_assets)
        controls_layout.addWidget(QLabel("Type:"))
        controls_layout.addWidget(self.asset_type_filter)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Active", "Inactive", "Maintenance", "Retired"])
        self.status_filter.currentTextChanged.connect(self.filter_assets)
        controls_layout.addWidget(QLabel("Status:"))
        controls_layout.addWidget(self.status_filter)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Asset summary cards
        summary_layout = QHBoxLayout()
        
        self.total_assets_card = self.create_summary_card("Total Assets", "0")
        summary_layout.addWidget(self.total_assets_card)
        
        self.active_assets_card = self.create_summary_card("Active Assets", "0")
        summary_layout.addWidget(self.active_assets_card)
        
        self.maintenance_due_card = self.create_summary_card("Maintenance Due", "0")
        summary_layout.addWidget(self.maintenance_due_card)
        
        self.total_value_card = self.create_summary_card("Total Value", "$0")
        summary_layout.addWidget(self.total_value_card)
        
        layout.addLayout(summary_layout)
        
        # Asset table
        self.asset_table = QTableWidget()
        self.asset_table.setColumnCount(9)
        self.asset_table.setHorizontalHeaderLabels([
            "Asset Tag", "Name", "Type", "Manufacturer", "Model", 
            "Location", "Condition", "Status", "Purchase Cost"
        ])
        
        header = self.asset_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.asset_table)
        
    def create_summary_card(self, title: str, value: str) -> QGroupBox:
        """Create a summary card widget."""
        card = QGroupBox(title)
        layout = QVBoxLayout(card)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: #D4AF37; padding: 10px;")
        
        layout.addWidget(value_label)
        card.value_label = value_label  # Store reference for updates
        
        return card
        
    def load_data(self):
        """Load asset data."""
        self.load_assets()
        self.update_summary()
        
    def load_assets(self):
        """Load asset data into table."""
        try:
            from models import get_assets
            with get_db_session() as session:
                assets = get_assets(session)
                
                self.asset_table.setRowCount(len(assets))
                
                for row, asset in enumerate(assets):
                    self.asset_table.setItem(row, 0, QTableWidgetItem(asset.asset_tag))
                    self.asset_table.setItem(row, 1, QTableWidgetItem(asset.name))
                    self.asset_table.setItem(row, 2, QTableWidgetItem(asset.asset_type.value))
                    self.asset_table.setItem(row, 3, QTableWidgetItem(asset.manufacturer or ""))
                    self.asset_table.setItem(row, 4, QTableWidgetItem(asset.model or ""))
                    self.asset_table.setItem(row, 5, QTableWidgetItem(asset.location or ""))
                    self.asset_table.setItem(row, 6, QTableWidgetItem(asset.condition))
                    self.asset_table.setItem(row, 7, QTableWidgetItem(asset.status.value))
                    self.asset_table.setItem(row, 8, QTableWidgetItem(f"${asset.purchase_cost:,.2f}"))
                    
        except Exception as e:
            logger.error(f"Error loading assets: {e}")
            
    def update_summary(self):
        """Update summary cards."""
        try:
            from models import get_assets
            with get_db_session() as session:
                assets = get_assets(session)
                
                total_assets = len(assets)
                active_assets = len([a for a in assets if a.status.value == 'active'])
                total_value = sum(asset.purchase_cost for asset in assets)
                
                self.total_assets_card.value_label.setText(str(total_assets))
                self.active_assets_card.value_label.setText(str(active_assets))
                self.total_value_card.value_label.setText(f"${total_value:,.2f}")
                
                # Demo: random maintenance due count
                import random
                maintenance_due = random.randint(0, max(1, total_assets // 5))
                self.maintenance_due_card.value_label.setText(str(maintenance_due))
                
        except Exception as e:
            logger.error(f"Error updating asset summary: {e}")
            
    def filter_assets(self):
        """Filter assets by type and status."""
        type_filter = self.asset_type_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        for row in range(self.asset_table.rowCount()):
            type_item = self.asset_table.item(row, 2)
            status_item = self.asset_table.item(row, 7)
            
            show_row = True
            
            if type_filter != "All Types" and type_item:
                show_row = show_row and (type_filter.lower() in type_item.text().lower())
                
            if status_filter != "All Status" and status_item:
                show_row = show_row and (status_filter.lower() in status_item.text().lower())
                
            self.asset_table.setRowHidden(row, not show_row)
            
    def add_asset(self):
        """Add new asset dialog."""
        QMessageBox.information(self, "Coming Soon", 
                              "Asset creation dialog will be implemented in the next phase.")
        
    def refresh_data(self):
        """Refresh all data."""
        self.load_data()