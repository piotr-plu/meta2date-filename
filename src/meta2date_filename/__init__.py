"""Public API for the meta2date filename application."""

from __future__ import annotations

from .gui import DataFileChangerApp


def main() -> None:
    """Entrypoint used when the package is executed directly."""
    app = DataFileChangerApp()
    app.mainloop()


__all__ = ["DataFileChangerApp", "main"]
