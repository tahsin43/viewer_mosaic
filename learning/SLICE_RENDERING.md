# Slice Rendering Process

The rendering process is the mechanism by which raw numerical data from NRRD files is converted into the visual images displayed on the screen. This task is encapsulated entirely within the `SliceRenderer` class, separating the logic of *what* to display from the logic of *how* to display it.

The `PlotNavigator` orchestrates this process. When it needs to display a new case (e.g., in its `current()` method), it first loads the data and then passes it to the renderer.

## 1. The `SliceRenderer` Class

*   **Purpose**: To handle all `pyqtgraph`-related drawing operations. It knows how to take NumPy arrays and turn them into a grid of images with overlays.
*   **Key Attributes**:
    *   `self.win`: A reference to the `pg.GraphicsLayoutWidget` (specifically, our `DroppablePlotWidget`) where the images will be drawn.
    *   `self.cols`: The number of columns to use for the grid layout.

## 2. The Rendering Method: `render_volume_slices`

This is the main method of the `SliceRenderer`. It takes two NumPy arrays as input: `vol_array` (the grayscale medical scan) and `seg_array` (the binary segmentation mask).

Here is a step-by-step breakdown of what happens inside this method:

1.  **Data Structure Creation**:
    *   `image_data = ImageData(vol_array, seg_array)`: It creates an `ImageData` dataclass object. While not fully utilized for caching in the current version, this structure is intended to hold the raw data and the corresponding `pyqtgraph` `ImageItem` objects together.

2.  **Clearing the Previous Display**:
    *   Before rendering, the `PlotNavigator` calls `self.win.clear()`. This is a `pyqtgraph` method that removes all previously added plots, view boxes, and items from the layout, ensuring a clean slate for the new data.

3.  **Iterating Through Slices**:
    *   The method iterates from `i = 0` to `num_slices - 1`. For each slice, it performs the following steps to place it correctly in the grid.

4.  **Calculating Grid Position**:
    *   `row = i // self.cols`
    *   `col = i % self.cols`
    *   This standard calculation converts a linear index `i` into a 2D grid coordinate (`row`, `col`).

5.  **Creating a ViewBox**:
    *   `vb = self.win.addViewBox(row=row, col=col)`: A `ViewBox` is a fundamental `pyqtgraph` container that holds the actual image items. It handles panning, zooming, and aspect ratio locking. A new, empty `ViewBox` is created and placed at the calculated `(row, col)` in the `GraphicsLayoutWidget`.

6.  **Rendering the Volume Image**:
    *   `img_item = pg.ImageItem(np.flip(vol_array[i, :, :], 0))`:
        *   `vol_array[i, :, :]`: The 2D NumPy array for the current slice is extracted.
        *   `np.flip(..., 0)`: The array is flipped vertically. This is often necessary to correct for differences in coordinate system origins between NumPy (where `[0,0]` is the top-left) and some imaging formats or display systems.
        *   `pg.ImageItem(...)`: A `pyqtgraph` `ImageItem` is created from the flipped array. This object is optimized for displaying image data.
    *   `vb.addItem(img_item)`: The new `ImageItem` is added to the `ViewBox`.
    *   `vb.setAspectLocked(True)`: This ensures the image is not stretched and maintains its correct proportions.

7.  **Creating and Rendering the Segmentation Mask Overlay**:
    *   This is the most complex part of the rendering. The goal is to create a semi-transparent red overlay that only appears where the `seg_array` is non-zero.
    *   `mask_array = np.flip(seg_array[i], 0)`: The segmentation slice is also flipped to match the volume's orientation.
    *   `rgba_mask = np.zeros((shape[1], shape[2], 4), dtype=np.ubyte)`: A new 3D NumPy array is created. It has the same height and width as the slice, but its depth is 4. This represents a 4-channel **RGBA** image (Red, Green, Blue, Alpha/Transparency). The `ubyte` data type (`uint8`) is used because color channel values range from 0 to 255.
    *   `rgba_mask[..., 0] = 255`: The first channel (Red) is set to 255 (full red) for all pixels.
    *   `rgba_mask[..., 1] = 0`: The Green channel is set to 0.
    *   `rgba_mask[..., 2] = 0`: The Blue channel is set to 0.
    *   `rgba_mask[..., 3] = (mask_array * 120).astype(np.ubyte)`: This is the key step for transparency.
        *   The `mask_array` contains values of 0s and 1s.
        *   Multiplying it by `120` results in an array of 0s and 120s.
        *   This array is then assigned to the fourth channel (Alpha). Where the mask was 0, the alpha will be 0 (fully transparent). Where the mask was 1, the alpha will be 120 (partially transparent, on a scale of 0-255).
    *   `mask_item = pg.ImageItem(rgba_mask)`: A second `ImageItem` is created from this 4-channel RGBA array.
    *   `vb.addItem(mask_item)`: This mask item is added **to the same `ViewBox`** as the volume image. `pyqtgraph` automatically layers items in the order they are added, so the mask is drawn on top of the volume.

8.  **Storing References**:
    *   `image_data.mask_imageItem.append(mask_item)`: A reference to each created `mask_item` is stored. This is essential for the "Toggle Masks" functionality, which needs to access these items later to set their visibility.

The method finishes by returning the list of mask items, which the `PlotNavigator` then stores in its `self.current_mask` attribute.
