"""Commands module"""
from .check import check_command
from .classify import classify_command
from .duplicates import duplicates_command
from .metadata import metadata_command

__all__ = [
    "check_command",
    "classify_command",
    "duplicates_command",
    "metadata_command",
]
