import sys
import requests
import csv
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QMessageBox, QComboBox, QFrame, QInputDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QScrollArea, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

MODERN_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e3c72, stop:1 #2a5298);
    color: white;
}
QWidget {
    background-color: transparent;
    color: white;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4facfe, stop:1 #00f2fe);
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: bold;
    color: white;
    min-height: 20px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6bb4ff, stop:1 #1affff);
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3d8bfe, stop:1 #00d5fe);
}
QPushButton#test_button {
    min-width: 120px;
    padding: 8px 16px;
    font-size: 12px;
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
QFrame {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 10px;
}
QGroupBox {
    font-size: 16px;
    font-weight: bold;
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    margin-top: 10px;
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: #4facfe;
}
QTableWidget {
    background-color: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.5);
    border-radius: 8px;
    gridline-color: rgba(255, 255, 255, 0.4);
    color: white;
    font-size: 13px;
    alternate-background-color: rgba(255, 255, 255, 0.05);
}
QTableWidget::item {
    padding: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background-color: rgba(255, 255, 255, 0.08);
}
QTableWidget::item:selected {
    background-color: rgba(79, 172, 254, 0.5);
    color: white;
}
QTableWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.15);
}
QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4facfe, stop:1 #00f2fe);
    color: white;
    padding: 12px 8px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    font-weight: bold;
    font-size: 14px;
    text-align: center;
}
QHeaderView::section:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6bb4ff, stop:1 #1affff);
}
QScrollArea {
    border: none;
    background-color: transparent;
}
"""


class CalLineVINUploader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧾 Cal Line + VIN Uploader")
        self.setStyleSheet(MODERN_STYLE)
        self.setWindowIcon(QIcon("logo.png"))
        self.backend_ip = "http://192.168.0.100:8000"
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Title Section
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        title_label = QLabel("🧾 Cal Line & VIN Spec Uploader")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white; margin: 10px;")
        subtitle_label = QLabel("Upload and manage vehicle/VIN-level metadata")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 16px; color: rgba(255,255,255,0.8); margin-bottom: 20px;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        # Connection Section
        connection_group = QGroupBox("🌐 Backend Connection")
        connection_layout = QHBoxLayout(connection_group)
        
        ip_label = QLabel("Backend IP:")
        ip_label.setStyleSheet("font-size: 14px; font-weight: bold; min-width: 80px;")
        self.ip_input = QLineEdit(self.backend_ip)
        self.ip_input.setPlaceholderText("http://192.168.x.x:8000")
        self.ip_input.textChanged.connect(lambda val: setattr(self, "backend_ip", val.strip()))
        
        btn_test = QPushButton("🔌 Test Connection")
        btn_test.setObjectName("test_button")
        btn_test.clicked.connect(self.test_backend)
        
        connection_layout.addWidget(ip_label)
        connection_layout.addWidget(self.ip_input, 1)
        connection_layout.addWidget(btn_test)

        # Create scroll area for the main content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # VIN Management Section
        vin_group = QGroupBox("🚗 VIN Specification Management")
        vin_layout = QVBoxLayout(vin_group)
        
        # First row - CSV Upload (primary method)
        csv_upload_layout = QHBoxLayout()
        btn_csv_upload = QPushButton("📁 Upload VIN CSV File")
        btn_csv_upload.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #45a049);
                font-size: 16px;
                padding: 15px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5CBF60, stop:1 #4CAF50);
            }
        """)
        btn_csv_upload.clicked.connect(self.upload_csv_file)
        csv_upload_layout.addWidget(btn_csv_upload)
        
        # Second row - Manual upload and management
        vin_buttons_layout = QHBoxLayout()
        btn_manual_upload = QPushButton("✏️ Manual VIN Entry")
        btn_manual_upload.clicked.connect(self.ask_how_many_vins)
        btn_view_vins = QPushButton("📄 View All VINs")
        btn_view_vins.clicked.connect(self.view_all_vins)
        btn_remove_one_vin = QPushButton("🗑️ Remove Specific VIN")
        btn_remove_one_vin.clicked.connect(self.remove_specific_vin)
        btn_remove_all_vins = QPushButton("❌ Remove All VINs")
        btn_remove_all_vins.clicked.connect(self.remove_all_vins)
        
        vin_buttons_layout.addWidget(btn_manual_upload)
        vin_buttons_layout.addWidget(btn_view_vins)
        vin_buttons_layout.addWidget(btn_remove_one_vin)
        vin_buttons_layout.addWidget(btn_remove_all_vins)
        
        vin_layout.addLayout(csv_upload_layout)
        vin_layout.addLayout(vin_buttons_layout)

        # Cal Line Worker Management Section
        worker_group = QGroupBox("👷 Cal Line Worker Management")
        worker_layout = QVBoxLayout(worker_group)
        
        worker_buttons_layout = QHBoxLayout()
        btn_worker_upload = QPushButton("📝 Upload Workers")
        btn_worker_upload.clicked.connect(self.ask_how_many_workers)
        btn_list_workers = QPushButton("📋 View All Workers")
        btn_list_workers.clicked.connect(self.list_all_workers)
        btn_remove_worker = QPushButton("�️ Remove Specific Worker")
        btn_remove_worker.clicked.connect(self.remove_specific_worker)
        
        worker_buttons_layout.addWidget(btn_worker_upload)
        worker_buttons_layout.addWidget(btn_list_workers)
        worker_buttons_layout.addWidget(btn_remove_worker)
        
        worker_layout.addLayout(worker_buttons_layout)

        # Add groups to scroll layout
        scroll_layout.addWidget(vin_group)
        scroll_layout.addWidget(worker_group)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Add all sections to main layout
        main_layout.addWidget(title_frame)
        main_layout.addWidget(connection_group)
        main_layout.addWidget(scroll_area, 1)

        self.setCentralWidget(central_widget)

    def test_backend(self):
        try:
            url = f"{self.backend_ip.rstrip('/')}/health"
            response = requests.get(url, timeout=5)
            if response.status_code == 200 and response.json().get("status") == "ok":
                QMessageBox.information(self, "✅ Connected", f"Backend is reachable at:\n{self.backend_ip}")
            else:
                QMessageBox.warning(self, "⚠️ Unexpected Response", f"Received unexpected response:\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "❌ Connection Failed", f"Could not connect to backend:\n{str(e)}")

    def upload_csv_file(self):
        # Open file dialog to select CSV file
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select VIN CSV File", 
            "", 
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return  # User cancelled file selection
        
        try:
            # Parse CSV file
            vin_data = self.parse_csv_file(file_path)
            
            if not vin_data:
                QMessageBox.warning(self, "⚠️ No Data", "No valid VIN data found in the CSV file.")
                return
            
            # Show preview and ask for confirmation
            self.show_csv_preview(vin_data, file_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read CSV file:\n{str(e)}")

    def parse_csv_file(self, file_path):
        vin_data = []
        
        with open(file_path, 'r', encoding='utf-8-sig', newline='') as csvfile:
            # Try different delimiters
            sample = csvfile.read(1024)
            csvfile.seek(0)
            
            # Detect delimiter
            sniffer = csv.Sniffer()
            delimiter = ','
            try:
                delimiter = sniffer.sniff(sample).delimiter
            except:
                delimiter = ','  # Default to comma
            
            reader = csv.reader(csvfile, delimiter=delimiter)
            
            # Skip header row
            header_found = False
            for row_num, row in enumerate(reader):
                if not header_found:
                    # Look for header row (contains "Vin" or "VIN" in first column)
                    if row and len(row) > 0 and any(keyword in str(row[0]).upper() for keyword in ['VIN', 'VEHICLE']):
                        header_found = True
                        continue
                    elif row_num == 0:  # Assume first row is header if no VIN keyword found
                        header_found = True
                        continue
                
                # Process data rows - only consider first 3 columns
                if len(row) >= 3:
                    vin_number = str(row[0]).strip()
                    engine_number = str(row[1]).strip()
                    kspec = str(row[2]).strip()
                    
                    # Skip empty rows or rows with empty essential data
                    if vin_number and engine_number and kspec:
                        vin_data.append({
                            'vin': vin_number,
                            'engineNumber': engine_number,
                            'kspec': kspec
                        })
        
        return vin_data

    def show_csv_preview(self, vin_data, file_path):
        # Create preview dialog
        preview_dialog = QWidget()
        preview_dialog.setWindowTitle("📋 CSV Data Preview")
        preview_dialog.setWindowModality(Qt.ApplicationModal)
        preview_dialog.resize(1000, 600)
        preview_dialog.setStyleSheet(MODERN_STYLE)
        
        layout = QVBoxLayout(preview_dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title and file info
        title = QLabel(f"📋 Preview CSV Data from: {os.path.basename(file_path)}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin: 10px;")
        layout.addWidget(title)
        
        info_label = QLabel(f"Found {len(vin_data)} valid VIN records")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 15px;")
        layout.addWidget(info_label)
        
        # Preview table (show first 10 records)
        preview_table = QTableWidget()
        display_count = min(10, len(vin_data))
        preview_table.setRowCount(display_count)
        preview_table.setColumnCount(3)
        preview_table.setHorizontalHeaderLabels(["VIN Number", "Engine Number", "KSpec"])
        
        for row, data in enumerate(vin_data[:display_count]):
            preview_table.setItem(row, 0, QTableWidgetItem(data['vin']))
            preview_table.setItem(row, 1, QTableWidgetItem(data['engineNumber']))
            preview_table.setItem(row, 2, QTableWidgetItem(data['kspec']))
        
        # Auto-resize columns
        header = preview_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        preview_table.verticalHeader().hide()
        
        layout.addWidget(preview_table)
        
        if len(vin_data) > 10:
            more_label = QLabel(f"... and {len(vin_data) - 10} more records")
            more_label.setAlignment(Qt.AlignCenter)
            more_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.6);")
            layout.addWidget(more_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        upload_btn = QPushButton("✅ Upload All Data")
        upload_btn.setStyleSheet("font-size: 16px; padding: 10px 30px; margin: 10px; background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #45a049);")
        upload_btn.clicked.connect(lambda: self.process_csv_upload(vin_data, preview_dialog))
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("font-size: 16px; padding: 10px 30px; margin: 10px;")
        cancel_btn.clicked.connect(preview_dialog.close)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(upload_btn)
        layout.addLayout(button_layout)
        
        preview_dialog.show()
        self.preview_dialog = preview_dialog  # Keep reference

    def process_csv_upload(self, vin_data, preview_dialog):
        preview_dialog.close()
        
        # Show progress
        QMessageBox.information(self, "🔄 Processing", f"Starting upload of {len(vin_data)} VIN records...")
        
        success_count = 0
        failed_count = 0
        failed_records = []
        
        for i, data in enumerate(vin_data):
            try:
                payload = {
                    "vin": data['vin'],
                    "engineNumber": data['engineNumber'],
                    "caseSpecCode": data['kspec']  # Note: using kspec directly as caseSpecCode
                }
                
                submit_url = f"{self.backend_ip.rstrip('/')}/upload_vin_spec"
                response = requests.post(submit_url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_records.append(f"VIN {data['vin']}: {response.text}")
            
            except Exception as e:
                failed_count += 1
                failed_records.append(f"VIN {data['vin']}: {str(e)}")
        
        # Show final results
        result_message = f"✅ Upload Complete!\n\nSuccessful: {success_count}\nFailed: {failed_count}"
        
        if failed_records:
            result_message += f"\n\nFirst few failures:\n" + "\n".join(failed_records[:3])
            if len(failed_records) > 3:
                result_message += f"\n... and {len(failed_records) - 3} more"
        
        QMessageBox.information(self, "📊 Upload Results", result_message)

    def ask_how_many_vins(self):
        count, ok = QInputDialog.getInt(self, "How Many VINs", "Enter number of VIN specifications to upload:", 1, 1, 50)
        if ok:
            self.upload_multiple_vins(count)

    def ask_how_many_workers(self):
        count, ok = QInputDialog.getInt(self, "How Many Workers", "Enter number of Cal Line workers to upload:", 1, 1, 50)
        if ok:
            self.upload_multiple_workers(count)

    def upload_multiple_workers(self, count):
        for i in range(count):
            name, ok1 = QInputDialog.getText(self, f"Worker {i+1}/{count}", "Enter Full Name:")
            if not ok1 or not name.strip():
                QMessageBox.warning(self, "Input Cancelled", "Skipping worker entry.")
                continue

            pno, ok2 = QInputDialog.getText(self, f"Worker {i+1}/{count}", "Enter P-Number:")
            if not ok2 or not pno.strip():
                QMessageBox.warning(self, "Input Cancelled", "Skipping worker entry.")
                continue

            dept, ok3 = QInputDialog.getText(self, f"Worker {i+1}/{count}", "Enter Department:")
            if not ok3 or not dept.strip():
                QMessageBox.warning(self, "Input Cancelled", "Skipping worker entry.")
                continue

            payload = {
                "name": name.strip(),
                "pno": pno.strip(),
                "department": dept.strip()
            }

            try:
                submit_url = f"{self.backend_ip.rstrip('/')}/upload_cal_worker"
                r = requests.post(submit_url, json=payload, timeout=10)
                if r.status_code == 200:
                    QMessageBox.information(self, "✅ Success", f"Uploaded Cal Line Worker {name} successfully.")
                else:
                    QMessageBox.warning(self, "⚠️ Failed", f"Failed to upload worker {name}: {r.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Exception occurred: {str(e)}")

    def upload_multiple_vins(self, count):
        try:
            url = f"{self.backend_ip.rstrip('/')}/kspecs"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                kspecs = response.json()
                model_options = [f"{ks['modelCode']} - {ks['variantName']}" for ks in kspecs]

                for i in range(count):
                    vin, ok1 = QInputDialog.getText(self, f"VIN {i+1}/{count}", "Enter Full VIN:")
                    if not ok1 or not vin.strip():
                        QMessageBox.warning(self, "Input Cancelled", "Skipping VIN entry.")
                        continue

                    engine, ok2 = QInputDialog.getText(self, f"Engine {i+1}/{count}", "Enter Engine Number:")
                    if not ok2 or not engine.strip():
                        QMessageBox.warning(self, "Input Cancelled", "Skipping VIN entry.")
                        continue

                    selected_model, ok3 = QInputDialog.getItem(self, f"Select Case Spec {i+1}/{count}",
                                                               "Choose Case Spec:", model_options, 0, False)
                    if not ok3:
                        QMessageBox.warning(self, "Input Cancelled", "Skipping VIN entry.")
                        continue

                    selected_code = selected_model.split(" - ")[0].strip()

                    payload = {
                        "vin": vin.strip(),
                        "engineNumber": engine.strip(),
                        "caseSpecCode": selected_code
                    }

                    submit_url = f"{self.backend_ip.rstrip('/')}/upload_vin_spec"
                    r = requests.post(submit_url, json=payload, timeout=10)
                    if r.status_code == 200:
                        QMessageBox.information(self, "✅ Success", f"Uploaded VIN {vin} successfully.")
                    else:
                        QMessageBox.warning(self, "⚠️ Failed", f"Failed to upload VIN {vin}: {r.text}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to fetch KSpecs: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Exception occurred: {str(e)}")

    def remove_specific_worker(self):
        try:
            fetch_url = f"{self.backend_ip.rstrip('/')}/workers"
            response = requests.get(fetch_url, timeout=10)
            if response.status_code != 200:
                QMessageBox.warning(self, "⚠️ Error", f"Failed to fetch workers: {response.text}")
                return

            workers = response.json().get("workers", [])
            if not workers:
                QMessageBox.information(self, "ℹ️ No Workers", "No Cal Line workers found in the system.")
                return

            options = [f"{w['name']} ({w['pno']}) - {w['department']}" for w in workers]
            selected_option, ok = QInputDialog.getItem(self, "Select Worker", "Choose worker to remove:", options, 0, False)
            if ok and selected_option:
                pno = selected_option.split('(')[-1].split(')')[0].strip()
                del_url = f"{self.backend_ip.rstrip('/')}/remove_worker/{pno}"
                del_resp = requests.delete(del_url, timeout=10)
                if del_resp.status_code == 200:
                    QMessageBox.information(self, "✅ Deleted", f"Worker {pno} deleted successfully.")
                else:
                    QMessageBox.warning(self, "⚠️ Error", f"Failed to delete worker: {del_resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Exception occurred: {str(e)}")

    def list_all_workers(self):
        try:
            url = f"{self.backend_ip.rstrip('/')}/workers"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                workers = response.json().get("workers", [])
                if not workers:
                    QMessageBox.information(self, "ℹ️ No Workers", "No Cal Line workers found in the system.")
                    return

                self.show_workers_table(workers)
            else:
                QMessageBox.warning(self, "⚠️ Failed", f"Failed to fetch workers: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Exception occurred: {str(e)}")

    def show_workers_table(self, workers):
        dialog = QWidget()
        dialog.setWindowTitle("📋 Cal Line Workers")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.resize(800, 500)
        dialog.setStyleSheet(MODERN_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📋 Cal Line Workers")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin: 15px; padding: 10px;")
        layout.addWidget(title)
        
        # Table
        table = QTableWidget()
        table.setRowCount(len(workers))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Name", "P-Number", "Department"])
        
        # Set table properties for better visibility
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setShowGrid(True)
        table.setSortingEnabled(True)
        
        for row, worker in enumerate(workers):
            name_item = QTableWidgetItem(worker['name'])
            pno_item = QTableWidgetItem(worker['pno'])
            dept_item = QTableWidgetItem(worker['department'])
            
            # Center align the text
            name_item.setTextAlignment(Qt.AlignCenter)
            pno_item.setTextAlignment(Qt.AlignCenter)
            dept_item.setTextAlignment(Qt.AlignCenter)
            
            table.setItem(row, 0, name_item)
            table.setItem(row, 1, pno_item)
            table.setItem(row, 2, dept_item)
        
        # Auto-resize columns
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Set minimum row height
        table.verticalHeader().setDefaultSectionSize(40)
        table.verticalHeader().hide()  # Hide row numbers
        
        layout.addWidget(table)
        
        # Close button
        close_btn = QPushButton("✅ Close")
        close_btn.setStyleSheet("font-size: 16px; padding: 10px 30px; margin: 10px;")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.show()
        self.workers_dialog = dialog  # Keep reference to prevent garbage collection

    def view_all_vins(self):
        try:
            url = f"{self.backend_ip.rstrip('/')}/list_all_vins"  # <-- Updated
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                vins = response.json()
                if not vins:
                    QMessageBox.information(self, "ℹ️ No VINs", "No VIN specifications found in the system.")
                    return

                self.show_vins_table(vins)
            else:
                QMessageBox.warning(self, "⚠️ Failed", f"Failed to fetch VINs: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Exception occurred: {str(e)}")

    def show_vins_table(self, vins):
        dialog = QWidget()
        dialog.setWindowTitle("📄 VIN Specifications")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.resize(1000, 600)
        dialog.setStyleSheet(MODERN_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📄 VIN Specifications")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin: 15px; padding: 10px;")
        layout.addWidget(title)
        
        # Table
        table = QTableWidget()
        table.setRowCount(len(vins))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["VIN Number", "Engine Number", "Case Specification"])
        
        # Set table properties for better visibility
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setShowGrid(True)
        table.setSortingEnabled(True)
        
        for row, vin_data in enumerate(vins):
            vin_item = QTableWidgetItem(vin_data['VIN_NUMBER'])
            engine_item = QTableWidgetItem(vin_data['ENGINE_NUMBER'])
            case_item = QTableWidgetItem(vin_data['CASE SPECIFICATION'])
            
            # Center align the text
            vin_item.setTextAlignment(Qt.AlignCenter)
            engine_item.setTextAlignment(Qt.AlignCenter)
            case_item.setTextAlignment(Qt.AlignCenter)
            
            table.setItem(row, 0, vin_item)
            table.setItem(row, 1, engine_item)
            table.setItem(row, 2, case_item)
        
        # Auto-resize columns
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Set minimum row height
        table.verticalHeader().setDefaultSectionSize(40)
        table.verticalHeader().hide()  # Hide row numbers
        
        layout.addWidget(table)
        
        # Close button
        close_btn = QPushButton("✅ Close")
        close_btn.setStyleSheet("font-size: 16px; padding: 10px 30px; margin: 10px;")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.show()
        self.vins_dialog = dialog  # Keep reference to prevent garbage collection


    def remove_all_vins(self):
        confirm = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete ALL VIN specifications?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                url = f"{self.backend_ip.rstrip('/')}/remove_all_vins"
                response = requests.delete(url, timeout=10)
                if response.status_code == 200:
                    QMessageBox.information(self, "✅ Deleted", "All VIN specifications have been deleted.")
                else:
                    QMessageBox.warning(self, "⚠️ Failed", f"Failed to delete: {response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Exception occurred: {str(e)}")

    def remove_specific_vin(self):
        try:
            fetch_url = f"{self.backend_ip.rstrip('/')}/vins"
            response = requests.get(fetch_url, timeout=10)
            if response.status_code != 200:
                QMessageBox.warning(self, "⚠️ Error", f"Failed to fetch VINs: {response.text}")
                return

            vins = response.json().get("vins", [])
            if not vins:
                QMessageBox.information(self, "ℹ️ No VINs", "No VINs found in the system.")
                return

            selected_vin, ok = QInputDialog.getItem(self, "Select VIN", "Choose VIN to remove:", vins, 0, False)
            if ok and selected_vin:
                del_url = f"{self.backend_ip.rstrip('/')}/remove_vin/{selected_vin}"
                del_resp = requests.delete(del_url, timeout=10)
                if del_resp.status_code == 200:
                    QMessageBox.information(self, "✅ Deleted", f"VIN {selected_vin} deleted successfully.")
                else:
                    QMessageBox.warning(self, "⚠️ Error", f"Failed to delete VIN: {del_resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalLineVINUploader()
    window.showMaximized()
    sys.exit(app.exec_())
