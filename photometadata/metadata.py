import exifread
import pendulum
import re


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
        except pendulum.parsing.exceptions.ParserError:
            try:
                return pendulum.parse(date.replace("-", "T").replace("_", "T"))
            except:
               raise

    def extract_date_from_filename(self):
        timestamp_regex = re.compile(r".*([12][0-9]{3}[01][0-9][0-3][0-9][-_T][0-9]{6}).*")
        if (m := timestamp_regex.match(self.path.name)) :
            return self.parse_date(m.group(1))
        return None

    @property
    def dates(self):
        return {
            "Filename": self.extract_date_from_filename(),
            "Exif.Image.DateTime": self.parse_date(self.tags["Image DateTime"].printable),
            "Exif.Photo.DateTimeDigitized": self.parse_date(self.tags["EXIF DateTimeDigitized"].printable),
            "Exif.Photo.DateTimeOriginal": self.parse_date(self.tags["EXIF DateTimeOriginal"].printable),
        }

    @property
    def copyright(self):
        try:
            return {"Exif.Image.Copyright": self.tags["Image Copyright"].printable.strip()}
        except KeyError:
            return {}

    @property
    def name(self):
        try:
            return {"Exif.Image.DocumentName": self.tags["Image DocumentName"].printable.strip()}
        except KeyError:
            return {}

    @property
    def comment(self):
        try:
            return {"Exif.Photo.UserComment": self.tags["EXIF UserComment"].printable.strip()}
        except KeyError:
            return {}

    @property
    def canonical_date(self):
        if self.all_dates_equal:
            return list(self.dates.values())[0]
        return None

    def all_dates_equal(self):
        dates = list(self.dates.values())
        return dates.count(dates[0]) == len(dates)

