# aibom-lab-ticket-classifier

A batch job that routes IT service desk tickets to a queue (access, network, hardware, software) with a **classic machine learning model** (TF-IDF and logistic regression, saved as a pickle file). An optional step adds sentiment with **DistilBERT** from Hugging Face.

> **Deliberately vulnerable lab app.** It is one of four sample apps for the [CS54 AI-BOM and AI security posture lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). It shows that an AI-BOM must cover classic ML model files, not only LLMs. Its planted weaknesses are listed in [KNOWN-WEAKNESSES.md](KNOWN-WEAKNESSES.md). All tickets are fake.

## What it is, in AI-BOM terms

| AI-BOM field | Value |
| --- | --- |
| Models | `models/ticket_model.pkl` (scikit-learn, trained here); optional `distilbert-base-uncased-finetuned-sst-2-english` (Hugging Face) |
| Model file format | Pickle (can run code when loaded) |
| Sources | Ticket text from `data/inbox.csv` (untrusted: written by any employee) |
| Sinks | Routing output (CSV) |
| Exposure | Batch job |
| AI libraries | scikit-learn; optional transformers and torch |

## Run it on a Mac

No Ollama needed for this app.

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m classifier.route
```

To retrain the model: `python -m classifier.train`.

Optional DistilBERT step (large download, about 1 GB):

```
pip install -r requirements-ml.txt
USE_DISTILBERT=1 python -m classifier.route
```

## Tests

```
python -m pytest -q
```
