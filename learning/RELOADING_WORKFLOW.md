# Reloading Workflow

This document details the sequence of events that occurs when a user clicks the "Reload Patient Data" button. The reloading mechanism is designed to be robust, ensuring that all components are updated with the new patient's data without leaving stale references.

The entire process is managed by the `MainWindow` class.

## 1. The Trigger: `handle_reload_click()`

The process begins when the user clicks the `reload_button`. This button's `clicked` signal is connected to the `MainWindow.handle_reload_click()` slot.

```python
# In MainWindow.__init__
self.reload_button.clicked.connect(self.handle_reload_click)
```

The `handle_reload_click` method performs two main tasks:

1.  **Prompts the User**: It opens a `QInputDialog` to ask the user for a new patient name. This dialog is pre-filled with the current patient's name for convenience.
2.  **Initiates the Reload**: If the user enters a new name and clicks "OK", it updates the `self.patient_name` and `self.root_dir` attributes and then calls the `self.load_all_data()` method, which does the heavy lifting.

## 2. The Core Logic: `load_all_data()`

This method is the heart of the reloading process. It orchestrates the complete teardown and setup of the data-related components for the entire application.

Here is the step-by-step flow:

1.  **Development Helper (Module Reloading)**:
    *   `importlib.reload(miniWidget)`: For development purposes, this line ensures that any changes made to the `miniWidget.py` file are picked up without having to restart the entire application.

2.  **Loading Data for the First Viewer**:
    *   `data_manager1 = self.viewer1.load_data(self.root_dir)`: The `MainWindow` tells the first `PlotViewerWidget` to load its data.
    *   Inside `viewer1.load_data()`:
        *   A **new** `DataManager` instance is created for the new patient directory.
        *   A **new** `SliceRenderer` is created.
        *   A **new** `PlotNavigator` is created, linking the new `DataManager` and `SliceRenderer`.
        *   All internal signals for this viewer are re-connected via `_connect_signals()`.
        *   `navigator.current()` is called to display the first slice of the new data.
    *   If successful, this method returns the newly created `DataManager` instance.

3.  **Loading Data for the Second Viewer**:
    *   `self.viewer2.load_data(self.root_dir)`: The same process is repeated for the second `PlotViewerWidget`, ensuring it also gets a completely new and independent set of data-handling objects.

4.  **Updating the Manifest**:
    *   `self.update_manifest_box(data_manager1.manifest)`: After the first viewer has successfully loaded its data, the `MainWindow` uses the new `DataManager` to get the manifest (the dictionary of available cases).
    *   Inside `update_manifest_box()`:
        *   It first checks if an old `manifest_widget` exists and, if so, calls `deleteLater()` on it. This is crucial for preventing memory leaks and UI glitches by ensuring the old set of `MiniWidget`s is properly removed.
        *   It then creates a new container widget and populates it with fresh `MiniWidget`s based on the new manifest.

5.  **Error Handling**:
    *   The entire process is wrapped in a `try...except` block. If the specified patient directory doesn't exist or contains invalid data (`FileNotFoundError`, `ValueError`), a `QMessageBox` is displayed to the user, and the application state remains unchanged.

## 3. Why This Approach is Effective

*   **State Encapsulation**: Each `PlotViewerWidget` is responsible for managing its own state. The `MainWindow` doesn't need to know about the internal details of the navigator or renderer; it just tells the viewer to load the data.
*   **No Stale Data**: By creating entirely new instances of `DataManager`, `PlotNavigator`, and `SliceRenderer`, we ensure that there are no lingering references to the old patient's data.
*   **Clear Flow of Control**: The logic flows in a clear, top-down manner from `MainWindow` to each `PlotViewerWidget`, making it easy to follow and debug.
*   **Robust UI Updates**: Explicitly deleting and recreating the manifest widget prevents issues where old and new UI elements might overlap or conflict.
