import re
import subprocess
import yaml
from cleo import Command
from emoji import emojize
from .processor import ProcessorMixin
from ..metadata import Metadata


class FixCommand(ProcessorMixin, Command):
    """
    Fixes a photo's metadata

    fix
        {path : Location to look for photos under}
        {--f|filename : If set, the date stored in the filename will be used in case of conflict}
        {--s|settings=settings : If set, load settings from the specified YAML file}
    """

    def __init__(self):
        self.settings = None
        super().__init__()

    def handle(self):
        if self.option("settings"):
            with open(self.option("settings"), "r") as f_yaml:
                try:
                    self.settings = yaml.safe_load(f_yaml)
                except:
                    self.line(
                        f"<error>Could not load {self.option('settings')}!</error>"
                    )
                    raise
        self.process_path(self.argument("path"))

    def process_metadata(self, metadata):
        tags2set = {}

        if not metadata.all_dates_equal():
            date = self.choose_date(metadata.dates)
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
                emojize(
                    f"... <info>:calendar:</info> will update all dates to ({date})"
                )
            )
        if not metadata.copyright:
            copyright_ = self.choose_copyright(metadata)
            tags2set.update({"Exif.Image.Copyright": copyright_})
            self.line(
                emojize(
                    f"... <info>:clipboard:</info> adding copyright holder ({copyright_})"
                )
            )
        if (not metadata.name) and (not metadata.comment):
            document_name = metadata.filepath.stem.split("- ")[-1].upper()
            tags2set.update({"Exif.Image.DocumentName": document_name})
            self.line(
                emojize(
                    f"... <info>:memo:</info> adding previously-missing DocumentName ({document_name})"
                )
            )

        if tags2set:
            self.update_metadata(tags2set, metadata.filepath.name)
            return False
        return True

    @staticmethod
    def update_metadata(tags, filename):
        # Update with exiv2
        exiv_cmds = [
            f'exiv2 -M "set {tag_name} {tag_value}" "{filename}"'
            for tag_name, tag_value in tags.items()
        ]
        exiv_cmds += [f'exiv2 -d t "{filename}"']
        for exiv_cmd in exiv_cmds:
            try:
                subprocess.call(exiv_cmd, shell=True)
            except (TypeError, ValueError):
                self.line(f"<error>{exiv_cmd} failed!</error>")
                raise

    def choose_date(self, dates):
        if self.option("filename") and dates["Filename"]:
            # self.line("... auto-accepting filename match for date")
            return dates["Filename"]
        available_dates = list(set([d for d in dates.values() if d]))
        self.line(f"... there are <info>{len(available_dates)}</info> different dates")
        date_map = {
            str(idx): date for idx, date in enumerate(sorted(available_dates), start=1)
        }
        for k, v in date_map.items():
            self.line(f"   {k}) {v}")
        self.line("    OR enter a date in 'YYYY:MM:DD HH:MM:SS' format")
        user_input = str(input("Change dates to one of these options? (1/2...) "))
        if user_input in date_map:
            return date_map[user_input]
        return Metadata.parse_date(user_input)

    def choose_copyright(self, metadata):
        if "copyright" in self.settings:
            for ruleset in self.settings["copyright"]:
                for rule in ruleset["whenever"]:
                    tag, value = list(rule.items())[0]
                    if tag == "filename-regex":
                        regex = re.compile(value)
                        if (m := regex.match(metadata.filepath.name)) :
                            return ruleset["name"]
                    elif metadata.read_tag(tag).upper() == value.upper():
                        return ruleset["name"]
        user_input = str(
            input(
                "No copyright rule found. Please enter the name of the copyright holder: "
            )
        )
        return user_input
