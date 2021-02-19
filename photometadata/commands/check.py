from cleo import Command
from pathlib import Path
from ..metadata import Metadata


class CheckCommand(Command):
    """
    Checks a photo's metadata

    check
        {path : Location to look for photos under}
    """

    def handle(self):
        nPhotos, nFailures = 0, 0
        for photo_path in Path(self.argument("path")).rglob("*.jpg"):
            nPhotos += 1
            self.line(f"{photo_path.name}")
            photo_metadata = Metadata(photo_path.resolve())
            failed = False
            if photo_metadata.all_dates_equal():
                self.line(f"... <info>\u2713</info> All dates are equal ({photo_metadata.canonical_date})")
            else:
                self.line(f"... <error>\u2717</error> Not all dates are equal!")
                failed = True
            if photo_metadata.copyright:
                self.line(f"... <info>\u2713</info> Found copyright information ({list(photo_metadata.copyright.values())[0]})")
            if (not photo_metadata.name) and (not photo_metadata.comment):
                self.line(f"... <error>\u2717</error> No comment or document name found!")
                failed = True
            else:
                if photo_metadata.name:
                    self.line(f"... <info>\u2713</info> Found document name ({list(photo_metadata.name.values())[0]})")
                if photo_metadata.comment:
                    self.line(f"... <info>\u2713</info> Found comment information ({list(photo_metadata.comment.values())[0]})")
            if failed:
                nFailures += 1
        self.line(f"Processed <question>{nPhotos}</question> photos, of which <question>{nFailures} ({100. * nFailures / nPhotos:.2f}%)</question> failed validation")
