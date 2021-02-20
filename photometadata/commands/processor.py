from cleo import Command
from pathlib import Path
from ..metadata import Metadata


class ProcessorMixin:
    """
    Mixin class for file processors
    """

    def process_path(self, path):
        nPhotos, nFailures = 0, 0
        for photo_path in Path(path).rglob("*.jpg"):
            nPhotos += 1
            self.line(f"{str(photo_path.resolve())}")
            photo_metadata = Metadata(photo_path.resolve())
            if not self.process_metadata(photo_metadata):
                nFailures += 1
        self.line(
            f"Processed <question>{nPhotos}</question> photos, of which <question>{nFailures} ({100. * nFailures / nPhotos:.2f}%)</question> failed validation"
        )

    def process_metadata(self, metadata):
        raise NotImplementedError(
            f"'process_metadata' must be implemented by {type(self).__name__}"
        )
