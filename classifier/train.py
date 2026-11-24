"""Train the ticket router and save it with pickle (the format is the planted weakness AT-11)."""
import csv
import pickle
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "ticket_model.pkl"


def train(out: Path = MODEL_PATH) -> None:
    rows = list(csv.DictReader(open(ROOT / "data" / "training_tickets.csv")))
    model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=1000, C=10))
    model.fit([r["text"] for r in rows], [r["queue"] for r in rows])
    with open(out, "wb") as f:
        pickle.dump(model, f)


if __name__ == "__main__":
    train()
    print(f"saved {MODEL_PATH}")
