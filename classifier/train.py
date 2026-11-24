"""Train the ticket router and save it as plain JSON (phase 6, CS54 PB-11: no more pickle).

After training, put the printed SHA-256 into MODEL_SHA256 in classifier/route.py. The router
refuses any model file whose hash does not match, so a retrained model is approved on purpose.
"""
import csv
import hashlib
import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from classifier.model_format import export

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "ticket_router.model.json"


def train(out: Path = MODEL_PATH) -> str:
    rows = list(csv.DictReader(open(ROOT / "data" / "training_tickets.csv")))
    model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=1000, C=10))
    model.fit([r["text"] for r in rows], [r["queue"] for r in rows])
    out.write_text(json.dumps(export(model), indent=1, sort_keys=True) + "\n")
    return hashlib.sha256(out.read_bytes()).hexdigest()


if __name__ == "__main__":
    digest = train()
    print(f"saved {MODEL_PATH}\nsha256 {digest}")
