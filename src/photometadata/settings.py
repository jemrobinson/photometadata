import logging
from pathlib import Path
from yaml import safe_load

logger = logging.getLogger(__name__)

class Settings:
    def __init__(self, path: str | Path) -> None:
        """Load a YAML settings file into a dict"""
        try:
            with open(path, "r", encoding="utf-8") as f_yaml:
                self.inner_dict = safe_load(f_yaml)
        except:
            logger.error(f"Could not load settings from {path}!</error>")
            raise

    def __getitem__(self, key: str) -> str:
        return self.inner_dict[key]
