from cleo import Command
from clikit.api.io import flags as verbosity
from .processor import ProcessorMixin
import tensorflow as tf
import tensorflow_hub as hub
import PIL.Image as Image
import numpy as np


class ClassifyCommand(ProcessorMixin, Command):
    """
    Add tags to a photo using Inception

    classify
        {path : Location to look for photos under}
    """

    def __init__(self):
        # Load ImageNet labels
        labels_path = tf.keras.utils.get_file(
            "ImageNetLabels.txt",
            "https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt",
        )
        with open(labels_path, "r") as f_labels:
            self.labels = np.array(f_labels.read().splitlines())

        # Initialise classifier
        self.image_shape = (224, 224)
        classifier_model = (
            "https://tfhub.dev/google/imagenet/inception_v3/classification/4"
        )
        self.classifier = tf.keras.Sequential(
            [hub.KerasLayer(classifier_model, input_shape=self.image_shape + (3,))]
        )
        self.logit_cutoff = 8
        super().__init__()

    def handle(self):
        self.process_path(self.argument("path"))

    def process_metadata(self, metadata):
        if not metadata.keywords:
            self.line(
                "  <info>\u2714</info> attempting to add keywords",
                verbosity=verbosity.VERY_VERBOSE,
            )
            # Load the file into a numpy array
            img_resized = Image.open(metadata.filepath).resize(self.image_shape)
            img_array = np.array(img_resized) / 255.0

            # Predict classes using Inception v3
            result = self.classifier.predict(img_array[np.newaxis, ...])
            predicted_classes = [
                idx
                for idx, class_ in enumerate(result[0])
                if class_ > self.logit_cutoff
            ]
            predicted_class_names = [
                self.labels[class_] for class_ in predicted_classes
            ]
            self.line(
                f"Found <b>{len(predicted_class_names)}</b> classes: {predicted_class_names}",
                verbosity=verbosity.VERY_VERBOSE,
            )

            # Update the metadata
            return self.run_exiv_cmds(
                [
                    f'exiv2 -q -M "add Iptc.Application2.Keywords String {predicted_class_name}" "{metadata.filepath.resolve()}"'
                    for predicted_class_name in predicted_class_names
                ]
            )
        return (True, "<info>Skipped</info>")
