#!/usr/bin/env python3
"""
NextFactory UI Components - Common UI Elements
==============================================

This module provides common UI components for the NextFactory ERP+MES system,
including the NextFactory banner and standardized module layouts.

Components:
    - NextFactoryBanner: Common banner with branding and optional user info
    - BaseModuleWidget: Base class for consistent module styling
    - ModuleHeaderWidget: Standardized module header component

Author: NextFactory Development Team
Created: 2024
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette


class NextFactoryBanner(QWidget):
    """
    Common NextFactory banner component for consistent branding across modules.
    
    Features:
    - Professional NextFactory branding
    - Responsive layout
    - Subtle visual styling with drop shadow
    - Optional user information display
    """
    
    def __init__(self, show_user_info: bool = False, user_info: str = "", parent: Optional[QWidget] = None):
        """
        Initialize the NextFactory banner.
        
        Args:
            show_user_info (bool): Whether to display user information
            user_info (str): User information to display
            parent (Optional[QWidget]): Parent widget
        """
        super().__init__(parent)
        self.show_user_info = show_user_info
        self.user_info = user_info
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the banner UI with professional styling."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        
        # NextFactory logo/title
        title_label = QLabel("NextFactory")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Set professional color scheme
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 5px 10px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ecf0f1, stop: 1 #d5dbdb);
                border: 1px solid #bdc3c7;
                border-radius: 6px;
            }
        """)
        
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Enterprise Resource Planning & Manufacturing Execution System")
        subtitle_font = QFont("Arial", 10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-left: 10px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(subtitle_label)
        
        # Stretch to push user info to the right
        layout.addStretch()
        
        # User information (optional)
        if self.show_user_info and self.user_info:
            user_label = QLabel(self.user_info)
            user_font = QFont("Arial", 9)
            user_label.setFont(user_font)
            user_label.setStyleSheet("""
                QLabel {
                    color: #34495e;
                    background: #ecf0f1;
                    padding: 3px 8px;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                }
            """)
            user_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(user_label)
        
        # Set banner background and styling
        self.setStyleSheet("""
            NextFactoryBanner {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-bottom: 2px solid #e9ecef;
            }
        """)
        
        # Set fixed height for consistent appearance
        self.setFixedHeight(50)


class ModuleHeaderWidget(QWidget):
    """
    Standardized module header component with consistent styling.
    
    Provides a professional module title with consistent spacing and alignment.
    """
    
    def __init__(self, module_name: str, parent: Optional[QWidget] = None):
        """
        Initialize the module header.
        
        Args:
            module_name (str): Name of the module to display
            parent (Optional[QWidget]): Parent widget
        """
        super().__init__(parent)
        self.module_name = module_name
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the module header UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)
        
        # Module title
        title_label = QLabel(self.module_name)
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Professional styling for module title
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 8px;
                margin-bottom: 5px;
            }
        """)
        
        layout.addWidget(title_label)
        
        # Subtle separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("""
            QFrame {
                color: #bdc3c7;
                background-color: #bdc3c7;
                height: 1px;
                margin: 0px 20px;
            }
        """)
        layout.addWidget(separator)
        
        # Add some bottom spacing
        layout.addSpacing(10)


class BaseModuleWidget(QWidget):
    """
    Base widget class for all NextFactory modules providing consistent layout and styling.
    
    Features:
    - NextFactory banner at the top
    - Standardized module header
    - Professional styling and spacing
    - Responsive layout
    """
    
    def __init__(self, module_name: str, user=None, show_user_info: bool = True, parent: Optional[QWidget] = None):
        """
        Initialize the base module widget.
        
        Args:
            module_name (str): Name of the module
            user: Current user object (optional)
            show_user_info (bool): Whether to show user info in banner
            parent (Optional[QWidget]): Parent widget
        """
        super().__init__(parent)
        self.module_name = module_name
        self.user = user
        self.show_user_info = show_user_info
        self.content_widget = None
        self.setup_base_ui()
        
    def setup_base_ui(self):
        """Set up the base UI structure with banner and header."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # NextFactory banner
        user_info = ""
        if self.show_user_info and self.user:
            try:
                user_info = f"{self.user.get_full_name()} ({self.user.role.display_name})"
            except:
                user_info = f"{self.user.username}"
        
        self.banner = NextFactoryBanner(
            show_user_info=self.show_user_info,
            user_info=user_info
        )
        self.main_layout.addWidget(self.banner)
        
        # Module header
        self.header = ModuleHeaderWidget(self.module_name)
        self.main_layout.addWidget(self.header)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 0, 10, 10)
        self.main_layout.addWidget(self.content_widget)
        
        # Set background styling
        self.setStyleSheet("""
            BaseModuleWidget {
                background-color: #ffffff;
            }
        """)
        
    def get_content_layout(self) -> QVBoxLayout:
        """
        Get the content layout for adding module-specific widgets.
        
        Returns:
            QVBoxLayout: The content layout where modules should add their widgets
        """
        return self.content_layout
        
    def set_content_widget(self, widget: QWidget):
        """
        Set a custom content widget for the module.
        
        Args:
            widget (QWidget): The widget to set as module content
        """
        # Remove existing content widget
        if self.content_widget:
            self.main_layout.removeWidget(self.content_widget)
            self.content_widget.deleteLater()
        
        # Add new content widget
        self.content_widget = widget
        self.main_layout.addWidget(self.content_widget)