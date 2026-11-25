# aibom-lab-ticket-classifier

A batch job that routes IT service desk tickets to a queue (access, network, hardware, software) with a **classic machine learning model** (TF-IDF and logistic regression, saved as plain JSON since phase 6; it was a pickle file). An optional step adds sentiment with **DistilBERT** from Hugging Face.

> **Deliberately vulnerable lab app.** It is one of four sample apps for the [CS54 AI-BOM and AI security posture lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). It shows that an AI-BOM must cover classic ML model files, not only LLMs. Its planted weaknesses, and the phase 6 fixes, are listed in [KNOWN-WEAKNESSES.md](KNOWN-WEAKNESSES.md). All tickets are fake.

## What it is, in AI-BOM terms

| AI-BOM field | Value |
| --- | --- |
| Models | `models/ticket_router.model.json` (trained here with scikit-learn, SHA-256 pinned in `classifier/route.py`); optional `distilbert/distilbert-base-uncased-finetuned-sst-2-english` (Hugging Face, pinned to a reviewed commit) |
| Model file format | JSON weights (data only, cannot run code); was pickle until phase 6 |
| Sources | Ticket text from `data/inbox.csv` (untrusted: written by any employee) |
| Sinks | Routing output (CSV) |
| Exposure | Batch job |
| AI libraries | scikit-learn (training only); optional transformers 5.24.0 and torch |

## Run it on a Mac

No Ollama needed for this app.

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m classifier.route
```

To retrain the model: `python -m classifier.train`. It prints the new file's SHA-256; put that in `MODEL_SHA256` in `classifier/route.py`, or the router refuses the new file. That is the approval step.

Optional DistilBERT step (large download, about 1 GB):

```
pip install -r requirements-ml.txt
USE_DISTILBERT=1 DISTILBERT_REVISION=<commit> python -m classifier.route
```

For `<commit>`, open the model's page on Hugging Face, go to "Files and versions", open the history, and copy the full 40-character hash of the commit you reviewed. Without it the step refuses to download anything.

## Tests

```
python -m pytest -q
```

The attack tests in `tests/test_attacks.py` assert the safe behaviour. In phase 3 they were expected failures, because the weaknesses were planted. Phase 6 fixed them, so they now pass and prove each fix holds. To see the attacks succeed, check out the last commit before the phase 6 fix PR and run `python -m pytest -q --runxfail tests/test_attacks.py`.

