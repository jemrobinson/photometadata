import logging
import typer

from rich.logging import RichHandler
from rich.highlighter import NullHighlighter

from photometadata.commands import DuplicatesCommand, FixCommand
from photometadata.commands import check_command, classify_command

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, highlighter=NullHighlighter())]
)

application = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Entrypoint for photometadata commands",
    no_args_is_help=True,
)
application.add_typer(check_command)
application.add_typer(classify_command)

@application.command(no_args_is_help=True)
def duplicates(path: str):
    """Check for duplicates among all photos in a given path."""
    cmd = DuplicatesCommand()
    cmd.process_path(path)

@application.command(no_args_is_help=True)
def fix(path: str):
    """Fix metadata issues for all photos in a given path."""
    cmd = FixCommand()
    cmd.process_path(path)

def main():
    application()

if __name__ == "__main__":
    main()
