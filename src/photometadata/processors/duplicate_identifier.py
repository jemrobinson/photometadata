import logging
from .processor import Processor, ProcessingResult
from photometadata.photo import Photo
from photometadata.settings import Settings
import operator
from functools import reduce
from typing import cast

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import ComputerVisionErrorResponseException, ImageTag, TagResult
import io
from msrest.pipeline import ClientRawResponse
from PIL import Image


logger = logging.getLogger(__name__)

class DuplicateIdentifier(Processor):
    def __init__(self) -> None:
        self.duplicates: dict[str, set[Photo]] = {}

    def __call__(self, photo: Photo) -> ProcessingResult:
        if photo.metadata.fingerprint in self.duplicates:
            self.duplicates[photo.metadata.fingerprint].add(photo)
            return ProcessingResult(True, "Identified as duplicate.")
        self.duplicates[photo.metadata.fingerprint] = {photo}
        return ProcessingResult(True, "Not a duplicate.")

    @property
    def n_duplicates(self) -> int:
        print(self.duplicates)
        n_photos = reduce(operator.add, (len(group) for group in self.duplicates.values()))
        n_groups = len(self.duplicates)
        return n_photos - n_groups
