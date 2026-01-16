"""Command for checking photo metadata"""
from typing import Any

from cleo import Command

from photometadata import Metadata
from photometadata.mixins import ProcessorMixin


class DuplicatesCommand(ProcessorMixin, Command):
    """
    Checks for duplicated photos

    duplicates
        {target : Location that photos are stored under}
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.database: list[Metadata] = []
        super().__init__(*args, **kwargs)

    def handle(self) -> None:
        self.process_path(self.argument("target"))

    def process_metadata(self, metadata: Metadata) -> tuple[bool, str]:

        for existing in self.database:
            if metadata.fingerprint == existing.fingerprint:
                self.line(f"<b>{metadata.filepath}</b> and <b>{existing.filepath}</b> are duplicates")
                # Comment
                if metadata.comment == existing.comment:
                    self.line(
                        f"  <info>\u2714</info> Comments match ({metadata.comment})",
                    )
                else:
                    self.line(
                        f"  <error>\u2716</error> Comment differs: <b>{metadata.comment}</b> and <b>{existing.comment}</b>",
                    )
                # Copyright
                if metadata.copyright == existing.copyright:
                    self.line(
                        f"  <info>\u2714</info> Copyright matches: ({metadata.comment})",
                    )
                else:
                    self.line(
                        f"  <error>\u2716</error> Copyright differs: <b>{metadata.copyright}</b> and <b>{existing.copyright}</b>",
                    )
                # Dates
                if metadata.canonical_date == existing.canonical_date:
                    self.line(
                        f"  <info>\u2714</info> All dates match ({metadata.canonical_date})",

                    )
                else:
                    self.line(
                        f"  <error>\u2716</error> Dates differ: <b>{metadata.dates}</b> and <b>{existing.dates}</b>",
                    )

                # Name
                if metadata.name == existing.name:
                    self.line(
                        f"  <info>\u2714</info> Name matches ({metadata.name})",

                    )
                else:
                    self.line(
                        f"  <error>\u2716</error> Name differs: <b>{metadata.name}</b> and <b>{existing.name}</b>",
                    )
        self.database.append(metadata)
        return (True, "")
