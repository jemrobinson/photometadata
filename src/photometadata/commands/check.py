"""Command for checking photo metadata"""
import logging
import typer

from photometadata.library import Library
from photometadata.settings import Settings

logger = logging.getLogger(__name__)

check_command = typer.Typer()

@check_command.command(no_args_is_help=True)
def check(path: str, settings: str = "settings.yaml") -> None:
    """Check metadata for all photos in a given path."""
    settings_ = Settings(settings)
    library = Library(path, settings_)
    library.check_photos()
