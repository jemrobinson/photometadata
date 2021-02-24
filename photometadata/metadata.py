import exifread
from iptcinfo3 import IPTCInfo
import logging
import pendulum
import re
from itertools import groupby

# Suppress 'Possibly corrupted field' messages from exifread
logging.getLogger("exifread").setLevel(logging.CRITICAL)

# Suppress 'problems with charset recognition' messages from iptcinfo3
logging.getLogger("iptcinfo").setLevel(logging.CRITICAL)


class Metadata:
    def __init__(self, file_path):
        self.path = file_path
        with open(str(self.path), "rb") as photo:
            self.tags = exifread.process_file(photo)
            self.keywords = (
                [kwd.decode() for kwd in iptc["keywords"]]
                if (iptc := IPTCInfo(photo))
                else []
            )
        self.bad_field_types = [
            idx
            for idx, field in enumerate(exifread.tags.FIELD_TYPES)
            if field[2] in ("Proprietary", "Undefined")
        ]

    def __repr__(self):
        return f"{self.path}"

    @staticmethod
    def parse_date(date):
        try:
            return pendulum.parse(date)
        except:
            try:
                return pendulum.parse(date.replace("-", "T").replace("_", "T"))
            except:
                return None

    def extract_date_from_filename(self):
        timestamp_regex = re.compile(
            r".*([12][0-9]{3}[01][0-9][0-3][0-9][-_T][0-9]{6}).*"
        )
        if (m := timestamp_regex.match(self.path.name)) :
            return self.parse_date(m.group(1))
        return None

    @property
    def dates(self):
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
    def filepath(self):
        return self.path

    def read_tag(self, name):
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
            if self.tags[name].field_type in self.bad_field_types:
                return None
            return self.tags[name].printable.strip()
        return None

    @property
    def copyright(self):
        return self.read_tag("Image Copyright")

    @property
    def name(self):
        return self.read_tag("Image DocumentName")

    @property
    def comment(self):
        return self.read_tag("EXIF UserComment")

    @property
    def canonical_date(self):
        if self.all_dates_equal:
            return [d for d in self.dates.values() if d][0]
        return None

    def all_dates_equal(self):
        dates = [d for d in self.dates.values() if d]
        if not dates:
            return False
        return dates.count(dates[0]) == len(dates)
