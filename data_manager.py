from pathlib import Path
import nrrd
import re
from PyQt5.QtCore import QObject, pyqtSignal



class DataManager:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.volume_dir = self.root_dir / "volume"
        self.segmentation_dir = self.root_dir / "segmentation"
        self.manifest = {}

        self.vol_list, self.seg_list = self.create_list()
        self.manifest = self.create_manifest()

    def create_list(self):
        vol_list = sorted(list(self.volume_dir.glob("*nrrd")))
        seg_list = sorted(list(self.segmentation_dir.glob("*nrrd")))
        return vol_list, seg_list

    def generator_pair(self, vol_list, seg_list):
        zipped = zip(vol_list, seg_list)
        for vol, seg in zipped:
            vol = self.loaddata(vol)
            seg = self.loaddata(seg)
            yield vol, seg

    def loaddata(self, data):
        data, header = nrrd.read(data, index_order="C")
        return data, header

    def load_data_pair(self, vol_path, seg_path):
        """Loads a single pair of nrrd files from their paths."""
        vol_data, vol_header = self.loaddata(vol_path)
        seg_data, seg_header = self.loaddata(seg_path)
        # Return whatever format is most useful for you
        # return (vol_data, vol_header), (seg_data, seg_header)

        return vol_data, seg_data

    # return a generator object
    def __iter__(self):
        return self.generator_pair(self.vol_list, self.seg_list)

    def __len__(self):
        return len(self.vol_list)

    def __getitem__(self, index):
        if not 0 <= index < len(self):
            raise IndexError(
                f"Index {index} is out of range for dataset of size {len(self)}."
            )
        vol_data = self.manifest[index]["vol"]
        seg_data = self.manifest[index]["seg"]

        return self.load_data_pair(vol_data, seg_data)

    def create_manifest(self):
        for index, (vol, seg) in enumerate(zip(self.vol_list, self.seg_list)):
            self.manifest[index] = {"vol": vol, "seg": seg}

        return self.manifest

    def find_match(self, pattern):
        regex_pattern = re.compile(pattern)
        match_found = [
            found for found in str(self.vol_list) if regex_pattern.search(found)
        ]
        return match_found

    def get_Manifest(self):
        return self.manifest


# A way control position_states:
#
class DataManagerNavigator:
    """
    A stateful navigator to provide next() and back() controls
    for a stateless DataManager.
    """

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self._position = 0  # Start at the first __getitem__

    @property
    def position(self):
        """Returns the current index."""
        return self._position

    def current(self):
        return self.data_manager[self._position]

    def next(self):
        """Moves to the next item and returns it."""
        if self._position >= len(self.data_manager) - 1:
            self._position = 0
            print(self._position)
            return self.current()

        

        print(self._position)

        self._position += 1
        return self.current()

    def back(self):
        """Moves to the previous item and returns it."""
        if self._position <= 0:
            raise IndexError("Already at the first item. Cannot go back.")
        self._position -= 1
        return self.current()

    def seek(self, index: int):
        """Jumps directly to a specific index."""
        # We can leverage the DataManager's bounds checking
        if not 0 <= index < len(self.data_manager):
            raise IndexError(f"Seek index {index} is out of range.")
        self._position = index
        return self.current()
