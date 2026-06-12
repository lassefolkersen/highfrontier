"""Savegame validation and wrapper helpers for High Frontier."""

import datetime
import os
import pickle

SAVE_FORMAT = "highfrontier-save"
SAVE_VERSION = 1
PAYLOAD_TYPE = "solarsystem-pickle"


class SaveNameError(ValueError):
    """Raised when a user supplied savegame name is unsafe."""


class SaveFormatError(ValueError):
    """Raised when a savegame file cannot be decoded safely."""


def validate_save_name(name):
    """Return a stripped save name, or raise if it is unsafe."""
    if not isinstance(name, str):
        raise SaveNameError("Savegame name must be text")

    save_name = name.strip()
    if not save_name:
        raise SaveNameError("Savegame name cannot be empty")
    if os.path.isabs(save_name):
        raise SaveNameError("Savegame name cannot be an absolute path")
    if "/" in save_name or "\\" in save_name:
        raise SaveNameError("Savegame name cannot contain path separators")
    if save_name in {".", ".."}:
        raise SaveNameError("Savegame name cannot be '.' or '..'")
    if save_name == "emptyfile":
        raise SaveNameError("Savegame name 'emptyfile' is reserved")
    if save_name.lower().endswith(".tmp"):
        raise SaveNameError("Temporary savegame files cannot be selected")

    return save_name


def savegame_path(save_dir, name):
    """Return the path for a validated savegame name inside save_dir."""
    return os.path.join(os.fspath(save_dir), validate_save_name(name))


def list_savegames(save_dir):
    """List selectable savegames, excluding temp/reserved/invalid entries."""
    save_dir = os.fspath(save_dir)
    if not os.path.isdir(save_dir):
        return []

    savegames = []
    for entry in os.listdir(save_dir):
        try:
            save_name = validate_save_name(entry)
        except SaveNameError:
            continue
        if not os.path.isfile(os.path.join(save_dir, save_name)):
            continue
        savegames.append(save_name)
    return sorted(savegames)


def make_save_wrapper(payload, created_at=None):
    """Wrap a solarsystem payload with explicit save format metadata."""
    if created_at is None:
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "format": SAVE_FORMAT,
        "version": SAVE_VERSION,
        "created_at": created_at,
        "payload_type": PAYLOAD_TYPE,
        "payload": payload,
    }


def unwrap_save_payload(saved_object):
    """Return the solarsystem object from a wrapper or legacy raw pickle."""
    if isinstance(saved_object, dict) and "format" in saved_object:
        save_format = saved_object.get("format")
        if save_format != SAVE_FORMAT:
            raise SaveFormatError(f"Unsupported savegame format: {save_format!r}")

        version = saved_object.get("version")
        if version != SAVE_VERSION:
            raise SaveFormatError(
                f"Unsupported savegame version: {version!r}; supported version is {SAVE_VERSION}"
            )

        payload_type = saved_object.get("payload_type")
        if payload_type != PAYLOAD_TYPE:
            raise SaveFormatError(f"Unsupported savegame payload type: {payload_type!r}")

        if "payload" not in saved_object:
            raise SaveFormatError("Savegame wrapper is missing payload")
        return saved_object["payload"]

    return saved_object


def load_payload(filename):
    """Load and unwrap a savegame payload from a pickle file."""
    filename = os.fspath(filename)
    try:
        with open(filename, "rb") as save_file:
            saved_object = pickle.load(save_file)
    except EOFError as exc:
        raise SaveFormatError(f"Savegame file is empty or truncated: {filename}") from exc
    except pickle.UnpicklingError as exc:
        raise SaveFormatError(f"Savegame file could not be unpickled: {filename}") from exc
    except SaveFormatError:
        raise
    except Exception as exc:
        raise SaveFormatError(f"Savegame file could not be loaded: {filename}: {exc}") from exc

    return unwrap_save_payload(saved_object)


def load_named_payload(save_dir, name):
    """Validate a save name, then load its payload from save_dir."""
    return load_payload(savegame_path(save_dir, name))
