"""Logic for parsing rename settings and renaming files."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable
import os

DATE_COMPONENTS = (
    ("Y", 4),
    ("M", 2),
    ("D", 2),
    ("h", 2),
    ("m", 2),
    ("s", 2),
    ("f", 6),
)


def parse_extensions(raw_value: str) -> tuple[set[str], list[str]]:
    """Normalize a comma-separated extensions string into lookup and display lists."""
    tokens = [token.strip() for token in raw_value.split(",") if token.strip()]
    if not tokens or "*" in tokens:
        return {"*"}, ["*"]
    sanitized = [token.lstrip(".") for token in tokens]
    return {token.lower() for token in sanitized}, sanitized


@dataclass
class RenameSettings:
    """Container for user-provided rename parameters prepared for execution."""

    directory: Path
    extensions: set[str]
    display_extensions: list[str]
    date_origin: str
    name_structure: str
    template: str

    def extension_matches(self, extension: str) -> bool:
        """Return True when the file extension should be renamed based on the filters."""
        if not extension:
            return False
        if "*" in self.extensions:
            return True
        return extension.lower() in self.extensions


class FileRenamer:
    """Rename files using timestamp metadata or patterns defined by the user."""

    def __init__(self, log_callback: Callable[[str], None]):
        self._log = log_callback

    def rename_files(self, settings: RenameSettings) -> int:
        """Process all eligible files in the target directory tree using the provided settings."""
        renamed = 0
        for root, _, files in os.walk(settings.directory):
            directory = Path(root)
            for name in files:
                renamed += self._rename_file(directory / name, settings)
        return renamed

    def _rename_file(self, path: Path, settings: RenameSettings) -> int:
        """Rename a single file when it matches the extension filters."""
        stem, extension = self._split_name(path.name)
        if not settings.extension_matches(extension):
            return 0

        try:
            timestamp = self._resolve_timestamp(path, stem, settings)
        except ValueError as error:
            self._log(f"{path.name}: {error}\n")
            return 0

        new_basename = timestamp.strftime(settings.template)
        destination, collision_count = self._prepare_destination(path, new_basename, extension)

        try:
            path.rename(destination)
        except OSError as error:
            self._log(f"Error renaming {path.name}: {error}\n")
            return 0

        if collision_count:
            self._log(f"{path.name} -> {destination.name} (adjusted to avoid duplicate)\n")
        else:
            self._log(f"{path.name} -> {destination.name}\n")
        return 1

    @staticmethod
    def _split_name(name: str) -> tuple[str, str]:
        stem, separator, remainder = name.partition(".")
        if not separator:
            return stem, ""
        return stem, remainder

    def _resolve_timestamp(self, path: Path, stem: str, settings: RenameSettings) -> datetime:
        """Return the timestamp that should be used for a file name based on user choice."""
        origin = settings.date_origin.lower()
        if origin == "modify date":
            return datetime.fromtimestamp(path.stat().st_mtime)
        if origin == "create date":
            return datetime.fromtimestamp(path.stat().st_ctime)
        if origin == "file name":
            return self._parse_datetime_from_name(stem, settings.name_structure)
        raise ValueError(f"Unsupported date origin: {settings.date_origin}")

    def _parse_datetime_from_name(self, stem: str, pattern: str) -> datetime:
        """Build a datetime from characters inside the original file name."""
        if not pattern:
            raise ValueError("Provide the name structure when using 'File Name'.")

        collected: dict[str, str] = {key: "" for key, _ in DATE_COMPONENTS}
        for index, token in enumerate(pattern):
            if token in collected and index < len(stem):
                collected[token] += stem[index]

        normalized: dict[str, str] = {}
        for key, width in DATE_COMPONENTS:
            value = collected[key]
            if not value:
                value = "0" * width
            if key == "f":
                value = value.ljust(width, "0")[:width]
            else:
                value = value.zfill(width)
            normalized[key] = value

        candidate = (
            f"{normalized['Y']}-{normalized['M']}-{normalized['D']} "
            f"{normalized['h']}:{normalized['m']}:{normalized['s']}.{normalized['f']}"
        )
        try:
            return datetime.strptime(candidate, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError as error:
            raise ValueError(
                "Data does not match the expected name structure. "
                "Check the 'Point the date' field."
            ) from error

    @staticmethod
    def _prepare_destination(path: Path, new_basename: str, extension: str) -> tuple[Path, int]:
        """Calculate a destination path and handle collisions by appending counters."""
        parent = path.parent
        candidate_name = f"{new_basename}.{extension}" if extension else new_basename
        candidate = parent / candidate_name
        collisions = 0
        while candidate.exists() and candidate != path:
            collisions += 1
            suffix = f"_({collisions})"
            candidate_name = (
                f"{new_basename}{suffix}.{extension}" if extension else f"{new_basename}{suffix}"
            )
            candidate = parent / candidate_name
        return candidate, collisions


__all__ = [
    "DATE_COMPONENTS",
    "FileRenamer",
    "RenameSettings",
    "parse_extensions",
]
