import sys
import os
import zipfile
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QComboBox, QHBoxLayout, QListWidget, QListWidgetItem, QScrollArea,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QAction,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QStyleFactory,
    QMenu, 
)
import random
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QIcon
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
import cv2
import numpy as np

def generate_random_color():
    return tuple(random.randint(50,255)for _ in range(3))



class SettingsDialog(QDialog):
    
    toggle_dark_mode = pyqtSignal()
    
    def __init__(self,current_classes, current_export_dir="",parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings⚙️")
        self.setFixedSize(450, 250)
        
        self.update_classes=current_classes.copy()
        self.export_dir=current_export_dir
        
        
        layout=QVBoxLayout()
        tabs=QTabWidget()
        
        
        #Pehla tab
        class_tab=QWidget()
        class_layout=QVBoxLayout()
        class_layout.addWidget(QLabel("Add class names, separated by commas:"))  
        self.class_input = QLineEdit()
        self.class_input.setText(",".join(current_classes))
        class_layout.addWidget(self.class_input)
        class_tab.setLayout(class_layout)
        
        #Doosra tab
        advanced_tab=QWidget()
        advanced_layout=QVBoxLayout()
        advanced_layout.addWidget(QLabel("Select directory to store images and labels:"))
        
        self.export_path_input = QLineEdit()
        self.export_path_input.setText(current_export_dir)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.choose_export_folder)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.export_path_input)
        path_layout.addWidget(browse_button)
        
        advanced_layout.addLayout(path_layout)
        advanced_tab.setLayout(advanced_layout)
        
        tabs.addTab(class_tab,"Classes")
        tabs.addTab(advanced_tab,"Advanced")
        
        layout.addWidget(tabs)
        
        #Ok/Caneceeceellll boootn
        button_layout=QHBoxLayout()
        ok_button=QPushButton("OK")
        cancel_button=QPushButton("Cancel")
        ok_button.clicked.connect(self.accept) 
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
              
        #self.class_input=QLineEdit()
        #self.class_input.setText(",".join(current_classes))
        #layout.addWidget(self.class_input)

        layout.addLayout(button_layout)
        toggle_theme_button=QPushButton("🌓 Toggle Dark Mode")
        toggle_theme_button.clicked.connect(self.emit_toggle_dark_mode)
        layout.addWidget(toggle_theme_button)
        self.setLayout(layout)
        
    def get_updated_classes(self):
        text=self.class_input.text()
        classes=[c.strip() for c in text.split(",") if c.strip()]
        return classes
    
    def choose_export_folder(self):
        folder=QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if folder:
            self.export_path_input.setText(folder)
    
    def get_export_directory(self):
        return self.export_path_input.text().strip()
    
    def emit_toggle_dark_mode(self):
        self.toggle_dark_mode.emit()
    
class Annotator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FAP: Fully Automated Production Annotator")
        
        BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(BASE_DIR, "logo.png")
        self.setWindowIcon(QIcon(icon_path))
        #self.setWindowIcon(QIcon("logo.png"))  # Ensure you have a logo.png in the same directory
        self.setGeometry(100, 100, 1000, 700)
        self.unsaved_changes=False

        self.class_names=["Autobiography","HSE"]
        self.class_colors={class_name:generate_random_color() for class_name in self.class_names}
        self.image = None
        self.image_path=""
        self.points = []
        self.class_name = ""
        self.image_dir=""
        self.image_list=[]
        self.annotations=[]
        self.current_points=[]
        self.export_dir=""
        self.dark_mode_enabled=False
        self.import_as_bw=False  # Store user preference for black and white import
        self.rotation_angle=0  # Track current rotation (0, 90, 180, 270)
        self.zoom_factor=1.0  # Track zoom level
        self.original_image=None  # Store original unscaled image

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        ##left side stuffs
        left_layout = QVBoxLayout()

        # Class selector
        self.class_dropdown = QComboBox()
        self.class_dropdown.addItems(self.class_names)
        self.class_dropdown.currentIndexChanged.connect(self.update_active_class_label)# Add your classes here
        self.active_class_label=QLabel()
        self.update_active_class_label()
        
        
        # Buttons
        load_button = QPushButton("Load")
        save_button = QPushButton("Save Annotation")
        clear_button = QPushButton("Clear Points")
        preview_button = QPushButton("Preview Annotation")
        reset_button = QPushButton("Reset Annotation(s)")
        settings_button = QPushButton("Settings⚙️")
        export_button = QPushButton("📦 Export to ZIP")
        mark_empty_button=QPushButton("Mark as Empty")
        annotation_counter_button = QPushButton("📊 View Counts")
        
        load_menu=QMenu()
        

        load_new_action=QAction("📂 Load New Image Folder (No Annotations)", self)
        load_exisiting_action=QAction("📁 Load Existing Project (With Annotations)", self)
        load_new_action.triggered.connect(self.load_new_folder)
        load_exisiting_action.triggered.connect(self.load_existing_project) 
        
        load_menu.addAction(load_new_action)
        load_menu.addAction(load_exisiting_action)
        load_button.setMenu(load_menu)
        
        
        #load_folder_button.clicked.connect(self.load_folder)
        save_button.clicked.connect(self.save_annotation)
        clear_button.clicked.connect(self.clear_points)
        preview_button.clicked.connect(self.preview_annotation)
        reset_button.clicked.connect(self.reset_annotations)
        settings_button.clicked.connect(self.open_settings)
        export_button.clicked.connect(self.export_to_zip)
        mark_empty_button.clicked.connect(self.mark_image_as_empty)
        annotation_counter_button.clicked.connect(self.show_annotation_counter)
        

        button_layout = QHBoxLayout()
        #button_layout.addWidget(load_folder_button)
        button_layout.addWidget(load_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(mark_empty_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(self.active_class_label)
        button_layout.addWidget(self.class_dropdown)
        button_layout.addWidget(preview_button)
        button_layout.addWidget(reset_button)
        button_layout.addWidget(settings_button)


        # Image display with scroll area for large images
        self.scroll_area = QScrollArea()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(False)
        self.image_label.mousePressEvent = self.get_mouse_position
        self.image_label.wheelEvent = self.wheel_zoom
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)

        #main_layout.addLayout(button_layout)
        #main_layout.addWidget(self.image_label)
        #main_layout.addWidget(self.status_label)
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        

        
        # Navigation and zoom buttons
        nav_layout = QHBoxLayout()
        prev_button = QPushButton("◀ Previous Image")
        next_button = QPushButton("Next Image ▶")
        rotate_button = QPushButton("🔄 Rotate Image")
        zoom_in_button = QPushButton("🔍+ Zoom In")
        zoom_out_button = QPushButton("🔍- Zoom Out")
        zoom_reset_button = QPushButton("🔍 Reset Zoom")
        
        prev_button.clicked.connect(self.previous_image)
        next_button.clicked.connect(self.next_image)
        rotate_button.clicked.connect(self.rotate_image)
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_out_button.clicked.connect(self.zoom_out)
        zoom_reset_button.clicked.connect(self.zoom_reset)
        
        nav_layout.addWidget(prev_button)
        nav_layout.addWidget(rotate_button)
        nav_layout.addWidget(zoom_out_button)
        nav_layout.addWidget(zoom_reset_button)
        nav_layout.addWidget(zoom_in_button)
        nav_layout.addWidget(next_button)
        
        #left side thingers
        left_layout.addLayout(button_layout)
        left_layout.addWidget(self.scroll_area)  # Use scroll area instead of direct image label
        left_layout.addWidget(self.status_label)
        left_layout.addLayout(nav_layout)
        left_layout.addWidget(export_button)   
        left_layout.addWidget(annotation_counter_button)
        
        #right side thinger
        self.image_list_widget=QListWidget()
        self.image_list_widget.itemClicked.connect(self.image_selected)
        
        #Mix them up
        main_layout.addLayout(left_layout,4)
        main_layout.addWidget(self.image_list_widget, 1)
        

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        

    def show_status(self, message, success=False):
        color = "green" if success else "red"
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.status_label.setText(message)
        
        
    def preview_annotation(self):
        if self.image is None:
            self.show_status("❌ No image loaded to preview.", success=False)
            return

        if not self.export_dir:
            self.show_status("❌ Export directory not set. Please configure in settings.", success=False)
            return

        if not self.image_path:
            self.show_status("❌ No image path available.", success=False)
            return

        # Get the label file path
        image_filename = os.path.basename(self.image_path)
        label_filename = os.path.splitext(image_filename)[0] + ".txt"
        label_path = os.path.join(self.export_dir, "labels", label_filename)

        img_copy = self.image.copy()
        annotations_found = False

        # Check if label file exists and load annotations
        if os.path.exists(label_path):
            try:
                with open(label_path, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 9:  # Valid annotation line
                            try:
                                class_id = int(parts[0])
                                if 0 <= class_id < len(self.class_names):
                                    class_name = self.class_names[class_id]
                                    coords = list(map(int, parts[1:]))
                                    points = [(coords[i], coords[i + 1]) for i in range(0, 8, 2)]
                                    
                                    # Get class color
                                    color = self.class_colors.get(class_name, (0, 255, 0))
                                    
                                    # Draw polygon
                                    pts = np.array(points, np.int32).reshape((-1, 1, 2))
                                    cv2.polylines(img_copy, [pts], isClosed=True, color=color, thickness=3)
                                    
                                    # Draw point numbers
                                    for idx, (x, y) in enumerate(points):
                                        cv2.circle(img_copy, (x, y), 6, (0, 0, 255), -1)
                                        cv2.putText(img_copy, str(idx + 1), (x + 8, y - 8),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                                    
                                    # Draw class label
                                    label_text = f"{class_name} ({class_id})"
                                    x_text, y_text = points[0]
                                    cv2.putText(img_copy, label_text, (x_text + 10, y_text - 10),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
                                    
                                    annotations_found = True
                                else:
                                    self.show_status(f"❌ Invalid class ID {class_id} in label file.", success=False)
                            except ValueError:
                                self.show_status("❌ Error parsing label file format.", success=False)
                                continue
                
                if not annotations_found:
                    # Empty label file
                    cv2.putText(img_copy, "Image is not labelled yet", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                    self.show_status("🟡 Image has empty label file - not labelled yet.", success=True)
                else:
                    self.show_status("✅ Displaying saved annotations from label file.", success=True)
                    
            except Exception as e:
                cv2.putText(img_copy, "Error reading label file", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                self.show_status(f"❌ Error reading label file: {str(e)}", success=False)
        else:
            # No label file exists
            QMessageBox.information(self,"Mismatch","⚠️ No label found for the image (The image is probably not labelled yet).")
            self.show_status("🟡 No label file found - image not labelled yet.", success=True)

        # Display the preview
        height, width, channel = img_copy.shape
        bytes_per_line = channel * width
        q_img = QImage(img_copy.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        self.image_label.setPixmap(pixmap)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            img = cv2.imread(file_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Keep original dimensions - no resizing
            self.original_image = img.copy()
            self.image = img
            self.zoom_factor = 1.0
            self.rotation_angle = 0
            self.display_image()
            self.points = []

    def display_image(self):
        if self.image is not None:
            img_copy = self.image.copy()
            
            # Draw existing annotations on original image
            for ann in self.annotations:
                pts=np.array(ann["points"],np.int32).reshape((-1,1,2))
                class_name=ann["class"]
                color=self.class_colors.get(class_name,(0,255,0))
                cv2.polylines(img_copy,[pts],isClosed=True,color=color,thickness=2)
                
                for(x,y) in ann["points"]:
                    cv2.circle(img_copy,(x,y),5,(0,0,255),-1)
                    
                
                class_index = self.class_names.index(class_name) if class_name in self.class_names else "?"
                label=f"{class_name} ({class_index})"
                x_text,y_text=ann["points"][0]
                cv2.putText(
                    img_copy, label, (x_text+5,y_text-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color,2, cv2.LINE_AA
                )
            
            # Draw current points being created
            for(x,y) in self.current_points:
                cv2.circle(img_copy, (x, y), 5, (255,0,0), -1)
                
            # Apply zoom to display - scale everything together
            if self.zoom_factor != 1.0:
                h, w = img_copy.shape[:2]
                new_h, new_w = int(h * self.zoom_factor), int(w * self.zoom_factor)
                img_copy = cv2.resize(img_copy, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

            height, width, channel = img_copy.shape
            bytes_per_line = channel * width
            q_img = QImage(img_copy.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.image_label.setPixmap(pixmap)
            
            # Update scroll area to accommodate new size
            self.image_label.adjustSize()


    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if not folder:
            return

        self.image_dir = folder
        self.image_list = sorted([
            f for f in os.listdir(folder)
            if f.lower().endswith(('.jpg', '.png', '.jpeg'))
        ])

        self.image_list_widget.clear()
        for img_name in self.image_list:
            item = QListWidgetItem(img_name)
            self.image_list_widget.addItem(item)

        self.show_status(f"📁 Loaded {len(self.image_list)} images from folder.", success=True)

        # Load first image by default
        if self.image_list:
            self.load_image_by_name(self.image_list[0])

    def get_mouse_position(self, event):
        if self.image is None:
            return
        pixmap = self.image_label.pixmap()
        if pixmap is None:
            return
        
        # Get click position relative to the image label
        click_x = event.pos().x()
        click_y = event.pos().y()
        
        # Get original image dimensions (before zoom)
        img_height, img_width = self.image.shape[:2]
        
        # Get displayed pixmap dimensions (after zoom)
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()
        
        # Get the image label dimensions
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        
        # Calculate offset if image is centered in label
        x_offset = max((label_width - pixmap_width) // 2, 0)
        y_offset = max((label_height - pixmap_height) // 2, 0)
        
        # Adjust click coordinates to account for centering
        adjusted_x = click_x - x_offset
        adjusted_y = click_y - y_offset
        
        # Check if click is within the displayed image bounds
        if adjusted_x < 0 or adjusted_y < 0 or adjusted_x >= pixmap_width or adjusted_y >= pixmap_height:
            return
        
        # Convert from zoomed display coordinates to original image coordinates
        actual_x = int(adjusted_x / self.zoom_factor)
        actual_y = int(adjusted_y / self.zoom_factor)
        
        # Ensure coordinates are within original image bounds
        if actual_x < 0 or actual_y < 0 or actual_x >= img_width or actual_y >= img_height:
            return
        
        self.current_points.append((actual_x, actual_y))
        
        if(len(self.current_points) == 4):
            class_index = self.class_dropdown.currentIndex()
            class_name=self.class_dropdown.currentText()
            self.annotations.append({
                "class": class_name,
                "points": self.current_points.copy()
            })
            self.current_points = []
            self.show_status(f"✅ Annotation added for class {class_name} #{len(self.annotations)}", success=True)

        self.display_image()
        self.unsaved_changes = True


    def load_image_by_name(self, filename):
        file_path = os.path.join(self.image_dir, filename)
        self.image_path = file_path
        self.annotations = []
        self.current_points=[]

        img = cv2.imread(file_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Apply black and white conversion if user preference is set
        if self.import_as_bw:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)  # Convert back to 3-channel
        
        # Keep original dimensions - no resizing to 1280x720
        self.original_image = img.copy()
        self.image = img
        self.zoom_factor = 1.0  # Reset zoom
        self.rotation_angle = 0  # Reset rotation when loading new image
        #self.display_image()

        # Try to load existing annotation
        #label_path = os.path.splitext(file_path)[0] + ".txt"
        if self.label_dir:
            label_path=os.path.join(self.label_dir,os.path.splitext(os.path.basename(file_path))[0]+".txt")
        else:
            label_path=os.path.splitext(file_path)[0] + ".txt"
            
        if os.path.exists(label_path):
            with open(label_path, "r") as f:
                for line in f:
                    parts=line.strip().split()
                    if(len(parts)==9):
                        try:
                            class_id=int(parts[0])
                            if 0 <= class_id < len(self.class_names):
                                class_name=self.class_names[class_id]
                                coords=list(map(int,parts[1:]))
                                points=[(coords[i],coords[i+1]) for i in range(0,8,2)]
                                self.annotations.append({
                                    "class":class_name,
                                    "points":points
                                })
                            else:
                                self.show_status(f"❌ Invalid class ID {class_id} in annotation file.", success=False)
                        except ValueError:
                            self.show_status("❌ Error parsing annotation file. Please check format.", success=False)
                #line = f.readline().strip().split()
                #if len(line) == 9:
                    #coords = list(map(int, line[1:]))
                    #self.points = [(coords[i], coords[i + 1]) for i in range(0, 8, 2)]
        self.display_image()

    def save_annotation(self):    
        if not self.export_dir:
            self.show_status("❌ Export directory not set. Please configure in settings.")
            return

        if not self.image_path:
            self.show_status("❌ No image loaded")
            return

        images_dir=os.path.join(self.export_dir,"images")
        labels_dir=os.path.join(self.export_dir,"labels")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)
        
        image_filename=os.path.basename(self.image_path)
        image_save_path=os.path.join(images_dir,image_filename)    
        label_filename=os.path.splitext(image_filename)[0]+".txt"
        label_save_path=os.path.join(labels_dir,label_filename)
        
        # Save the ORIGINAL image (not the potentially rotated/modified one)
        if self.original_image is not None:
            original_img_bgr = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(image_save_path, original_img_bgr)
        else:
            # Fallback to current image if original is not available
            resized_img_bgr=cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(image_save_path, resized_img_bgr)
        
        # Transform annotations back to original image coordinates if needed
        annotations_to_save = self.get_original_coordinates_annotations()
        
        with open(label_save_path,"w")as f:
            for ann in annotations_to_save:
                class_name=ann["class"]
                try:
                    class_index=self.class_names.index(class_name)
                except ValueError:
                    self.show_status(f"❌ Class '{class_name}' not found in class list.")
                    return
                coords=" ".join([f"{x} {y}" for x, y in ann["points"]])
                f.write(f"{class_index} {coords}\n")
        
        self.unsaved_changes=False
        
        if self.annotations:
            self.show_status(f"✅ Saved {len(self.annotations)} annotation(s) to {label_save_path}", success=True)

        else:
            self.show_status(f"🟡 No annotations found. Saved empty label file to {label_save_path}", success=True)
        # Save annotation
        #label_path = os.path.splitext(self.image_path)[0] + ".txt"
        
        #with open(label_path, "w") as f:
        #    for ann in self.annotations:
        #        coords=" ".join([f"{x} {y}" for x, y in ann["points"]])
        #        f.write(f"{ann['class']} {coords}\n")
        #        
        #    class_index = self.class_dropdown.currentIndex()
        #    flat_coords = " ".join([f"{x} {y}" for x, y in self.points])
        #    f.write(f"{class_index} {flat_coords}\n")
        #self.status_label.setText(f"✅ Annotation saved to {label_path}")
        #print(f"✅ Saved annotation to {label_path}")

        # Save the resized image (1280x720) to same location, overwrite original
        #image_save_path = self.image_path
        #resized_img_bgr = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)  # Convert back to BGR for OpenCV saving
        #cv2.imwrite(image_save_path, resized_img_bgr)
        #self.status_label.setText(f"✅ Saved {len(self.annotations)} annotation(s) to file.", success=True)
        #print(f"📸 Resized image saved to {image_save_path}")


    def clear_points(self):
        if self.current_points:
            self.current_points=[]
            self.show_status("Cleared in progress points")
        elif self.annotations:
            removed=self.annotations.pop()
            class_name=removed['class']
            class_index=self.class_dropdown.findText(class_name)
            self.show_status(
                f"🗑️ Removed annotation for class {class_name} ({class_index}) #{len(self.annotations) + 1}",
                success=True
            )
        else:
            self.show_status("Nothing to clear.")
        #self.points = []
        self.display_image()
        self.unsaved_changes = True

    def image_selected(self, item):
        if self.unsaved_changes:
            reply = QMessageBox.question(self,'Unsaved Annotations','You have unsaved annotations. Do you want to continue without saving?',QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        image_name = item.text()
        self.load_image_by_name(image_name)
        self.unsaved_changes=False
        
    def reset_annotations(self):
        self.annotations=[]
        self.current_points=[]
        self.display_image()
        self.unsaved_changes = True
        self.show_status("🧹 Cleared all annotations for this image.")
        
    def update_active_class_label(self):
        index=self.class_dropdown.currentIndex()
        name=self.class_dropdown.currentText()
        self.active_class_label.setText(f"Class: {name} ({index})")
        
    def open_settings(self):
        dialog=SettingsDialog(self.class_names, self.export_dir, self)
        dialog.toggle_dark_mode.connect(self.toggle_dark_mode)
        if dialog.exec_():
            new_classes=dialog.get_updated_classes()
            if new_classes:
                self.class_names=new_classes
                self.class_dropdown.clear()
                self.class_dropdown.addItems(new_classes)
                self.update_active_class_label()
                self.class_colors={cls:generate_random_color() for cls in self.class_names}
                self.show_status(f"Class list updated: {', '.join(new_classes)}", success=True)
            else:
                self.show_status("⚠️ No classes provided. Class list not updated.")
            
            new_export_dir=dialog.get_export_directory()
            if new_export_dir:
                self.export_dir=new_export_dir
                self.show_status(f"📁 Export directory set to: {self.export_dir}")
    
    def export_to_zip(self):
        if not self.export_dir or not self.class_names:
            self.show_status("❌ Export directory or class names not set. Please configure in settings.")
            return
        
        images_dir = os.path.join(self.export_dir, "images")
        labels_dir = os.path.join(self.export_dir, "labels")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)
        
        #clasese.txt ka kam
        classes_path=os.path.join(self.export_dir,"classes.txt")
        with open(classes_path,"w") as f:
            f.write("\n".join(self.class_names))
        
        zip_path,_=QFileDialog.getSaveFileName(self,"SAVE ZIP File","Zip Files (*.zip)")
        if not zip_path:
            self.show_status("❌ Export cancelled.")
            return
        
        try:
            with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as zipf:
                for folder_name in ['images','labels']:
                    folder_path=os.path.join(self.export_dir,folder_name)
                    for root, _,files in os.walk(folder_path):
                        for file in files:
                            full_path=os.path.join(root, file)
                            rel_path=os.path.relpath(full_path,self.export_dir)
                            zipf.write(full_path,arcname=rel_path)
                            
                zipf.write(classes_path,arcname="classes.txt")
            
            self.show_status(f"✅ Exported dataset to {zip_path}", success=True)
        
        except Exception as e:
            self.show_status(f"❌ Export failed: {str(e)}", success=False)

    def mark_image_as_empty(self):
        if not self.image_path:
            self.show_status("❌ No image loaded.", success=False)
            return
        
        self.annotations=[]
        self.current_points=[]
        
        label_path=os.path.splitext(self.image_path)[0]+".txt"
        with open(label_path,"w") as f:
            pass
        
        if self.export_dir:
            os.makedirs(os.path.join(self.export_dir,"labels"),exist_ok=True)
            export_label_path=os.path.join(self.export_dir,"labels",os.path.basename(label_path))
            with open(export_label_path, "w")as f:
                pass
        self.display_image() 
        self.show_status("🟡 Marked image as empty and saved label file.", success=True)

    def toggle_dark_mode(self):
        if self.dark_mode_enabled:
            QApplication.setStyle(QStyleFactory.create('Fussion'))
            self.setStyleSheet("")
            self.dark_mode_enabled=False
            self.show_status("☀️ Light Mode Enabled", success=True)
            
        else:
            dark_palette=self.palette()
            dark_palette.setColor(self.backgroundRole(),Qt.black)
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #2e2e2e;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 5px;
                }
                QLineEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #555;
                }
                QLabel {
                    color: #ffffff;
                }
                QComboBox {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QListWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                }
                QTabBar::tab {
                    background: #2e2e2e;
                    color: white;
                    padding: 6px;
                    border: 1px solid #555;
                    border-bottom: none;
                }
                QTabBar::tab:selected {
                    background: #444;
                    font-weight: bold;
                }
        
            """)
            self.dark_mode_enabled=True
            self.show_status("🌙 Dark Mode Enabled", success=True)
    
    def load_new_folder(self):
        QMessageBox.information(self,"Reminder","⚠️ Please ensure your class names are configured in Settings before loading.")
        folder=QFileDialog.getExistingDirectory(self, "Select Image Folder (No annotations)")
        if not folder:
            return
        
        # Ask user once for black and white preference
        reply = QMessageBox.question(
            self, 
            'Import Options', 
            '🎨 Do you want to import ALL images as black and white?\n\n'
            '• Yes: Convert all images to grayscale (still 3-channel RGB)\n'
            '• No: Keep original colors for all images',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        self.import_as_bw = (reply == QMessageBox.Yes)
        if self.import_as_bw:
            self.show_status("🎨 All images will be imported as black and white", success=True)
        
        self.image_dir=folder
        self.label_dir=None
        self.image_list=[f for f in os.listdir(folder) if f.lower().endswith((".jpg",".jpeg",".png"))]
        self.image_list.sort()
        
        if not self.image_list:
            self.show_status("❌ No valid image files found in folder.")
            return
        
        self.image_list_widget.clear()
        for img_name in self.image_list:
            item=QListWidgetItem(img_name)
            self.image_list_widget.addItem(item)
            
        self.load_image_by_name(self.image_list[0])
        self.show_status(f"📁 Loaded {len(self.image_list)} image(s) without annotations.", success=True)

    def load_existing_project(self):
        QMessageBox.information(self,"Reminder","⚠️ Please ensure your class names are configured in Settings before loading.")
        
        QMessageBox.information(self,"Image Folder","Please select image folder where all your images are currently stored, regardless of whether they are labelled or not")
        image_folder=QFileDialog.getExistingDirectory(self,"Select Image Folder")
        
        if not image_folder:
            return
        
        QMessageBox.information(self,"Label Folder","Please select label folder where all your labels are stored, for images that are already labelled")
        label_folder=QFileDialog.getExistingDirectory(self,"Select Label Folder (txt files please)")
        if not label_folder:
            return
        
        # Ask user once for black and white preference
        reply = QMessageBox.question(
            self, 
            'Import Options', 
            '🎨 Do you want to import ALL images as black and white?\n\n'
            '• Yes: Convert all images to grayscale (still 3-channel RGB)\n'
            '• No: Keep original colors for all images',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        self.import_as_bw = (reply == QMessageBox.Yes)
        if self.import_as_bw:
            self.show_status("🎨 All images will be imported as black and white", success=True)
        
        self.image_dir=image_folder
        self.label_dir=label_folder
        self.image_list=[f for f in os.listdir(image_folder) if f.lower().endswith((".jpg",".jpeg",".png"))]
        self.image_list.sort()
        
        if not self.image_list:
            self.show_status("❌ No valid image files found in image folder.")
            return
        
        self.image_list_widget.clear()
        for img_name in self.image_list:
            item=QListWidgetItem(img_name)
            self.image_list_widget.addItem(item)
            
        self.load_image_by_name(self.image_list[0])
        self.show_status(f"✅ Loaded {len(self.image_list)} image(s) with existing annotations.",success=True)

    def keyPressEvent(self,event):
        key=event.key()
        modifiers=event.modifiers()
        
        if key==Qt.Key_S:
            self.save_annotation()
        elif key==Qt.Key_M:
            self.mark_image_as_empty()
        elif key==Qt.Key_N:
            self.next_image()
        elif key==Qt.Key_B:
            self.previous_image()
        elif key==Qt.Key_C:
            self.clear_points()
        elif key==Qt.Key_R:
            self.reset_annotations()
        elif key==Qt.Key_T:
            self.rotate_image()
        elif key==Qt.Key_Plus or key==Qt.Key_Equal:
            self.zoom_in()
        elif key==Qt.Key_Minus:
            self.zoom_out()
        elif key==Qt.Key_0:
            self.zoom_reset()
        elif key==Qt.Key_Escape:
            self.current_points.clear()
            self.display_image()
        elif modifiers==Qt.ControlModifier and key==Qt.Key_D:
            self.toggle_dark_mode()
        
        elif modifiers==Qt.ControlModifier and key==Qt.Key_H:
            self.show_shortcuts()
        
        elif Qt.Key_0<=key<=Qt.Key_9:
            index=key-Qt.Key_0-1
            if 0<=index<self.class_dropdown.count():
                self.class_dropdown.setCurrentIndex(index)
    
    def show_shortcuts(self):
        shortcut_info = """
        🔑 **Keyboard Shortcuts:**

        • S → Save annotation
        • M → Mark image as empty
        • N → Next image
        • B → Previous image
        • C → Clear current polygon points
        • R → Reset all annotations for current image
        • T → Rotate image by 90°
        • + or = → Zoom in
        • - → Zoom out  
        • 0 → Reset zoom to 1.0x
        • Mouse Wheel → Zoom in/out (scroll up = zoom in, scroll down = zoom out)
        • Esc → Cancel current drawing (clears selected points)
        • Ctrl + H → Show this help popup
        • Ctrl + D → Toggle Dark Mode
        • 1, 2, 3... → Switch to class 1, 2, 3 etc.
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcut_info)
        
    def next_image(self):
        if self.unsaved_changes:
            reply = QMessageBox.question(self, 'Unsaved Changes', 'You have unsaved annotations. Do you want to continue without saving?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        current_index = self.image_list_widget.currentRow()
        if current_index+1<self.image_list_widget.count():
            next_index = current_index + 1
            self.image_list_widget.setCurrentRow(next_index)
            # Directly load the image since setCurrentRow doesn't trigger itemClicked
            image_name = self.image_list[next_index]
            self.load_image_by_name(image_name)
            self.unsaved_changes = False
            
    def previous_image(self):
        if self.unsaved_changes:
            reply = QMessageBox.question(self, 'Unsaved Changes', 'You have unsaved annotations. Do you want to continue without saving?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        current_index = self.image_list_widget.currentRow()
        if current_index > 0:
            prev_index = current_index - 1
            self.image_list_widget.setCurrentRow(prev_index)
            # Directly load the image since setCurrentRow doesn't trigger itemClicked
            image_name = self.image_list[prev_index]
            self.load_image_by_name(image_name)
            self.unsaved_changes = False
    
    def rotate_image(self):
        if self.image is None:
            self.show_status("❌ No image loaded to rotate.", success=False)
            return
        
        # Increment rotation angle by 90 degrees
        self.rotation_angle = (self.rotation_angle + 90) % 360
        
        # Rotate the image
        self.image = self.rotate_image_90(self.image)
        
        # Transform existing annotations
        self.transform_annotations_for_rotation()
        
        # Update display
        self.display_image()
        self.unsaved_changes = True
        
        self.show_status(f"🔄 Image rotated to {self.rotation_angle}°", success=True)
    
    def zoom_in(self):
        if self.image is None:
            self.show_status("❌ No image loaded to zoom.", success=False)
            return
        
        self.zoom_factor = min(self.zoom_factor * 1.25, 5.0)  # Max 5x zoom
        self.display_image()
        self.show_status(f"🔍 Zoomed in to {self.zoom_factor:.1f}x", success=True)
    
    def zoom_out(self):
        if self.image is None:
            self.show_status("❌ No image loaded to zoom.", success=False)
            return
        
        self.zoom_factor = max(self.zoom_factor / 1.25, 0.1)  # Min 0.1x zoom
        self.display_image()
        self.show_status(f"🔍 Zoomed out to {self.zoom_factor:.1f}x", success=True)
    
    def zoom_reset(self):
        if self.image is None:
            self.show_status("❌ No image loaded to reset zoom.", success=False)
            return
        
        self.zoom_factor = 1.0
        self.display_image()
        self.show_status("🔍 Zoom reset to 1.0x", success=True)
    
    def wheel_zoom(self, event):
        """Handle mouse wheel zoom functionality"""
        if self.image is None:
            return
        
        # Get the scroll direction
        delta = event.angleDelta().y()
        
        if delta > 0:
            # Scroll up - zoom in
            self.zoom_factor = min(self.zoom_factor * 1.1, 5.0)  # Max 5x zoom
            self.display_image()
            self.show_status(f"🔍 Zoomed in to {self.zoom_factor:.1f}x", success=True)
        elif delta < 0:
            # Scroll down - zoom out
            self.zoom_factor = max(self.zoom_factor / 1.1, 0.1)  # Min 0.1x zoom
            self.display_image()
            self.show_status(f"🔍 Zoomed out to {self.zoom_factor:.1f}x", success=True)

    def rotate_image_90(self, img):
        """Rotate image by 90 degrees clockwise - preserve original dimensions"""
        # Rotate 90 degrees clockwise
        rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        return rotated
    
    def transform_annotations_for_rotation(self):
        """Transform annotation coordinates after 90-degree clockwise rotation"""
        if not self.annotations:
            return
        
        # Use current image dimensions (not fixed 1280x720)
        orig_height, orig_width = self.image.shape[:2]
        
        # Transform each annotation
        for ann in self.annotations:
            new_points = []
            for x, y in ann["points"]:
                # 90-degree clockwise rotation transformation
                # new_x = y, new_y = orig_width - x
                new_x = y
                new_y = orig_width - x
                new_points.append((new_x, new_y))
            ann["points"] = new_points
        
        # Transform current points being drawn
        if self.current_points:
            new_current_points = []
            for x, y in self.current_points:
                new_x = y
                new_y = orig_width - x
                new_current_points.append((new_x, new_y))
            self.current_points = new_current_points

    def get_original_coordinates_annotations(self):
        """Transform current annotations back to original image coordinates if rotation was applied"""
        if self.rotation_angle == 0 or not self.annotations:
            return self.annotations
        
        # Get original image dimensions
        if self.original_image is not None:
            orig_height, orig_width = self.original_image.shape[:2]
        else:
            return self.annotations
        
        transformed_annotations = []
        
        for ann in self.annotations:
            new_points = []
            for x, y in ann["points"]:
                # Reverse the rotation transformations based on rotation_angle
                if self.rotation_angle == 90:
                    # Reverse 90° clockwise: new_x = orig_height - y, new_y = x
                    new_x = orig_height - y
                    new_y = x
                elif self.rotation_angle == 180:
                    # Reverse 180°: new_x = orig_width - x, new_y = orig_height - y
                    new_x = orig_width - x
                    new_y = orig_height - y
                elif self.rotation_angle == 270:
                    # Reverse 270° clockwise: new_x = y, new_y = orig_width - x
                    new_x = y
                    new_y = orig_width - x
                else:
                    # No rotation or invalid angle
                    new_x, new_y = x, y
                
                new_points.append((new_x, new_y))
            
            transformed_annotations.append({
                "class": ann["class"],
                "points": new_points
            })
        
        return transformed_annotations

    def show_annotation_counter(self):
        counts = self.get_annotation_counts()
        
        text = "📊 Annotation Counts (Total):\n\n"
        for cls, count in counts.items():
            text += f"{cls}: {count}\n"
        
        if all(count == 0 for count in counts.values()):
            text += "\nNo annotations found."
        
        QMessageBox.information(self, "Annotation Counter", text.strip())
    
    def get_annotation_counts(self):
        counts = {class_name: 0 for class_name in self.class_names}
        
        # Count annotations across all images if we have a project loaded
        if self.image_list and (self.export_dir or self.label_dir):
            for image_name in self.image_list:
                label_filename = os.path.splitext(image_name)[0] + ".txt"
                
                # Try export directory first, then label directory, then same as image
                if self.export_dir:
                    label_path = os.path.join(self.export_dir, "labels", label_filename)
                elif self.label_dir:
                    label_path = os.path.join(self.label_dir, label_filename)
                else:
                    label_path = os.path.join(self.image_dir, label_filename)
                
                if os.path.exists(label_path):
                    try:
                        with open(label_path, "r") as f:
                            for line in f:
                                parts = line.strip().split()
                                if len(parts) >= 9:  # Valid annotation line
                                    class_id = int(parts[0])
                                    if 0 <= class_id < len(self.class_names):
                                        class_name = self.class_names[class_id]
                                        counts[class_name] += 1
                    except (ValueError, IndexError):
                        continue  # Skip malformed lines
        else:
            # Fallback to current image only if no project is loaded
            for ann in self.annotations:
                class_name = ann['class']
                if class_name in counts:
                    counts[class_name] += 1
        
        return counts

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Annotator()
    window.showMaximized()  # Maximize the window after creation
    sys.exit(app.exec_())


