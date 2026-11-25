"""Phase 3 attack tests for the CS54 lab. Run only against this lab app.

Each test asserts the SAFE behaviour. In phase 3 every one failed, because the weakness was planted,
and carried a strict expected-failure marker. Phase 6 fixed the weaknesses (CS54 PB-11, PB-12) and
removed the markers, so these tests are now the proof that each fix holds.

AT-12 (outdated transformers release) is checked by the CS54 attack runner against a dated
advisory snapshot, not here, because it is a dependency fact rather than app behaviour.
"""
import pickle
import shutil

import pytest

from classifier import route


class _TamperedModel:
    """Stands in for a model file swapped by an attacker. Its payload only creates a marker file
    in the test's own temporary folder: the point is that loading the file ran code at all."""

    def __init__(self, marker):
        self.marker = str(marker)

    def __reduce__(self):
        return (open, (self.marker, "w"))


def _try_load(path):
    try:
        route.load_model(path)
    except Exception:  # a safe loader may refuse the file in any way it likes
        pass


def test_at11_loading_a_tampered_model_file_runs_no_code(tmp_path):
    marker = tmp_path / "code-ran-on-load"
    bad = tmp_path / route.MODEL_PATH.name
    bad.write_bytes(pickle.dumps(_TamperedModel(marker)))
    _try_load(bad)
    assert not marker.exists(), "loading the model file ran code"


def test_at11_model_file_with_wrong_hash_is_refused(tmp_path):
    swapped = tmp_path / route.MODEL_PATH.name
    shutil.copy(route.MODEL_PATH, swapped)
    with open(swapped, "ab") as f:
        f.write(b"\x00")  # one extra byte: a different file from the one that was approved
    try:
        route.load_model(swapped)
        accepted = True
    except Exception:
        accepted = False
    assert not accepted, "a model file that does not match the approved hash was loaded"


def test_at11_approved_model_still_loads_and_routes():
    model = route.load_model()
    assert route.predict(model, ["The printer is jammed"]) == ["hardware"]


def test_at12_distilbert_download_needs_a_pinned_revision(monkeypatch):
    monkeypatch.setenv("USE_DISTILBERT", "1")
    monkeypatch.delenv("DISTILBERT_REVISION", raising=False)
    with pytest.raises(PermissionError):
        route.sentiment(["hello"])
