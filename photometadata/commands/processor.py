"""Mixin class for file processing commands"""
from collections import Counter
from pathlib import Path
import subprocess
from clikit.api.io import flags as verbosity
import yaml
from ..metadata import Metadata


class ProcessorMixin:
    """
    Mixin class for file processors
    """

    extensions = ["jpg", "JPG", "jpeg", "JPEG"]

    def load_settings(self, path):
        """Load a YAML settings file into a dict"""
        try:
            with open(path, "r") as f_yaml:
                return yaml.safe_load(f_yaml)
        except:
            self.line(f"<error>Could not load {self.option('settings')}!</error>")
            raise

    def process_path(self, path):
        """Process all photos under the given path"""
        base_path = Path(path)
        photo_paths = sum(
            [list(base_path.rglob(f"*.{ext}")) for ext in self.extensions], []
        )
        self.line(
            f"Processing <b>{len(photo_paths)}</b> files from <comment>{base_path.resolve()}</comment>"
        )

        # Iterate over the photos in directory order
        current_dir = None
        n_photos = Counter()
        for photo_path in sorted(photo_paths):
            if photo_path.parent != current_dir:
                current_dir = photo_path.parent
                self.line(
                    f"Working on directory <comment>{current_dir.resolve()}</comment>"
                )
            # Process the photo
            photo_metadata = Metadata(photo_path.resolve())
            result = self.process_metadata(photo_metadata)
            if not result[0]:
                n_photos["failed"] += 1
            self.line(
                f"{result[1]} {str(photo_metadata.filepath.resolve())}",
                verbosity=verbosity.VERBOSE,
            )
            n_photos["processed"] += 1
        percentage = (
            100.0 * n_photos["failed"] / n_photos["processed"]
            if n_photos["processed"]
            else 0
        )
        self.line(
            f"Processed <b>{n_photos['processed']}</b> photos of which <info>{n_photos['failed']}</info> (<info>{percentage:.2f}%</info>) failed validation"
        )

    def process_metadata(self, metadata):
        """Process some metadata"""
        raise NotImplementedError(
            f"'process_metadata' must be implemented by {type(self).__name__}"
        )

    def run_exiv_cmds(self, exiv_cmds):
        """Run one or more external exiv2 commands"""
        for exiv_cmd in exiv_cmds:
            self.line(
                f"  <info>\u2728</info> running <b>{exiv_cmd}</b>",
                verbosity=verbosity.VERY_VERBOSE,
            )
            try:
                subprocess.call(exiv_cmd, shell=True)
            except (TypeError, ValueError):
                self.line(f"<error>{exiv_cmd} failed!</error>")
                return (False, "<error>Failed to update</error>")
        return (True, "<info>Updated</info>")
