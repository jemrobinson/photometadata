import logging
from pathlib import Path
from photometadata.photo import Photo
from photometadata.settings import Settings

logger = logging.getLogger(__name__)

class Library:
    def __init__(self, path: str | Path, settings: Settings) -> None:
        self.base_path = Path(path).resolve(strict=True)
        self.settings = settings
        self.photos: list[Photo] = [
           Photo(filepath)
           for ext in self.settings.extensions
           for filepath in self.base_path.rglob(f"*.{ext}")
        ]
        logger.info(f"Found [bold]{len(self.photos)}[/] files under [cyan]{self.base_path}[/].")
