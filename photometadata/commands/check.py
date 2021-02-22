from cleo import Command
from clikit.api.io import flags as verbosity
from .processor import ProcessorMixin


class CheckCommand(ProcessorMixin, Command):
    """
    Checks a photo's metadata

    check
        {path : Location to look for photos under}
    """

    def handle(self):
        self.process_path(self.argument("path"))

    def process_metadata(self, metadata):
        output_tuple = (True, "<info>Validated</info>")
        if metadata.all_dates_equal():
            self.line(
                f"  <info>\u2714</info> All dates are equal ({metadata.canonical_date})",
                verbosity=verbosity.VERY_VERBOSE,
            )
        else:
            self.line(
                f"  <error>\u2716</error> Not all dates are equal!",
                verbosity=verbosity.VERY_VERBOSE,
            )
            output_tuple = (False, "<error>Failed to validate</error>")
        if metadata.copyright:
            self.line(
                f"  <info>\u2714</info> Found copyright information ({metadata.copyright})",
                verbosity=verbosity.VERY_VERBOSE,
            )
        else:
            output_tuple = (False, "<error>Failed to validate</error>")
        if (not metadata.name) and (not metadata.comment):
            self.line(
                f"  <error>\u2716</error> No comment or document name found!",
                verbosity=verbosity.VERY_VERBOSE,
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
