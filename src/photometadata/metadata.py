"""Class for holding photo metadata"""
import logging
import re
from hashlib import sha256
from itertools import groupby
from pathlib import Path
from PIL import Image

import exifread
import pendulum
from exifread.core.exif_header import IfdTag
from exifread.tags.fields import FieldType
from struct import error as StructError
from iptcinfo3 import IPTCInfo
from pendulum.parsing.exceptions import ParserError
from pendulum.tz import UTC

# Suppress 'Possibly corrupted field' messages from exifread
logging.getLogger("exifread").setLevel(logging.CRITICAL)

# Suppress 'problems with charset recognition' messages from iptcinfo3
logging.getLogger("iptcinfo").setLevel(logging.CRITICAL)


class Metadata:
    """Class for holding photo metadata"""

    IGNORED_FIELD_TYPES = [
        FieldType.PROPRIETARY,
        FieldType.UNDEFINED,
    ]

    def __init__(self, file_path: str | Path) -> None:
        """Constructor"""
        self.path = Path(file_path).resolve()
        try:
            with open(self.path, "rb") as photo:
                try:
                    self.tags: dict[str, IfdTag] = exifread.process_file(photo)
                except StructError:
                    self.tags = {}
                    self.fingerprint = "NotAvailable"
                self.keywords = (
                    [kwd.decode() for kwd in iptc["keywords"]]
                    if (iptc := IPTCInfo(photo))
                    else []
                )
            try:
                with Image.open(self.path) as im:
                    self.histogram = im.histogram()
                    self.height = im.height
                    self.width = im.width
                self.fingerprint = sha256(str([self.width, self.height] + self.histogram).encode("utf-8")).hexdigest()
            # Broken image file
            except OSError:
                self.fingerprint = "NotAvailable"
        except Exception as exc:
            print(type(exc), exc)
            raise

    def __repr__(self) -> str:
        """String representation"""
        return f"{self.path}"

    @property
    def canonical_date(self) -> pendulum.DateTime | None:
        """Return a date if there is one, unambiguous one"""
        if self.all_dates_equal():
            return [d for d in self.dates.values() if d][0]
        return None

    @property
    def comment(self) -> str | None:
        """Return the value of the user comment tag"""
        return self.read_tag("EXIF UserComment")

    @property
    def copyright(self) -> str | None:
        """Return the value of the copyright tag"""
        return self.read_tag("Image Copyright")

    @property
    def dates(self) -> dict[str, pendulum.DateTime | None]:
        """Get all available dates for this file"""
        return {
            "Filename": self.extract_date_from_filename(),
            "Exif.Image.DateTime": self.parse_date(self.read_tag("Image DateTime")),
            "Exif.Photo.DateTimeDigitized": self.parse_date(
                self.read_tag("EXIF DateTimeDigitized")
            ),
            "Exif.Photo.DateTimeOriginal": self.parse_date(
                self.read_tag("EXIF DateTimeOriginal")
            ),
        }

    @property
    def filename(self) -> str:
        """Return the filename for the file in question"""
        return self.path.name

    @property
    def filepath(self) -> Path:
        """Return the path for the file in question"""
        return self.path

    @property
    def name(self) -> str | None:
        """Return the value of the document name tag"""
        return self.read_tag("Image DocumentName")

    @staticmethod
    def parse_date(date: str) -> pendulum.DateTime:
        """Attempt to parse a string into a date"""
        try:
            parsed_date = pendulum.parse(date)
        except (ParserError, TypeError, ValueError):
            try:
                parsed_date = pendulum.parse(date.replace("-", "T").replace("_", "T"))
            except (AttributeError, ParserError, TypeError, ValueError):
                parsed_date = None
        # Unexpected date type
        if not isinstance(parsed_date, pendulum.DateTime):
            msg = f"String '{date}' could not be parsed as a date!"
            raise ValueError(msg)
        return parsed_date

    def all_dates_equal(self) -> bool:
        """Check whether all dates are equal"""
        dates = [d for d in self.dates.values() if d]
        if not dates:
            return False
        return dates.count(dates[0]) == len(dates)

    def extract_date_from_filename(self) -> pendulum.DateTime | None:
        """Extract a date from a filename"""
        timestamp_regex = re.compile(
            r".*([12][0-9]{3}[01][0-9][0-3][0-9][-_T][0-9]{6}).*"
        )
        if match := timestamp_regex.match(self.path.name):
            return self.parse_date(match.group(1))
        return None

    def read_tag(self, name: str) -> str | None:
        """Return the value of a given tag"""
        if name == "Camera":
            raw_string = " ".join(
                [
                    t
                    for t in [self.read_tag("Image Make"), self.read_tag("Image Model")]
                    if t
                ]
            )
            return " ".join([group[0] for group in groupby(raw_string.split(" "))])
        if name in self.tags:
            if self.tags[name].field_type in self.IGNORED_FIELD_TYPES:
                return None
            return self.tags[name].printable.strip()
        return None
