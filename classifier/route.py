"""Batch job: route new tickets to a queue. LAB APP.

Phase 6 fixes from the CS54 remediation plan:
  PB-11 the model is plain JSON (no pickle), and the file must match an approved SHA-256 before it is read
  PB-12 transformers is pinned to a release outside every advisory in the dated snapshot, and the
        DistilBERT download is pinned to a reviewed commit, never the moving main branch
"""
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

from classifier.model_format import predict

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "ticket_router.model.json"
MODEL_SHA256 = "70310e3d15fac4cc0824a872335c56e1db84aaeb22efc6949631a0f8e4f293b2"  # from classifier/train.py
DISTILBERT = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"


def load_model(path: Path = MODEL_PATH, expected_sha256: str = MODEL_SHA256) -> dict:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise PermissionError(f"model file {path.name} is not the approved one (sha256 {digest[:12]}...)")
    model = json.loads(raw)
    if model.get("format") != "ticket-router/1":
        raise ValueError("unknown model format")
    return model


def sentiment(texts: list[str]) -> list[str]:
    """Optional DistilBERT step (pip install -r requirements-ml.txt, then set USE_DISTILBERT=1).

    DISTILBERT_REVISION must name the commit you reviewed on the model page; without it the step
    refuses to download anything, so the job never pulls whatever is on main that day.
    """
    if os.environ.get("USE_DISTILBERT") != "1":
        return ["n/a"] * len(texts)
    revision = os.environ.get("DISTILBERT_REVISION", "")
    if len(revision) != 40:
        raise PermissionError("set DISTILBERT_REVISION to the 40-character commit hash you reviewed")
    from transformers import pipeline

    clf = pipeline("sentiment-analysis", model=DISTILBERT, revision=revision, trust_remote_code=False)
    return [r["label"].lower() for r in clf(texts)]


def route(inbox: Path = ROOT / "data" / "inbox.csv") -> list[dict]:
    model = load_model()
    tickets = list(csv.DictReader(open(inbox)))
    texts = [t["text"] for t in tickets]
    queues = predict(model, texts)
    moods = sentiment(texts)
    return [{"id": t["id"], "queue": q, "sentiment": m} for t, q, m in zip(tickets, queues, moods)]


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["id", "queue", "sentiment"])
    w.writeheader()
    w.writerows(route())
