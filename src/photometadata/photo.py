import logging
from pathlib import Path
from photometadata.metadata import Metadata
# from photometadata.processors import ProcessingResult


logger = logging.getLogger(__name__)


class Photo:
    def __init__(self, path: Path) -> None:
        self.metadata = Metadata(path)

    @property
    def directory(self) -> Path:
        return self.metadata.filepath.parent

    # def add_tag(self, tag: str) -> None:
    #     # if tag not in self.metadata.keywords:
    #     #     self.metadata.keywords.append(tag)

    #     # f'exiv2 -q -M "add Iptc.Application2.Keywords String {tag_name}" "{photo.metadata.filepath}"'
    #                     # for tag_name in tags_selected
