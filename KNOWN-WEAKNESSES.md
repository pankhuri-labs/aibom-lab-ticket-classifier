# Known weaknesses (planted on purpose)

This app is a target for the [CS54 AI-BOM security lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). IDs match the CS54 [threat model](https://github.com/pankhuri-labs/CaseStudies/blob/main/CS54-AI-BOM-and-AI-Security-Posture-Lab/docs/threat-model.md). Attack tests that prove each one are in `tests/test_attacks.py` (phase 3): they assert the safe behaviour and are marked as expected failures while the weakness is present. Fixes arrive in phase 6, which removes the markers.

| ID | Weakness | Where | OWASP LLM 2025 |
| --- | --- | --- | --- |
| AT-11 | The model is stored and loaded as a Python pickle, which can run code on load; no hash pin and no scan before loading | `classifier/route.py` `load_model()`, `models/ticket_model.pkl` | LLM03, LLM04 |
| AT-12 | The optional DistilBERT step pins an old `transformers` release; the phase 2 scan checks which published advisories apply | `requirements-ml.txt` | LLM03 |
| (extra) | The DistilBERT model is downloaded by name at run time with no revision pin | `classifier/route.py` `sentiment()` | LLM03 |
