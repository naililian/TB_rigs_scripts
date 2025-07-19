from ToonBoom import harmony
from PySide6.QtWidgets import (QApplication, QDialog, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QListWidget, 
                             QListWidgetItem, QAbstractItemView, QCheckBox,
                             QMessageBox)
from PySide6.QtCore import Qt
import sys

def get_frames_number():
    print("Getting frame number from Markers")
    
    # Get Markers of scene:
    sess = harmony.session()
    current_proj = sess.project
    marker_list = current_proj.timeline_markers
    
    frame_numbers = []
    for marker in marker_list:
        frame_numbers.append((marker.frame, marker.name))
    
    return frame_numbers

class CheckableListItem(QListWidgetItem):
    def __init__(self, text, frame_num):
        super().__init__()
        self.setText(text)
        self.frame_num = frame_num
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        # Default check state based on frame number
        if frame_num < 8:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)

class FrameSelectionDialog(QDialog):
    def __init__(self, marker_frames, parent=None):
        super().__init__(parent)
        
        self.marker_frames = marker_frames
        
        # Set up the window
        self.setWindowTitle("Frame Selection")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Add label
        label = QLabel("Select frames to export:")
        main_layout.addWidget(label)
        
        # Create list widget for frame selection
        self.list_widget = QListWidget()
        
        # Add marker frames to list widget with checkboxes
        for frame, name in marker_frames:
            item = CheckableListItem(f"Frame {frame}: {name}", frame)
            self.list_widget.addItem(item)
        
        main_layout.addWidget(self.list_widget)
        
        # Create buttons for selection
        selection_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        selection_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)
        selection_layout.addWidget(deselect_all_btn)
        
        main_layout.addLayout(selection_layout)
        
        # Create buttons for actions
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.accept)
        button_layout.addWidget(export_button)
        
        main_layout.addLayout(button_layout)
    
    def select_all(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.Checked)
    
    def deselect_all(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.Unchecked)
    
    def get_selected_frames(self):
        selected_frames = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_frames.append(self.marker_frames[i])
        return selected_frames

def show_frame_selection_interface():
    # Get marker frames
    marker_frames = get_frames_number()
    
    if not marker_frames:
        print("No markers found in the scene.")
        return []
    
    # Create application if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create dialog
    dialog = FrameSelectionDialog(marker_frames)
    
    # Show dialog and get result
    result = dialog.exec()
    
    if result == QDialog.Accepted:
        return dialog.get_selected_frames()
    else:
        return []

def verify_write_node_exists(current_scene):
    """Check if the required Write node exists in the scene"""
    write_node_name = "Top/Render_Write"
    
    try:
        node = current_scene.nodes[write_node_name]
        if node is None:
            return False, f"Write node '{write_node_name}' not found in the scene."
        return True, node
    except KeyError:
        return False, f"Write node '{write_node_name}' not found in the scene."
    except Exception as e:
        return False, f"Error accessing Write node: {str(e)}"

def show_error_message(message):
    """Display an error message box"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Error")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()

def exporter_by_markers():
    print("LP_exporter_by_markers () Starting.....")

    # Getting information about scene:
    sess = harmony.session()                                     
    current_proj = sess.project 
    current_scene = current_proj.scene
    
    # Verify the Write node exists before showing the interface
    node_exists, result = verify_write_node_exists(current_scene)
    if not node_exists:
        error_message = result
        print(f"ERROR: {error_message}")
        show_error_message(error_message)
        return
    
    node = result
    
    # Show interface to select frames
    selected_frames = show_frame_selection_interface()
    
    if not selected_frames:
        print("No frames selected for export. Operation cancelled.")
        return
    
    # Creating the render handler:
    render_handler = current_proj.create_render_handler()                
    render_handler.blocking = True    
    
    # Get the Specific: Write nodes on the scene:
    print("Rendering : %s" % (node))
    
    for frame_info in selected_frames:
        frame_number = frame_info[0]
        name_marker = frame_info[1]
        
        # Render about the found Write Node
        render_handler.node_add(node)
        render_handler.render(frame_number, frame_number)   
        print("Frame %s (%s) RENDERED" % (frame_number, name_marker))                               
    
    print("ALL RENDER WERE DONE!!")