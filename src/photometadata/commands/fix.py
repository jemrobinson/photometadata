"""Command for fixing photo metadata"""
import re

from cleo import Command
from clikit.api.io import flags as verbosity
import pendulum

from photometadata import Metadata

from photometadata.mixins import ProcessorMixin


class FixCommand(ProcessorMixin, Command):
    """
    Fixes a photo's metadata

    fix
        {path : Location to look for photos under}
        {--f|filename : If set, the date stored in the filename will be used in case of conflict}
        {--s|settings=settings.yaml : If set, load settings from the specified YAML file}
    """

    def __init__(self):
        # Objects that will be initialised on first use
        self.settings = None
        super().__init__()

    def handle(self) -> None:
        if not self.settings and self.option("settings"):
            self.settings = self.load_settings(self.option("settings"))
        self.process_path(self.argument("path"))

    def process_metadata(self, metadata: Metadata) -> tuple[bool, str]:
        tags2set = {}

        if not metadata.all_dates_equal():
            date = self.choose_date(metadata)
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
            self.line(
                f"  <info>\u2714</info> updating all dates to ({date})",
                verbosity=verbosity.VERY_VERBOSE,
            )
            self.set_filename_date(metadata, date)
        if not metadata.copyright:
            copyright_ = self.choose_copyright(metadata)
            tags2set.update({"Exif.Image.Copyright": copyright_})
            self.line(
                f"  <info>\u2714</info> adding copyright holder ({copyright_})",
                verbosity=verbosity.VERY_VERBOSE,
            )
        if (not metadata.name) and (not metadata.comment):
            document_name = metadata.filepath.stem.split("- ")[-1].upper()
            tags2set.update({"Exif.Image.DocumentName": document_name})
            self.line(
                f"  <info>\u2714</info> setting DocumentName ({document_name})",
                verbosity=verbosity.VERY_VERBOSE,
            )

        if tags2set:
            return self.update_metadata(tags2set, metadata.filepath.resolve())
        return (True, "<info>Validated</info>")

    def update_metadata(self, tags: dict[str, str], filename: str) -> tuple[bool, str]:
        """Update file metadata using exiv2"""
        # Update with exiv2
        exiv_cmds = [
            f'exiv2 -q -M "set {tag_name} {tag_value}" "{filename}"'
            for tag_name, tag_value in tags.items()
        ]
        exiv_cmds += [f'exiv2 -q -d t "{filename}"']
        return self.run_exiv_cmds(exiv_cmds)

    def choose_date(self, metadata: Metadata) -> pendulum.DateTime:
        """Choose the most appropriate date using user input"""
        if self.option("filename") and metadata.dates["Filename"]:
            self.line(
                f"  <info>\u2714</info> auto-accepting filename match for date ({metadata.dates['Filename']})",
                verbosity=verbosity.VERY_VERBOSE,
            )
            return metadata.dates["Filename"]
        available_dates = sorted(
            list({date for date in metadata.dates.values() if date})
        )
        self.line(
            f"Found <info>{len(available_dates)}</info> different dates in {metadata.filepath.resolve()}"
        )
        date_map = {str(idx): date for idx, date in enumerate(available_dates, start=1)}
        for idx, date in date_map.items():
            self.line(f"  <b>{idx})</b> {date}")
        # Automatically take the earliest timestamp if they're all within 5 seconds
        if (available_dates[-1] - available_dates[0]).as_duration().seconds < 5:
            self.line(f"Automatically selecting <b>{date_map['1']}</b> among close-together timestamps.")
            return date_map["1"]
        else:
            user_input = self.ask(
                "Please pick one of these options (1, 2, 3 etc.) or enter a date in 'YYYY:MM:DD HH:MM:SS' format:"
            )
            if user_input in date_map:
                return date_map[user_input]
        return Metadata.parse_date(user_input)

    def choose_copyright(self, metadata: Metadata) -> str:
        """Choose the most appropriate copyright using user input"""
        if "copyright" in self.settings:
            for ruleset in self.settings["copyright"]:
                for rule in ruleset["whenever"]:
                    tag, value = list(rule.items())[0]
                    if tag == "filename-regex":
                        regex = re.compile(value)
                        if regex.match(metadata.filename):
                            return ruleset["name"]
                    elif metadata.read_tag(tag).upper() == value.upper():
                        return ruleset["name"]
        self.line(f"No copyright rule found for {metadata.filepath.resolve()}")
        return self.ask("Please enter the name of the copyright holder:")

    def set_filename_date(self, metadata: Metadata, date: pendulum.DateTime) -> None:
        filename_date = metadata.extract_date_from_filename()
        if (not filename_date) or filename_date == date:
            return
        filename = metadata.filename.replace(
            filename_date.strftime(r"%Y%m%d_%H%M%S"),
            date.strftime(r"%Y%m%d_%H%M%S")
        )
        filepath = metadata.filepath.parent / filename
        metadata.path = metadata.filepath.rename(filepath)

