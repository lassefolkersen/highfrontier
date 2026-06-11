"""Filesystem path helpers for High Frontier assets and data files."""

from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent


def repo_root() -> Path:
    """Return the repository/application root directory."""
    return _REPO_ROOT


def asset_path(*parts: str) -> Path:
    """Return an absolute path for a bundled runtime asset."""
    return _REPO_ROOT.joinpath(*parts)


def data_path(*parts: str) -> Path:
    """Return an absolute path under the bundled data directory."""
    return _REPO_ROOT.joinpath("data", *parts)
