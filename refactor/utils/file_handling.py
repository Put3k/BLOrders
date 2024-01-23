import logging

from pathlib import Path


def is_valid_path(file_path: str) -> bool:
    """
    Checks if given file path exists.
    """
    if file_path and Path(file_path).exists():
        return True
    return False
