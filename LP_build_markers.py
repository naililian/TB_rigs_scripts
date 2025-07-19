from ToonBoom import harmony
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                              QCheckBox, QPushButton, QGroupBox, QMessageBox,
                              QLabel, QScrollArea, QWidget)

class Marker:
    def __init__(self, frame, length, name, note, colour):
        self.frame = frame
        self.length = length
        self.name = name
        self.note = note
        self.colour = colour
    
    def __str__(self):
        return f"{self.name} (Frame {self.frame})"


class MarkersDialog(QDialog):
    def __init__(self, parent=None, markers=None):
        super().__init__(parent)
        
        self.setWindowTitle("Build Scene Markers")
        self.resize(400, 500)
        
        self.selected_markers = []
        self.markers_list = markers or []
        
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create a scroll area for lots of checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Group for Turn Around markers
        turn_group = QGroupBox("Turn Around Markers")
        turn_layout = QVBoxLayout()
        
        # Group for Mouth markers
        mouth_group = QGroupBox("Mouth Markers")
        mouth_layout = QVBoxLayout()
        
        # Checkboxes for all markers
        self.marker_checkboxes = {}
        
        for marker in self.markers_list:
            checkbox = QCheckBox(str(marker))
            checkbox.setChecked(True)  # Default all to checked
            self.marker_checkboxes[marker] = checkbox
            
            # Organize checkboxes by type
            if "MOUTH" in marker.name:
                mouth_layout.addWidget(checkbox)
            else:
                turn_layout.addWidget(checkbox)
        
        turn_group.setLayout(turn_layout)
        mouth_group.setLayout(mouth_layout)
        
        scroll_layout.addWidget(turn_group)
        scroll_layout.addWidget(mouth_group)
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        # Select All/None buttons
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self.select_none)
        
        # Create/Cancel buttons
        create_btn = QPushButton("Create Markers")
        create_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(select_all_btn)
        buttons_layout.addWidget(select_none_btn)
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(cancel_btn)
        
        main_layout.addWidget(scroll)
        main_layout.addLayout(buttons_layout)
    
    def select_all(self):
        for checkbox in self.marker_checkboxes.values():
            checkbox.setChecked(True)
    
    def select_none(self):
        for checkbox in self.marker_checkboxes.values():
            checkbox.setChecked(False)
    
    def get_selected_markers(self):
        return [marker for marker, checkbox in self.marker_checkboxes.items() 
                if checkbox.isChecked()]


def create_marker_list():
    """Create list of all possible markers"""
    markers = []
    
    # Turn Around markers
    markers.append(Marker(
        frame=1, 
        length=1, 
        name="1-Front",
        note="",
        colour=[127, 255, 212]    # Aquamarine   #7FFFD4
    ))
    
    markers.append(Marker(
        frame=2, 
        length=1, 
        name="2-F3QR",
        note="",
        colour=[255, 127, 80]     # Coral #FF7F50
    ))
    
    markers.append(Marker(
        frame=3, 
        length=1, 
        name="3-PR-Right",
        note="",
        colour=[0, 255, 255]      # Aqua  #00FFFF
    ))
    
    markers.append(Marker(
        frame=4, 
        length=1, 
        name="4-B3Q-Right",
        note="",
        colour=[250, 128, 114]    # Salmon   #FA8072
    ))
    
    markers.append(Marker(
        frame=5, 
        length=1, 
        name="5-Back",
        note="",
        colour=[255, 215, 0]      # Gold  #FFD700
    ))
    
    markers.append(Marker(
        frame=6, 
        length=1, 
        name="6-B3QL_Flipped",
        note="",
        colour=[250, 128, 114]    # Salmon   #FA8072
    ))
    
    markers.append(Marker(
        frame=7, 
        length=1, 
        name="7-PL_Flipped",
        note="",
        colour=[0, 255, 255]      # Aqua  #00FFFF
    ))
    
    markers.append(Marker(
        frame=8, 
        length=1, 
        name="8-F3QL_Flipped",
        note="", 
        colour=[255, 127, 80]     # Coral #FF7F50
    ))
    
    markers.append(Marker(
        frame=9, 
        length=1, 
        name="9-OFF Draw 01",
        note="",
        colour=[220, 20, 60]      # Crimson
    ))
    
    markers.append(Marker(
        frame=10, 
        length=1, 
        name="10-OFF Draw 02",
        note="",
        colour=[139, 0, 0]        # Dark Red
    ))
    
    # Mouth markers
    markers.append(Marker(
        frame=20, 
        length=19, 
        name="MOUTH_FR",
        note="",
        colour=[153, 50, 204]     # Dark Orchid
    ))
    
    markers.append(Marker(
        frame=42, 
        length=19, 
        name="MOUTH_QF",
        note="",
        colour=[139, 0, 139]      # Dark Magenta
    ))
    
    markers.append(Marker(
        frame=64, 
        length=19, 
        name="MOUTH_Side",
        note="",
        colour=[148, 0, 211]      # Dark Violet
    ))
    
    return markers


def get_existing_markers(timeline_markers):
    """Get list of existing markers in the project"""
    existing = []
    
    # In Harmony's Python API, TimelineMarkerList doesn't have a count() method
    # Instead, we'll iterate through the markers
    # We can use a try/except to check if there are any markers
    try:
        # We don't know how many markers exist, so we'll try until we get an IndexError
        i = 0
        while True:
            try:
                marker = timeline_markers.marker_at(i)
                # Create a custom Marker object to ensure consistent structure
                existing_marker = Marker(
                    frame=marker.frame,
                    length=getattr(marker, 'length', 1),  # Default to 1 if not available
                    name=getattr(marker, 'name', f"Marker {i}"),  # Default name if not available
                    note=getattr(marker, 'note', ""),  # Default empty note
                    colour=getattr(marker, 'colour', [255, 255, 255])  # Default white
                )
                existing.append(existing_marker)
                i += 1
            except Exception as e:
                # Skip this marker if there's an error accessing its properties
                i += 1
                if i > 100:  # Safety limit to prevent infinite loops
                    break
    except (IndexError, AttributeError):
        # No more markers or the marker_at method doesn't exist
        pass
    
    return existing


def find_conflicting_markers(marker, existing_markers):
    """Find markers that conflict with the one we want to create"""
    conflicts = []
    
    for existing in existing_markers:
        # Check if frame matches (potential conflict)
        if existing.frame == marker.frame:
            conflicts.append(existing)
    
    return conflicts


def confirm_overwrite_with_details(marker, conflicts):
    """Ask user to confirm overwriting markers with detailed information"""
    msgbox = QMessageBox()
    msgbox.setWindowTitle("Confirm Overwrite")
    
    # Build detailed message about conflicting markers
    conflict_details = "\n".join([f"• {conflict.name} (Frame {conflict.frame})" for conflict in conflicts])
    
    msgbox.setText(f"The following marker(s) already exist at frame {marker.frame}:\n\n"
                   f"{conflict_details}\n\n"
                   f"Do you want to replace them with '{marker.name}'?")
    
    msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgbox.setDefaultButton(QMessageBox.No)
    return msgbox.exec() == QMessageBox.Yes


def build_markers():
    """Main function to build markers"""
    try:
        # Get Harmony session and project
        sess = harmony.session()
        current_project = sess.project
        
        # Get existing markers
        timeline_markers = current_project.timeline_markers
        existing_markers = get_existing_markers(timeline_markers)
        
        # Check if any markers exist
        if not existing_markers:
            # No markers exist, show dialog to select which to create
            app = QApplication.instance() or QApplication([])
            
            all_markers = create_marker_list()
            dialog = MarkersDialog(markers=all_markers)
            
            if dialog.exec() == QDialog.Accepted:
                selected_markers = dialog.get_selected_markers()
                
                # Create selected markers
                for marker in selected_markers:
                    timeline_markers.create(
                        marker.frame, 
                        marker.length, 
                        marker.name, 
                        marker.note, 
                        marker.colour
                    )
                
                return "Successfully created markers"
            else:
                return "Operation canceled by user"
        else:
            # Markers already exist, let user select which to create/overwrite
            app = QApplication.instance() or QApplication([])
            
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Scene Markers Exist")
            msgbox.setText(f"There are {len(existing_markers)} scene markers already in the project.\n"
                        "Do you want to add new markers?")
            msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            
            if msgbox.exec() == QMessageBox.Yes:
                all_markers = create_marker_list()
                dialog = MarkersDialog(markers=all_markers)
                
                if dialog.exec() == QDialog.Accepted:
                    selected_markers = dialog.get_selected_markers()
                    markers_created = 0
                    
                    # Check each selected marker if it exists
                    for marker in selected_markers:
                        # Find any conflicting markers
                        conflicts = find_conflicting_markers(marker, existing_markers)
                        
                        if conflicts:
                            # Ask for confirmation to overwrite with detailed information
                            if confirm_overwrite_with_details(marker, conflicts):
                                # Remove existing markers at this frame
                                try:
                                    # First, find all indices of markers at this frame
                                    indices_to_remove = []
                                    i = 0
                                    while True:
                                        try:
                                            existing = timeline_markers.marker_at(i)
                                            if hasattr(existing, 'frame') and existing.frame == marker.frame:
                                                indices_to_remove.append(i)
                                            i += 1
                                        except (IndexError, AttributeError):
                                            break
                                        except Exception:
                                            i += 1
                                            if i > 100:  # Safety limit
                                                break
                                    
                                    # Remove markers in reverse order to avoid index shifting
                                    for idx in sorted(indices_to_remove, reverse=True):
                                        try:
                                            timeline_markers.remove(idx)
                                        except Exception:
                                            pass
                                    
                                    # Create new marker
                                    timeline_markers.create(
                                        marker.frame, 
                                        marker.length, 
                                        marker.name, 
                                        marker.note, 
                                        marker.colour
                                    )
                                    markers_created += 1
                                    
                                except Exception as e:
                                    # Show error dialog but continue with other markers
                                    error_msg = QMessageBox()
                                    error_msg.setIcon(QMessageBox.Warning)
                                    error_msg.setWindowTitle("Error")
                                    error_msg.setText(f"Error processing marker {marker.name}: {str(e)}")
                                    error_msg.exec()
                        else:
                            # No conflicts, create new marker
                            try:
                                timeline_markers.create(
                                    marker.frame, 
                                    marker.length, 
                                    marker.name, 
                                    marker.note, 
                                    marker.colour
                                )
                                markers_created += 1
                            except Exception as e:
                                # Show error dialog but continue with other markers
                                error_msg = QMessageBox()
                                error_msg.setIcon(QMessageBox.Warning)
                                error_msg.setWindowTitle("Error")
                                error_msg.setText(f"Error creating marker {marker.name}: {str(e)}")
                                error_msg.exec()
                    
                    if markers_created > 0:
                        return f"Successfully created/updated {markers_created} markers"
                    else:
                        return "No markers were created or updated"
                else:
                    return "Operation canceled by user"
            else:
                return "Operation canceled by user"
    
    except Exception as e:
        # Show error dialog
        app = QApplication.instance() or QApplication([])
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("Error")
        error_msg.setText(f"An unexpected error occurred: {str(e)}")
        error_msg.exec()
        
        return f"Error: {str(e)}"


if __name__ == "__main__":
    build_markers()


