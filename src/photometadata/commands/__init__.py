"""Commands module"""
from .check import check_command
from .classify import classify_command
from .duplicates import duplicates_command
from .fix import fix_command

__all__ = [
    "check_command",
    "classify_command",
    "duplicates_command",
    "fix_command",
]
