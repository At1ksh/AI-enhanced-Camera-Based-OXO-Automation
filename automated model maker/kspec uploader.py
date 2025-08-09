import sys
import os
import torch
from ultralytics import YOLO
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QFileDialog, QMessageBox, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QComboBox, QCheckBox, QGridLayout, QInputDialog,
    QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt
import json
import requests

# Modern styling constants
MODERN_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #1e3c72, stop:1 #2a5298);
    color: white;
}

QWidget {
    background-color: transparent;
    color: white;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4facfe, stop:1 #00f2fe);
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: bold;
    color: white;
    min-height: 20px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #6bb4ff, stop:1 #1affff);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3d8bfe, stop:1 #00d5fe);
}

QLineEdit {
    background-color: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    padding: 10px 15px;
    font-size: 14px;
    color: white;
    min-height: 20px;
}

QLineEdit:focus {
    border: 2px solid #4facfe;
    background-color: rgba(255, 255, 255, 0.15);
}

QLineEdit::placeholder {
    color: rgba(255, 255, 255, 0.6);
}

QLabel {
    color: white;
    font-size: 14px;
    padding: 5px;
}

QComboBox {
    background-color: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    padding: 8px 15px;
    font-size: 14px;
    color: white;
    min-height: 20px;
}

QComboBox:hover {
    border: 2px solid #4facfe;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 8px solid white;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: rgba(30, 60, 114, 0.95);
    border: 1px solid #4facfe;
    border-radius: 8px;
    color: white;
    selection-background-color: #4facfe;
}

QCheckBox {
    color: white;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    background-color: rgba(255, 255, 255, 0.1);
}

QCheckBox::indicator:checked {
    background-color: #4facfe;
    border: 2px solid #4facfe;
}

QScrollArea {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
}

QScrollBar:vertical {
    background-color: rgba(255, 255, 255, 0.1);
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #4facfe;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6bb4ff;
}

QMessageBox {
    background-color: #1e3c72;
    color: white;
}

QMessageBox QPushButton {
    min-width: 80px;
    margin: 5px;
}

QFrame {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 10px;
}
"""

class KSpecUploader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚗 KSpec Uploader - Modern Dashboard")
        self.show()  # Always start in windowed mode
        self.setWindowIcon(QIcon("logo.png"))
        
        # Apply modern styling
        self.setStyleSheet(MODERN_STYLE)
        
        self.model_code=""
        self.model_name=""
        self.variant_name=""
        self.total_interior=0
        self.total_exterior=0
        self.total_loose=0
        self.main_image_path=""
        self.interior_components=[]
        self.exterior_components=[]
        self.loose_components=[]
        self.backend_ip = "http://192.168.0.100:8000" 
        
        self.init_home_ui()
        
    def init_home_ui(self):
        # Create main container with modern layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Title section with modern styling
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(79, 172, 254, 0.3), stop:1 rgba(0, 242, 254, 0.3));
                border-radius: 20px;
                padding: 30px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("🚗 KSpec Uploader")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 48px; 
            font-weight: bold; 
            color: white;
            margin: 20px;
        """)
        
        subtitle_label = QLabel("Modern Vehicle Specification Management System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 18px; 
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 20px;
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Buttons section with modern cards
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(40)
        
        # Test Backend Button
        btn_test = QPushButton("🔌 Test Backend Connectivity")
        btn_test.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ff6b6b, stop:1 #ee5a24);
                font-size: 16px;
                padding: 20px 30px;
                border-radius: 15px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ff7675, stop:1 #fd79a8);
            }
        """)
        btn_test.clicked.connect(self.test_backend)
        
        # Upload KSpec Button
        btn_upload = QPushButton("📝 Upload New KSpec")
        btn_upload.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #00b894, stop:1 #00cec9);
                font-size: 16px;
                padding: 20px 30px;
                border-radius: 15px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #55efc4, stop:1 #81ecec);
            }
        """)
        btn_upload.clicked.connect(self.open_basic_metadata_page)
        
        # Reference Upload Button
        btn_ref_upload = QPushButton("🧬 Upload New KSpec From Existing")
        btn_ref_upload.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #a29bfe, stop:1 #6c5ce7);
                font-size: 16px;
                padding: 20px 30px;
                border-radius: 15px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #b2a9fe, stop:1 #7c6ce7);
            }
        """)
        btn_ref_upload.clicked.connect(self.upload_from_existing)
        buttons_layout.addWidget(btn_ref_upload)
        
        btn_view_kspecs = QPushButton("📂 View Existing KSpecs")
        btn_view_kspecs.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #74b9ff, stop:1 #0984e3);
                font-size: 16px;
                padding: 20px 30px;
                border-radius: 15px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #81c3ff, stop:1 #2d96ff);
            }
        """)
        btn_view_kspecs.clicked.connect(self.view_existing_kspecs)
        
        # Remove KSpec
        btn_remove_kspec = QPushButton("🗑️ Remove Existing KSpec")
        btn_remove_kspec.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ff6b6b, stop:1 #ee5a24);
                font-size: 16px;
                padding: 20px 30px;
                border-radius: 15px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ff7675, stop:1 #fd79a8);
            }
        """)
        btn_remove_kspec.clicked.connect(self.remove_existing_kspec)

        # Backend IP field
        ip_layout = QHBoxLayout()
        ip_label = QLabel("🔗 Backend IP:")
        ip_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.ip_input = QLineEdit()
        self.ip_input.setText(self.backend_ip)
        self.ip_input.setPlaceholderText("e.g., http://192.168.0.100:8000")
        self.ip_input.setMinimumWidth(300)
        self.ip_input.textChanged.connect(lambda val: setattr(self, "backend_ip", val.strip()))

        ip_layout.addStretch()
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(self.ip_input)
        ip_layout.addStretch()

        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_test)
        buttons_layout.addWidget(btn_upload)
        buttons_layout.addWidget(btn_view_kspecs)
        buttons_layout.addWidget(btn_remove_kspec)
        buttons_layout.addStretch()
        
        # Add everything to main layout
        main_layout.addWidget(title_frame)
        main_layout.addStretch()
        main_layout.addWidget(buttons_frame)
        main_layout.addStretch()
        main_layout.addLayout(ip_layout)
        
        self.setCentralWidget(main_widget)
    def upload_from_existing(self):
        try:
            backend_url = f"{self.backend_ip.rstrip('/')}/kspecs"
            response = requests.get(backend_url)

            if response.status_code == 200:
                kspecs = response.json()
                kspec_options = [f"{k['modelCode']} - {k['variantName']}" for k in kspecs]
                selection, ok = QInputDialog.getItem(
                    self, "Select Existing KSpec", "Choose a KSpec to base the new one on:", kspec_options, 0, False
                )
                if ok and selection:
                    selected_code = selection.split(" - ")[0]
                    self.load_kspec_for_cloning(selected_code)
            else:
                QMessageBox.critical(self, "Error", f"Failed to fetch KSpecs:\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed:\n{str(e)}")
    
    def load_kspec_for_cloning(self, model_code):
        try:
            backend_url = f"{self.backend_ip.rstrip('/')}/kspec/{model_code}"
            response = requests.get(backend_url)

            if response.status_code == 200:
                kspec_data = response.json()

                # Clear modelCode for user to rename
                kspec_data["modelCode"] = ""

                # ✅ Store original paths without modification for now
                # The backend will handle path changes when a new model code is provided
                # We DON'T need to replace paths here because:
                # 1. The user will provide a new model code in FinalReviewPage
                # 2. The backend will copy files and update paths automatically
                
                # Just pass the data as-is to FinalReviewPage
                self.review_page = FinalReviewPage(self, kspec_data)
                self.review_page.show()

            else:
                QMessageBox.critical(self, "Error", f"Failed to load KSpec:\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed:\n{str(e)}")

  
    def finalize_all(self):
        all_components = []
        all_components += getattr(self, "interior_components", [])
        all_components += getattr(self, "exterior_components", [])
        all_components += getattr(self, "loose_components", [])

        # Collect all subcomponents from components
        all_subcomponents = []
        for component in all_components:
            if "subComponents" in component:
                all_subcomponents.extend(component["subComponents"])

        final_kspec = {
            "modelCode": self.model_code,
            "modelName": self.model_name,
            "variantName": self.variant_name,
            "totalInterior": self.total_interior,
            "totalExterior": self.total_exterior,
            "totalLoose": self.total_loose,
            "mainImagePath": self.main_image_path,
            "components": all_components,
            "subComponents": all_subcomponents
        }

        # ✅ Instead of just saving, show final review page
        self.review_page = FinalReviewPage(self, final_kspec)
        self.review_page.show()

    def test_backend(self):
        try:
            url = f"{self.backend_ip}/health"
            response = requests.get(url, timeout=5)
            if response.status_code == 200 and response.json().get("status") == "ok":
                QMessageBox.information(self, "Backend Connected ✅", f"Successfully connected to backend at:\n{self.backend_ip}")
            else:
                QMessageBox.critical(self, "Backend Error", f"Received error from backend:\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed ❌", f"Failed to connect to backend at {self.backend_ip}\n\nError: {str(e)}")

        
    def open_basic_metadata_page(self):
        self.step1=BasicMetadataPage(self)
        self.step1.show()
        self.hide()
        
    def view_existing_kspecs(self):
        self.close()
        self.viewer = ViewKSpecsPage(main_app=self)
        self.viewer.showMaximized()


    def remove_existing_kspec(self):
        self.close()
        self.remover = ConfirmAndRemovePage(main_app=self)
        self.remover.showMaximized()


class ViewKSpecsPage(QWidget):
    def __init__(self,main_app):
        super().__init__()
        self.main_app = main_app 
        self.setWindowTitle("📂 Active KSpecs")
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet(MODERN_STYLE)

        layout = QVBoxLayout()
        title = QLabel("📂 Existing KSpecs")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        self.kspec_area = QScrollArea()
        self.kspec_area.setWidgetResizable(True)
        self.kspec_area.setStyleSheet("margin-top: 20px;")

        layout.addWidget(title)
        layout.addWidget(self.kspec_area)
        self.setLayout(layout)
        back_btn = QPushButton("🔙 Return to Main Page")
        back_btn.setStyleSheet("font-size: 18px; padding: 12px; background-color: #2d3436; color: white; border-radius: 8px;")
        back_btn.clicked.connect(self.return_to_main)

        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        self.load_kspecs()
    def return_to_main(self):
        self.close()
        self.main_app.init_home_ui()
        self.main_app.show()

    def load_kspecs(self):
        try:
            backend_url = f"{self.main_app.backend_ip.rstrip('/')}/kspecs"
            response = requests.get(backend_url)
            if response.status_code == 200:
                kspecs = response.json()
                widget = QWidget()
                vbox = QVBoxLayout(widget)
                for kspec in kspecs:
                    label = QLabel(f"📌 {kspec['modelCode']} - {kspec['variantName']}")
                    label.setStyleSheet("font-size: 16px; padding: 8px; color: white; background-color: rgba(255,255,255,0.1); border-radius: 6px;")
                    vbox.addWidget(label)
                self.kspec_area.setWidget(widget)
            else:
                QMessageBox.critical(self, "Error", f"Failed to load KSpecs:\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect:\n{str(e)}")

            
class ConfirmAndRemovePage(QWidget):
    def __init__(self, main_app=None):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle("🗑️ Remove a KSpec")
        self.setGeometry(200, 200, 600, 300)
        self.setStyleSheet(MODERN_STYLE)

        layout = QVBoxLayout()

        label = QLabel("Select a KSpec to remove")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.combo = QComboBox()
        layout.addWidget(label)
        layout.addWidget(self.combo)

        self.btn_remove = QPushButton("🗑️ Remove Selected")
        self.btn_remove.clicked.connect(self.remove_selected)
        layout.addWidget(self.btn_remove)
        
        
        back_btn = QPushButton("🔙 Return to Main Page")
        back_btn.setStyleSheet("font-size: 18px; padding: 12px; background-color: #2d3436; color: white; border-radius: 8px;")
        back_btn.clicked.connect(self.return_to_main)

        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.load_kspecs()
    def return_to_main(self):
        self.close()
        self.main_app.init_home_ui()
        self.main_app.show()

    def load_kspecs(self):
        try:
            backend_url = f"{self.main_app.backend_ip.rstrip('/')}/kspecs"
            response = requests.get(backend_url)
            if response.status_code == 200:
                kspecs = response.json()
                self.kspec_list = kspecs
                self.combo.addItems([f"{k['modelCode']} - {k['variantName']}" for k in kspecs])
            else:
                QMessageBox.critical(self, "Error", f"Failed to load:\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def remove_selected(self):
        index = self.combo.currentIndex()
        if index < 0:
            return
        model_code = self.kspec_list[index]['modelCode']

        confirm = QMessageBox.question(self, "Confirm Deletion", f"Remove {model_code} permanently?",
                                    QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                backend_url = f"{self.main_app.backend_ip.rstrip('/')}/kspec/{model_code}"
                response = requests.delete(backend_url)
                if response.status_code == 200:
                    QMessageBox.information(self, "Removed", f"KSpec {model_code} successfully removed.")
                    self.refresh_kspec_list()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to delete:\n{response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def refresh_kspec_list(self):
        self.combo.clear()
        try:
            backend_url = f"{self.main_app.backend_ip.rstrip('/')}/kspecs"
            response = requests.get(backend_url)
            if response.status_code == 200:
                kspecs = response.json()
                self.kspec_list = kspecs
                self.combo.addItems([f"{k['modelCode']} - {k['variantName']}" for k in kspecs])
            else:
                QMessageBox.critical(self, "Error", f"Failed to reload KSpecs:\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect:\n{str(e)}")

class BasicMetadataPage(QWidget):
    def __init__(self,parent_window):
        super().__init__()
        self.parent_window=parent_window
        self.setWindowTitle("📋 Basic KSpec Metadata")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(MODERN_STYLE)
        
        # Main container
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(60, 40, 60, 40)
        
        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(79, 172, 254, 0.3), stop:1 rgba(0, 242, 254, 0.3));
                border-radius: 15px;
                padding: 25px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("📋 Step 1: Basic Vehicle Details")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 36px; font-weight: bold; color: white; margin: 10px;")
        
        subtitle_label = QLabel("Enter the fundamental information about your vehicle specification")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 16px; color: rgba(255, 255, 255, 0.8); margin-bottom: 10px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        # Form container
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 15px;
                padding: 30px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        
        # Input fields with modern styling
        self.model_code_input = QLineEdit()
        self.model_name_input = QLineEdit()
        self.variant_name_input = QLineEdit()
        self.total_interior_input = QLineEdit()
        self.total_exterior_input = QLineEdit()
        self.total_loose_input = QLineEdit()
        
        self.model_code_input.setPlaceholderText("🔢 Enter Model Code (e.g., KB118)")
        self.model_name_input.setPlaceholderText("🚗 Enter Model Name (e.g., Range Rover Autobiography)")
        self.variant_name_input.setPlaceholderText("⚙️ Enter Variant Name (e.g., 300P)")
        self.total_interior_input.setPlaceholderText("🏠 Enter Total Interior Parts")
        self.total_exterior_input.setPlaceholderText("🌍 Enter Total Exterior Parts")
        self.total_loose_input.setPlaceholderText("🔧 Enter Total Loose Parts")
        
        # Create form rows
        fields = [
            ("📋 Model Code:", self.model_code_input),
            ("🚗 Model Name:", self.model_name_input),
            ("⚙️ Variant Name:", self.variant_name_input),
            ("🏠 Total Interior Parts:", self.total_interior_input),
            ("🌍 Total Exterior Parts:", self.total_exterior_input),
            ("🔧 Total Loose Parts:", self.total_loose_input)
        ]
        
        for label_text, input_field in fields:
            field_layout = QVBoxLayout()
            field_layout.setSpacing(8)
            
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-left: 5px;")
            
            field_layout.addWidget(label)
            field_layout.addWidget(input_field)
            form_layout.addLayout(field_layout)
        
        # Image selection section
        self.main_image_path = ""
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px dashed rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        image_layout = QVBoxLayout(image_frame)
        
        image_label = QLabel("📷 Main Car Image")
        image_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-bottom: 10px;")
        
        btn_select_image = QPushButton("📁 Select Main Car Image")
        btn_select_image.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ffecd2, stop:1 #fcb69f);
                color: #333;
                font-size: 15px;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ffedcc, stop:1 #fdbb9c);
            }
        """)
        btn_select_image.clicked.connect(self.select_main_image)
        
        image_layout.addWidget(image_label)
        image_layout.addWidget(btn_select_image)
        
        # Proceed button
        btn_save = QPushButton("🚀 Proceed to Components")
        btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #667eea, stop:1 #764ba2);
                font-size: 18px;
                padding: 18px 35px;
                border-radius: 12px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #7c88ea, stop:1 #8a5cb2);
            }
        """)
        btn_save.clicked.connect(self.save_and_go_next)
        
        # Add everything to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(form_frame)
        main_layout.addWidget(image_frame)
        main_layout.addWidget(btn_save)
        main_layout.addStretch()
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidget(main_widget)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        self.setLayout(layout)
        
    def select_main_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Main Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.main_image_path = file_path
            QMessageBox.information(self,"Main Image", f"Selected: {file_path}")
            
    def save_and_go_next(self):
        try:
            self.parent_window.model_code = self.model_code_input.text().strip()
            self.parent_window.model_name = self.model_name_input.text().strip()
            self.parent_window.variant_name = self.variant_name_input.text().strip()
            self.parent_window.total_interior = int(self.total_interior_input.text().strip())
            self.parent_window.total_exterior = int(self.total_exterior_input.text().strip())
            self.parent_window.total_loose = int(self.total_loose_input.text().strip())
            self.parent_window.main_image_path = self.main_image_path
            
            if not self.parent_window.model_code or not self.parent_window.main_image_path:
                raise ValueError("Model Code and Main Image are mandatory!")
            
            self.step2= ComponentFillingPage(self.parent_window,"Interior",self.parent_window.total_interior)
            self.step2.show()
            self.close()
            
        except ValueError as e:
            QMessageBox.critical(self,"Error", f"{str(e)}")
            
class ComponentFillingPage(QWidget):
    def __init__(self,parent_window,component_type,total_parts):
        super().__init__()
        self.parent_window = parent_window
        self.component_type=component_type
        self.total_parts = total_parts
        self.current_part= 1
        
        self.main_image_path = ""
        self.yolo_dontdetect_path = ""
        self.yolo_roidetect_path = ""
        self.yolo_simpledetect_path = ""
        
        self.simple_class_checkboxes = []
        self.dont_class_checkboxes = []
        self.model_class_names = []
        self.completed_components = []
        
        self.pipeline_config = {}
        
        self.setWindowTitle(f"🔧 Step 2: {component_type} Component {self.current_part}/{self.total_parts}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(MODERN_STYLE)
        
        self.init_ui()
        
    def init_ui(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Main content widget
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(25)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(116, 185, 255, 0.3), stop:1 rgba(118, 75, 162, 0.3));
                border-radius: 20px;
                padding: 30px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        self.title_label = QLabel(f"🔧 Step 2: {self.component_type} Component {self.current_part}/{self.total_parts}")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 36px; font-weight: bold; color: white; margin: 15px;")
        
        self.completed_list_label = QLabel("Completed Components: None yet")
        self.completed_list_label.setAlignment(Qt.AlignCenter)
        self.completed_list_label.setStyleSheet("font-size: 16px; color: rgba(255, 255, 255, 0.8);")
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.completed_list_label)
        
        # Component basic info section
        basic_frame = QFrame()
        basic_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        basic_layout = QVBoxLayout(basic_frame)
        
        basic_title = QLabel("📝 Component Basic Information")
        basic_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 15px;")
        basic_layout.addWidget(basic_title)
        
        # Component name
        name_layout = QVBoxLayout()
        name_label = QLabel("🏷️ Component Name:")
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-left: 5px;")
        
        self.component_name_input = QLineEdit()
        self.component_name_input.setPlaceholderText("🏷️ Enter Component Name")
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.component_name_input)
        basic_layout.addLayout(name_layout)
        
        # Main image section
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px dashed rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 20px;
                margin-top: 15px;
            }
        """)
        image_layout = QVBoxLayout(image_frame)
        
        image_label = QLabel("📷 Component Main Image")
        image_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-bottom: 10px;")
        
        image_button_layout = QHBoxLayout()
        btn_image = QPushButton("📁 Select Component Main Image")
        btn_image.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ffecd2, stop:1 #fcb69f);
                color: #333;
                font-size: 14px;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ffedcc, stop:1 #fdbb9c);
            }
        """)
        btn_image.clicked.connect(lambda: self.browse_file("main_image"))
        
        self.main_image_tick = QLabel("❌ No Image Selected")
        self.main_image_tick.setStyleSheet("font-size: 14px; color: rgba(255, 255, 255, 0.7); margin-left: 15px;")
        
        image_button_layout.addWidget(btn_image)
        image_button_layout.addWidget(self.main_image_tick)
        image_button_layout.addStretch()
        
        image_layout.addWidget(image_label)
        image_layout.addLayout(image_button_layout)
        
        basic_layout.addWidget(image_frame)
        
        # Pipeline configuration section
        pipeline_frame = QFrame()
        pipeline_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        pipeline_layout = QVBoxLayout(pipeline_frame)
        
        pipeline_title = QLabel("⚙️ Pipeline Configuration")
        pipeline_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 15px;")
        pipeline_layout.addWidget(pipeline_title)
        
        # Don't Detect section
        dont_section = self.create_model_section(
            "🚫 Don't Detect Model", 
            "yolo_dontdetect",
            "#ff6b6b"
        )
        pipeline_layout.addWidget(dont_section)
        
        self.dont_class_selection_area = QScrollArea()
        self.dont_class_selection_area.setMinimumHeight(100)
        self.dont_class_selection_area.setStyleSheet("""
            QScrollArea {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                margin: 5px 0px;
            }
        """)
        pipeline_layout.addWidget(self.dont_class_selection_area)
        
        # ROI Detect section
        roi_section = self.create_model_section(
            "🎯 ROI Detect Model", 
            "yolo_roidetect",
            "#4ecdc4"
        )
        pipeline_layout.addWidget(roi_section)
        
        # Convert to BW section
        bw_layout = QVBoxLayout()
        bw_label = QLabel("⚫ Convert to Black and White:")
        bw_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin: 10px 5px 5px 5px;")
        
        self.convert_bw_dropdown = QComboBox()
        self.convert_bw_dropdown.addItems(["SKIP", "YES"])
        
        bw_layout.addWidget(bw_label)
        bw_layout.addWidget(self.convert_bw_dropdown)
        pipeline_layout.addLayout(bw_layout)
        
        # Simple Detect section
        simple_section = self.create_model_section(
            "🔍 Simple Detect Model", 
            "yolo_simpledetect",
            "#45b7d1"
        )
        pipeline_layout.addWidget(simple_section)
        
        self.simple_class_selection_area = QScrollArea()
        self.simple_class_selection_area.setMinimumHeight(100)
        self.simple_class_selection_area.setStyleSheet("""
            QScrollArea {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                margin: 5px 0px;
            }
        """)
        pipeline_layout.addWidget(self.simple_class_selection_area)
        
        # OCR section
        ocr_layout = QVBoxLayout()
        ocr_label = QLabel("📖 Enable OCR Detection:")
        ocr_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin: 10px 5px 5px 5px;")
        
        self.ocr_detect_dropdown = QComboBox()
        self.ocr_detect_dropdown.addItems(["SKIP", "YES"])
        self.ocr_detect_dropdown.currentIndexChanged.connect(self.toggle_ocr_annotation)
        
        self.ocr_annotation_input = QLineEdit()
        self.ocr_annotation_input.setPlaceholderText("📝 Enter OCR Annotation")
        self.ocr_annotation_input.setEnabled(False)
        
        ocr_layout.addWidget(ocr_label)
        ocr_layout.addWidget(self.ocr_detect_dropdown)
        ocr_layout.addWidget(self.ocr_annotation_input)
        pipeline_layout.addLayout(ocr_layout)
        
        # Subcomponents section
        sub_frame = QFrame()
        sub_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        sub_layout = QVBoxLayout(sub_frame)
        
        sub_title = QLabel("🔧 Subcomponents")
        sub_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 15px;")
        
        sub_count_layout = QVBoxLayout()
        sub_count_label = QLabel("🔢 Total Subcomponents:")
        sub_count_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-left: 5px;")
        
        self.subcomponent_count_input = QLineEdit()
        self.subcomponent_count_input.setPlaceholderText("🔢 Enter Subcomponents Count")
        
        sub_count_layout.addWidget(sub_count_label)
        sub_count_layout.addWidget(self.subcomponent_count_input)
        
        sub_layout.addWidget(sub_title)
        sub_layout.addLayout(sub_count_layout)
        
        # Next button
        btn_next = QPushButton("🚀 Save and Next Component")
        btn_next.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #667eea, stop:1 #764ba2);
                font-size: 18px;
                padding: 18px 35px;
                border-radius: 12px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #7c88ea, stop:1 #8a5cb2);
            }
        """)
        btn_next.clicked.connect(self.save_and_next)
        
        # Add all to main layout
        layout.addWidget(header_frame)
        layout.addWidget(basic_frame)
        layout.addWidget(pipeline_frame)
        layout.addWidget(sub_frame)
        layout.addWidget(btn_next)
        layout.addStretch()
        
        # Set scroll area
        scroll.setWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def create_model_section(self, title, field_name, color):
        """Create a modern model selection section"""
        section_frame = QFrame()
        section_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.05);
                border-left: 4px solid {color};
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0px;
            }}
        """)
        section_layout = QVBoxLayout(section_frame)
        
        section_title = QLabel(title)
        section_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color}; margin-bottom: 10px;")
        section_layout.addWidget(section_title)
        
        button_layout = QHBoxLayout()
        
        # Select button
        btn_select = QPushButton(f"📁 Select {title.split(' ')[-1]}")
        btn_select.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 13px;
                padding: 10px 15px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """)
        btn_select.clicked.connect(lambda: self.browse_file(field_name))
        
        # Remove button
        btn_remove = QPushButton("🗑️ Remove")
        btn_remove.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 13px;
                padding: 10px 15px;
                border-radius: 8px;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        btn_remove.clicked.connect(lambda: self.remove_model(field_name))
        
        # Status label
        if field_name == "yolo_dontdetect":
            self.dontdetect_tick = QLabel("❌ No Model Selected")
            status_label = self.dontdetect_tick
        elif field_name == "yolo_roidetect":
            self.roidetect_tick = QLabel("❌ No Model Selected")
            status_label = self.roidetect_tick
        elif field_name == "yolo_simpledetect":
            self.simpledetect_tick = QLabel("❌ No Model Selected")
            status_label = self.simpledetect_tick
        status_label.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.7); margin-left: 10px;")
        
        button_layout.addWidget(btn_select)
        button_layout.addWidget(btn_remove)
        button_layout.addWidget(status_label)
        button_layout.addStretch()
        
        section_layout.addLayout(button_layout)
        
        return section_frame
    
    def remove_model(self,field):
        if field == "yolo_dontdetect":
            self.yolo_dontdetect_path=""
            self.dontdetect_tick.setText("No Model Selected")
            self.dont_class_checkboxes=[]
            self.dont_class_selection_area.takeWidget()
            
        elif field == "yolo_roidetect":
            self.yolo_roidetect_path=""
            self.roidetect_tick.setText("No Model Selected")
        
        elif field == "yolo_simpledetect":
            self.yolo_simpledetect_path=""
            self.simpledetect_tick.setText("No Model Selected")
            self.simple_class_checkboxes=[]
            self.simple_class_selection_area.takeWidget()
            
        QMessageBox.information(self,"Model Removed",f"{field.replace('_',' ').title()} cleared (set to SKIP).")
        
    def browse_file(self, field):
        file_path, _ = QFileDialog.getOpenFileName(self,"Select File","","All Files (*.*)")
        if file_path:
            if field == "main_image":
                self.main_image_path = file_path
                self.main_image_tick.setText(f"✅ {os.path.basename(file_path)}")
                self.main_image_tick.setStyleSheet("font-size: 14px; color: #00b894; margin-left: 15px; font-weight: bold;")
                
            elif field == "yolo_dontdetect":
                self.yolo_dontdetect_path = file_path
                self.dontdetect_tick.setText(f"✅ {os.path.basename(file_path)}")
                self.dontdetect_tick.setStyleSheet("font-size: 12px; color: #00b894; margin-left: 10px; font-weight: bold;")
                self.load_model_classes(file_path, target="dont")
                
                
            elif field == "yolo_roidetect":
                self.roidetect_tick.setText(f"✅ {os.path.basename(file_path)}")
                self.roidetect_tick.setStyleSheet("font-size: 12px; color: #00b894; margin-left: 10px; font-weight: bold;")
                self.yolo_roidetect_path = file_path
                
            elif field == "yolo_simpledetect":
                self.yolo_simpledetect_path = file_path
                self.simpledetect_tick.setText(f"✅ {os.path.basename(file_path)}")
                self.simpledetect_tick.setStyleSheet("font-size: 12px; color: #00b894; margin-left: 10px; font-weight: bold;")
                self.load_model_classes(file_path, target="simple")
            
            QMessageBox.information(self,"✅ File Selected", f"Successfully selected: {os.path.basename(file_path)}")
                
    def toggle_ocr_annotation(self):
        if self.ocr_detect_dropdown.currentText() == "YES":
            self.ocr_annotation_input.setEnabled(True)
        else:
            self.ocr_annotation_input.clear()
            self.ocr_annotation_input.setEnabled(False)
    
    
    
    def load_model_classes(self, model_path, target):
        """Automatically load YOLO model and show class selection checkboxes"""
        try:
            model = YOLO(model_path)
            class_names = list(model.names.values())

            grid = QWidget()
            grid.setStyleSheet("""
                QWidget {
                    background-color: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            grid_layout = QGridLayout(grid)
            grid_layout.setSpacing(8)

            if target == "simple":
                self.simple_class_checkboxes = []
                for i, cls in enumerate(class_names):
                    cb = QCheckBox(cls)
                    cb.setStyleSheet("""
                        QCheckBox {
                            font-size: 13px;
                            color: white;
                            padding: 5px;
                            spacing: 10px;
                        }
                        QCheckBox::indicator {
                            width: 18px;
                            height: 18px;
                            border-radius: 3px;
                            border: 2px solid #4facfe;
                            background-color: rgba(255, 255, 255, 0.1);
                        }
                        QCheckBox::indicator:checked {
                            background-color: #4facfe;
                            border: 2px solid #4facfe;
                        }
                        QCheckBox::indicator:hover {
                            border: 2px solid #6bb4ff;
                        }
                    """)
                    grid_layout.addWidget(cb, i // 4, i % 4)
                    self.simple_class_checkboxes.append(cb)
                
                self.simple_class_selection_area.setWidget(grid)
                self.simple_class_selection_area.setMinimumHeight(150)

            else:
                self.dont_class_checkboxes = []
                for i, cls in enumerate(class_names):
                    cb = QCheckBox(cls)
                    cb.setStyleSheet("""
                        QCheckBox {
                            font-size: 13px;
                            color: white;
                            padding: 5px;
                            spacing: 10px;
                        }
                        QCheckBox::indicator {
                            width: 18px;
                            height: 18px;
                            border-radius: 3px;
                            border: 2px solid #ff6b6b;
                            background-color: rgba(255, 255, 255, 0.1);
                        }
                        QCheckBox::indicator:checked {
                            background-color: #ff6b6b;
                            border: 2px solid #ff6b6b;
                        }
                        QCheckBox::indicator:hover {
                            border: 2px solid #ff7675;
                        }
                    """)
                    grid_layout.addWidget(cb, i // 4, i % 4)
                    self.dont_class_checkboxes.append(cb)
                
                self.dont_class_selection_area.setWidget(grid)
                self.dont_class_selection_area.setMinimumHeight(150)

            QMessageBox.information(self, "✅ Model Classes Loaded", f"Successfully loaded {len(class_names)} classes for selection.")

        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Failed to load model classes: {str(e)}")
            
    def save_and_next(self):
        if not self.main_image_path:
            QMessageBox.warning(self,"Missing info","Main Image is required!")
            return 
        if not self.component_name_input.text().strip():
            QMessageBox.warning(self, "Missing info", "Component Name is required!")
            return

        # Collect selected classes
        selected_simple_classes = [cb.text() for cb in self.simple_class_checkboxes if cb.isChecked()]
        selected_dont_classes = [cb.text() for cb in self.dont_class_checkboxes if cb.isChecked()]

        # Build component data
        component_data = {
            "name": self.component_name_input.text().strip(),
            "type": self.component_type,
            "totalSubComponents": int(self.subcomponent_count_input.text().strip()) if self.subcomponent_count_input.text().strip() else 0,
            "mainImage": self.main_image_path,
            "pipelineConfig": {
                "YOLO_DONTDETECT": self.yolo_dontdetect_path if self.yolo_dontdetect_path else "SKIP",
                "YOLO_ROIDETECT": self.yolo_roidetect_path if self.yolo_roidetect_path else "SKIP",
                "YOLO_CONVERTTOBW": self.convert_bw_dropdown.currentText(),
                "YOLO_SIMPLEDETECT": self.yolo_simpledetect_path if self.yolo_simpledetect_path else "SKIP",
                "OCR_DETECT": self.ocr_detect_dropdown.currentText(),
                "YOLO_DONTDETECTANNOTATION": ", ".join(selected_dont_classes) if selected_dont_classes else "SKIP",
                "YOLO_SIMPLEDETECTANNOTATION": ", ".join(selected_simple_classes) if selected_simple_classes else "SKIP",
                "OCR_DETECTANNOTATION": self.ocr_annotation_input.text().strip() if self.ocr_detect_dropdown.currentText() == "YES" else "SKIP"
            }
        }

        total_subs = component_data["totalSubComponents"]

        if total_subs > 0:
            # Launch Subcomponent Filling Page
            self.sub_page = SubComponentFillingPage(self, component_data, total_subs)
            self.sub_page.show()
            self.hide()
        else:
            # No subcomponents → directly save and continue
            self.completed_components.append(component_data)
            self.resume_next_component()
            
    def resume_next_component(self):
        # ✅ Check if we are in edit/add mode (has return_to_review callback)
        if hasattr(self, "return_to_review") and callable(self.return_to_review):
            # In edit/add mode - return to review immediately after completing the component
            self.return_to_review(self.completed_components)
            self.close()
            return
        
        # Ensure the window is properly restored and visible
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Force layout refresh to prevent shrinking
        self.update()
        self.repaint()
        QApplication.processEvents()
        
        self.current_part += 1

        names = [comp["name"] for comp in self.completed_components]
        self.completed_list_label.setText(
            f"Completed Components: {', '.join(names) if names else 'None yet'}"
        )

        if self.current_part <= self.total_parts:
            self.reset_for_next_component()
        else:
            QMessageBox.information(self, "Completed", f"Finished all {self.component_type} components!")
            print("Finished all components:\n", json.dumps(self.completed_components, indent=2))

            if self.component_type == "Interior":
                self.parent_window.interior_components = self.completed_components
                if self.parent_window.total_exterior > 0:
                    self.step_exterior = ComponentFillingPage(
                        self.parent_window, "Exterior", self.parent_window.total_exterior
                    )
                    self.step_exterior.show()
                else:
                    self.parent_window.finalize_all()

            elif self.component_type == "Exterior":
                self.parent_window.exterior_components = self.completed_components
                if self.parent_window.total_loose > 0:
                    self.step_loose = ComponentFillingPage(
                        self.parent_window, "Loose", self.parent_window.total_loose
                    )
                    self.step_loose.show()
                else:
                    self.parent_window.finalize_all()

            elif self.component_type == "Loose":
                self.parent_window.loose_components = self.completed_components
                self.parent_window.finalize_all()

            self.close()

            
    def reset_for_next_component(self):
        self.component_name_input.clear()
        self.main_image_path = ""
        self.yolo_dontdetect_path = ""
        self.yolo_roidetect_path = ""
        self.yolo_simpledetect_path = ""
        self.subcomponent_count_input.clear()
        
        self.simple_class_checkboxes=[]
        self.dont_class_checkboxes=[]
        self.simple_class_selection_area.takeWidget()
        self.dont_class_selection_area.takeWidget()
        
        self.main_image_tick.setText("No Image Selected")
        self.dontdetect_tick.setText("No Model Selected")
        self.roidetect_tick.setText("No Model Selected")
        self.simpledetect_tick.setText("No Model Selected")
        
        self.convert_bw_dropdown.setCurrentText("SKIP")
        self.ocr_detect_dropdown.setCurrentText("SKIP")
        self.ocr_annotation_input.clear()
        self.ocr_annotation_input.setEnabled(False)
        
        self.title_label.setText(f"Step 2: {self.component_type} Component {self.current_part}/{self.total_parts}")
        
        # Force layout refresh to prevent shrinking
        self.update()
        self.repaint()
        QApplication.processEvents()
        
class SubComponentFillingPage(QWidget):
    def __init__(self, parent_window, component_data, total_subcomponents):
        super().__init__()
        self.parent_window = parent_window
        self.component_data = component_data  # dict from ComponentFillingPage
        self.total_subcomponents = total_subcomponents
        self.current_sub = 1
        self.subcomponents = []

        self.reference_image_path = ""

        self.setWindowTitle(f"🔧 Subcomponents for {self.component_data['name']}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()

    def init_ui(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Main content widget
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(25)
        layout.setContentsMargins(50, 30, 50, 30)

        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(253, 203, 110, 0.3), stop:1 rgba(225, 112, 85, 0.3));
                border-radius: 20px;
                padding: 30px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)

        self.title_label = QLabel(
            f"🔧 Subcomponent {self.current_sub}/{self.total_subcomponents} for {self.component_data['name']}"
        )
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white; margin: 15px;")
        
        self.completed_subs_label = QLabel("Completed Subcomponents: None yet")
        self.completed_subs_label.setAlignment(Qt.AlignCenter)
        self.completed_subs_label.setStyleSheet("font-size: 16px; color: rgba(255, 255, 255, 0.8);")
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.completed_subs_label)

        # Form section
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 15px;
                padding: 30px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)

        # Subcomponent Name
        name_layout = QVBoxLayout()
        name_label = QLabel("📍 Subcomponent Location:")
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 8px;")
        
        self.sub_name_input = QLineEdit()
        self.sub_name_input.setPlaceholderText("📍 Enter Subcomponent Location/Name")
        self.sub_name_input.setStyleSheet("font-size: 16px; padding: 15px;")
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.sub_name_input)

        # Instruction
        instruction_layout = QVBoxLayout()
        instruction_label = QLabel("📝 Instruction:")
        instruction_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 8px;")
        
        self.sub_instruction_input = QLineEdit()
        self.sub_instruction_input.setPlaceholderText("📝 Enter detailed instruction for this subcomponent")
        self.sub_instruction_input.setStyleSheet("font-size: 16px; padding: 15px;")
        
        instruction_layout.addWidget(instruction_label)
        instruction_layout.addWidget(self.sub_instruction_input)

        # Reference Image section
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px dashed rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 25px;
                margin-top: 10px;
            }
        """)
        image_layout = QVBoxLayout(image_frame)

        image_title = QLabel("📷 Reference Image")
        image_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 15px;")

        ref_button_layout = QHBoxLayout()
        
        btn_ref_image = QPushButton("📁 Select Reference Image")
        btn_ref_image.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #74b9ff, stop:1 #0984e3);
                font-size: 15px;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #81c3ff, stop:1 #2d96ff);
            }
        """)
        btn_ref_image.clicked.connect(self.select_reference_image)
        
        btn_remove_ref = QPushButton("🗑️ Remove")
        btn_remove_ref.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                font-size: 14px;
                padding: 15px 20px;
                border-radius: 10px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        btn_remove_ref.clicked.connect(self.remove_reference_image)

        self.ref_tick = QLabel("❌ No Image Selected")
        self.ref_tick.setStyleSheet("font-size: 14px; color: rgba(255, 255, 255, 0.7); margin-left: 15px;")

        ref_button_layout.addWidget(btn_ref_image)
        ref_button_layout.addWidget(btn_remove_ref)
        ref_button_layout.addWidget(self.ref_tick)
        ref_button_layout.addStretch()

        image_layout.addWidget(image_title)
        image_layout.addLayout(ref_button_layout)

        # Add all to form
        form_layout.addLayout(name_layout)
        form_layout.addLayout(instruction_layout)
        form_layout.addWidget(image_frame)

        # Save & Next button
        btn_next = QPushButton("🚀 Save & Next Subcomponent")
        btn_next.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #00b894, stop:1 #00cec9);
                font-size: 18px;
                padding: 20px 40px;
                border-radius: 12px;
                font-weight: bold;
                margin-top: 25px;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #55efc4, stop:1 #81ecec);
            }
        """)
        btn_next.clicked.connect(self.save_and_next_subcomponent)

        # Add everything to main layout
        layout.addWidget(header_frame)
        layout.addWidget(form_frame)
        layout.addWidget(btn_next)
        layout.addStretch()

        # Set scroll area
        scroll.setWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def select_reference_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Reference Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.reference_image_path = file_path
            self.ref_tick.setText(f"✅ Image Selected at {file_path}")
            QMessageBox.information(self, "Reference Image", f"Selected: {file_path}")

    def remove_reference_image(self):
        self.reference_image_path = ""
        self.ref_tick.setText("No Image Selected")
        QMessageBox.information(self, "Removed", "Reference image removed.")

    def save_and_next_subcomponent(self):
        if not self.sub_name_input.text().strip():
            QMessageBox.warning(self, "Missing Info", "Subcomponent Name is required!")
            return

        if not self.sub_instruction_input.text().strip():
            QMessageBox.warning(self, "Missing Info", "Instruction is required!")
            return

        if not self.reference_image_path:
            QMessageBox.warning(self, "Missing Info", "Reference Image is required!")
            return
        

        # Save current subcomponent
        self.subcomponents.append({
            "component": self.component_data["name"],
            "name": self.sub_name_input.text().strip(),
            "instruction": self.sub_instruction_input.text().strip(),
            "referenceImage": self.reference_image_path
        })
        done_names = [sub["name"] for sub in self.subcomponents]
        self.completed_subs_label.setText("Completed Subcomponents: " + ", ".join(done_names) if done_names else "Completed Subcomponents: None yet")

        self.current_sub += 1

        if self.current_sub <= self.total_subcomponents:
            # Reset for next subcomponent
            self.sub_name_input.clear()
            self.sub_instruction_input.clear()
            self.reference_image_path = ""
            self.ref_tick.setText("❌ No Image Selected")
            self.ref_tick.setStyleSheet("font-size: 14px; color: rgba(255, 255, 255, 0.7); margin-left: 15px;")
            self.title_label.setText(
                f"🔧 Subcomponent {self.current_sub}/{self.total_subcomponents} for {self.component_data['name']}"
            )
        else:
            # Done all subcomponents, push to parent_window
            self.component_data["subComponents"] = self.subcomponents
            self.parent_window.completed_components.append(self.component_data)
            QMessageBox.information(
                self, "Completed", f"✅ Finished all {self.total_subcomponents} subcomponents for {self.component_data['name']}!"
            )
            self.close()
            self.parent_window.resume_next_component()
        
class FinalReviewPage(QWidget):
    def __init__(self, parent_window, final_kspec):
        super().__init__()
        self.parent_window = parent_window
        self.final_kspec = final_kspec

        self.setWindowTitle("✅ Final KSpec Review")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()

    def init_ui(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Main content widget
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(50, 30, 50, 30)

        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(0, 206, 201, 0.3), stop:1 rgba(0, 184, 148, 0.3));
                border-radius: 20px;
                padding: 30px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("✅ Final KSpec Review")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 42px; font-weight: bold; color: white; margin: 15px;")
        
        subtitle = QLabel("Review your vehicle specification before upload")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: rgba(255, 255, 255, 0.8);")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        # Model info section
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        info_layout = QGridLayout(info_frame)
        info_layout.setSpacing(15)
        
        info_title = QLabel("📋 Vehicle Information")
        info_title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 15px;")
        info_layout.addWidget(info_title, 0, 0, 1, 2)
        
        # Create info cards
        info_items = [
            ("🔢 Model Code:", self.final_kspec['modelCode']),
            ("🚗 Model Name:", self.final_kspec['modelName']),
            ("⚙️ Variant Name:", self.final_kspec['variantName']),
            ("🏠 Total Interior:", str(self.final_kspec['totalInterior'])),
            ("🌍 Total Exterior:", str(self.final_kspec['totalExterior'])),
            ("🔧 Total Loose:", str(self.final_kspec['totalLoose'])),
            ("📷 Main Image:", os.path.basename(self.final_kspec['mainImagePath']))
        ]
        
        row = 1
        for i, (label_text, value) in enumerate(info_items):
            col = i % 2
            if col == 0:
                row += 1
            
            info_card = QFrame()
            info_card.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px;
                }
            """)
            card_layout = QVBoxLayout(info_card)
            
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4facfe;")
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("font-size: 16px; color: white; margin-top: 5px;")
            value_label.setWordWrap(True)
            
            card_layout.addWidget(label)
            card_layout.addWidget(value_label)
            
            info_layout.addWidget(info_card, row, col)

        # Components table section
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setSpacing(15)
        table_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to fix spacing

        table_title = QLabel("📊 Components Summary")
        table_title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 10px;")
        table_layout.addWidget(table_title)

        # Create scrollable table
        table_scroll = QScrollArea()
        table_scroll.setWidgetResizable(True)
        table_scroll.setMaximumHeight(400)  # Limit height for 50+ components
        table_scroll.setStyleSheet("""
            QScrollArea {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
            }
        """)
        
        table_widget = QWidget()
        grid = QGridLayout(table_widget)
        grid.setSpacing(2)
        grid.setContentsMargins(10, 10, 10, 10)

        # Modern table headers
        headers = ["Component Name", "Type", "Subcomponents", "Main Image"]
        header_colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24"]
        
        for col, (header, color) in enumerate(zip(headers, header_colors)):
            header_frame = QFrame()
            header_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                    padding: 12px;
                    margin: 2px;
                }}
            """)
            header_layout = QVBoxLayout(header_frame)
            header_layout.setContentsMargins(5, 5, 5, 5)
            
            header_label = QLabel(f"<b>{header}</b>")
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
            header_layout.addWidget(header_label)
            
            grid.addWidget(header_frame, 0, col)

        # Table rows with alternating colors
        for i, comp in enumerate(self.final_kspec["components"], start=1):
            row_color = "rgba(255, 255, 255, 0.1)" if i % 2 == 0 else "rgba(255, 255, 255, 0.05)"
            
            # Component name (clickable button)
            name_btn = QPushButton(comp["name"])
            name_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {row_color};
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 6px;
                    padding: 10px;
                    text-align: left;
                    font-size: 13px;
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: rgba(79, 172, 254, 0.3);
                    border: 1px solid #4facfe;
                }}
            """)
            name_btn.clicked.connect(lambda _, c=comp: self.show_component_details(c))
            grid.addWidget(name_btn, i, 0)
            
            # Other columns
            columns = [comp["type"], str(comp["totalSubComponents"]), os.path.basename(comp["mainImage"])]
            for col, text in enumerate(columns, 1):
                cell_frame = QFrame()
                cell_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {row_color};
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        border-radius: 6px;
                        padding: 8px;
                        margin: 1px;
                    }}
                """)
                cell_layout = QVBoxLayout(cell_frame)
                cell_layout.setContentsMargins(5, 5, 5, 5)
                
                cell_label = QLabel(text)
                cell_label.setAlignment(Qt.AlignCenter)
                cell_label.setStyleSheet("color: white; font-size: 12px;")
                cell_label.setWordWrap(True)
                cell_layout.addWidget(cell_label)
                
                grid.addWidget(cell_frame, i, col)

        table_scroll.setWidget(table_widget)
        table_layout.addWidget(table_scroll)

        # Action buttons
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(20)
        
        # Upload button
        upload_btn = QPushButton("⬆️ Upload to Backend")
        upload_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #00b894, stop:1 #00cec9);
                font-size: 16px;
                padding: 18px 30px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #55efc4, stop:1 #81ecec);
            }
        """)
        upload_btn.clicked.connect(self.dummy_upload)
        
        # Edit button
        edit_btn = QPushButton("✏️ Edit KSpec")
        edit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #fdcb6e, stop:1 #e17055);
                font-size: 16px;
                padding: 18px 30px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #fdd85e, stop:1 #e17755);
            }
        """)
        edit_btn.clicked.connect(self.edit_kspec)
        
        # Remove button
        remove_btn = QPushButton("🗑️ Remove Component")
        remove_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ff6b6b, stop:1 #ee5a24);
                font-size: 16px;
                padding: 18px 30px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ff7675, stop:1 #fd79a8);
            }
        """)
        remove_btn.clicked.connect(self.remove_component)
        
        # Add button
        add_btn = QPushButton("➕ Add Component")
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #74b9ff, stop:1 #0984e3);
                font-size: 16px;
                padding: 18px 30px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #81c3ff, stop:1 #2d96ff);
            }
        """)
        add_btn.clicked.connect(self.add_component)
        
        # Edit Component button (direct)
        edit_comp_btn = QPushButton("🔧 Edit Component")
        edit_comp_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #a29bfe, stop:1 #6c5ce7);
                font-size: 16px;
                padding: 18px 30px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #b2a9fe, stop:1 #7c6ce7);
            }
        """)
        edit_comp_btn.clicked.connect(self.edit_component)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(upload_btn)
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(remove_btn)
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(edit_comp_btn)
        buttons_layout.addStretch()

        # Add all sections to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(info_frame)
        main_layout.addWidget(table_frame)
        main_layout.addWidget(buttons_frame)
        main_layout.addStretch()

        # Set the scroll area as the main layout
        scroll.setWidget(main_widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def dummy_upload(self):
        progress_msg = None
        try:
            # Show progress message
            #
            QApplication.processEvents()

            # ✅ Use dynamic backend IP from main window
            backend_url = f"{self.parent_window.backend_ip.rstrip('/')}/recievenewkspec"

            data = {
                'kspec_metadata': json.dumps(self.final_kspec, ensure_ascii=False)
            }

            response = requests.post(backend_url, data=data, timeout=60)

            if response.status_code == 200:
                try:
                    result = response.json()
                    QMessageBox.information(
                        self,
                        "✅ Upload Successful",
                        f"KSpec metadata successfully uploaded!\n\n"
                        f"Model: {self.final_kspec['modelCode']} - {self.final_kspec['variantName']}\n"
                        f"Total Components: {len(self.final_kspec['components'])}\n\n"
                        f"Backend Response: {result.get('message', 'Upload completed')}"
                    )
                except:
                    QMessageBox.information(
                        self,
                        "✅ Upload Successful",
                        f"KSpec metadata uploaded!\n\n"
                        f"Model: {self.final_kspec['modelCode']} - {self.final_kspec['variantName']}\n"
                        f"Total Components: {len(self.final_kspec['components'])}\n\n"
                        f"Server Response: {response.text[:200]}..."
                    )
            else:
                QMessageBox.critical(
                    self,
                    "❌ Upload Failed",
                    f"Backend returned error {response.status_code}:\n{response.text[:500]}"
                )

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(
                self,
                "❌ Connection Error",
                f"Could not connect to backend at {backend_url}\n\n"
                f"Please check:\n"
                f"• Backend server is running\n"
                f"• IP address is correct\n"
                f"• Network connectivity"
            )
        except requests.exceptions.Timeout:
            QMessageBox.critical(
                self,
                "❌ Upload Timeout",
                "Upload timed out (metadata only). Please try again."
            )
        except Exception as req_error:
            QMessageBox.critical(
                self,
                "❌ Request Error",
                f"Upload request failed:\n{str(req_error)}"
            )
        finally:
            if progress_msg:
                progress_msg.close()


    
    def remove_component(self):
        comp_names = [c["name"] for c in self.final_kspec["components"]]
        if not comp_names:
            QMessageBox.warning(self, "Remove Component", "No components to remove!")
            return

        comp_name, ok = QInputDialog.getItem(
            self, "Remove Component", "Which component do you want to remove?", comp_names, 0, False
        )
        if ok and comp_name:
            # Find the component type before removing it
            component_type = None
            for comp in self.final_kspec["components"]:
                if comp["name"] == comp_name:
                    component_type = comp["type"]
                    break
            
            # Remove the component
            self.final_kspec["components"] = [c for c in self.final_kspec["components"] if c["name"] != comp_name]
            
            # Update the total counts in final_kspec
            if component_type == "Interior":
                self.final_kspec["totalInterior"] = max(0, self.final_kspec["totalInterior"] - 1)
                self.parent_window.total_interior = self.final_kspec["totalInterior"]
            elif component_type == "Exterior":
                self.final_kspec["totalExterior"] = max(0, self.final_kspec["totalExterior"] - 1) 
                self.parent_window.total_exterior = self.final_kspec["totalExterior"]
            elif component_type == "Loose":
                self.final_kspec["totalLoose"] = max(0, self.final_kspec["totalLoose"] - 1)
                self.parent_window.total_loose = self.final_kspec["totalLoose"]
                
            QMessageBox.information(self, "Removed", f"Component '{comp_name}' removed successfully!")
            self.refresh_display()
            
    def add_component(self):
        module_options = ["Interior", "Exterior", "Loose"]
        module_type, ok = QInputDialog.getItem(
            self, "Add Component", "Which module do you want to add this component to?", module_options, 0, False
        )

        if ok and module_type:
            self.add_page = ComponentFillingPage(self.parent_window, module_type, 1)
            self.add_page.return_to_review = lambda comps: self.append_new_component(comps, module_type)
            self.add_page.show()
            self.close()

    def append_new_component(self, comps, module_type):
        if comps:
            new_component = comps[0]
            self.final_kspec["components"].append(new_component)

            # Also update in parent_window for consistency
            if module_type == "Interior":
                self.parent_window.interior_components.append(new_component)
                # Increase the total count
                self.final_kspec["totalInterior"] += 1
                self.parent_window.total_interior = self.final_kspec["totalInterior"]
            elif module_type == "Exterior":
                self.parent_window.exterior_components.append(new_component)
                # Increase the total count
                self.final_kspec["totalExterior"] += 1
                self.parent_window.total_exterior = self.final_kspec["totalExterior"]
            elif module_type == "Loose":
                self.parent_window.loose_components.append(new_component)
                # Increase the total count
                self.final_kspec["totalLoose"] += 1
                self.parent_window.total_loose = self.final_kspec["totalLoose"]

            QMessageBox.information(self, "Added", f"Component '{new_component['name']}' added to {module_type} successfully!")
            self.refresh_display()

        
    def edit_kspec(self):
        options = ["Model Code", "Model Name", "Variant Name", "Main Image"]
        choice, ok = QInputDialog.getItem(self, "Edit KSpec", "What do you want to edit?", options, 0, False)

        if ok and choice:
            if choice == "Model Code":
                new_value, ok2 = QInputDialog.getText(self, "Edit Model Code", "Enter correct Model Code:")
                if ok2 and new_value.strip():
                    self.final_kspec["modelCode"] = new_value.strip()

            elif choice == "Model Name":
                new_value, ok2 = QInputDialog.getText(self, "Edit Model Name", "Enter correct Model Name:")
                if ok2 and new_value.strip():
                    self.final_kspec["modelName"] = new_value.strip()

            elif choice == "Variant Name":
                new_value, ok2 = QInputDialog.getText(self, "Edit Variant Name", "Enter correct Variant Name:")
                if ok2 and new_value.strip():
                    self.final_kspec["variantName"] = new_value.strip()

            elif choice == "Main Image":
                file_path, _ = QFileDialog.getOpenFileName(self, "Select Correct Main Image", "", "Images (*.png *.jpg *.jpeg)")
                if file_path:
                    self.final_kspec["mainImagePath"] = file_path

            # Refresh the page after any edit
            QMessageBox.information(self, "Updated", f"{choice} updated successfully!")
            self.refresh_display()
    
    def show_component_details(self, comp):
        details = f"""
    <b>Component:</b> {comp['name']} ({comp['type']})
    <b>Main Image:</b> {os.path.basename(comp['mainImage'])}

    <b>Pipeline Config:</b>
    """
        for key, value in comp["pipelineConfig"].items():
            details += f"{key}: {value}<br>"

        details += "<br><b>Subcomponents:</b><br>"
        subs = comp.get("subComponents", [])
        if subs:
            for s in subs:
                details += f"- {s['name']} | {s['instruction']} | {os.path.basename(s['referenceImage'])}<br>"
        else:
            details += "No subcomponents defined.<br>"

        msg = QMessageBox(self)
        msg.setWindowTitle(f"{comp['name']} Details")
        msg.setTextFormat(1)  # Allow HTML formatting
        msg.setText(details)
        msg.exec_()

    def edit_component(self):
        comp_names = [c["name"] for c in self.final_kspec["components"]]
        if not comp_names:
            QMessageBox.warning(self, "Edit Component", "No components to edit!")
            return

        comp_name, ok = QInputDialog.getItem(
            self, "Select Component", "Which component do you want to edit?", comp_names, 0, False
        )

        if ok and comp_name:
            # Find the component to edit and store its module type
            component_type = None
            for comp in self.final_kspec["components"]:
                if comp["name"] == comp_name:
                    component_type = comp["type"]
                    break
            
            if component_type:
                # Step 1: Remove the component using existing remove logic
                self.final_kspec["components"] = [c for c in self.final_kspec["components"] if c["name"] != comp_name]
                
                # Also update in parent_window for consistency
                if component_type == "Interior":
                    self.parent_window.interior_components = [c for c in self.parent_window.interior_components if c["name"] != comp_name]
                    # Decrease the total count
                    self.final_kspec["totalInterior"] = max(0, self.final_kspec["totalInterior"] - 1)
                    self.parent_window.total_interior = self.final_kspec["totalInterior"]
                elif component_type == "Exterior":
                    self.parent_window.exterior_components = [c for c in self.parent_window.exterior_components if c["name"] != comp_name]
                    # Decrease the total count
                    self.final_kspec["totalExterior"] = max(0, self.final_kspec["totalExterior"] - 1) 
                    self.parent_window.total_exterior = self.final_kspec["totalExterior"]
                elif component_type == "Loose":
                    self.parent_window.loose_components = [c for c in self.parent_window.loose_components if c["name"] != comp_name]
                    # Decrease the total count
                    self.final_kspec["totalLoose"] = max(0, self.final_kspec["totalLoose"] - 1)
                    self.parent_window.total_loose = self.final_kspec["totalLoose"]
                
                QMessageBox.information(self, "Component Removed", f"Component '{comp_name}' removed. Now you can add it back with changes.")
                
                # Step 2: Now call the existing add component logic with the specific module type
                self.add_component_to_module(component_type)

    def add_component_to_module(self, module_type):
        """Add a component to a specific module type (used for editing)"""
        self.add_page = ComponentFillingPage(self.parent_window, module_type, 1)
        self.add_page.return_to_review = lambda comps: self.append_new_component(comps, module_type)
        self.add_page.show()
        self.close()


    def refresh_display(self):
        self.deleteLater()  # ✅ Fully deletes this widget from memory
        new_page = FinalReviewPage(self.parent_window, self.final_kspec)
        new_page.show()
            
if __name__ == "__main__":
    app=QApplication(sys.argv)
    window = KSpecUploader()
    window.show()
    sys.exit(app.exec_())
        
   