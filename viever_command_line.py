from data_manager import DataManager, DataManagerNavigator
from Plot_object_command_line import PlotObject
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.figure import Figure


def load_data(root_dir):
    data_manager = DataManager(root_dir=root_dir)
    for index, (vol, seg) in enumerate(data_manager):
        vol_data, _ = vol
        seg_data, _ = seg
        figure = Figure(figsize=(10, 6))

        save_path = Path(root_dir) / "mosaic_2"
        seg_path = f"{index}_png"

        save_seg = save_path / seg_path
        plot = PlotObject(vol_data, seg_data, figure, save_seg)
        plot.visualize_all_image_and_mask()


if __name__ == "__main__":
    root_dir = "/Users/tahsin/gdrive/My Drive/OPAL/krispy_kreme_tahsin/03-006"

    load_data(root_dir)
