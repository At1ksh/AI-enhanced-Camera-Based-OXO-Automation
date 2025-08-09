import sys
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, 
    QFrame, QTextEdit, QSplitter
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer
from functools import partial

class SidebarButton(QPushButton):
    def __init__(self, title, icon, is_dark_mode=True, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.setMinimumHeight(80)
        self.setMaximumHeight(80)
        
        # Set up the button style based on theme
        if is_dark_mode:
            self.setStyleSheet("""
                QPushButton {
                    background: #404040;
                    border: 1px solid #555555;
                    border-radius: 8px;
                    color: #ffffff;
                    font-weight: 500;
                    font-size: 14px;
                    text-align: left;
                    padding: 12px 15px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background: #505050;
                    border: 1px solid #666666;
                }
                QPushButton:pressed {
                    background: #353535;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    color: #333333;
                    font-weight: 500;
                    font-size: 14px;
                    text-align: left;
                    padding: 12px 15px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background: #f0f0f0;
                    border: 1px solid #cccccc;
                }
                QPushButton:pressed {
                    background: #e8e8e8;
                }
            """)
        
        # Set button text
        self.setText(f"{icon}  {title}")

class ContentArea(QFrame):
    def __init__(self, is_dark_mode=True, parent=None):
        super().__init__(parent)
        self.is_dark_mode = is_dark_mode
        
        # Remove borders - clean background only
        if is_dark_mode:
            self.setStyleSheet("""
                QFrame {
                    background: #1e1e1e;
                    border: none;
                    margin: 0px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: #ffffff;
                    border: none;
                    margin: 0px;
                }
            """)
        
        # Main layout for content area
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(30)
        
        # Show default content (logo)
        self.show_default_content()
    
    def show_default_content(self):
        # Clear existing content
        self.clear_content()
        
        # Try to load and display the main logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Try to load the logo image
        logo_path = "OXO VISION ENGINE.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale the image to fit nicely - larger size
            scaled_pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            # Fallback if image not found
            logo_label.setText("OXO VISION ENGINE")
            if self.is_dark_mode:
                logo_label.setStyleSheet("""
                    QLabel {
                        font-size: 36px;
                        font-weight: bold;
                        color: #ffffff;
                        margin: 80px;
                        background: transparent;
                        border: none;
                    }
                """)
            else:
                logo_label.setStyleSheet("""
                    QLabel {
                        font-size: 36px;
                        font-weight: bold;
                        color: #333333;
                        margin: 80px;
                        background: transparent;
                        border: none;
                    }
                """)
        
        self.layout.addStretch()
        self.layout.addWidget(logo_label)
        self.layout.addStretch()
    
    def show_tool_info(self, tool_name, description, logo_path, script_path):
        # Clear existing content
        self.clear_content()
        
        # Tool logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale the image to be much larger for app screenshots
            scaled_pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            # Fallback text logo - no borders
            logo_label.setText(tool_name)
            if self.is_dark_mode:
                logo_label.setStyleSheet("""
                    QLabel {
                        font-size: 28px;
                        font-weight: bold;
                        color: #ffffff;
                        margin: 30px;
                        background: transparent;
                        border: none;
                        padding: 60px;
                    }
                """)
            else:
                logo_label.setStyleSheet("""
                    QLabel {
                        font-size: 28px;
                        font-weight: bold;
                        color: #333333;
                        margin: 30px;
                        background: transparent;
                        border: none;
                        padding: 60px;
                    }
                """)
        
        # Tool title - no borders
        title_label = QLabel(tool_name)
        title_label.setAlignment(Qt.AlignCenter)
        if self.is_dark_mode:
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #ffffff;
                    margin: 15px 10px 5px 10px;
                    background: transparent;
                    border: none;
                }
            """)
        else:
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #000000;
                    margin: 15px 10px 5px 10px;
                    background: transparent;
                    border: none;
                }
            """)
        
        # Tool description - no borders
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        if self.is_dark_mode:
            desc_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #cccccc;
                    margin: 5px 20px 20px 20px;
                    line-height: 1.4;
                    background: transparent;
                    border: none;
                }
            """)
        else:
            desc_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #666666;
                    margin: 5px 20px 20px 20px;
                    line-height: 1.4;
                    background: transparent;
                    border: none;
                }
            """)
        
        # Start button
        start_btn = QPushButton("START APPLICATION")
        start_btn.setFixedSize(220, 55)
        if self.is_dark_mode:
            start_btn.setStyleSheet("""
                QPushButton {
                    background: #ffffff;
                    color: #000000;
                    border: none;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #f0f0f0;
                }
                QPushButton:pressed {
                    background: #e0e0e0;
                }
            """)
        else:
            start_btn.setStyleSheet("""
                QPushButton {
                    background: #000000;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #333333;
                }
                QPushButton:pressed {
                    background: #555555;
                }
            """)
        start_btn.clicked.connect(partial(self.launch_tool, script_path))
        
        # Add all elements to layout
        self.layout.addStretch()
        self.layout.addWidget(logo_label)
        self.layout.addWidget(title_label)
        self.layout.addWidget(desc_label)
        self.layout.addStretch()
        
        # Center the start button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(start_btn)
        button_layout.addStretch()
        
        self.layout.addLayout(button_layout)
        self.layout.addStretch()
    
    def clear_content(self):
        # Remove all widgets from layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def launch_tool(self, script_path):
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            full_path = os.path.join(base_path, script_path)

            if not os.path.exists(full_path):
                print(f"[ERROR] Script not found: {full_path}")
                return

            subprocess.Popen(["python", full_path])
        except Exception as e:
            print(f"Failed to launch {script_path}: {e}")


class MainLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OXO Vision Engine")
        
        # Set window icon
        if os.path.exists("logo.png"):
            self.setWindowIcon(QIcon("logo.png"))
        elif os.path.exists("OXO VISION ENGINE.png"):
            self.setWindowIcon(QIcon("OXO VISION ENGINE.png"))
        
        # Make it fullscreen
        self.showFullScreen()
        
        # Start with dark mode - MUST be set before init_ui()
        self.is_dark_mode = True
        
        # Set up the new UI
        self.init_ui()
        
        # Apply theme
        self.apply_theme()
        
    def apply_theme(self):
        if self.is_dark_mode:
            # Dark mode styling
            self.setStyleSheet("""
                QWidget {
                    background: #1e1e1e;
                    color: #ffffff;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                }
            """)
        else:
            # Light mode styling
            self.setStyleSheet("""
                QWidget {
                    background: #ffffff;
                    color: #000000;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                }
            """)
        
        # Update all child widgets
        self.update_all_styles()
    
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
    
    def update_all_styles(self):
        # This will be called after theme change to update all styles
        # Clear the existing layout properly
        if self.layout():
            QWidget().setLayout(self.layout())
        
        # Recreate the UI with new theme
        self.init_ui()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Compact header with title
        header = QLabel("OXO Vision Engine")
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(60)
        
        if self.is_dark_mode:
            header.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #ffffff;
                    background: #2d2d2d;
                    border-bottom: 2px solid #404040;
                    padding: 15px;
                }
            """)
        else:
            header.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #000000;
                    background: #f5f5f5;
                    border-bottom: 2px solid #e0e0e0;
                    padding: 15px;
                }
            """)
        
        # Create horizontal splitter for sidebar and content
        splitter = QSplitter(Qt.Horizontal)
        if self.is_dark_mode:
            splitter.setStyleSheet("""
                QSplitter::handle {
                    background: #404040;
                    width: 1px;
                }
            """)
        else:
            splitter.setStyleSheet("""
                QSplitter::handle {
                    background: #e0e0e0;
                    width: 1px;
                }
            """)
        
        # Left sidebar with buttons
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        if self.is_dark_mode:
            sidebar.setStyleSheet("""
                QFrame {
                    background: #2d2d2d;
                    border-right: 1px solid #404040;
                }
            """)
        else:
            sidebar.setStyleSheet("""
                QFrame {
                    background: #f8f8f8;
                    border-right: 1px solid #e0e0e0;
                }
            """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)
        
        # Sidebar title
        sidebar_title = QLabel("Applications")
        if self.is_dark_mode:
            sidebar_title.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #ffffff;
                    margin-bottom: 15px;
                    padding: 10px 0;
                }
            """)
        else:
            sidebar_title.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #333333;
                    margin-bottom: 15px;
                    padding: 10px 0;
                }
            """)
        sidebar_layout.addWidget(sidebar_title)
        
        # Button configurations with app screenshots
        tools_config = [
            ("OXO Vision Studio", "🎨", "Annotation Tool - Advanced image annotation and labeling for computer vision projects", "1.png", "annotation_tool/app.py"),
            ("OXO Vision Builder", "🚀", "YOLO Training - Automated YOLO model training and optimization platform", "2.png", "yolo_builder/app.py"),
            ("OXO KSpec Manager", "📊", "Specification Management - Comprehensive configuration management system", "3.png", "kspec_uploader/app.py"),
            ("OXO VIN Config", "🔧", "Data Management - Vehicle identification and people data management tool", "4.png", "vin_config/app.py"),
        ]
        
        # Create content area
        self.content_area = ContentArea(self.is_dark_mode)
        
        # Create sidebar buttons
        for title, icon, description, logo_path, script_path in tools_config:
            btn = SidebarButton(title, icon, self.is_dark_mode)
            btn.clicked.connect(partial(self.content_area.show_tool_info, title, description, logo_path, script_path))
            sidebar_layout.addWidget(btn)
        
        # Add stretch to push buttons to top
        sidebar_layout.addStretch()
        
        # Light/Dark mode toggle button
        theme_btn = QPushButton("🌞" if self.is_dark_mode else "🌙")
        theme_btn.setFixedSize(45, 45)
        if self.is_dark_mode:
            theme_btn.setStyleSheet("""
                QPushButton {
                    background: #404040;
                    border: 2px solid #666666;
                    border-radius: 8px;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 16px;
                    margin-bottom: 10px;
                }
                QPushButton:hover {
                    background: #555555;
                }
            """)
        else:
            theme_btn.setStyleSheet("""
                QPushButton {
                    background: #ffffff;
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    color: #333333;
                    font-weight: bold;
                    font-size: 16px;
                    margin-bottom: 10px;
                }
                QPushButton:hover {
                    background: #f0f0f0;
                }
            """)
        theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(theme_btn)
        
        # Exit button at bottom of sidebar
        exit_btn = QPushButton("✕ Exit")
        if self.is_dark_mode:
            exit_btn.setStyleSheet("""
                QPushButton {
                    background: #2d2d2d;
                    border: 2px solid #ff4444;
                    border-radius: 8px;
                    color: #ff4444;
                    font-weight: bold;
                    padding: 12px;
                }
                QPushButton:hover {
                    background: #ff4444;
                    color: white;
                }
            """)
        else:
            exit_btn.setStyleSheet("""
                QPushButton {
                    background: #ffffff;
                    border: 2px solid #ff4444;
                    border-radius: 8px;
                    color: #ff4444;
                    font-weight: bold;
                    padding: 12px;
                }
                QPushButton:hover {
                    background: #ff4444;
                    color: white;
                }
            """)
        exit_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(exit_btn)
        
        # Add sidebar and content area to splitter
        splitter.addWidget(sidebar)
        splitter.addWidget(self.content_area)
        
        # Set splitter proportions (sidebar smaller, content area larger)
        splitter.setSizes([300, 900])
        
        # Add everything to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)

    def keyPressEvent(self, event):
        # Allow ESC key to exit fullscreen
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application icon (for taskbar, etc.)
    if os.path.exists("logo.png"):
        app.setWindowIcon(QIcon("logo.png"))
    elif os.path.exists("OXO VISION ENGINE.png"):
        app.setWindowIcon(QIcon("OXO VISION ENGINE.png"))
    
    launcher = MainLauncher()
    launcher.show()
    sys.exit(app.exec_())