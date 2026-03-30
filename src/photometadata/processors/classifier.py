import logging
from .processor import Processor, ProcessingResult
from photometadata.photo import Photo
from photometadata.settings import Settings
from typing import cast

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import (
    ComputerVisionErrorResponseException,
    ImageTag,
    TagResult,
)
import io
from PIL import Image


logger = logging.getLogger(__name__)


class Classifier(Processor):
    def __init__(self, settings: Settings) -> None:
        self.cv_client_: ComputerVisionClient | None = None
        self.settings = settings
        self.resized_image_shape = (512, 512)
        self.confidence_cutoff = 0.8

    @property
    def cv_client(self) -> ComputerVisionClient:
        if not self.cv_client_:
            self.cv_client_ = ComputerVisionClient(
                self.settings.azure.endpoint,
                CognitiveServicesCredentials(self.settings.azure.subscription_key),
            )
        return self.cv_client_

    def __call__(self, photo: Photo) -> ProcessingResult:
        if photo.metadata.keywords:
            return ProcessingResult(True, "Skipping as photo is already tagged.")

        # Get tags from Azure computer vision
        logger.debug("\u2714 attempting to load tags from Azure Computer Vision")
        img_bytes = open(photo.metadata.filepath, "rb")
        try:
            cv_results = self.cv_client.tag_image_in_stream(img_bytes)
        except ComputerVisionErrorResponseException:
            img_bytes = io.BytesIO()
            Image.open(photo.metadata.filepath).resize(self.resized_image_shape).save(
                img_bytes, format="JPEG"
            )
            img_bytes.seek(0)
            cv_results = self.cv_client.tag_image_in_stream(img_bytes)

        # Add all tags with a high enough confidence score
        if isinstance(cv_results, TagResult):
            tags_all = sorted(
                cast(list[ImageTag], cv_results.tags),
                key=lambda tag: tag.confidence,
                reverse=True,
            )
            tags_selected = [tags_all[0].name] + [
                tag.name
                for tag in tags_all[1:]
                if tag.confidence > self.confidence_cutoff
            ]

            # Update the metadata
            logger.debug(f"Found <b>{len(tags_selected)}</b> classes: {tags_selected}")
            return self.run_exiv_cmds(
                [
                    f'exiv2 -q -M "add Iptc.Application2.Keywords String {tag_name}" "{photo.metadata.filepath}"'
                    for tag_name in tags_selected
                ]
            )

        # Return an error if tags could not be retrieved
        logger.error("  [red]\u2716[/] Failed to get tags from Azure Computer Vision")
        return ProcessingResult(False, "[red]Failed to classify[/]")
