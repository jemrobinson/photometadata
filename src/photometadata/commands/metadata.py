"""Command for fixing photo metadata"""

import logging
import typer

from photometadata.library import Library
from photometadata.settings import Settings

logger = logging.getLogger(__name__)

metadata_command = typer.Typer()


@metadata_command.command(no_args_is_help=True)
def metadata(path: str, settings: str = "settings.yaml") -> None:
    """Fix inconsistent photo metadata."""
    settings_ = Settings(settings)
    library = Library(path, settings_)
    library.fix_metadata()
