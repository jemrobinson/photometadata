"""Command for adding tags to a photo"""
import io
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import (
    ComputerVisionErrorException,
)
from cleo import Command
from clikit.api.io import flags as verbosity
from msrest.authentication import CognitiveServicesCredentials
import PIL.Image as Image
from .processor import ProcessorMixin


class ClassifyCommand(ProcessorMixin, Command):
    """
    Add tags to a photo using Inception

    classify
        {path : Location to look for photos under}
        {--s|settings=settings.yaml : If set, load settings from the specified YAML file}
    """

    def __init__(self):
        # Objects that will be initialised on first use
        self.cv_client = None
        self.settings = None

        # Constants
        self.resized_image_shape = (512, 512)
        self.confidence_cutoff = 0.8
        super().__init__()

    def handle(self):
        if not self.settings and self.option("settings"):
            self.settings = self.load_settings(self.option("settings"))
        if not self.cv_client:
            self.cv_client = ComputerVisionClient(
                self.settings["azure"]["endpoint"],
                CognitiveServicesCredentials(
                    self.settings["azure"]["subscription_key"]
                ),
            )
        self.process_path(self.argument("path"))

    def process_metadata(self, metadata):
        if not metadata.keywords:
            self.line(
                "  <info>\u2714</info> attempting to add keywords",
                verbosity=verbosity.VERY_VERBOSE,
            )
            # Get tags from Azure computer vision
            img_bytes = open(metadata.filepath, "rb")
            try:
                cv_results = self.cv_client.tag_image_in_stream(img_bytes)
            except ComputerVisionErrorException:
                img_bytes = io.BytesIO()
                Image.open(metadata.filepath).resize(self.resized_image_shape).save(
                    img_bytes, format="JPEG"
                )
                img_bytes.seek(0)
                cv_results = self.cv_client.tag_image_in_stream(img_bytes)
            # Take all tags with a high enough confidence score
            tags_all = sorted(
                cv_results.tags, key=lambda tag: tag.confidence, reverse=True
            )
            tags_selected = [tags_all[0].name] + [
                tag.name
                for tag in tags_all[1:]
                if tag.confidence > self.confidence_cutoff
            ]

        if not metadata.keywords:
            # Update the metadata
            self.line(
                f"Found <b>{len(tags_selected)}</b> classes: {tags_selected}",
                verbosity=verbosity.VERY_VERBOSE,
            )
            return self.run_exiv_cmds(
                [
                    f'exiv2 -q -M "add Iptc.Application2.Keywords String {tag_name}" "{metadata.filepath.resolve()}"'
                    for tag_name in tags_selected
                ]
            )
        return (True, "<info>Skipped</info>")
