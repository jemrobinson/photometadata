import logging
import typer

from rich.logging import RichHandler
from rich.highlighter import NullHighlighter

from photometadata.commands import check_command, classify_command, duplicates_command, metadata_command

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(markup=True, highlighter=NullHighlighter())]
    )

    # Build the typer application
    application = typer.Typer(
        context_settings={"help_option_names": ["-h", "--help"]},
        help="Entrypoint for photometadata commands",
        no_args_is_help=True,
    )
    application.add_typer(check_command)
    application.add_typer(classify_command)
    application.add_typer(duplicates_command)
    application.add_typer(metadata_command)

    # Run the application
    application()

if __name__ == "__main__":
    main()
