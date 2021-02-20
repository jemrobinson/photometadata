from cleo import Command
from .processor import ProcessorMixin


class CheckCommand(ProcessorMixin, Command):
    """
    Checks a photo's metadata

    check
        {path : Location to look for photos under}
    """

    def handle(self):
        self.names = set()
        self.process_path(self.argument("path"))
        self.line(f"<error>{self.names}</error>")

    def process_metadata(self, metadata):
        failed = False
        if metadata.all_dates_equal():
            self.line(
                f"... <info>\u2713</info> All dates are equal ({metadata.canonical_date})"
            )
        else:
            self.line(f"... <error>\u2717</error> Not all dates are equal!")
            failed = True
        if metadata.copyright:
            self.line(
                f"... <info>\u2713</info> Found copyright information ({metadata.copyright})"
            )
        if (not metadata.name) and (not metadata.comment):
            self.line(f"... <error>\u2717</error> No comment or document name found!")
            failed = True
        else:
            if metadata.name:
                self.line(
                    f"... <info>\u2713</info> Found document name ({metadata.name})"
                )
            if metadata.comment:
                self.line(
                    f"... <info>\u2713</info> Found comment information ({metadata.comment})"
                )
        if metadata.read_tag("Camera") == "Panasonic DMC-TZ6":
            self.names.add(metadata.filepath.name)
        return not failed
