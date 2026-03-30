import logging
from pathlib import Path
from photometadata.metadata import Metadata
# from photometadata.processors import ProcessingResult


logger = logging.getLogger(__name__)


class Photo:
    def __init__(self, path: Path) -> None:
        self.metadata = Metadata(path)

    @property
    def directory(self) -> Path:
        return self.metadata.filepath.parent
