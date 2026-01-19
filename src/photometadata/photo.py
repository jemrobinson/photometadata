from pathlib import Path
from photometadata.metadata import Metadata

class Photo:
    def __init__(self, path: Path) -> None:
        self.metadata = Metadata(path)