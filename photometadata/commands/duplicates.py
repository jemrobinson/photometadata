"""Command for checking photo metadata"""
from cleo import Command

from photometadata import Metadata
from photometadata.mixins import ProcessorMixin


class DuplicatesCommand(ProcessorMixin, Command):
    """
    Checks for duplicated photos

    duplicates
        {target : Location that photos should be stored under}
        {sources : Locations where duplicate photos might exist}
    """

    def handle(self) -> None:
        self.process_path(self.argument("target"))

    def process_metadata(self, metadata: Metadata) -> tuple[bool, str]:
        return (True, "")
