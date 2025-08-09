import os 
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import sys
import zipfile
import random
import shutil
import yaml
import subprocess
from ultralytics import YOLO
import cv2
from PIL import Image
import numpy as np
from PyQt5.QtWidgets import QApplication,QGroupBox,QGridLayout,QScrollArea,QTabWidget, QMainWindow,QLineEdit,QSlider, QTextEdit, QWidget, QVBoxLayout,QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QComboBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon, QTransform, QImage

class TrainingThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self,yaml_path,epochs,save_dir,model_name):
        super().__init__()
        self.yaml_path = yaml_path
        self.epochs = epochs
        self.save_dir = save_dir
        self.model_name = model_name
        
    def run(self):
        command=[
            "yolo",
            "task=obb",
            "mode=train",
            f"data={self.yaml_path}",
            f"epochs={self.epochs}",
            f"project={self.save_dir}",
            f"name={self.model_name}",
            "exist_ok=True",
            "imgsz=640",
            "device=cpu",
            "workers=4",
            "verbose=True"
        ]
        
        process=subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,bufsize=1)
        
        for line in process.stdout:
            self.log_signal.emit(line)
            
        process.wait()
        self.finished_signal.emit() 
        
class MODELTrainerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Detector Modeler")
        self.setWindowIcon(QIcon("logo.png"))
        self.setGeometry(300,200,800,600)
        self.resize(900,700)
        
        
        self.source_path = ""
        self.destination_path = ""
        self.image_rotation_angles={}
        self.current_enlarged_image_path= None
        self.browsed_model_path = None
        self.dark_mode_enabled = False
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.tabs=QTabWidget()
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.tabs)
        
        self.train_tab=QWidget()
        self.train_layout=QVBoxLayout(self.train_tab)
        
        #model name ka
        model_group = QGroupBox("Model Name")
        model_layout= QVBoxLayout()
        self.model_name_input=QLineEdit()
        self.model_name_input.setPlaceholderText("Enter your model name (default: custom_train)")
        model_layout.addWidget(QLabel("Model Name:"))
        model_layout.addWidget(self.model_name_input)
        model_group.setLayout(model_layout)
        
        #zip uploading ka 
        zip_group=QGroupBox("📦 Upload ZIP Dataset")
        zip_layout = QVBoxLayout()
        self.select_source_button=QPushButton("Select ZIP File")
        self.select_source_button.clicked.connect(self.select_zip_file)
        self.source_path_label = QLabel("🔍 Source ZIP Path: Not selected")
        zip_layout.addWidget(self.select_source_button)
        zip_layout.addWidget(self.source_path_label)
        zip_group.setLayout(zip_layout)
        
        #Destination ka 
        dest_group = QGroupBox("Output Folder")
        dest_layout= QVBoxLayout()
        self.select_dest_button=QPushButton("Select Destination Folder")
        self.select_dest_button.clicked.connect(self.select_destination_folder)
        self.dest_path_label = QLabel("💾 Destination Folder: Not set")
        dest_layout.addWidget(self.select_dest_button)
        dest_layout.addWidget(self.dest_path_label)
        dest_group.setLayout(dest_layout)
        
        #submit ka
        self.submit_button = QPushButton ("Submit and Prepare Dataset")
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.submit_processing)
        
        #epochs
        epoch_group=QGroupBox("🔁 Training Settings")
        epoch_layout = QVBoxLayout()
        self.epoch_label = QLabel("Number of Epochs: 60")
        self.epoch_slider= QSlider(Qt.Horizontal)
        self.epoch_slider.setMinimum(1)
        self.epoch_slider.setMaximum(100)
        self.epoch_slider.setValue(60)
        self.epoch_slider.valueChanged.connect(
            lambda val: self.epoch_label.setText(f"Number of epochs: {val}")
        )
        epoch_layout.addWidget(self.epoch_label)
        epoch_layout.addWidget(self.epoch_slider)
        epoch_group.setLayout(epoch_layout)
        
        #training butt-onnn hehe
        self.train_button=QPushButton("Start training")
        self.train_button.setEnabled(False)
        self.train_button.clicked.connect(self.start_training)
        
        #console stfs
        console_group=QGroupBox("Console output")
        console_layout = QVBoxLayout()
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        console_layout.addWidget(self.console_output)
        console_group.setLayout(console_layout)
        
        self.train_layout.addWidget(model_group)
        self.train_layout.addWidget(zip_group)
        self.train_layout.addWidget(dest_group)
        self.train_layout.addWidget(self.submit_button)
        self.train_layout.addWidget(epoch_group)
        self.train_layout.addWidget(self.train_button)
        self.train_layout.addWidget(console_group)
        
        self.tabs.addTab(self.train_tab,"Train")
        
        #Validation tab
        self.validate_tab = QWidget()
        self.validate_layout=QVBoxLayout(self.validate_tab)
        
        # Import Model section
        model_import_group = QGroupBox("🤖 Import Model")
        model_import_layout = QVBoxLayout()
        
        # Model type dropdown
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["Import Current Model", "Import Other Model"])
        self.model_type_combo.currentTextChanged.connect(self.on_model_type_changed)
        
        # Browse button for other model (initially hidden)
        self.browse_model_button = QPushButton("Browse Model File")
        self.browse_model_button.clicked.connect(self.browse_model_file)
        self.browse_model_button.setVisible(False)
        
        # Model path label
        self.model_path_label = QLabel("No model selected")
        self.model_path_label.setStyleSheet("color: red;")
        
        # Import button
        self.import_model_button = QPushButton("Import Model")
        self.import_model_button.clicked.connect(self.import_selected_model)
        self.import_model_button.setEnabled(False)
        
        model_import_layout.addWidget(QLabel("Select Model Type:"))
        model_import_layout.addWidget(self.model_type_combo)
        model_import_layout.addWidget(self.browse_model_button)
        model_import_layout.addWidget(self.model_path_label)
        model_import_layout.addWidget(self.import_model_button)
        model_import_group.setLayout(model_import_layout)
        
        # Track selected model
        self.selected_model_path = None
        self.current_model_available = False
        
        #Enlarging the image
        self.image_display_label = QLabel("🔍 Click an image from the list below to preview.")
        self.image_display_label.setAlignment(Qt.AlignCenter)
        self.image_display_label.setFixedHeight(600)
        self.image_display_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        
        #rotate button
        self.rotate_button=QPushButton("Rotate 90")
        self.rotate_button.setEnabled(False)
        self.rotate_button.clicked.connect(self.rotate_current_image)
        
        #run inference button
        self.inference_button = QPushButton("Run Inference")
        self.inference_button.setEnabled(False)
        self.inference_button.clicked.connect(self.run_inference_on_image)
        
        #thumbnail preview
        self.thumbnail_scroll = QScrollArea()
        self.thumbnail_container = QWidget()
        self.thumbnail_layout = QGridLayout(self.thumbnail_container)
        self.thumbnail_scroll.setWidgetResizable(True)
        self.thumbnail_scroll.setWidget(self.thumbnail_container)
        
        # Left side - Main image display
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.image_display_label)
        left_layout.addWidget(self.rotate_button)
        left_layout.addWidget(self.inference_button)
        
        # Right side - Controls and thumbnails arranged vertically
        right_layout = QVBoxLayout()
        
        # Button group at the top right
        button_group = QGroupBox("📂 Load Images")
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        self.valset_button = QPushButton("📂 Validate with Val Set")
        self.valset_button.clicked.connect(self.load_val_set_images)
        
        self.import_button = QPushButton("📥 Import to Validate")
        self.import_button.clicked.connect(self.import_images_to_validate)
        
        button_layout.addWidget(self.valset_button)
        button_layout.addWidget(self.import_button)
        button_group.setLayout(button_layout)
        
        # Thumbnail group below the buttons
        thumbnail_group = QGroupBox("🖼️ Image Thumbnails")
        thumbnail_group_layout = QVBoxLayout()
        thumbnail_group_layout.addWidget(self.thumbnail_scroll)
        thumbnail_group.setLayout(thumbnail_group_layout)
        
        # Add groups to right layout
        right_layout.addWidget(button_group)
        right_layout.addWidget(thumbnail_group)
        
        # Main horizontal layout combining left and right
        main_validate_layout = QHBoxLayout()
        main_validate_layout.addLayout(left_layout, 2)  # Left side takes 2/3 of space
        main_validate_layout.addLayout(right_layout, 1)  # Right side takes 1/3 of space
        
        #Final Layout 
        self.validate_layout.addWidget(model_import_group)
        self.validate_layout.addLayout(main_validate_layout)
        
        
        self.tabs.addTab(self.validate_tab,"Validate")
        self.tabs.setTabEnabled(1,True)
        
        # Crop tab
        self.crop_tab = QWidget()
        self.crop_layout = QVBoxLayout(self.crop_tab)
        
        # Model selection group
        crop_model_group = QGroupBox("🤖 Select YOLO Model")
        crop_model_layout = QVBoxLayout()
        
        self.crop_model_path_input = QLineEdit()
        self.crop_model_path_input.setPlaceholderText("Select YOLO model file (.pt, .torchscript, or .onnx)")
        self.crop_model_path_input.setReadOnly(True)
        
        self.browse_crop_model_button = QPushButton("Browse Model File")
        self.browse_crop_model_button.clicked.connect(self.browse_crop_model)
        
        crop_model_layout.addWidget(QLabel("Model Path:"))
        crop_model_layout.addWidget(self.crop_model_path_input)
        crop_model_layout.addWidget(self.browse_crop_model_button)
        crop_model_group.setLayout(crop_model_layout)
        
        # Import directory group
        import_dir_group = QGroupBox("📂 Import Directory")
        import_dir_layout = QVBoxLayout()
        
        self.import_dir_path_input = QLineEdit()
        self.import_dir_path_input.setPlaceholderText("Select folder containing images to be cropped")
        self.import_dir_path_input.setReadOnly(True)
        
        self.browse_import_dir_button = QPushButton("Browse Import Directory")
        self.browse_import_dir_button.clicked.connect(self.browse_import_directory)
        
        import_dir_layout.addWidget(QLabel("Import Directory:"))
        import_dir_layout.addWidget(self.import_dir_path_input)
        import_dir_layout.addWidget(self.browse_import_dir_button)
        import_dir_group.setLayout(import_dir_layout)
        
        # Export directory group
        export_dir_group = QGroupBox("💾 Export Directory")
        export_dir_layout = QVBoxLayout()
        
        self.crop_export_dir_input = QLineEdit()
        self.crop_export_dir_input.setPlaceholderText("Select folder where cropped images will be saved")
        self.crop_export_dir_input.setReadOnly(True)
        
        self.browse_crop_export_button = QPushButton("Browse Export Directory")
        self.browse_crop_export_button.clicked.connect(self.browse_crop_export_directory)
        
        export_dir_layout.addWidget(QLabel("Export Directory:"))
        export_dir_layout.addWidget(self.crop_export_dir_input)
        export_dir_layout.addWidget(self.browse_crop_export_button)
        export_dir_group.setLayout(export_dir_layout)
        
        # Start cropping button
        self.start_crop_button = QPushButton("🔪 Start Cropping Process")
        self.start_crop_button.setEnabled(False)
        self.start_crop_button.clicked.connect(self.start_cropping_process)
        self.start_crop_button.setFixedHeight(50)
        
        # Progress and status
        self.crop_status_label = QLabel("Ready to start cropping...")
        self.crop_status_label.setStyleSheet("color: blue; font-weight: bold;")
        
        # Console output for cropping
        crop_console_group = QGroupBox("📋 Cropping Progress")
        crop_console_layout = QVBoxLayout()
        self.crop_console_output = QTextEdit()
        self.crop_console_output.setReadOnly(True)
        self.crop_console_output.setMaximumHeight(200)
        crop_console_layout.addWidget(self.crop_console_output)
        crop_console_group.setLayout(crop_console_layout)
        
        # Add all groups to crop layout
        self.crop_layout.addWidget(crop_model_group)
        self.crop_layout.addWidget(import_dir_group)
        self.crop_layout.addWidget(export_dir_group)
        self.crop_layout.addWidget(self.start_crop_button)
        self.crop_layout.addWidget(self.crop_status_label)
        self.crop_layout.addWidget(crop_console_group)
        self.crop_layout.addStretch()
        
        # Initialize crop variables
        self.crop_model_path = ""
        self.import_directory = ""
        self.crop_export_directory = ""
        
        self.tabs.addTab(self.crop_tab, "Crop")
        
        # Settings tab
        self.settings_tab = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_tab)
        
        # Theme settings group
        theme_group = QGroupBox("🎨 Theme Settings")
        theme_layout = QVBoxLayout()
        
        # Dark mode toggle button
        self.dark_mode_button = QPushButton("🌓 Toggle Dark Mode")
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        self.dark_mode_button.setFixedSize(200, 40)
        
        # Theme description
        theme_description = QLabel("Switch between light and dark themes for better visibility.")
        theme_description.setWordWrap(True)
        theme_description.setStyleSheet("color: gray; font-style: italic;")
        
        theme_layout.addWidget(self.dark_mode_button)
        theme_layout.addWidget(theme_description)
        theme_layout.addStretch()
        theme_group.setLayout(theme_layout)
        
        # Add theme group to settings layout
        self.settings_layout.addWidget(theme_group)
        self.settings_layout.addStretch()
        
        # Add settings tab
        self.tabs.addTab(self.settings_tab, "Settings")
        
        self.central_widget.setLayout(main_layout)
        
        
    def log(self, message):
        print(message)
        self.console_output.append(message)
    
    def start_training(self): 
        model_name = self.model_name_input.text().strip()
        if not model_name:
            model_name="custom_train"
            
        yaml_path=os.path.join(self.destination_path, "dataset", "data.yaml")
        if not os.path.exists(yaml_path):
            QMessageBox.critical(self, "Error", "YAML file not found. Please prepare the dataset first.")
            return
        self.console_output.clear()
        self.console_output.append("Starting training...")
        
        epochs = self.epoch_slider.value()
        self.train_thread = TrainingThread(yaml_path,epochs, self.destination_path,model_name=model_name)
        self.train_thread.log_signal.connect(self.console_output.append)
        self.train_thread.finished_signal.connect(self.on_training_complete)
        self.train_thread.start()
    
    def on_training_complete(self):
        self.console_output.append("Training Completed!")
        self.tabs.setTabEnabled(1,True)
        self.current_model_available = True
        if self.model_type_combo.currentText() == "Import Current Model":
            self.import_model_button.setEnabled(True)
            self.model_path_label.setText("Current trained model ready to import")
            self.model_path_label.setStyleSheet("color: green;")
    
    def load_val_set_images(self):
        val_dir = os.path.join(self.destination_path,"dataset","images","val")
        if not os.path.exists(val_dir):
            QMessageBox.critical(self,"Error","Validation images directory not found")
            return
        
        images= [f for f in os.listdir(val_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        while self.thumbnail_layout.count():
            child = self.thumbnail_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        for i, image_file in enumerate(images):
            image_path = os.path.join(val_dir, image_file)
            pixmap = QPixmap(image_path).scaled(120,120,Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            thumb_button = QPushButton()
            thumb_button.setIcon(QIcon(pixmap))
            thumb_button.setIconSize(QSize(120,120))
            thumb_button.setFixedSize(130,130)
            thumb_button.clicked.connect(lambda _, p=image_path: self.show_enlarged_image(p))
            
            row,col = divmod(i,6)
            self.thumbnail_layout.addWidget(thumb_button,row,col)
        
    def import_images_to_validate(self):
        file_dialog = QFileDialog()
        files,_ =file_dialog.getOpenFileNames(self,"Select Images","","Image Files(*.png *.jpg *jpeg)")
        if files:
            folder = os.path.dirname(files[0])
            image_files = [os.path.basename(f) for f in files]
            self.display_validation_image_list(image_files,folder)
    
    def display_validation_image_list(self, image_files, folder_path):
        # Clear previous thumbnails
        while self.thumbnail_layout.count():
            child = self.thumbnail_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add new thumbnails
        for i, image_file in enumerate(image_files):
            image_path = os.path.join(folder_path, image_file)
            pixmap = QPixmap(image_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            thumb_button = QPushButton()
            thumb_button.setIcon(QIcon(pixmap))
            thumb_button.setIconSize(QSize(120, 120))
            thumb_button.setFixedSize(130, 130)
            thumb_button.clicked.connect(lambda _, p=image_path: self.show_enlarged_image(p))
            
            row, col = divmod(i, 6)
            self.thumbnail_layout.addWidget(thumb_button, row, col)

            
    def show_enlarged_image(self, image_path):
        if not os.path.exists(image_path):
            QMessageBox.warning(self, "Error", "Image not found")
            return 

        self.current_enlarged_image_path = image_path

        if image_path not in self.image_rotation_angles:
            self.image_rotation_angles[image_path] = 0

        self.display_image_with_rotation(image_path)
        self.rotate_button.setEnabled(True)
        self.inference_button.setEnabled(True)
        
    def run_inference_on_image(self):
        if not self.current_enlarged_image_path:
            QMessageBox.warning(self,"Error","No image selected for inference.")
            return
        
        if not self.selected_model_path:
            QMessageBox.warning(self, "Error", "Please choose a model first using the Import Model section.")
            return
        
        try:
            angle = self.image_rotation_angles.get(self.current_enlarged_image_path,0)
            pil_image = Image.open(self.current_enlarged_image_path).convert("RGB")
            if angle!=0:
                pil_image = pil_image.rotate(-angle,expand=True)
            
            temp_path=os.path.join(os.getcwd(),"temp_rotated_input.jpg")
            pil_image.save(temp_path)
            
            # Log model type for debugging
            model_ext = os.path.splitext(self.selected_model_path)[1].lower()
            if model_ext == '.pt':
                model_type = "PyTorch"
            elif model_ext == '.torchscript':
                model_type = "TorchScript"
            else:
                model_type = "ONNX"
            self.log(f"Running inference with {model_type} model...")
            
            try:
                model = YOLO(self.selected_model_path)
                
                # Use different inference parameters for ONNX models
                if model_ext == '.onnx':
                    # ONNX models might need different parameters
                    results = model.predict(temp_path, conf=0.4, verbose=False, imgsz=640)
                else:
                    # PyTorch and TorchScript models use standard method
                    results = model(temp_path, conf=0.4)
                
                if not results or len(results) == 0:
                    QMessageBox.information(self,"Inference","No objects detected in the image")
                    self.display_image_with_rotation(self.current_enlarged_image_path)
                    return
                
                result_image = results[0].plot()
                
                height,width,channel= result_image.shape
                bytes_per_line=3*width
                result_image_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
                qimage=QImage(result_image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage).scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                self.image_display_label.setPixmap(pixmap)
                self.log(f"Inference completed successfully with {model_type} model")
                
            except Exception as inference_error:
                raise Exception(f"Inference failed with {model_type} model: {str(inference_error)}")
            
            finally:
                # Always clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        except Exception as e:
            error_msg = str(e)
            if "ONNX" in error_msg or "onnx" in error_msg.lower():
                error_msg += "\n\nONNX Troubleshooting:\n• Install onnxruntime: pip install onnxruntime\n• Try using a PyTorch (.pt) model instead\n• Check if the ONNX model is corrupted"
            
            QMessageBox.critical(self,"Inference Error",f"An error occurred during inference:\n{error_msg}")
            self.log(f"Inference error: {error_msg}")
            
            # Clean up temp file on error
            temp_path=os.path.join(os.getcwd(),"temp_rotated_input.jpg")
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    def display_image_with_rotation(self, image_path):
        try:
            angle = self.image_rotation_angles.get(image_path, 0)
            pixmap = QPixmap(image_path)
            if angle != 0:
                transform = QTransform().rotate(angle)
                pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)

            self.image_display_label.setPixmap(
                pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display image:\n{str(e)}")

    
    def rotate_current_image(self):
        if not self.current_enlarged_image_path:
            return
        
        prev_angle = self.image_rotation_angles.get(self.current_enlarged_image_path,0)
        new_angle = (prev_angle+90)%360
        self.image_rotation_angles[self.current_enlarged_image_path]=new_angle
        
        self.display_image_with_rotation(self.current_enlarged_image_path)
            

                     
    def normalize_quad_coords(Self,coords,img_w,img_h):
        normalized=[]
        for i in range(0, len(coords), 2):
            x = coords[i] / img_w
            y = coords[i + 1] / img_h
            normalized.extend([round(x, 6), round(y, 6)])
        return normalized
    
    def select_zip_file(self):
        zip_path, _ = QFileDialog.getOpenFileName(self, "Select ZIP File", "", "ZIP Files (*.zip)")
        if zip_path:
            self.source_path = zip_path
            self.source_path_label.setText(f"🔍Source ZIP Path: {zip_path}")
            self.log(f"Selected ZIP file: {zip_path}")
            self.check_ready_to_submit()
            
        
    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self,"Select Destination Folder")
        if folder:
            self.destination_path = folder
            self.dest_path_label.setText(f"💾Destination Folder: {folder}")
            self.log(f"Selected destination folder: {folder}")
            self.check_ready_to_submit()
            
        
    
    def check_ready_to_submit(self):
        if self.source_path and self.destination_path:
            self.submit_button.setEnabled(True)
            self.log("Ready to submit: Source and destination paths are set.")
            
    
    def submit_processing(self):
        working_dir = os.path.join(self.destination_path, "dataset")
        try:
            if os.path.exists(working_dir):
                shutil.rmtree(working_dir)
            os.makedirs(working_dir)
            
            with zipfile.ZipFile(self.source_path, 'r') as zip_ref:
                zip_ref.extractall(working_dir)
                
            self.prepare_dataset(working_dir)
            self.train_button.setEnabled(True)
            QMessageBox.information(self, "Success", "Dataset prepared successfully!")
            self.log("Dataset prepared successfully!")
        except Exception as e:
            self.log(f"Error preparing dataset: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to prepare dataset: {str(e)}")
        
            
    def prepare_dataset(self, working_dir):
        images_dir = os.path.join(working_dir, "images")
        labels_dir = os.path.join(working_dir, "labels")
        classes_path= os.path.join(working_dir, "classes.txt")
        assert os.path.exists(images_dir), "Images directory not found"
        assert os.path.exists(labels_dir), "Labels directory not found"
        assert os.path.exists(classes_path), "Classes file not found"
        
        #Read classes
        with open(classes_path, 'r') as f:
            class_names = [line.strip() for line in f.readlines() if line.strip()]
        nc=len(class_names)
        print(nc)
        
        train_images_dir = os.path.join(working_dir,"images/train")
        val_images_dir = os.path.join(working_dir, "images/val")
        train_labels_dir = os.path.join(working_dir, "labels/train")
        val_labels_dir = os.path.join(working_dir, "labels/val")
        os.makedirs(train_images_dir, exist_ok=True)
        os.makedirs(val_images_dir, exist_ok=True)
        os.makedirs(train_labels_dir, exist_ok=True)
        os.makedirs(val_labels_dir, exist_ok=True)
        
        images_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        print("Total images:", len(images_files))
        self.log(f"Total images found: {len(images_files)}")
        self.log(f"Total classes: {nc}")
        
        random.shuffle(images_files)
        split_idx = int(0.85 * len(images_files))
        
        train_files = images_files[:split_idx]
        val_files = images_files[split_idx:]
        def move_files_normalized(file_list,dest_img,dest_lbl):
            for img_file in file_list:
                base = os.path.splitext(img_file)[0]
                label_file = base + ".txt"
                
                src_img = os.path.join(images_dir, img_file)
                dest_img_path = os.path.join(dest_img, img_file)
                
                # Get actual image dimensions before moving
                try:
                    with Image.open(src_img) as img:
                        img_w, img_h = img.size
                except Exception as e:
                    print(f"Error reading image {img_file}: {e}")
                    img_w, img_h = 1280, 720  # fallback to default
                
                shutil.move(src_img, dest_img_path)
                
                #normalizing nw
                src_label = os.path.join(labels_dir, label_file)
                dest_label_path = os.path.join(dest_lbl, label_file)
                
                if os.path.exists(src_label):
                    with open(src_label, 'r') as f:
                        lines=f.readlines()
                    
                    new_lines = []
                    for line in lines:
                        parts=line.strip().split()
                        if len(parts) == 1:
                            dot_split = line.strip().split()
                            if len(dot_split) > 1 and dot_split[0].isdigit():
                                class_id = dot_split[0]
                                rest = ".".join(dot_split[1:]).strip().split()
                                parts = [class_id] + rest
                                
                        if len(parts) == 9:
                            class_id = int(parts[0])
                            coords = list(map(float, parts[1:]))
                            normalized = self.normalize_quad_coords(coords, img_w, img_h)
                            line_str = f"{class_id} " + " ".join(f"{v:.6f}" for v in normalized)
                            new_lines.append(line_str)
                        else:
                            print(f"Skipping line with unexpected format: {line.strip()}")
                    
                    with open(dest_label_path, 'w') as f:
                        f.write("\n".join(new_lines) + "\n")
                    
                    os.remove(src_label)
                else:
                    open(dest_label_path, 'w').close()
        
        move_files_normalized(train_files, train_images_dir, train_labels_dir)
        move_files_normalized(val_files, val_images_dir, val_labels_dir)
        
        yaml_path = os.path.join(working_dir, "data.yaml")
        with open(yaml_path, 'w') as f:
            f.write(f"path: {os.path.abspath(working_dir)}\n")
            f.write(f"train: images/train\n")
            f.write(f"val: images/val\n\n")
            f.write(f"nc: {nc}\n")
            f.write(f"names: {class_names}")
        
        with open(yaml_path, 'r') as f:
            yaml_content = yaml.safe_load(f)
            self.log("YAML Configuration:")
            self.log(yaml.dump(yaml_content, default_flow_style=False))

        print("✅ Dataset ready at:", working_dir)

    def on_model_type_changed(self):
        if self.model_type_combo.currentText() == "Import Other Model":
            self.browse_model_button.setVisible(True)
            self.import_model_button.setEnabled(False)
            self.model_path_label.setText("Please browse and select a model file")
            self.model_path_label.setStyleSheet("color: red;")
        else:  # Import Current Model
            self.browse_model_button.setVisible(False)
            if self.current_model_available:
                self.import_model_button.setEnabled(True)
                self.model_path_label.setText("Current trained model ready to import")
                self.model_path_label.setStyleSheet("color: green;")
            else:
                self.import_model_button.setEnabled(False)
                self.model_path_label.setText("No current model available. Please train a model first.")
                self.model_path_label.setStyleSheet("color: red;")
    
    def browse_model_file(self):
        model_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Model File", 
            "", 
            "All Supported Models (*.pt *.torchscript *.onnx);;PyTorch Models (*.pt);;TorchScript Models (*.torchscript);;ONNX Models (*.onnx);;All Files (*.*)"
        )
        if model_path:
            self.import_model_button.setEnabled(True)
            self.model_path_label.setText(f"Selected: {os.path.basename(model_path)}")
            self.model_path_label.setStyleSheet("color: blue;")
            self.browsed_model_path = model_path
    
    def import_selected_model(self):
        try:
            if self.model_type_combo.currentText() == "Import Current Model":
                model_name = self.model_name_input.text().strip()
                if not model_name:
                    model_name = "custom_train"
                model_path = os.path.join(self.destination_path, model_name, "weights", "best.pt")
                if not os.path.exists(model_path):
                    QMessageBox.warning(self, "Error", f"Current model not found at: {model_path}")
                    return
            else:  # Import Other Model
                if not hasattr(self, 'browsed_model_path') or not self.browsed_model_path:
                    QMessageBox.warning(self, "Error", "Please browse and select a model file first.")
                    return
                model_path = self.browsed_model_path
            
            # Check file extension
            file_ext = os.path.splitext(model_path)[1].lower()
            if file_ext not in ['.pt', '.torchscript', '.onnx']:
                QMessageBox.warning(self, "Error", 
                                  f"Unsupported model format: {file_ext}\n\n"
                                  "Supported formats: .pt (PyTorch), .torchscript (TorchScript), .onnx (ONNX)")
                return
            
            # Test loading the model
            try:
                model = YOLO(model_path)
                
                # Additional validation for ONNX models
                if file_ext == '.onnx':
                    # Try a simple inference test with ONNX model
                    try:
                        import numpy as np
                        # Create a dummy image for tes
                        # ting (640x640x3)
                        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
                        test_results = model.predict(dummy_image, verbose=False)
                        self.log("ONNX model validation successful")
                    except Exception as onnx_error:
                        raise Exception(f"ONNX model validation failed: {str(onnx_error)}")
                
                self.selected_model_path = model_path
                
                # Show success message with model type
                if file_ext == '.pt':
                    model_type = "PyTorch"
                elif file_ext == '.torchscript':
                    model_type = "TorchScript"
                else:
                    model_type = "ONNX"
                self.model_path_label.setText(f"✅ {model_type} model imported: {os.path.basename(model_path)}")
                self.model_path_label.setStyleSheet("color: green;")
                QMessageBox.information(self, "Success", f"{model_type} model imported and validated successfully!")
                self.log(f"{model_type} model imported: {model_path}")
                
            except Exception as model_error:
                raise Exception(f"Model loading failed: {str(model_error)}")
            
        except Exception as e:
            error_msg = str(e)
            if "ONNX" in error_msg:
                error_msg += "\n\nTroubleshooting ONNX issues:\n• Ensure ONNX runtime is installed: pip install onnxruntime\n• Verify the ONNX model is compatible with your YOLO version\n• Try converting the model again if possible"
            
            QMessageBox.critical(self, "Error", f"Failed to import model:\n{error_msg}")
            self.model_path_label.setText("❌ Failed to import model")
            self.model_path_label.setStyleSheet("color: red;")

    def browse_crop_model(self):
        """Browse and select YOLO model for cropping"""
        model_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select YOLO Model", 
            "", 
            "All Supported Models (*.pt *.torchscript *.onnx);;PyTorch Models (*.pt);;TorchScript Models (*.torchscript);;ONNX Models (*.onnx);;All Files (*.*)"
        )
        if model_path:
            self.crop_model_path = model_path
            self.crop_model_path_input.setText(model_path)
            self.crop_log(f"Selected model: {os.path.basename(model_path)}")
            
            # Check file extension and show appropriate warning
            file_ext = os.path.splitext(model_path)[1].lower()
            if file_ext == '.pt':
                QMessageBox.information(self, "Model Selection", 
                                      "✅ PyTorch model selected.\n\n"
                                      "Please ensure this is a YOLO v8 OBB (Oriented Bounding Box) model for best results.")
            elif file_ext == '.torchscript':
                QMessageBox.information(self, "Model Selection", 
                                      "✅ TorchScript model selected.\n\n"
                                      "TorchScript models are compiled PyTorch models for faster inference.")
            elif file_ext == '.onnx':
                # Check if onnxruntime is available
                try:
                    import onnxruntime
                    QMessageBox.information(self, "Model Selection", 
                                          "✅ ONNX model selected.\n\n"
                                          "ONNX runtime detected. Model should work correctly.")
                except ImportError:
                    QMessageBox.warning(self, "ONNX Runtime Missing", 
                                      "⚠️ ONNX model selected but onnxruntime is not installed!\n\n"
                                      "Please install it with: pip install onnxruntime\n\n"
                                      "The model may not work without it.")
            else:
                QMessageBox.warning(self, "Model Selection", 
                                  "⚠️ Unsupported file format detected.\n\n"
                                  "Please select a .pt (PyTorch), .torchscript (TorchScript), or .onnx model file.")
            
            self.check_crop_ready()
    
    def browse_import_directory(self):
        """Browse and select import directory containing images"""
        directory = QFileDialog.getExistingDirectory(self, "Select Import Directory")
        if directory:
            self.import_directory = directory
            self.import_dir_path_input.setText(directory)
            
            # Count images in directory
            image_files = [f for f in os.listdir(directory) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
            self.crop_log(f"Selected import directory: {directory}")
            self.crop_log(f"Found {len(image_files)} image(s) to process")
            self.check_crop_ready()
    
    def browse_crop_export_directory(self):
        """Browse and select export directory for cropped images"""
        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if directory:
            self.crop_export_directory = directory
            self.crop_export_dir_input.setText(directory)
            self.crop_log(f"Selected export directory: {directory}")
            self.check_crop_ready()
    
    def check_crop_ready(self):
        """Check if all required fields are filled for cropping"""
        if self.crop_model_path and self.import_directory and self.crop_export_directory:
            self.start_crop_button.setEnabled(True)
            self.crop_status_label.setText("✅ Ready to start cropping!")
            self.crop_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.start_crop_button.setEnabled(False)
            missing_items = []
            if not self.crop_model_path:
                missing_items.append("Model")
            if not self.import_directory:
                missing_items.append("Import Directory")
            if not self.crop_export_directory:
                missing_items.append("Export Directory")
            
            self.crop_status_label.setText(f"❌ Missing: {', '.join(missing_items)}")
            self.crop_status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def crop_log(self, message):
        """Log message to crop console"""
        print(f"[CROP] {message}")
        self.crop_console_output.append(f"[{self.get_timestamp()}] {message}")
    
    def get_timestamp(self):
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def start_cropping_process(self):
        """Start the cropping process"""
        try:
            self.crop_console_output.clear()
            self.crop_log("Starting cropping process...")
            self.start_crop_button.setEnabled(False)
            self.crop_status_label.setText("🔄 Processing...")
            self.crop_status_label.setStyleSheet("color: orange; font-weight: bold;")
            
            # Load model
            self.crop_log("Loading YOLO model...")
            try:
                model = YOLO(self.crop_model_path)
                
                # Check model type and log it
                model_ext = os.path.splitext(self.crop_model_path)[1].lower()
                if model_ext == '.pt':
                    model_type = "PyTorch"
                elif model_ext == '.torchscript':
                    model_type = "TorchScript"
                else:
                    model_type = "ONNX"
                self.crop_log(f"✅ {model_type} model loaded successfully")
                
                # Test model with a small inference if it's ONNX
                if model_ext == '.onnx':
                    self.crop_log("Validating ONNX model...")
                    try:
                        # Simple validation test
                        import numpy as np
                        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
                        test_results = model.predict(dummy_image, verbose=False)
                        self.crop_log("ONNX model validation passed")
                    except Exception as validation_error:
                        self.crop_log(f"❌ ONNX model validation failed: {str(validation_error)}")
                        raise Exception(f"ONNX model validation failed: {str(validation_error)}")
                        
            except Exception as model_error:
                self.crop_log(f"❌ Failed to load model: {str(model_error)}")
                QMessageBox.critical(self, "Model Error", f"Failed to load model:\n{str(model_error)}")
                self.reset_crop_status()
                return
            
            # Get image files
            image_files = [f for f in os.listdir(self.import_directory) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
            
            if not image_files:
                self.crop_log("❌ No image files found in import directory")
                QMessageBox.warning(self, "No Images", "No image files found in the selected directory.")
                self.reset_crop_status()
                return
            
            # Create export directory if it doesn't exist
            os.makedirs(self.crop_export_directory, exist_ok=True)
            
            total_crops = 0
            processed_images = 0
            
            # Process each image
            for image_file in image_files:
                image_path = os.path.join(self.import_directory, image_file)
                self.crop_log(f"Processing: {image_file}")
                
                try:
                    # Run inference with appropriate method based on model type
                    model_ext = os.path.splitext(self.crop_model_path)[1].lower()
                    
                    if model_ext == '.onnx':
                        # Use predict method for ONNX models with explicit parameters
                        results = model.predict(image_path, conf=0.4, verbose=False, imgsz=640)
                    else:
                        # Use standard call for PyTorch and TorchScript models
                        results = model(image_path, conf=0.4)
                    
                    if not results or len(results) == 0:
                        self.crop_log(f"  ⚠️ No results for {image_file}")
                        continue
                    
                    result = results[0]
                    
                    # Check if any detections were found (OBB model uses .obb instead of .boxes)
                    if result.obb is None or len(result.obb) == 0:
                        self.crop_log(f"  ⚠️ No detections found in {image_file}")
                        continue
                    
                    # Load original image
                    original_image = cv2.imread(image_path)
                    if original_image is None:
                        self.crop_log(f"  ❌ Failed to load {image_file}")
                        continue
                    
                    # Process each detection
                    detections = result.obb
                    base_name = os.path.splitext(image_file)[0]
                    
                    for idx, obb in enumerate(detections):
                        # Get bounding box coordinates from OBB
                        # For OBB, we use xyxy which gives us the axis-aligned bounding box
                        x1, y1, x2, y2 = map(int, obb.xyxy[0].cpu().numpy())
                        
                        # Ensure coordinates are within image bounds
                        height, width = original_image.shape[:2]
                        x1 = max(0, x1)
                        y1 = max(0, y1)
                        x2 = min(width, x2)
                        y2 = min(height, y2)
                        
                        # Crop the image
                        cropped_image = original_image[y1:y2, x1:x2]
                        
                        if cropped_image.size > 0:  # Check if crop is valid
                            # Generate crop filename
                            crop_filename = f"{base_name}_crop_{idx+1}.jpg"
                            crop_path = os.path.join(self.crop_export_directory, crop_filename)
                            
                            # Save cropped image
                            cv2.imwrite(crop_path, cropped_image)
                            total_crops += 1
                            
                            self.crop_log(f"  ✅ Saved crop {idx+1}: {crop_filename}")
                        else:
                            self.crop_log(f"  ⚠️ Invalid crop {idx+1} for {image_file}")
                    
                    processed_images += 1
                    
                except Exception as e:
                    self.crop_log(f"  ❌ Error processing {image_file}: {str(e)}")
                    continue
            
            # Final summary
            self.crop_log("\n" + "="*50)
            self.crop_log(f"📊 CROPPING SUMMARY:")
            self.crop_log(f"📁 Images processed: {processed_images}/{len(image_files)}")
            self.crop_log(f"✂️ Total crops saved: {total_crops}")
            self.crop_log(f"📂 Export directory: {self.crop_export_directory}")
            self.crop_log("="*50)
            
            if total_crops > 0:
                self.crop_status_label.setText(f"✅ Completed! {total_crops} crops saved")
                self.crop_status_label.setStyleSheet("color: green; font-weight: bold;")
                QMessageBox.information(self, "Cropping Complete", 
                                      f"Successfully processed {processed_images} images and saved {total_crops} crops to:\n{self.crop_export_directory}")
            else:
                self.crop_status_label.setText("⚠️ No crops generated")
                self.crop_status_label.setStyleSheet("color: orange; font-weight: bold;")
                QMessageBox.warning(self, "No Crops", "No valid crops were generated. Please check your model and images.")
            
        except Exception as e:
            self.crop_log(f"❌ FATAL ERROR: {str(e)}")
            QMessageBox.critical(self, "Cropping Error", f"An error occurred during cropping:\n{str(e)}")
            self.crop_status_label.setText("❌ Error occurred")
            self.crop_status_label.setStyleSheet("color: red; font-weight: bold;")
        
        finally:
            self.reset_crop_status()
    
    def reset_crop_status(self):
        """Reset cropping status and enable button"""
        self.start_crop_button.setEnabled(True)
        if self.crop_status_label.text().startswith("🔄"):
            self.crop_status_label.setText("Ready to start cropping...")
            self.crop_status_label.setStyleSheet("color: blue; font-weight: bold;")

    def toggle_dark_mode(self):
        """Toggle between light and dark mode themes"""
        if self.dark_mode_enabled:
            # Switch to light mode
            self.setStyleSheet("")
            self.dark_mode_enabled = False
            self.dark_mode_button.setText("🌓 Toggle Dark Mode")
            self.log("☀️ Light mode enabled")
        else:
            # Switch to dark mode
            dark_stylesheet = """
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #3c3c3c;
                }
                QTabBar::tab {
                    background-color: #404040;
                    color: #ffffff;
                    padding: 8px 16px;
                    margin: 2px;
                    border: 1px solid #555555;
                    border-bottom: none;
                    border-radius: 4px 4px 0px 0px;
                }
                QTabBar::tab:selected {
                    background-color: #3c3c3c;
                    border-bottom: 1px solid #3c3c3c;
                }
                QTabBar::tab:hover {
                    background-color: #505050;
                }
                QPushButton {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #505050;
                    border: 1px solid #777777;
                }
                QPushButton:pressed {
                    background-color: #353535;
                }
                QPushButton:disabled {
                    background-color: #2d2d2d;
                    color: #666666;
                    border: 1px solid #444444;
                }
                QLineEdit {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 6px;
                    border-radius: 4px;
                }
                QLineEdit:focus {
                    border: 2px solid #0078d4;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #666666;
                    border-radius: 4px;
                }
                QLabel {
                    color: #ffffff;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #666666;
                    border-radius: 8px;
                    margin: 8px 0px;
                    padding: 8px;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0px 8px 0px 8px;
                    color: #ffffff;
                }
                QComboBox {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 6px;
                    border-radius: 4px;
                }
                QComboBox:hover {
                    border: 1px solid #777777;
                }
                QComboBox::drop-down {
                    border: none;
                    background-color: #505050;
                    border-radius: 4px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #ffffff;
                    width: 0px;
                    height: 0px;
                }
                QComboBox QAbstractItemView {
                    background-color: #404040;
                    color: #ffffff;
                    selection-background-color: #0078d4;
                    border: 1px solid #666666;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #666666;
                    height: 8px;
                    background: #404040;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #0078d4;
                    border: 1px solid #0078d4;
                    width: 18px;
                    height: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }
                QSlider::handle:horizontal:hover {
                    background: #106ebe;
                }
                QScrollArea {
                    background-color: #3c3c3c;
                    border: 1px solid #666666;
                    border-radius: 4px;
                }
                QScrollBar:vertical {
                    background-color: #404040;
                    width: 16px;
                    border-radius: 8px;
                }
                QScrollBar::handle:vertical {
                    background-color: #666666;
                    border-radius: 8px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #777777;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar:horizontal {
                    background-color: #404040;
                    height: 16px;
                    border-radius: 8px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #666666;
                    border-radius: 8px;
                    min-width: 20px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #777777;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
            """
            self.setStyleSheet(dark_stylesheet)
            self.dark_mode_enabled = True
            self.dark_mode_button.setText("☀️ Toggle Light Mode")
            self.log("🌙 Dark mode enabled")

    # ...existing code...
    
if __name__ == "__main__":
    app = QApplication([])
    window = MODELTrainerApp()
    window.showMaximized()
    app.exec_()
