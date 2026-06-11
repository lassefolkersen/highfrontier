import os
import pickle

import pytest

from savegame import (
    PAYLOAD_TYPE,
    SAVE_FORMAT,
    SAVE_VERSION,
    SaveNameError,
    list_savegames,
    load_named_payload,
    make_save_wrapper,
    savegame_path,
    validate_save_name,
)


@pytest.mark.parametrize(
    "name",
    [
        "",
        "   ",
        os.path.abspath("slot1"),
        "../slot1",
        "slot1/backup",
        r"slot1\\backup",
        ".",
        "..",
        "emptyfile",
        "autosave.tmp",
        "AUTOSAVE.TMP",
    ],
)
def test_validate_save_name_rejects_unsafe_names(name):
    with pytest.raises(SaveNameError):
        validate_save_name(name)


def test_savegame_path_uses_validated_name_inside_save_dir(tmp_path):
    save_dir = tmp_path / "savegames"

    path = savegame_path(save_dir, " campaign-1 ")

    assert path == os.path.join(os.fspath(save_dir), "campaign-1")


def test_list_savegames_excludes_empty_temp_invalid_and_directories(tmp_path):
    save_dir = tmp_path / "savegames"
    save_dir.mkdir()
    for name in ["campaign-1", "zulu", "emptyfile", "autosave.tmp", "   "]:
        (save_dir / name).write_bytes(b"placeholder")
    (save_dir / "nested").mkdir()

    assert list_savegames(save_dir) == ["campaign-1", "zulu"]


def test_new_save_wrapper_has_versioned_metadata():
    payload = object()

    wrapper = make_save_wrapper(payload, created_at="2026-06-11T12:00:00+00:00")

    assert wrapper == {
        "format": SAVE_FORMAT,
        "version": SAVE_VERSION,
        "created_at": "2026-06-11T12:00:00+00:00",
        "payload_type": PAYLOAD_TYPE,
        "payload": payload,
    }


def test_invalid_load_names_are_rejected_before_pickle_load(tmp_path, monkeypatch):
    def fail_if_called(file_obj):
        raise AssertionError("pickle.load should not run for invalid save names")

    monkeypatch.setattr(pickle, "load", fail_if_called)

    with pytest.raises(SaveNameError):
        load_named_payload(tmp_path, "../campaign-1")
