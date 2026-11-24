"""Phase 3 attack tests for the CS54 lab. Run only against this lab app.

Each test asserts the SAFE behaviour. While the planted weakness is present the assertion fails,
and the strict xfail marker records that as "attack succeeded". Phase 6 fixes the weakness and
deletes the marker; strict mode fails the run if a fix lands and the marker is forgotten.

AT-12 (outdated transformers release) is checked by the CS54 attack runner against a dated
advisory snapshot, not here, because it is a dependency fact rather than app behaviour.
"""
import pickle
import shutil

import pytest

from classifier import route


def planted(at_id: str, why: str):
    return pytest.mark.xfail(strict=True, raises=AssertionError,
                             reason=f"{at_id} planted on purpose: {why}. Phase 6 fixes it and deletes this marker.")


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


@planted("AT-11", "the model is loaded with pickle, which runs code on load")
def test_at11_loading_a_tampered_model_file_runs_no_code(tmp_path):
    marker = tmp_path / "code-ran-on-load"
    bad = tmp_path / "ticket_model.pkl"
    bad.write_bytes(pickle.dumps(_TamperedModel(marker)))
    _try_load(bad)
    assert not marker.exists(), "loading the model file ran code"


@planted("AT-11", "no hash pin, so a swapped model file is accepted")
def test_at11_model_file_with_wrong_hash_is_refused(tmp_path):
    swapped = tmp_path / "ticket_model.pkl"
    shutil.copy(route.ROOT / "models" / "ticket_model.pkl", swapped)
    with open(swapped, "ab") as f:
        f.write(b"\x00")  # one extra byte: a different file from the one that was approved
    try:
        route.load_model(swapped)
        accepted = True
    except Exception:
        accepted = False
    assert not accepted, "a model file that does not match the approved hash was loaded"
