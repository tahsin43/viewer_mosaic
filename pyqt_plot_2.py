import importlib
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QMainWindow,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QInputDialog,
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg

# Local imports
from DroppablePlotWidget import DroppablePlotWidget
from PlotNavigator import PlotNavigator, SliceRenderer
from data_manager import DataManager
from miniWidget import MiniWidget

# --- Configuration ---
pg.setConfigOption("imageAxisOrder", "row-major")
pg.setConfigOptions(useOpenGL=True)


class PlotViewerWidget(QWidget):
    """
    A widget that encapsulates a single plot view, its controls,
    and its data navigation logic.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = None
        self.renderer = None
        self.navigator = None

        # --- UI Elements ---
        self.output_label = QLabel("Index 0")
        self.win = DroppablePlotWidget()
        self.toggle_button = QPushButton("Toggle Masks")
        self.next_button = QPushButton("Next Volume")
        self.prev_button = QPushButton("Previous Volume")

        # --- Layout ---
        layout = QVBoxLayout(self)
        layout.addWidget(self.output_label)
        layout.addWidget(self.win)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.prev_button)

    def load_data(self, root_dir):
        """
        Loads data from a directory and sets up the navigator and renderer.
        Returns the DataManager instance on success, None on failure.
        """
        try:
            self.data_manager = DataManager(root_dir)
            self.renderer = SliceRenderer(self.win)
            self.navigator = PlotNavigator(self.data_manager, self.win, self.renderer)
            self._connect_signals()
            self.navigator.current()
            return self.data_manager
        except (ValueError, FileNotFoundError) as e:
            # Let the main window handle the error message
            raise e

    def _connect_signals(self):
        """Connects internal signals and slots."""
        if not self.navigator:
            return

        # Connect navigator signals
        self.navigator.position_changed.connect(
            lambda pos: self.output_label.setText(f"Index Position {pos} !")
        )

        # Connect button signals
        self.toggle_button.clicked.connect(self.navigator.toggle_all_masks)
        self.next_button.clicked.connect(self.navigator.next)
        self.prev_button.clicked.connect(self.navigator.back)

        # Connect drop signal
        self.win.slice_dropped.connect(self.navigator.goto)


class MainWindow(QWidget):
    """
    The main application window that holds the two plot viewers
    and the shared manifest/reload controls.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manifest_widget = None
        self.patient_name = ""
        self.root_dir = ""

        # --- UI Elements ---
        self.viewer1 = PlotViewerWidget()
        self.viewer2 = PlotViewerWidget()
        self.reload_button = QPushButton("Reload Patient Data")

        # --- Layouts ---
        main_layout = QHBoxLayout(self)
        manifest_layout = QVBoxLayout()

        # --- Setup Manifest/Reload Area ---
        manifest_layout.addWidget(self.reload_button)
        # A container for the miniwidgets to allow easy replacement
        self.manifest_container = QWidget()
        self.manifest_container_layout = QVBoxLayout(self.manifest_container)
        self.manifest_container_layout.setContentsMargins(0, 0, 0, 0)
        manifest_layout.addWidget(self.manifest_container)
        manifest_layout.addStretch()  # Pushes widgets to the top

        # --- Assemble Main Layout ---
        main_layout.addLayout(manifest_layout)
        main_layout.addWidget(self.viewer1)
        main_layout.addWidget(self.viewer2)

        # --- Initial Data Load ---
        self._get_initial_patient()
        if self.patient_name:
            self.load_all_data()

        # --- Connections ---
        self.reload_button.clicked.connect(self.handle_reload_click)

    def _get_initial_patient(self):
        """Prompts the user for the initial patient name via the console."""
        name = input("Patient_number: ")
        if not name.strip():
            print("No patient name provided. Exiting.")
            sys.exit(1)
        self.patient_name = name.strip()
        self.root_dir = f"/Users/tahsin/gdrive/My Drive/OPAL/krispy_kreme_tahsin/{self.patient_name}"

    def load_all_data(self):
        """Loads data for both viewers and updates the manifest."""
        print(f"--- loading data from {self.root_dir} ---")
        try:
            # For development: reload the miniWidget module
            import miniWidget

            importlib.reload(miniWidget)

            # Load data for the first viewer and get the manifest from it
            data_manager1 = self.viewer1.load_data(self.root_dir)
            self.viewer2.load_data(self.root_dir)

            if data_manager1:
                self.update_manifest_box(data_manager1.manifest)

        except (ValueError, FileNotFoundError) as e:
            print(f"Error loading data for patient '{self.patient_name}': {e}")
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText(f"Failed to load data for patient: {self.patient_name}")
            msg_box.setInformativeText(str(e))
            msg_box.setWindowTitle("Error")
            msg_box.exec_()

    def update_manifest_box(self, manifest):
        """Clears and rebuilds the manifest widget list."""
        # Clear existing manifest widgets
        if self.manifest_widget is not None:
            self.manifest_widget.deleteLater()

        # Create a new container widget for the manifest items
        self.manifest_widget = QWidget()
        layout = QVBoxLayout(self.manifest_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        for item_key in manifest.keys():
            mini = MiniWidget(str(item_key))
            layout.addWidget(mini)

        # Add the new manifest widget to its container layout
        self.manifest_container_layout.addWidget(self.manifest_widget)

    def handle_reload_click(self):
        """Handles the reload button click, prompting for a new patient."""
        text, ok = QInputDialog.getText(
            self,
            "Reload Data",
            "Enter patient name:",
            text=self.patient_name,
        )
        if ok and text.strip():
            new_patient_name = text.strip()
            print(f"Reloading data for patient: {new_patient_name}")

            self.patient_name = new_patient_name
            self.root_dir = f"/Users/tahsin/gdrive/My Drive/OPAL/krispy_kreme_tahsin/{self.patient_name}"
            self.load_all_data()
        else:
            print("Reload cancelled or no patient name entered.")


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.setWindowTitle("PyQtGraph Dual Viewer")
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()