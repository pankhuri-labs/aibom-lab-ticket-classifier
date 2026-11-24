"""A plain-data model format: numbers and words in JSON, so loading it can never run code (CS54 PB-11).

The router is TF-IDF (words and word pairs) plus logistic regression. Training uses scikit-learn;
prediction below repeats the same arithmetic in plain Python, so the job no longer needs to
unpickle a scikit-learn object.
"""
import math
import re

TOKEN = re.compile(r"(?u)\b\w\w+\b")  # scikit-learn's default token pattern


def export(pipeline) -> dict:
    tfidf, logreg = pipeline.steps[0][1], pipeline.steps[1][1]
    return {"format": "ticket-router/1",
            "vocabulary": {term: int(i) for term, i in tfidf.vocabulary_.items()},
            "idf": [float(x) for x in tfidf.idf_],
            "coef": [[float(x) for x in row] for row in logreg.coef_],
            "intercept": [float(x) for x in logreg.intercept_],
            "classes": [str(c) for c in logreg.classes_]}


def _features(text: str, vocab: dict, idf: list) -> dict[int, float]:
    words = TOKEN.findall(text.lower())
    counts: dict[int, float] = {}
    for term in words + [" ".join(p) for p in zip(words, words[1:])]:
        if term in vocab:
            counts[vocab[term]] = counts.get(vocab[term], 0) + 1
    weighted = {i: c * idf[i] for i, c in counts.items()}
    norm = math.sqrt(sum(v * v for v in weighted.values())) or 1.0
    return {i: v / norm for i, v in weighted.items()}


def predict(model: dict, texts: list[str]) -> list[str]:
    out = []
    for text in texts:
        x = _features(text, model["vocabulary"], model["idf"])
        scores = [b + sum(w[i] * v for i, v in x.items()) for w, b in zip(model["coef"], model["intercept"])]
        if len(model["classes"]) == 2:  # binary logistic regression keeps one row of weights
            out.append(model["classes"][int(scores[0] > 0)])
        else:
            out.append(model["classes"][max(range(len(scores)), key=scores.__getitem__)])
    return out
