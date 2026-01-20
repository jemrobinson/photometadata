import logging
from collections import Counter
from collections.abc import Generator, Iterable
from pathlib import Path
from photometadata.photo import Photo
from photometadata.settings import Settings

logger = logging.getLogger(__name__)

class Library:
    def __init__(self, path: str | Path, settings: Settings) -> None:
        self.base_path = Path(path).resolve(strict=True)
        logger.info(f"Looking for files under [cyan]{self.base_path}[/]")
        self.settings = settings
        self.photos: list[Photo] = sorted((
           Photo(filepath)
           for ext in self.settings.extensions
           for filepath in self.base_path.rglob(f"*.{ext}")
        ), key=lambda p: p.metadata.filepath)
        logger.info(f"Found [bold]{len(self.photos)}[/] files under [cyan]{self.base_path}[/]")

    def check_photos(self) -> None:
        """Check metadata for all photos in the library."""
        self.summarise(map(lambda photo: photo.check(), self.walk()))

    def summarise(self, result: Iterable[tuple[bool, str]]) -> None:
        """Summarise the result of a photo processing operation."""
        n_photos = Counter()
        for success, msg in result:
            if success:
                logger.debug(msg)
            else:
                logger.error(msg)
                n_photos["failed"] += 1
            n_photos["processed"] += 1
        percentage = (
            100.0 * n_photos["failed"] / n_photos["processed"]
            if n_photos["processed"]
            else 0
        )
        logger.info(
            f"Processed [bold]{n_photos['processed']}[/] photos of which [red]{n_photos['failed']}[/] ([red]{percentage:.2f}%[/]) failed validation"
        )

    def walk(self) -> Generator[Photo, None, None]:
        """Generator that yields all photos in the library."""
        current_dir = None
        for photo in self.photos:
            if photo.directory != current_dir:
                current_dir = photo.directory
                logger.info(f"Working on directory [cyan]{current_dir}[/]")
            yield photo
