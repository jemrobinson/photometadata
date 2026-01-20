import logging
from pathlib import Path
from photometadata.metadata import Metadata

logger = logging.getLogger(__name__)
class Photo:
    def __init__(self, path: Path) -> None:
        self.metadata = Metadata(path)

    @property
    def directory(self) -> Path:
        return self.metadata.filepath.parent

    def check(self) -> tuple[bool, str]:
        output_tuple = (True, "<info>Validated</info>")
        # Check for broken image
        if self.metadata.fingerprint == "NotAvailable":
            logger.error("  <error>\u2716</error> Image data is broken!")
            output_tuple = (False, "<error>Failed to validate</error>")
        # Check for equal dates
        if self.metadata.all_dates_equal():
            logger.debug(f"  <info>\u2714</info> All dates are equal ({self.metadata.canonical_date})")
        else:
            logger.error("  <error>\u2716</error> Not all dates are equal!")
            output_tuple = (False, "<error>Failed to validate</error>")
        # Check for copyright
        if self.metadata.copyright:
            logger.debug(
                f"  <info>\u2714</info> Found copyright information ({self.metadata.copyright})",
            )
        else:
            logger.info("  <error>\u2716</error> Copyright is missing!")
            output_tuple = (False, "<error>Failed to validate</error>")
        # Check for name or comment
        if (not self.metadata.name) and (not self.metadata.comment):
            logger.info("  <error>\u2716</error> No comment or document name found!")
            output_tuple = (False, "<error>Failed to validate</error>")
        else:
            if self.metadata.name:
                logger.debug(f"  <info>\u2714</info> Found document name ({self.metadata.name})")
            if self.metadata.comment:
                logger.debug(f"  <info>\u2714</info> Found comment information ({self.metadata.comment})")
        return output_tuple