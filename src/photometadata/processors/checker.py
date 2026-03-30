import logging
from .processor import Processor, ProcessingResult
from photometadata.photo import Photo

logger = logging.getLogger(__name__)

class Checker(Processor):
    def __call__(self, photo: Photo) -> ProcessingResult:
        output = ProcessingResult(True, f"[blue]Validated {photo.metadata.path}[/]")
        # Check for broken image
        if photo.metadata.fingerprint == "NotAvailable":
            logger.error("  [red]\u2716[/] Image data is broken!")
            output = ProcessingResult(False, f"[red]Failed to validate {photo.metadata.path}[/]")
        # Check for equal dates
        if photo.metadata.all_dates_equal():
            logger.debug(f"  [blue]\u2714[/] All dates are equal ({photo.metadata.canonical_date})")
        else:
            logger.error("  [red]\u2716[/] Not all dates are equal!")
            output = ProcessingResult(False, f"[red]Failed to validate {photo.metadata.path}[/]")
        # Check for copyright
        if photo.metadata.copyright:
            logger.debug(
                f"  [blue]\u2714[/] Found copyright information ({photo.metadata.copyright})",
            )
        else:
            logger.info("  [red]\u2716[/] Copyright is missing!")
            output = ProcessingResult(False, f"[red]Failed to validate {photo.metadata.path}[/]")
        # Check for name or comment
        if (not photo.metadata.name) and (not photo.metadata.comment):
            logger.info("  [red]\u2716[/] No comment or document name found!")
            output = ProcessingResult(False, f"[red]Failed to validate {photo.metadata.path}[/]")
        else:
            if photo.metadata.name:
                logger.debug(f"  [blue]\u2714[/] Found document name ({photo.metadata.name})")
            if photo.metadata.comment:
                logger.debug(f"  [blue]\u2714[/] Found comment information ({photo.metadata.comment})")
        return output