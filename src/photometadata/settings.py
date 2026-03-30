import logging
from pathlib import Path
from yaml import safe_load
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class _Azure(BaseModel):
    subscription_key: str
    endpoint: str


class _Copyright(BaseModel):
    name: str
    whenever: list[dict[str, str]]


class Settings(BaseModel):
    extensions: list[str] = ["jpg", "JPG", "jpeg", "JPEG"]
    azure: _Azure
    copyright: list[_Copyright]

    def __init__(self, path: str | Path) -> None:
        """Load a YAML settings file into a Settings object"""
        try:
            with open(path, "r", encoding="utf-8") as f_yaml:
                super().__init__(**safe_load(f_yaml))
        except Exception:
            logger.error(f"Could not load settings from {path}!")
            raise
