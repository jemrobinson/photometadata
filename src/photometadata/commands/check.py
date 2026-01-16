"""Command for checking photo metadata"""
from cleo import Command
from clikit.api.io import flags as verbosity

from photometadata import Metadata
from photometadata.mixins import ProcessorMixin


class CheckCommand(ProcessorMixin, Command):
    """
    Checks a photo's metadata

    check
        {path : Location to look for photos under}
    """

    def handle(self) -> None:
        self.process_path(self.argument("path"))

    def process_metadata(self, metadata: Metadata):
        output_tuple = (True, "<info>Validated</info>")
        # Check for broken image
        if metadata.fingerprint == "NotAvailable":
            self.line(
                "  <error>\u2716</error> Image data is broken!",
                verbosity=verbosity.NORMAL,
            )
            output_tuple = (False, "<error>Failed to validate</error>")
        # Check for equal dates
        if metadata.all_dates_equal():
            self.line(
                f"  <info>\u2714</info> All dates are equal ({metadata.canonical_date})",
                verbosity=verbosity.VERY_VERBOSE,
            )
        else:
            self.line(
                "  <error>\u2716</error> Not all dates are equal!",
                verbosity=verbosity.NORMAL,
            )
            output_tuple = (False, "<error>Failed to validate</error>")
        # Check for copyright
        if metadata.copyright:
            self.line(
                f"  <info>\u2714</info> Found copyright information ({metadata.copyright})",
                verbosity=verbosity.VERY_VERBOSE,
            )
        else:
            self.line(
                "  <error>\u2716</error> Copyright is missing!",
                verbosity=verbosity.NORMAL,
            )
            output_tuple = (False, "<error>Failed to validate</error>")
        # Check for name or comment
        if (not metadata.name) and (not metadata.comment):
            self.line(
                "  <error>\u2716</error> No comment or document name found!",
                verbosity=verbosity.NORMAL,
            )
            output_tuple = (False, "<error>Failed to validate</error>")
        else:
            if metadata.name:
                self.line(
                    f"  <info>\u2714</info> Found document name ({metadata.name})",
                    verbosity=verbosity.VERY_VERBOSE,
                )
            if metadata.comment:
                self.line(
                    f"  <info>\u2714</info> Found comment information ({metadata.comment})",
                    verbosity=verbosity.VERY_VERBOSE,
                )
        return output_tuple
