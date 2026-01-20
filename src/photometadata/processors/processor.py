from abc import ABC, abstractmethod
import logging
from photometadata.photo import Photo
from dataclasses import dataclass
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    success: bool
    message: str

class Processor(ABC):
    @abstractmethod
    def __call__(self, photo: Photo) -> ProcessingResult:
        pass

    def run_exiv_cmd(self, exiv_cmd: str) -> ProcessingResult:
        """Run a single external exiv2 commands"""
        logger.debug(f"[blue]\u2728[/] running [bold]{exiv_cmd}[/]")
        try:
            subprocess.run(exiv_cmd, shell=True, check=True)
        except (subprocess.CalledProcessError, TypeError, ValueError):
            logger.error(f"{exiv_cmd} failed!")
            return ProcessingResult(False, f"Failed to run {exiv_cmd}!")
        return ProcessingResult(True, f"Ran {exiv_cmd} successfully.")

    def run_exiv_cmds(self, exiv_cmds: list[str]) -> ProcessingResult:
        """Run one or more external exiv2 commands"""
        for exiv_cmd in exiv_cmds:
            result = self.run_exiv_cmd(exiv_cmd)
            if not result.success:
                return result
        return ProcessingResult(True, "All commands ran successfully.")