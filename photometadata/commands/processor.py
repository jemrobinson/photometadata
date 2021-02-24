import subprocess
from collections import Counter
from cleo import Command
from clikit.api.io import flags as verbosity
from pathlib import Path
from ..metadata import Metadata


class ProcessorMixin:
    """
    Mixin class for file processors
    """

    extensions = ["jpg", "JPG", "jpeg", "JPEG"]

    def process_path(self, path):
        base_path = Path(path)
        photo_paths = sum(
            [list(base_path.rglob(f"*.{ext}")) for ext in self.extensions], []
        )
        self.line(
            f"Processing <b>{len(photo_paths)}</b> files from <comment>{base_path.resolve()}</comment>"
        )

        # Iterate over the photos in directory order
        current_dir = None
        nPhotos = Counter()
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
                nPhotos["failed"] += 1
            self.line(
                f"{result[1]} {str(photo_metadata.filepath.resolve())}",
                verbosity=verbosity.VERBOSE,
            )
            nPhotos["processed"] += 1
        percentage = (
            100.0 * nPhotos["failed"] / nPhotos["processed"]
            if nPhotos["processed"]
            else 0
        )
        self.line(
            f"Processed <b>{nPhotos['processed']}</b> photos of which <info>{nPhotos['failed']}</info> (<info>{percentage:.2f}%</info>) failed validation"
        )

    def process_metadata(self, metadata):
        raise NotImplementedError(
            f"'process_metadata' must be implemented by {type(self).__name__}"
        )

    def run_exiv_cmds(self, exiv_cmds):
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
