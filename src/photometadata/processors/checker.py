import logging
from .processor import Processor, ProcessingResult
from photometadata.photo import Photo

logger = logging.getLogger(__name__)

class Checker(Processor):
    def __call__(self, photo: Photo) -> ProcessingResult:
        output = ProcessingResult(True, "<info>Validated</info>")
        # Check for broken image
        if photo.metadata.fingerprint == "NotAvailable":
            logger.error("  <error>\u2716</error> Image data is broken!")
            output = ProcessingResult(False, "<error>Failed to validate</error>")
        # Check for equal dates
        if photo.metadata.all_dates_equal():
            logger.debug(f"  <info>\u2714</info> All dates are equal ({photo.metadata.canonical_date})")
        else:
            logger.error("  <error>\u2716</error> Not all dates are equal!")
            output = ProcessingResult(False, "<error>Failed to validate</error>")
        # Check for copyright
        if photo.metadata.copyright:
            logger.debug(
                f"  <info>\u2714</info> Found copyright information ({photo.metadata.copyright})",
            )
        else:
            logger.info("  <error>\u2716</error> Copyright is missing!")
            output = ProcessingResult(False, "<error>Failed to validate</error>")
        # Check for name or comment
        if (not photo.metadata.name) and (not photo.metadata.comment):
            logger.info("  <error>\u2716</error> No comment or document name found!")
            output = ProcessingResult(False, "<error>Failed to validate</error>")
        else:
            if photo.metadata.name:
                logger.debug(f"  <info>\u2714</info> Found document name ({photo.metadata.name})")
            if photo.metadata.comment:
                logger.debug(f"  <info>\u2714</info> Found comment information ({photo.metadata.comment})")
        return output