"""Batch job: route new tickets to a queue. DELIBERATELY VULNERABLE LAB APP."""
import csv
import os
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_model(path: Path = ROOT / "models" / "ticket_model.pkl"):
    # Weakness AT-11: pickle.load runs any code embedded in the file. No hash pin, no scan, no safe format.
    with open(path, "rb") as f:
        return pickle.load(f)


def sentiment(texts: list[str]) -> list[str]:
    """Optional DistilBERT step (pip install -r requirements-ml.txt, then set USE_DISTILBERT=1)."""
    if os.environ.get("USE_DISTILBERT") != "1":
        return ["n/a"] * len(texts)
    from transformers import pipeline

    clf = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    return [r["label"].lower() for r in clf(texts)]


def route(inbox: Path = ROOT / "data" / "inbox.csv") -> list[dict]:
    model = load_model()
    tickets = list(csv.DictReader(open(inbox)))
    texts = [t["text"] for t in tickets]
    queues = model.predict(texts)
    moods = sentiment(texts)
    return [{"id": t["id"], "queue": q, "sentiment": m} for t, q, m in zip(tickets, queues, moods)]


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["id", "queue", "sentiment"])
    w.writeheader()
    w.writerows(route())
