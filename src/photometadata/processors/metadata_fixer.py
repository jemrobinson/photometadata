import logging
from pathlib import Path
from .processor import Processor, ProcessingResult
from photometadata.photo import Photo
from photometadata.metadata import Metadata
from photometadata.settings import Settings
import pendulum
from rich.prompt import Prompt
import re

logger = logging.getLogger(__name__)


class MetadataFixer(Processor):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def __call__(self, photo: Photo) -> ProcessingResult:
        tags2set = {}
        if not photo.metadata.all_dates_equal():
            date = self.choose_date(photo.metadata)
            tags2set.update(
                {
                    key: date.strftime(r"%Y:%m:%d %H:%M:%S")
                    for key in (
                        "Exif.Image.DateTime",
                        "Exif.Photo.DateTimeDigitized",
                        "Exif.Photo.DateTimeOriginal",
                    )
                }
            )
            logger.debug(f"  <info>\u2714</info> updating all dates to ({date})")
            self.set_filename_date(photo.metadata, date)
        if not photo.metadata.copyright:
            copyright_ = self.choose_copyright(photo.metadata)
            tags2set.update({"Exif.Image.Copyright": copyright_})
            logger.debug(
                f"  <info>\u2714</info> adding copyright holder ({copyright_})",
            )
        if (not photo.metadata.name) and (not photo.metadata.comment):
            document_name = photo.metadata.filepath.stem.split("- ")[-1].upper()
            tags2set.update({"Exif.Image.DocumentName": document_name})
            logger.debug(
                f"  <info>\u2714</info> setting DocumentName ({document_name})",
            )

        if tags2set:
            return self.update_metadata(tags2set, photo.metadata.filepath)
        return ProcessingResult(True, "<info>Validated</info>")

    def update_metadata(self, tags: dict[str, str], filepath: Path) -> ProcessingResult:
        """Update file metadata using exiv2"""
        # Update with exiv2
        exiv_cmds = [
            f'exiv2 -q -M "set {tag_name} {tag_value}" "{str(filepath)}"'
            for tag_name, tag_value in tags.items()
        ]
        exiv_cmds += [f'exiv2 -q -d t "{str(filepath)}"']
        return self.run_exiv_cmds(exiv_cmds)

    def choose_date(self, metadata: Metadata) -> pendulum.DateTime:
        """Choose the most appropriate date using user input"""
        # if self.option("filename") and metadata.dates["Filename"]:
        #     self.line(
        #         f"  <info>\u2714</info> auto-accepting filename match for date ({metadata.dates['Filename']})",
        #         verbosity=verbosity.VERY_VERBOSE,
        #     )
        #     return metadata.dates["Filename"]
        available_dates = sorted(
            list({date for date in metadata.dates.values() if date})
        )
        logger.info(
            f"Found [bold]{len(available_dates)}[/] different dates in [blue]{metadata.filepath}[/]"
        )
        date_map = {str(idx): date for idx, date in enumerate(available_dates, start=1)}
        for idx, date in date_map.items():
            logger.info(f"  [b]{idx})[/b] {date}")
        # Automatically take the earliest timestamp if they're all within 5 seconds
        if (available_dates[-1] - available_dates[0]).as_duration().seconds < 5:
            logger.info(
                f"Automatically selecting [b]{date_map['1']}[/b] among close-together timestamps."
            )
            return date_map["1"]
        else:
            user_input = Prompt.ask(
                "Please pick one of these options (1, 2, 3 etc.) or enter a date in 'YYYY:MM:DD HH:MM:SS' format:"
            )
            if user_input in date_map:
                return date_map[user_input]
        return Metadata.parse_date(user_input)

    def choose_copyright(self, metadata: Metadata) -> str:
        """Choose the most appropriate copyright using user input"""
        for ruleset in self.settings.copyright:
            for rule in ruleset.whenever:
                tag, value = list(rule.items())[0]
                if tag == "filename-regex":
                    regex = re.compile(value)
                    if regex.match(metadata.filename):
                        return ruleset.name
                elif (tag_value := metadata.read_tag(tag)) and (
                    tag_value.casefold() == value.casefold()
                ):
                    return ruleset.name
        logger.warning(f"No copyright rule found for {metadata.filepath}")
        return Prompt.ask("Please enter the name of the copyright holder:")

    def set_filename_date(self, metadata: Metadata, date: pendulum.DateTime) -> None:
        filename_date = metadata.extract_date_from_filename()
        if (not filename_date) or filename_date == date:
            return
        filename = metadata.filename.replace(
            filename_date.strftime(r"%Y%m%d_%H%M%S"), date.strftime(r"%Y%m%d_%H%M%S")
        )
        filepath = metadata.filepath.parent / filename
        metadata.path = metadata.filepath.rename(filepath)
