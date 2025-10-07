import pyqtgraph as pg

import sys
from PyQt5.QtCore import Qt, QObject, pyqtSignal
import data_manager
from miniWidget import MiniWidget

# this is a test to see how good pyqt plot is
from data_manager import DataManager, DataManagerNavigator
from skimage import exposure
from PIL.Image import alpha_composite
from matplotlib import image
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import nrrd
from importlib import reload
import math
from data_manager import DataManager
from matplotlib.widgets import Slider

# load the nrrd data
from PIL import Image, ImageEnhance
from skimage import exposure
from matplotlib.widgets import Button
from pyqtgraph.Qt import QtWidgets

from dataclasses import dataclass
from typing import List, Any  #
import math
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QMainWindow,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QTextEdit,
    QLabel,
)

pg.setConfigOption("imageAxisOrder", "row-major")
pg.setConfigOptions(useOpenGL=True)


@dataclass
class ImageData:
    vol_item: np.ndarray
    mask_item: np.ndarray
    visible: bool = True  # Add default value with type annotation
    mask_imageItem = []
    vol_imageItem = []
    viewboxes = []  # Add viewboxes storage

class PlotNavigator(QObject):
    position_changed = pyqtSignal(int)

    def __init__(self, data_manager: DataManager, win, renderer, name="Navigator"):
        super().__init__()
        self.name = name  # Add identifier for debugging
        self.navigator_id = id(self)  # Unique ID for this navigator instance
        self.data_manager = data_manager
        self.win = win
        self.renderer = renderer
        self._position = 0  # Start at the first __getitem__
        data_len = len(data_manager)
        # self.imageDatas: List[ImageData] = [None] * data_len  # Preallocate list
        self.current_mask = None
        self.current_vol = None
        self.visible = True
        self.is_zoomed = False  # Add zoom state
        self.zoomed_slice_index = None
        # Store references for hide/show approach
        self.grid_viewboxes = []
        self.zoom_viewbox = None
        self.current_vol_array = None
        self.current_seg_array = None

    @property
    def position(self):
        """Returns the current index."""
        return self._position

    def _clear_display(self):
        """Simple and reliable: just clear everything and reset state"""
        print(f"{self.name} clearing display completely...")
        
        # Reset state
        self.is_zoomed = False
        self.zoomed_slice_index = None
        self.grid_viewboxes = []
        self.zoom_viewbox = None
        
        # Simple clear - each widget is isolated
        try:
            self.win.clear()
            print(f"{self.name} cleared successfully")
        except Exception as e:
            print(f"{self.name} clear failed: {e}")
            # Force clear if needed
            try:
                if hasattr(self.win, 'ci') and hasattr(self.win.ci, 'layout'):
                    self.win.ci.layout.clear()
            except:
                pass

    def current(self):
        try:
            print(f"\n{self.name} === CURRENT START === Widget: {id(self.win)}")
            print(f"{self.name} Widget visible: {self.win.isVisible()}")
            print(f"{self.name} Widget size: {self.win.size()}")
            
            self._clear_display()
            vol, seg = self.load_data()
            # Store data for zoom functionality
            self.current_vol_array, self.current_seg_array = vol, seg
            vol_array, seg_array = vol, seg
            num_slices = vol_array.shape[0]
            cols = math.ceil(math.sqrt(num_slices))
            self.renderer.cols = cols

            if self.current_mask is not None:
                self.current_mask.clear()
                self.current_mask = None
            if self.current_vol is not None:
                self.current_vol.clear()
                self.current_vol = None

            # Pass callback to connect clicks
            print(f"{self.name} Rendering {num_slices} slices in {cols}x{cols} grid...")
            image_data = self.renderer.render_volume_slices(
                self.data_manager, self._position, self._on_slice_double_click
            )
            self.current_mask = image_data.mask_imageItem
            self.current_vol = image_data.vol_imageItem
            self.grid_viewboxes = image_data.viewboxes  # Store viewbox references
            
            # BREAKPOINT 1: Check visibility after rendering
            print(f"{self.name} Created {len(self.grid_viewboxes)} viewboxes")
            for i, vb in enumerate(self.grid_viewboxes):
                print(f"{self.name} Viewbox {i}: visible={vb.isVisible()}, items={len(vb.allChildren())}")
            
            print(f"{self.name} Widget after render - visible: {self.win.isVisible()}")
            print(f"{self.name} === CURRENT COMPLETE ===\n")
            return self.current_mask
        except Exception as e:
            print(f"Error in current(): {e}")
            import traceback
            traceback.print_exc()
            # Reset state on error
            self.is_zoomed = False
            self.grid_viewboxes = []
            self.zoom_viewbox = None
            return []

    def _on_slice_double_click(self, slice_index):
        """Handle click on a slice - toggle between grid and zoom"""
        print(f"{self.name} slice {slice_index} clicked, is_zoomed={self.is_zoomed}")
        
        if self.is_zoomed:
            # Return to grid
            self.show_grid_view()
        else:
            # Zoom to slice
            self.show_full_view(slice_index)

    def show_full_view(self, slice_index):
        """Show single slice by completely re-rendering as zoom view"""
        print(f"{self.name} === ZOOM: Re-rendering slice {slice_index} ===")
        
        # Validate slice index first
        vol_data, seg_data = self.data_manager[self._position]
        if slice_index < 0 or slice_index >= vol_data.shape[0]:
            print(f"{self.name} Invalid slice index {slice_index}")
            return
        
        # Set zoom state
        self.is_zoomed = True
        self.zoomed_slice_index = slice_index
        
        # Complete re-render: clear everything and render just the zoom view
        self._clear_display()
        
        try:
            # Create single zoom viewbox
            self.zoom_viewbox = self.win.addViewBox(row=0, col=0)
            
            # Add click handler to return to grid
            def handle_zoom_click(event):
                if event.button() == Qt.LeftButton:
                    print(f"{self.name} zoom clicked - returning to grid")
                    self.show_grid_view()
            
            self.zoom_viewbox.mouseClickEvent = handle_zoom_click
            
            # Render the zoomed slice
            self.renderer.render_slice_in_viewbox(
                self.zoom_viewbox, 
                self.data_manager,
                self._position,
                slice_index
            )
            
            print(f"{self.name} Zoom render complete")
            
        except Exception as e:
            print(f"{self.name} Zoom failed: {e}")
            # Fallback to grid view
            self.show_grid_view()

    def show_grid_view(self):
        """Show grid by completely re-rendering the full grid"""
        print(f"{self.name} === GRID: Re-rendering full grid ===")
        
        # Set grid state
        self.is_zoomed = False
        self.zoomed_slice_index = None
        
        # Complete re-render: just call current() which will render the full grid
        try:
            self.current()
            print(f"{self.name} Grid re-render complete")
        except Exception as e:
            print(f"{self.name} Grid re-render failed: {e}")

    def load_data(self):
        vol, seg = self.data_manager[self._position]
        return vol, seg

    def next(self):
        """Moves to the next item and returns it."""
        if self._position >= len(self.data_manager) - 1:
            self._position = 0
            self.position_changed.emit(self._position)
            return self.current()
        self._position += 1
        self.position_changed.emit(self._position)
        return self.current()

    def back(self):
        """Moves to the previous item and returns it."""
        if self._position <= 0:
            self._position = len(self.data_manager) - 1
            self.position_changed.emit(self._position)  # ← Emit signal!
            return self.current()
        self.position_changed.emit(self._position)  # ← Emit signal!
        self._position -= 1

        return self.current()

    def getImagedata(self):
        return self.current_mask

    def goto(self, index):
        print(f"{self.name} goto function called with index {index}")
        print(f"{self.name} current state - position: {self._position}, is_zoomed: {self.is_zoomed}")
        
        # Force return to grid view if zoomed to avoid state conflicts
        if self.is_zoomed:
            print(f"{self.name} forcing return to grid view before goto")
            self.show_grid_view()
        
        self._position = index
        self.position_changed.emit(self._position)  # ← Emit signal!
        
        try:
            return self.current()
        except Exception as e:
            print(f"{self.name} Error in goto->current(): {e}")
            # Reset state and try again
            self.is_zoomed = False
            self.grid_viewboxes = []
            self.zoom_viewbox = None
            return self.current()

    def toggle_all_masks(self):
        current_data = self.visible
        new_visible_state = not current_data
        self.visible = new_visible_state

        if self.is_zoomed:
            # Handle single slice view - toggle zoom viewbox masks
            if self.zoom_viewbox is not None:
                for item in self.zoom_viewbox.allChildren():
                    if isinstance(item, pg.ImageItem) and hasattr(item, 'image'):
                        # Check if it's a mask (has alpha channel)
                        if item.image.shape[-1] == 4:  # RGBA image (mask)
                            item.setVisible(self.visible)
        else:
            # Handle grid view
            if self.current_mask is not None:
                for mask in self.current_mask:
                    mask.setVisible(self.visible)

        print(f"new visible state: {new_visible_state}")

    def reset(self):
        """Reset navigator to first position"""
        self._position = 0
        return self.current()
    
    def update_data_manager(self, new_data_manager: DataManager):
        """Update the data manager and reset position"""
        print(f"{self.name} Updating data manager...")
        self.data_manager = new_data_manager
        self._clear_display()
        result = self.reset()
        self.debug_visibility_state()
        return result
    
    def debug_state(self):
        """Debug current navigator state"""
        print(f"\n=== {self.name} STATE DEBUG ===")
        print(f"Position: {self._position}")
        print(f"Is zoomed: {self.is_zoomed}")
        print(f"Zoom slice: {self.zoomed_slice_index}")
        print(f"Grid viewboxes: {len(self.grid_viewboxes)}")
        print(f"Widget items: {len(self.win.ci.layout.items) if hasattr(self.win, 'ci') else 'N/A'}")
        print("=== END STATE DEBUG ===\n")
    
    def force_reset(self):
        """Force complete re-render - nuclear option"""
        print(f"\n{self.name} === FORCE RESET ===")
        self.is_zoomed = False
        self.zoomed_slice_index = None
        try:
            self.current()  # Complete re-render
            print(f"{self.name} Force reset complete")
        except Exception as e:
            print(f"{self.name} Force reset failed: {e}")
        print(f"{self.name} === RESET COMPLETE ===\n")

class SliceRenderer:
    """Handles all the plotting/rendering logic"""

    def __init__(
        self,
        win: pg.GraphicsLayoutWidget,
        cols: int = 5,
    ):
        self.win = win
        self.cols = cols

    def render_volume_slices(self, data_manager, position, click_callback=None):
        """Creates ImageData with all rendered slices - loads fresh data each time"""
        print(f"SliceRenderer: Widget {id(self.win)} loading fresh data at position {position}")
        
        # Load fresh data each time
        vol_array, seg_array = data_manager[position]
        print(f"SliceRenderer: Widget {id(self.win)} loaded fresh data - vol shape: {vol_array.shape}, seg shape: {seg_array.shape}")
        
        image_data = ImageData(vol_array, seg_array)
        image_data.visible = True

        # Clear existing plots
        num_slices = vol_array.shape[0]
        for i in range(num_slices):
            row = i // self.cols
            col = i % self.cols
            print(f"SliceRenderer: Creating viewbox {i} at ({row},{col}) for widget {id(self.win)}")
            vb = self.win.addViewBox(row=row, col=col)
            vb._slice_index = i  # Store slice index for debugging
            vb._widget_id = id(self.win)  # Track which widget this belongs to
            
            # BREAKPOINT 2: Check viewbox creation
            print(f"SliceRenderer: Viewbox {i} created - visible: {vb.isVisible()}")
            
            image_data.viewboxes.append(vb)  # Store viewbox reference

            # Volume image
            img_item = pg.ImageItem(np.flip(vol_array[i, :, :], 0))
            vb.addItem(img_item)
            vb.setAspectLocked(True)
            image_data.vol_imageItem.append(img_item)  # Store volume items

            # Add click detection - SIMPLIFIED: Single click
            if click_callback:
                def make_click_handler(slice_idx):
                    def handle_click(event):
                        if event.button() == Qt.LeftButton:
                            print(f"Clicked slice {slice_idx} on widget {id(self.win)}")
                            click_callback(slice_idx)
                    return handle_click
            
                vb.mouseClickEvent = make_click_handler(i)

            shape = seg_array.shape
            # Mask overlay
            mask_array = np.flip(seg_array[i], 0)
            rgba_mask = np.zeros((shape[1], shape[2], 4), dtype=np.ubyte)
            rgba_mask[..., 0] = 255  # RED
            rgba_mask[..., 1] = 0  # GREEN
            rgba_mask[..., 2] = 0  # BLUE
            rgba_mask[..., 3] = (mask_array * 120).astype(np.ubyte)  # ALPHA

            mask_item = pg.ImageItem(rgba_mask)
            vb.addItem(mask_item)
            image_data.mask_imageItem.append(mask_item)
            
            # BREAKPOINT 3: Final viewbox check
            print(f"SliceRenderer: Viewbox {i} final state - visible: {vb.isVisible()}, items: {len(vb.allChildren())}")
    
        print(f"SliceRenderer: Render complete for widget {id(self.win)}")
        return image_data  # Return full ImageData object

    def render_slice_in_viewbox(self, viewbox, data_manager, position, slice_index):
        """Render a single slice in an existing viewbox - loads fresh data"""
        print(f"SliceRenderer: Loading fresh data for zoom - position {position}, slice {slice_index}")
        
        # Load fresh data each time
        vol_array, seg_array = data_manager[position]
        print(f"SliceRenderer: Zoom data loaded - vol shape: {vol_array.shape}, seg shape: {seg_array.shape}")
        
        # Volume image
        img_item = pg.ImageItem(np.flip(vol_array[slice_index, :, :], 0))
        viewbox.addItem(img_item)
        viewbox.setAspectLocked(True)
        
        # Mask overlay
        shape = seg_array.shape
        mask_array = np.flip(seg_array[slice_index], 0)
        rgba_mask = np.zeros((shape[1], shape[2], 4), dtype=np.ubyte)
        rgba_mask[..., 0] = 255  # RED
        rgba_mask[..., 1] = 0  # GREEN
        rgba_mask[..., 2] = 0  # BLUE
        rgba_mask[..., 3] = (mask_array * 120).astype(np.ubyte)  # ALPHA

        mask_item = pg.ImageItem(rgba_mask)
        viewbox.addItem(mask_item)
        
        # Click handler is added in show_full_view(), not here
        
        return [img_item, mask_item]
