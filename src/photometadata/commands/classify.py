"""Command for adding tags to a photo"""

import logging
import typer

from photometadata.library import Library
from photometadata.settings import Settings

logger = logging.getLogger(__name__)

classify_command = typer.Typer()


@classify_command.command(no_args_is_help=True)
def classify(path: str, settings: str = "settings.yaml") -> None:
    """Add tags to a photo using Azure Compute Vision."""
    settings_ = Settings(settings)
    library = Library(path, settings_)
    library.classify_photos()
