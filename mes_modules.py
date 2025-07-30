#!/usr/bin/env python3
"""
NextFactory MES Modules - Phase 2 Implementation
================================================

This module implements the MES (Manufacturing Execution System) modules for
the NextFactory exhibition demo, including production scheduling, real-time
data collection, quality management, and performance analysis.

Modules:
    - ProductionSchedulingModule: Task scheduling and dispatching with calendar view
    - RealTimeDataModule: Sensor data simulation and live monitoring
    - QualityManagementModule: Quality checks and defect tracking
    - PerformanceAnalysisModule: OEE calculations and metrics

Author: NextFactory Development Team
Created: 2024
"""

import sys
import logging
import random
import threading
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateTimeEdit,
    QCheckBox, QGroupBox, QFrame, QMessageBox, QHeaderView,
    QTabWidget, QSplitter, QProgressBar, QListWidget, QListWidgetItem,
    QCalendarWidget, QSlider, QDial, QLCDNumber
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QDateTime, QDate, QMutex
)
from PyQt6.QtGui import QFont, QColor, QPalette

# Import plotting libraries
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

from database import get_db_session
from models import (
    User, ProductionTask, TaskStatusEnum, PriorityEnum, SensorData, SensorDataType,
    QualityCheck, get_production_tasks, get_recent_sensor_data, get_quality_checks
)

logger = logging.getLogger(__name__)


class SensorSimulator(QThread):
    """
    Background thread for simulating sensor data generation.
    
    This simulator generates realistic sensor readings for demonstration
    purposes, including normal operating conditions and occasional anomalies.
    """
    
    data_generated = pyqtSignal(dict)  # Signal emitted when new data is generated
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.mutex = QMutex()
        
        # Sensor configurations
        self.sensors = {
            "Temperature_Sensor_1": {
                "type": SensorDataType.TEMPERATURE,
                "unit": "°C",
                "min_normal": 18.0,
                "max_normal": 25.0,
                "min_threshold": 15.0,
                "max_threshold": 30.0,
                "equipment": "HVAC_System_A",
                "location": "Production Floor A"
            },
            "Pressure_Sensor_1": {
                "type": SensorDataType.PRESSURE,
                "unit": "PSI",
                "min_normal": 80.0,
                "max_normal": 120.0,
                "min_threshold": 70.0,
                "max_threshold": 140.0,
                "equipment": "Hydraulic_Press_1",
                "location": "Manufacturing Cell 1"
            },
            "Vibration_Monitor_1": {
                "type": SensorDataType.VIBRATION,
                "unit": "mm/s",
                "min_normal": 0.5,
                "max_normal": 2.0,
                "min_threshold": 0.0,
                "max_threshold": 5.0,
                "equipment": "CNC_Machine_1",
                "location": "Machining Center"
            },
            "Motor_Speed_1": {
                "type": SensorDataType.SPEED,
                "unit": "RPM",
                "min_normal": 1450.0,
                "max_normal": 1550.0,
                "min_threshold": 1400.0,
                "max_threshold": 1600.0,
                "equipment": "Conveyor_Motor_1",
                "location": "Assembly Line"
            },
            "Power_Monitor_1": {
                "type": SensorDataType.POWER,
                "unit": "kW",
                "min_normal": 15.0,
                "max_normal": 25.0,
                "min_threshold": 10.0,
                "max_threshold": 35.0,
                "equipment": "Main_Production_Line",
                "location": "Power Panel A"
            }
        }
        
    def start_simulation(self):
        """Start the sensor simulation."""
        self.mutex.lock()
        self.running = True
        self.mutex.unlock()
        self.start()
        
    def stop_simulation(self):
        """Stop the sensor simulation."""
        self.mutex.lock()
        self.running = False
        self.mutex.unlock()
        self.wait()
        
    def run(self):
        """Main simulation loop."""
        while True:
            self.mutex.lock()
            should_continue = self.running
            self.mutex.unlock()
            
            if not should_continue:
                break
                
            # Generate data for each sensor
            for sensor_name, config in self.sensors.items():
                data = self.generate_sensor_reading(sensor_name, config)
                self.data_generated.emit(data)
                
            # Sleep for simulation interval (2 seconds)
            time.sleep(2)
            
    def generate_sensor_reading(self, sensor_name: str, config: Dict) -> Dict:
        """Generate a single sensor reading."""
        # Generate normal reading with some random variation
        normal_range = config["max_normal"] - config["min_normal"]
        base_value = config["min_normal"] + (normal_range * 0.5)  # Middle of normal range
        variation = normal_range * 0.2 * (random.random() - 0.5)  # ±10% variation
        
        value = base_value + variation
        
        # Occasionally generate anomalies (5% chance)
        is_anomaly = random.random() < 0.05
        if is_anomaly:
            if random.random() < 0.5:
                # High anomaly
                value = config["max_threshold"] * (0.8 + 0.4 * random.random())
            else:
                # Low anomaly
                value = config["min_threshold"] * (0.5 + 0.5 * random.random())
        
        # Check if value is outside thresholds
        is_anomaly = (value < config["min_threshold"] or value > config["max_threshold"])
        
        return {
            "sensor_name": sensor_name,
            "data_type": config["type"],
            "value": round(value, 2),
            "unit": config["unit"],
            "equipment_id": config["equipment"],
            "location": config["location"],
            "is_anomaly": is_anomaly,
            "threshold_min": config["min_threshold"],
            "threshold_max": config["max_threshold"],
            "recorded_at": datetime.utcnow()
        }


class ProductionSchedulingModule(QWidget):
    """
    Production scheduling and dispatching module with calendar view.
    
    Features:
    - Interactive calendar for task scheduling
    - Task creation and assignment
    - Priority management
    - Status tracking
    """
    
    def __init__(self, user: User, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()
        self.load_tasks()
        
    def setup_ui(self):
        """Set up the production scheduling UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Production Scheduling & Dispatching")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Create splitter for layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Calendar and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Task list and details
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
    def create_left_panel(self) -> QWidget:
        """Create the left panel with calendar and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Calendar widget
        calendar_group = QGroupBox("Schedule Calendar")
        calendar_layout = QVBoxLayout(calendar_group)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar)
        
        layout.addWidget(calendar_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        if self.user.role.can_modify_schedule:
            create_task_btn = QPushButton("Create New Task")
            create_task_btn.clicked.connect(self.create_task)
            actions_layout.addWidget(create_task_btn)
        
        view_today_btn = QPushButton("View Today's Tasks")
        view_today_btn.clicked.connect(self.view_today_tasks)
        actions_layout.addWidget(view_today_btn)
        
        view_week_btn = QPushButton("View This Week")
        view_week_btn.clicked.connect(self.view_week_tasks)
        actions_layout.addWidget(view_week_btn)
        
        refresh_btn = QPushButton("Refresh Tasks")
        refresh_btn.clicked.connect(self.load_tasks)
        actions_layout.addWidget(refresh_btn)
        
        layout.addWidget(actions_group)
        
        # Task statistics
        stats_group = QGroupBox("Task Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.total_tasks_label = QLabel("0")
        self.total_tasks_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        stats_layout.addWidget(QLabel("Total Tasks:"), 0, 0)
        stats_layout.addWidget(self.total_tasks_label, 0, 1)
        
        self.active_tasks_label = QLabel("0")
        self.active_tasks_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        stats_layout.addWidget(QLabel("Active:"), 1, 0)
        stats_layout.addWidget(self.active_tasks_label, 1, 1)
        
        self.completed_tasks_label = QLabel("0")
        self.completed_tasks_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        stats_layout.addWidget(QLabel("Completed:"), 2, 0)
        stats_layout.addWidget(self.completed_tasks_label, 2, 1)
        
        layout.addWidget(stats_group)
        
        return panel
        
    def create_right_panel(self) -> QWidget:
        """Create the right panel with task list."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Task filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Status Filter:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses")
        for status in TaskStatusEnum:
            self.status_filter.addItem(status.value.title())
        self.status_filter.currentTextChanged.connect(self.apply_task_filter)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addWidget(QLabel("Priority:"))
        self.priority_filter = QComboBox()
        self.priority_filter.addItem("All Priorities")
        for priority in PriorityEnum:
            self.priority_filter.addItem(priority.value.title())
        self.priority_filter.currentTextChanged.connect(self.apply_task_filter)
        filter_layout.addWidget(self.priority_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Tasks table
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(7)
        self.tasks_table.setHorizontalHeaderLabels([
            "Task Number", "Title", "Priority", "Status", 
            "Assigned To", "Planned Start", "Progress"
        ])
        
        header = self.tasks_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setSortingEnabled(True)
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.tasks_table)
        
        return panel
        
    def load_tasks(self):
        """Load production tasks from database."""
        try:
            with get_db_session() as session:
                tasks = get_production_tasks(session)
                self.all_tasks = tasks
                self.display_tasks(tasks)
                self.update_task_statistics()
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            
    def display_tasks(self, tasks: List[ProductionTask]):
        """Display tasks in the table."""
        self.tasks_table.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            # Task number
            self.tasks_table.setItem(row, 0, QTableWidgetItem(task.task_number))
            
            # Title
            self.tasks_table.setItem(row, 1, QTableWidgetItem(task.title))
            
            # Priority with color coding
            priority_item = QTableWidgetItem(task.priority.value.upper())
            if task.priority == PriorityEnum.URGENT:
                priority_item.setBackground(QColor("#ffcdd2"))
                priority_item.setForeground(QColor("#d32f2f"))
            elif task.priority == PriorityEnum.HIGH:
                priority_item.setBackground(QColor("#fff3e0"))
                priority_item.setForeground(QColor("#f57c00"))
            self.tasks_table.setItem(row, 2, priority_item)
            
            # Status with color coding
            status_item = QTableWidgetItem(task.status.value.upper())
            if task.status == TaskStatusEnum.COMPLETED:
                status_item.setBackground(QColor("#e8f5e8"))
                status_item.setForeground(QColor("#4caf50"))
            elif task.status == TaskStatusEnum.IN_PROGRESS:
                status_item.setBackground(QColor("#e3f2fd"))
                status_item.setForeground(QColor("#2196f3"))
            self.tasks_table.setItem(row, 3, status_item)
            
            # Assigned to
            assigned_to = task.assigned_to.get_full_name() if task.assigned_to else "Unassigned"
            self.tasks_table.setItem(row, 4, QTableWidgetItem(assigned_to))
            
            # Planned start
            start_date = task.planned_start.strftime("%Y-%m-%d %H:%M") if task.planned_start else "TBD"
            self.tasks_table.setItem(row, 5, QTableWidgetItem(start_date))
            
            # Progress (simplified calculation)
            progress = 100 if task.status == TaskStatusEnum.COMPLETED else \
                      50 if task.status == TaskStatusEnum.IN_PROGRESS else 0
            progress_item = QTableWidgetItem(f"{progress}%")
            self.tasks_table.setItem(row, 6, progress_item)
            
    def update_task_statistics(self):
        """Update task statistics display."""
        if not hasattr(self, 'all_tasks'):
            return
            
        total_tasks = len(self.all_tasks)
        active_tasks = len([t for t in self.all_tasks 
                           if t.status in [TaskStatusEnum.IN_PROGRESS, TaskStatusEnum.READY]])
        completed_tasks = len([t for t in self.all_tasks 
                              if t.status == TaskStatusEnum.COMPLETED])
        
        self.total_tasks_label.setText(str(total_tasks))
        self.active_tasks_label.setText(str(active_tasks))
        self.completed_tasks_label.setText(str(completed_tasks))
        
    def apply_task_filter(self):
        """Apply current filter settings to task display."""
        if not hasattr(self, 'all_tasks'):
            return
            
        filtered_tasks = self.all_tasks.copy()
        
        # Status filter
        status_text = self.status_filter.currentText()
        if status_text != "All Statuses":
            status_value = status_text.lower()
            filtered_tasks = [t for t in filtered_tasks if t.status.value == status_value]
        
        # Priority filter
        priority_text = self.priority_filter.currentText()
        if priority_text != "All Priorities":
            priority_value = priority_text.lower()
            filtered_tasks = [t for t in filtered_tasks if t.priority.value == priority_value]
        
        self.display_tasks(filtered_tasks)
        
    def on_date_selected(self):
        """Handle calendar date selection."""
        selected_date = self.calendar.selectedDate()
        # This could filter tasks for the selected date
        # For now, just show a message
        date_str = selected_date.toString("yyyy-MM-dd")
        
    def view_today_tasks(self):
        """Show today's tasks."""
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        
    def view_week_tasks(self):
        """Show this week's tasks."""
        QMessageBox.information(
            self,
            "Weekly View",
            "Weekly task view will be implemented in the next phase.\n\n"
            "This would show:\n"
            "• Tasks scheduled for the current week\n"
            "• Resource allocation overview\n"
            "• Capacity planning information"
        )
        
    def create_task(self):
        """Create a new production task."""
        QMessageBox.information(
            self,
            "Create Task",
            "Task creation will be fully implemented in the next phase.\n\n"
            "This would include:\n"
            "• Task details form\n"
            "• Resource assignment\n"
            "• Scheduling constraints\n"
            "• Priority and dependency settings"
        )


class RealTimeDataModule(QWidget):
    """
    Real-time data collection module with sensor simulation and monitoring.
    
    Features:
    - Live sensor data display
    - Anomaly detection and alerts
    - Data logging and history
    - Equipment monitoring dashboard
    """
    
    def __init__(self, user: User, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.sensor_simulator = SensorSimulator()
        self.setup_ui()
        self.start_monitoring()
        
    def setup_ui(self):
        """Set up the real-time data collection UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Real-Time Data Collection")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Create splitter for layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Live data display
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Alerts and history
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
    def create_left_panel(self) -> QWidget:
        """Create the left panel with live sensor displays."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.start_stop_btn = QPushButton("Stop Monitoring")
        self.start_stop_btn.clicked.connect(self.toggle_monitoring)
        controls_layout.addWidget(self.start_stop_btn)
        
        clear_btn = QPushButton("Clear Data")
        clear_btn.clicked.connect(self.clear_data)
        controls_layout.addWidget(clear_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Sensor dashboard
        dashboard_group = QGroupBox("Live Sensor Dashboard")
        dashboard_layout = QGridLayout(dashboard_group)
        
        # Create sensor displays
        self.sensor_displays = {}
        sensor_configs = [
            ("Temperature", "°C", QColor("#ff6b6b")),
            ("Pressure", "PSI", QColor("#4ecdc4")),
            ("Vibration", "mm/s", QColor("#45b7d1")),
            ("Motor Speed", "RPM", QColor("#f7b731")),
            ("Power", "kW", QColor("#5f27cd"))
        ]
        
        for i, (name, unit, color) in enumerate(sensor_configs):
            display = self.create_sensor_display(name, unit, color)
            self.sensor_displays[name] = display
            row, col = divmod(i, 2)
            dashboard_layout.addWidget(display, row, col)
            
        layout.addWidget(dashboard_group)
        
        return panel
        
    def create_right_panel(self) -> QWidget:
        """Create the right panel with alerts and data feed."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Anomaly alerts
        alerts_group = QGroupBox("Anomaly Alerts")
        alerts_layout = QVBoxLayout(alerts_group)
        
        self.alerts_list = QListWidget()
        self.alerts_list.setMaximumHeight(150)
        alerts_layout.addWidget(self.alerts_list)
        
        layout.addWidget(alerts_group)
        
        # Live data feed
        feed_group = QGroupBox("Live Data Feed")
        feed_layout = QVBoxLayout(feed_group)
        
        self.data_feed = QListWidget()
        feed_layout.addWidget(self.data_feed)
        
        layout.addWidget(feed_group)
        
        return panel
        
    def create_sensor_display(self, name: str, unit: str, color: QColor) -> QWidget:
        """Create a sensor display widget."""
        widget = QGroupBox(name)
        layout = QVBoxLayout(widget)
        
        # Value display
        value_label = QLabel("0.0")
        value_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"color: {color.name()};")
        layout.addWidget(value_label)
        
        # Unit label
        unit_label = QLabel(unit)
        unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(unit_label)
        
        # Status indicator
        status_label = QLabel("NORMAL")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet("background-color: #4caf50; color: white; padding: 2px; border-radius: 3px;")
        layout.addWidget(status_label)
        
        # Store references for updates
        widget.value_label = value_label
        widget.status_label = status_label
        
        return widget
        
    def start_monitoring(self):
        """Start the real-time monitoring."""
        self.sensor_simulator.data_generated.connect(self.on_sensor_data)
        self.sensor_simulator.start_simulation()
        
    def toggle_monitoring(self):
        """Toggle monitoring on/off."""
        if self.start_stop_btn.text() == "Stop Monitoring":
            self.sensor_simulator.stop_simulation()
            self.start_stop_btn.setText("Start Monitoring")
        else:
            self.sensor_simulator.start_simulation()
            self.start_stop_btn.setText("Stop Monitoring")
            
    @pyqtSlot(dict)
    def on_sensor_data(self, data: Dict):
        """Handle new sensor data."""
        try:
            # Store data in database
            with get_db_session() as session:
                sensor_data = SensorData(**data)
                session.add(sensor_data)
                session.commit()
            
            # Update display
            self.update_sensor_display(data)
            self.add_to_data_feed(data)
            
            # Check for anomalies
            if data["is_anomaly"]:
                self.add_anomaly_alert(data)
                
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
            
    def update_sensor_display(self, data: Dict):
        """Update the sensor display with new data."""
        sensor_name = data["sensor_name"].replace("_", " ").split(" ")[0]  # Extract base name
        
        if sensor_name in self.sensor_displays:
            display = self.sensor_displays[sensor_name]
            display.value_label.setText(f"{data['value']:.1f}")
            
            # Update status
            if data["is_anomaly"]:
                display.status_label.setText("ANOMALY")
                display.status_label.setStyleSheet(
                    "background-color: #f44336; color: white; padding: 2px; border-radius: 3px;"
                )
            else:
                display.status_label.setText("NORMAL")
                display.status_label.setStyleSheet(
                    "background-color: #4caf50; color: white; padding: 2px; border-radius: 3px;"
                )
                
    def add_to_data_feed(self, data: Dict):
        """Add new data to the live feed."""
        timestamp = data["recorded_at"].strftime("%H:%M:%S")
        status = "⚠️" if data["is_anomaly"] else "✓"
        
        item_text = f"{timestamp} {status} {data['sensor_name']}: {data['value']:.1f} {data['unit']}"
        
        item = QListWidgetItem(item_text)
        if data["is_anomaly"]:
            item.setForeground(QColor("#f44336"))
        
        self.data_feed.insertItem(0, item)
        
        # Keep only last 50 items
        while self.data_feed.count() > 50:
            self.data_feed.takeItem(self.data_feed.count() - 1)
            
    def add_anomaly_alert(self, data: Dict):
        """Add anomaly alert to the alerts list."""
        timestamp = data["recorded_at"].strftime("%H:%M:%S")
        alert_text = f"{timestamp} - {data['sensor_name']}: {data['value']:.1f} {data['unit']} (Threshold: {data['threshold_min']:.1f}-{data['threshold_max']:.1f})"
        
        item = QListWidgetItem(f"⚠️ {alert_text}")
        item.setForeground(QColor("#f44336"))
        
        self.alerts_list.insertItem(0, item)
        
        # Keep only last 20 alerts
        while self.alerts_list.count() > 20:
            self.alerts_list.takeItem(self.alerts_list.count() - 1)
            
    def clear_data(self):
        """Clear the data displays."""
        self.data_feed.clear()
        self.alerts_list.clear()
        
    def closeEvent(self, event):
        """Handle widget close event."""
        self.sensor_simulator.stop_simulation()
        super().closeEvent(event)


class QualityManagementModule(QWidget):
    """
    Quality management module with inspection workflows and defect tracking.
    
    Features:
    - Quality check forms
    - Defect categorization
    - Pass/Fail tracking
    - Corrective action management
    """
    
    def __init__(self, user: User, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()
        self.load_quality_data()
        
    def setup_ui(self):
        """Set up the quality management UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Quality Management")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Tab widget for different functions
        self.tab_widget = QTabWidget()
        
        # Quality checks tab
        self.checks_tab = self.create_checks_tab()
        self.tab_widget.addTab(self.checks_tab, "Quality Checks")
        
        # New check form tab
        if self.user.role.can_access_mes:
            self.new_check_tab = self.create_new_check_tab()
            self.tab_widget.addTab(self.new_check_tab, "New Inspection")
        
        # Analytics tab
        self.analytics_tab = self.create_analytics_tab()
        self.tab_widget.addTab(self.analytics_tab, "Quality Analytics")
        
        layout.addWidget(self.tab_widget)
        
    def create_checks_tab(self) -> QWidget:
        """Create the quality checks history tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_quality_data)
        controls_layout.addWidget(refresh_btn)
        
        # Result filter
        controls_layout.addWidget(QLabel("Filter by Result:"))
        self.result_filter = QComboBox()
        self.result_filter.addItems(["All Results", "Pass", "Fail", "Review"])
        self.result_filter.currentTextChanged.connect(self.apply_quality_filter)
        controls_layout.addWidget(self.result_filter)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Quality checks table
        self.quality_table = QTableWidget()
        self.quality_table.setColumnCount(7)
        self.quality_table.setHorizontalHeaderLabels([
            "Check Number", "Type", "Result", "Defects", 
            "Inspector", "Date", "Task"
        ])
        
        header = self.quality_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.quality_table.setAlternatingRowColors(True)
        self.quality_table.setSortingEnabled(True)
        
        layout.addWidget(self.quality_table)
        
        return widget
        
    def create_new_check_tab(self) -> QWidget:
        """Create the new quality check form tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Form for new quality check
        form_group = QGroupBox("Quality Inspection Form")
        form_layout = QFormLayout(form_group)
        
        # Check type
        self.check_type_combo = QComboBox()
        self.check_type_combo.addItems([
            "Visual Inspection",
            "Dimensional Check",
            "Material Testing",
            "Functional Test",
            "Safety Inspection",
            "Final Quality Check"
        ])
        form_layout.addRow("Inspection Type:", self.check_type_combo)
        
        # Task selection
        self.task_combo = QComboBox()
        self.task_combo.addItem("No Task Selected")
        form_layout.addRow("Related Task:", self.task_combo)
        
        # Result
        self.result_combo = QComboBox()
        self.result_combo.addItems(["Pass", "Fail", "Review"])
        self.result_combo.currentTextChanged.connect(self.on_result_changed)
        form_layout.addRow("Result:", self.result_combo)
        
        # Defects found
        self.defects_spin = QSpinBox()
        self.defects_spin.setRange(0, 999)
        form_layout.addRow("Defects Found:", self.defects_spin)
        
        # Defect description
        self.defect_description = QTextEdit()
        self.defect_description.setMaximumHeight(80)
        self.defect_description.setEnabled(False)
        form_layout.addRow("Defect Description:", self.defect_description)
        
        # Corrective action
        self.corrective_action = QTextEdit()
        self.corrective_action.setMaximumHeight(80)
        self.corrective_action.setEnabled(False)
        form_layout.addRow("Corrective Action:", self.corrective_action)
        
        layout.addWidget(form_group)
        
        # Submit button
        submit_btn = QPushButton("Submit Quality Check")
        submit_btn.clicked.connect(self.submit_quality_check)
        layout.addWidget(submit_btn)
        
        layout.addStretch()
        return widget
        
    def create_analytics_tab(self) -> QWidget:
        """Create the quality analytics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Quality metrics
        metrics_group = QGroupBox("Quality Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        # Pass rate
        self.pass_rate_label = QLabel("0%")
        self.pass_rate_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.pass_rate_label.setStyleSheet("color: #4caf50;")
        metrics_layout.addWidget(QLabel("Pass Rate:"), 0, 0)
        metrics_layout.addWidget(self.pass_rate_label, 0, 1)
        
        # Total checks
        self.total_checks_label = QLabel("0")
        self.total_checks_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        metrics_layout.addWidget(QLabel("Total Checks:"), 1, 0)
        metrics_layout.addWidget(self.total_checks_label, 1, 1)
        
        # Failed checks
        self.failed_checks_label = QLabel("0")
        self.failed_checks_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.failed_checks_label.setStyleSheet("color: #f44336;")
        metrics_layout.addWidget(QLabel("Failed Checks:"), 2, 0)
        metrics_layout.addWidget(self.failed_checks_label, 2, 1)
        
        layout.addWidget(metrics_group)
        
        # Recent trends (placeholder)
        trends_label = QLabel("Quality trends and charts will be available in the next phase.")
        trends_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trends_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(trends_label)
        
        layout.addStretch()
        return widget
        
    def load_quality_data(self):
        """Load quality check data."""
        try:
            with get_db_session() as session:
                checks = get_quality_checks(session)
                self.all_checks = checks
                self.display_quality_checks(checks)
                self.update_quality_metrics()
        except Exception as e:
            logger.error(f"Error loading quality data: {e}")
            
    def display_quality_checks(self, checks: List[QualityCheck]):
        """Display quality checks in the table."""
        self.quality_table.setRowCount(len(checks))
        
        for row, check in enumerate(checks):
            # Check number
            self.quality_table.setItem(row, 0, QTableWidgetItem(check.check_number))
            
            # Type
            self.quality_table.setItem(row, 1, QTableWidgetItem(check.check_type))
            
            # Result with color coding
            result_item = QTableWidgetItem(check.result.upper())
            if check.result.lower() == "pass":
                result_item.setBackground(QColor("#e8f5e8"))
                result_item.setForeground(QColor("#4caf50"))
            elif check.result.lower() == "fail":
                result_item.setBackground(QColor("#ffebee"))
                result_item.setForeground(QColor("#f44336"))
            else:  # Review
                result_item.setBackground(QColor("#fff3e0"))
                result_item.setForeground(QColor("#ff9800"))
            self.quality_table.setItem(row, 2, result_item)
            
            # Defects
            self.quality_table.setItem(row, 3, QTableWidgetItem(str(check.defects_found)))
            
            # Inspector
            inspector_name = check.inspector.get_full_name() if check.inspector else "Unknown"
            self.quality_table.setItem(row, 4, QTableWidgetItem(inspector_name))
            
            # Date
            inspection_date = check.inspection_date.strftime("%Y-%m-%d %H:%M")
            self.quality_table.setItem(row, 5, QTableWidgetItem(inspection_date))
            
            # Task
            task_number = check.task.task_number if check.task else "N/A"
            self.quality_table.setItem(row, 6, QTableWidgetItem(task_number))
            
    def update_quality_metrics(self):
        """Update quality metrics display."""
        if not hasattr(self, 'all_checks'):
            return
            
        total_checks = len(self.all_checks)
        passed_checks = len([c for c in self.all_checks if c.result.lower() == "pass"])
        failed_checks = len([c for c in self.all_checks if c.result.lower() == "fail"])
        
        pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        self.total_checks_label.setText(str(total_checks))
        self.pass_rate_label.setText(f"{pass_rate:.1f}%")
        self.failed_checks_label.setText(str(failed_checks))
        
    def apply_quality_filter(self):
        """Apply result filter to quality checks display."""
        if not hasattr(self, 'all_checks'):
            return
            
        filter_text = self.result_filter.currentText()
        if filter_text == "All Results":
            filtered_checks = self.all_checks
        else:
            filtered_checks = [c for c in self.all_checks if c.result.lower() == filter_text.lower()]
        
        self.display_quality_checks(filtered_checks)
        
    def on_result_changed(self, result: str):
        """Handle result selection change."""
        # Enable/disable defect fields based on result
        has_issues = result in ["Fail", "Review"]
        self.defect_description.setEnabled(has_issues)
        self.corrective_action.setEnabled(has_issues)
        
        if not has_issues:
            self.defects_spin.setValue(0)
            self.defect_description.clear()
            self.corrective_action.clear()
            
    def submit_quality_check(self):
        """Submit a new quality check (placeholder)."""
        check_type = self.check_type_combo.currentText()
        result = self.result_combo.currentText()
        defects = self.defects_spin.value()
        
        QMessageBox.information(
            self,
            "Quality Check Submitted",
            f"Quality check submitted successfully!\n\n"
            f"Type: {check_type}\n"
            f"Result: {result}\n"
            f"Defects Found: {defects}\n\n"
            f"In a full implementation, this would:\n"
            f"• Save the check to the database\n"
            f"• Generate check number\n"
            f"• Update production task status\n"
            f"• Trigger corrective actions if needed"
        )
        
        # Clear form
        self.defects_spin.setValue(0)
        self.defect_description.clear()
        self.corrective_action.clear()
        self.result_combo.setCurrentText("Pass")


class PerformanceAnalysisModule(QWidget):
    """
    Performance analysis module with OEE calculations and metrics.
    
    Features:
    - OEE (Overall Equipment Effectiveness) calculations
    - Throughput analysis
    - Efficiency metrics
    - Performance trending
    """
    
    def __init__(self, user: User, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()
        self.calculate_metrics()
        
    def setup_ui(self):
        """Set up the performance analysis UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Performance Analysis")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Create splitter for layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Metrics and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Charts and analysis
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
    def create_left_panel(self) -> QWidget:
        """Create the left panel with metrics and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Time period selection
        period_group = QGroupBox("Analysis Period")
        period_layout = QFormLayout(period_group)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last 24 Hours", "Last Week", "Last Month", "Custom Range"])
        self.period_combo.currentTextChanged.connect(self.calculate_metrics)
        period_layout.addRow("Time Period:", self.period_combo)
        
        layout.addWidget(period_group)
        
        # OEE Metrics
        oee_group = QGroupBox("OEE (Overall Equipment Effectiveness)")
        oee_layout = QGridLayout(oee_group)
        
        # Overall OEE
        self.oee_label = QLabel("0%")
        self.oee_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.oee_label.setStyleSheet("color: #2196f3;")
        oee_layout.addWidget(QLabel("Overall OEE:"), 0, 0)
        oee_layout.addWidget(self.oee_label, 0, 1)
        
        # Availability
        self.availability_label = QLabel("0%")
        self.availability_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        oee_layout.addWidget(QLabel("Availability:"), 1, 0)
        oee_layout.addWidget(self.availability_label, 1, 1)
        
        # Performance
        self.performance_label = QLabel("0%")
        self.performance_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        oee_layout.addWidget(QLabel("Performance:"), 2, 0)
        oee_layout.addWidget(self.performance_label, 2, 1)
        
        # Quality
        self.quality_label = QLabel("0%")
        self.quality_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        oee_layout.addWidget(QLabel("Quality:"), 3, 0)
        oee_layout.addWidget(self.quality_label, 3, 1)
        
        layout.addWidget(oee_group)
        
        # Additional metrics
        metrics_group = QGroupBox("Additional Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        self.throughput_label = QLabel("0")
        metrics_layout.addWidget(QLabel("Throughput:"), 0, 0)
        metrics_layout.addWidget(self.throughput_label, 0, 1)
        
        self.downtime_label = QLabel("0h")
        metrics_layout.addWidget(QLabel("Downtime:"), 1, 0)
        metrics_layout.addWidget(self.downtime_label, 1, 1)
        
        self.efficiency_label = QLabel("0%")
        metrics_layout.addWidget(QLabel("Efficiency:"), 2, 0)
        metrics_layout.addWidget(self.efficiency_label, 2, 1)
        
        layout.addWidget(metrics_group)
        
        # Control buttons
        controls_layout = QVBoxLayout()
        
        refresh_btn = QPushButton("Refresh Metrics")
        refresh_btn.clicked.connect(self.calculate_metrics)
        controls_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("Export Report")
        export_btn.clicked.connect(self.export_report)
        controls_layout.addWidget(export_btn)
        
        layout.addLayout(controls_layout)
        layout.addStretch()
        
        return panel
        
    def create_right_panel(self) -> QWidget:
        """Create the right panel with charts."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Chart selection
        chart_controls = QHBoxLayout()
        chart_controls.addWidget(QLabel("Chart:"))
        
        self.chart_combo = QComboBox()
        self.chart_combo.addItems([
            "OEE Trends",
            "Throughput Analysis",
            "Downtime Breakdown",
            "Quality Metrics"
        ])
        self.chart_combo.currentTextChanged.connect(self.update_chart)
        chart_controls.addWidget(self.chart_combo)
        
        chart_controls.addStretch()
        layout.addLayout(chart_controls)
        
        # Chart area (placeholder)
        self.chart_area = QLabel("Performance charts will be displayed here.\n\nCharts will include:\n• OEE trending over time\n• Equipment utilization\n• Quality rate analysis\n• Throughput metrics")
        self.chart_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_area.setStyleSheet("border: 1px solid #ccc; background-color: #f9f9f9; color: #666;")
        self.chart_area.setMinimumHeight(300)
        layout.addWidget(self.chart_area)
        
        return panel
        
    def calculate_metrics(self):
        """Calculate performance metrics (using simulated data)."""
        # Simulate performance metrics
        # In a real system, this would calculate from actual production data
        
        # Simulate OEE components
        availability = random.uniform(85, 95)  # 85-95%
        performance = random.uniform(75, 90)   # 75-90%
        quality = random.uniform(92, 98)       # 92-98%
        
        # Calculate overall OEE
        oee = (availability * performance * quality) / 10000
        
        # Update displays
        self.oee_label.setText(f"{oee:.1f}%")
        self.availability_label.setText(f"{availability:.1f}%")
        self.performance_label.setText(f"{performance:.1f}%")
        self.quality_label.setText(f"{quality:.1f}%")
        
        # Additional metrics
        throughput = random.randint(450, 550)  # units per hour
        downtime = random.uniform(0.5, 2.0)    # hours
        efficiency = random.uniform(82, 92)    # %
        
        self.throughput_label.setText(f"{throughput} units/hr")
        self.downtime_label.setText(f"{downtime:.1f}h")
        self.efficiency_label.setText(f"{efficiency:.1f}%")
        
        # Color coding for OEE
        if oee >= 85:
            color = "#4caf50"  # Green
        elif oee >= 70:
            color = "#ff9800"  # Orange
        else:
            color = "#f44336"  # Red
            
        self.oee_label.setStyleSheet(f"color: {color};")
        
    def update_chart(self, chart_name: str):
        """Update the chart display."""
        chart_info = {
            "OEE Trends": "OEE trending over the selected time period",
            "Throughput Analysis": "Production throughput and capacity utilization",
            "Downtime Breakdown": "Equipment downtime analysis by cause",
            "Quality Metrics": "Quality rates and defect trends"
        }
        
        info_text = chart_info.get(chart_name, "Chart information")
        self.chart_area.setText(f"📊 {chart_name}\n\n{info_text}\n\nInteractive charts will be available in the next phase.")
        
    def export_report(self):
        """Export performance report."""
        QMessageBox.information(
            self,
            "Export Report",
            "Performance report export will be fully implemented in the next phase.\n\n"
            "The report will include:\n"
            "• Complete OEE analysis\n"
            "• Trend charts and graphs\n"
            "• Equipment utilization data\n"
            "• Recommendations for improvement\n"
            "• Export formats: PDF, Excel, CSV"
        )