import typer

from photometadata.commands import (CheckCommand, ClassifyCommand,
                                    DuplicatesCommand, FixCommand)

application = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Entrypoint for photometadata commands",
    no_args_is_help=True,
)

@application.command(no_args_is_help=True)
def check(path: str):
    """Check metadata for all photos in a given path."""
    cmd = CheckCommand()
    cmd.process_path(path)

@application.command(no_args_is_help=True)
def classify(path: str, settings: str = "settings.yaml"):
    """Add tags to a photo using Azure Compute Vision."""
    cmd = ClassifyCommand()
    cmd.process_path(path)

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
