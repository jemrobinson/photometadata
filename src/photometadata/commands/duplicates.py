"""Command for checking photo metadata for duplicates."""
import logging
import typer

from photometadata.library import Library
from photometadata.settings import Settings

logger = logging.getLogger(__name__)

duplicates_command = typer.Typer()

@duplicates_command.command(no_args_is_help=True)
def duplicates(path: str, settings: str = "settings.yaml") -> None:
    """Check for duplicated photos."""
    settings_ = Settings(settings)
    library = Library(path, settings_)
    library.identify_duplicates()
