import exifread
import pendulum
import re
from itertools import groupby


class Metadata:
    def __init__(self, file_path):
        self.path = file_path
        with open(str(self.path), "rb") as photo:
            self.tags = exifread.process_file(photo)

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
                print(f"Failed to parse '{date}'")
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
            return self.tags[name].printable.strip()
        return None

    @property
    def copyright(self):
        # return {"Exif.Image.Copyright": self.read_tag("Image Copyright")}
        return self.read_tag("Image Copyright")

    @property
    def name(self):
        # return {"Exif.Image.DocumentName": self.read_tag("Image DocumentName")}
        return self.read_tag("Image DocumentName")

    @property
    def comment(self):
        # return {"Exif.Photo.UserComment": self.read_tag("EXIF UserComment")}
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
