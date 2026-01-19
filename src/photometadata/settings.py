import logging
from typing import Any
from pathlib import Path
from yaml import safe_load

logger = logging.getLogger(__name__)

class Settings:
    def __init__(self, path: str | Path) -> None:
        """Load a YAML settings file into a dict"""
        try:
            with open(path, "r", encoding="utf-8") as f_yaml:
                dict_: dict[str, Any] = safe_load(f_yaml)
                self.extensions = dict_.get("extensions", ["jpg", "JPG", "jpeg", "JPEG"])
        except:
            logger.error(f"Could not load settings from {path}!</error>")
            raise
