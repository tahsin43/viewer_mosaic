from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class DroppablePlotWidget(pg.GraphicsLayoutWidget):
    slice_dropped = pyqtSignal(int)  # Signal: "Someone dropped slice X on me"

    def __init__(self, parent=None):
        super().__init__(parent)
        # MUST enable drops or nothing will work!
        self.setAcceptDrops(True)
        self.slice_index=None

    def dragEnterEvent(self, event):
        """A drag entered my area - do I want it?"""
        # Check if it has text (our slice index)
        print(f"Drag entered, has text: {event.mimeData().hasText()}")
        print(f"Drop received with data: {event.mimeData().text()}")
        if event.mimeData().hasText():
            # Yes! I accept this drop
            print("Yes i accept this dtop")
            event.acceptProposedAction()
        else:
            # No, I don't want this
            event.ignore()
    
    
    def dragMoveEvent(self, event):
        """Called as the drag moves over the widget"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
     
    def dropEvent(self, event):
        """User dropped something on me!"""
        # Open the package and get the slice index
        print(f"DroppablePlot received slice {self.slice_index}")
        slice_index = int(event.mimeData().text())
        print(f"DroppablePlot received slice {slice_index}")

        # Send out MY signal to tell everyone about the drop
        self.slice_index=slice_index
        self.slice_dropped.emit(self.slice_index)

        # Tell Qt the drop was successful
        event.acceptProposedAction()
