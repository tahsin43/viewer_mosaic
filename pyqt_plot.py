import importlib
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Any

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QMainWindow,
    QFileDialog,
    QTextEdit,
    QLabel,
    QInputDialog
)
from pyqtgraph.Qt import QtWidgets
import pyqtgraph as pg

from DroppablePlotWidget import DroppablePlotWidget
from PlotNavigator import PlotNavigator, SliceRenderer
from data_manager import DataManager
from miniWidget import MiniWidget

# Configure pyqtgraph
pg.setConfigOption("imageAxisOrder", "row-major")
pg.setConfigOptions(useOpenGL=True)


class PlotViewer(QMainWindow):
    def __init__(self, patient_name: str):
        super().__init__()
        self.patient_name = patient_name
        self.root_dir = f"/Users/tahsin/gdrive/My Drive/OPAL/krispy_kreme_tahsin/{patient_name}"
        
        # Initialize data managers and navigators
        self.data_manager1 = None
        self.data_manager2 = None
        self.navigator1 = None
        self.navigator2 = None
        
        # UI components
        self.main_widget = None
        self.layout = None
        
        self.init_ui()
        self.init_data()
        self.connect_signals()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        # Main horizontal layout
        self.main_layout = QHBoxLayout(self.main_widget)
        
        # Left side layout
        self.left_layout = QVBoxLayout()
        self.left_label = QLabel("Index 0")
        self.left_plot = DroppablePlotWidget()
        
        self.left_layout.addWidget(self.left_label)
        self.left_layout.addWidget(self.left_plot)
        
        # Right side layout  
        self.right_layout = QVBoxLayout()
        self.right_label = QLabel("NONE")
        self.right_plot = DroppablePlotWidget()
        
        self.right_layout.addWidget(self.right_label)
        self.right_layout.addWidget(self.right_plot)
        
        # Control buttons for left side
        self.left_toggle_btn = QPushButton("Toggle Masks")
        self.left_next_btn = QPushButton("Next Volume")
        self.left_prev_btn = QPushButton("Previous Volume")
        self.left_debug_btn = QPushButton("Debug Visibility")
        self.left_reset_btn = QPushButton("FORCE RESET")
        self.left_reset_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        
        self.left_layout.addWidget(self.left_toggle_btn)
        self.left_layout.addWidget(self.left_next_btn)
        self.left_layout.addWidget(self.left_prev_btn)
        self.left_layout.addWidget(self.left_debug_btn)
        self.left_layout.addWidget(self.left_reset_btn)
        
        # Control buttons for right side
        self.right_toggle_btn = QPushButton("Toggle Masks")
        self.right_next_btn = QPushButton("Next Volume")
        self.right_prev_btn = QPushButton("Previous Volume")
        self.right_debug_btn = QPushButton("Debug Visibility")
        self.right_reset_btn = QPushButton("FORCE RESET")
        self.right_reset_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        
        self.right_layout.addWidget(self.right_toggle_btn)
        self.right_layout.addWidget(self.right_next_btn)
        self.right_layout.addWidget(self.right_prev_btn)
        self.right_layout.addWidget(self.right_debug_btn)
        self.right_layout.addWidget(self.right_reset_btn)
        
        # Manifest layout (left side)
        self.manifest_layout = QVBoxLayout()
        self.reload_btn = QPushButton("Reload Data")
        self.reload_btn.setToolTip("Click to enter new patient name and reload data")  # Add tooltip
        self.manifest_layout.addWidget(self.reload_btn)
        
        # Add layouts to main layout
        self.main_layout.addLayout(self.manifest_layout)
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout)
        
        self.setWindowTitle(f"Plot Viewer - Patient {self.patient_name}")
        self.resize(1200, 800)
        
    def init_data(self):
        """Initialize data managers and navigators"""
        try:
            # Initialize first data manager and navigator
            self.data_manager1 = DataManager(self.root_dir)
            renderer1 = SliceRenderer(self.left_plot)
            self.navigator1 = PlotNavigator(self.data_manager1, self.left_plot, renderer1)
            
            # Initialize second data manager and navigator
            self.data_manager2 = DataManager(self.root_dir)
            renderer2 = SliceRenderer(self.right_plot)
            self.navigator2 = PlotNavigator(self.data_manager2, self.right_plot, renderer2)
            
            # Display current slice
            self.navigator1.current()
            
            # Add manifest box
            self.add_manifest_box()
            
        except ValueError as e:
            print(f"Error initializing data: {e}")
            sys.exit(1)
            
    def connect_signals(self):
        """Connect all signals and slots"""
        if self.navigator1:
            # Left navigator signals
            self.navigator1.position_changed.connect(
                lambda pos: self.left_label.setText(f"Index Position {pos} !")
            )
            self.left_toggle_btn.clicked.connect(self.navigator1.toggle_all_masks)
            self.left_next_btn.clicked.connect(self.navigator1.next)
            self.left_prev_btn.clicked.connect(self.navigator1.back)
            self.left_debug_btn.clicked.connect(self.navigator1.debug_state)
            self.left_reset_btn.clicked.connect(self.navigator1.force_reset)
            self.left_plot.slice_dropped.connect(self.navigator1.goto)
            
        if self.navigator2:
            # Right navigator signals
            self.navigator2.position_changed.connect(
                lambda pos: self.right_label.setText(f"Index Position {pos} !")
            )
            self.right_toggle_btn.clicked.connect(self.navigator2.toggle_all_masks)
            self.right_next_btn.clicked.connect(self.navigator2.next)
            self.right_prev_btn.clicked.connect(self.navigator2.back)
            self.right_debug_btn.clicked.connect(self.navigator2.debug_state)
            self.right_reset_btn.clicked.connect(self.navigator2.force_reset)
            self.right_plot.slice_dropped.connect(self.navigator2.goto)
            
        # Reload button
        self.reload_btn.clicked.connect(self.handle_reload_click)

        
    def add_manifest_box(self):
        """Add manifest widgets to the layout"""
        if not self.navigator1 or not self.navigator1.data_manager:
            return
            
        widget = QWidget()
        layout = QVBoxLayout()
        
        manifest = self.navigator1.data_manager.manifest
        for item in manifest.keys():
            mini = MiniWidget(str(item))
            layout.addWidget(mini)
            # Connect mini widget signals if needed
            # mini.clicked.connect(lambda idx=item: self.navigator1.goto(idx))
            
        widget.setLayout(layout)
        
        # Insert at the beginning of manifest layout (before reload button)
        self.manifest_layout.insertWidget(0, widget)
    
    
    
    def handle_reload_click(self):
        """Handle reload button click with input dialog"""
        # Show input dialog for new patient name
        text, ok = QInputDialog.getText(
            self, 
            'Reload Data', 
            'Enter patient name:',
            text=self.patient_name  # Pre-fill with current patient name
        )
        if ok and text.strip():
            new_patient_name = text.strip()
            print(f"Reloading data for patient: {new_patient_name}")
            
            # Update patient name and root directory
            self.patient_name = new_patient_name
            self.root_dir = f"/Users/tahsin/gdrive/My Drive/OPAL/krispy_kreme_tahsin/{new_patient_name}"
            
            # Update window title 
            # Call reload data with new patient
            self.reload_data()
        else:
            print("Reload cancelled or no patient name provided") 
    
    
    def reload_data(self):
        # Create new DataManager instances
        new_data_manager1 = DataManager(self.root_dir)
        new_data_manager2 = DataManager(self.root_dir)
       
       
           # Update navigators with new data managers
        
        # Update our references
        self.data_manager1 = new_data_manager1
        self.data_manager2 = new_data_manager2 
        self.remove_manifest_box()
        self.add_manifest_box()
        if self.navigator1:
           self.navigator1.update_data_manager(new_data_manager1) 
        if self.navigator2:
            self.navigator2.update_data_manager(new_data_manager2) 
        # Refresh displays
        if self.navigator1:
            self.navigator1.current()
        if self.navigator2:
            self.navigator2.current()
  
    def remove_manifest_box(self):
        """Reload the UI and data"""
        print("--- reloading ui ---")
        
        # Remove existing manifest widgets (keep reload button)
        while self.manifest_layout.count() > 1:
            item = self.manifest_layout.itemAt(0)
            if item:
                widget_to_delete = item.widget()
                self.manifest_layout.removeWidget(widget_to_delete)
                widget_to_delete.deleteLater()
                
        # Reload the module
        import miniWidget
        importlib.reload(MiniWidget)
         
    def closeEvent(self, event):
        """Handle application close event"""
        print("Closing application...")
        event.accept()


class PlotViewerApp:
    """Main application class"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.viewer = None
        
    def run(self):
        """Run the application"""
        patient_name = input("Patient_number: ")
        if not patient_name.strip():
            print("No patient name provided")
            return
            
        self.viewer = PlotViewer(patient_name)
        self.viewer.show()
        
        return self.app.exec_()


if __name__ == "__main__":
    app = PlotViewerApp()
    sys.exit(app.run())