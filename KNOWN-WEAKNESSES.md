# Known weaknesses (planted on purpose, fixed in phase 6)

This app is a target for the [CS54 AI-BOM security lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). IDs match the CS54 [threat model](https://github.com/pankhuri-labs/CaseStudies/blob/main/CS54-AI-BOM-and-AI-Security-Posture-Lab/docs/threat-model.md). Attack tests that prove each one are in `tests/test_attacks.py` (phase 3): they assert the safe behaviour and are marked as expected failures while the weakness is present. Phase 6 fixed them and removed the markers; the second table shows each fix.

| ID | Weakness | Where | OWASP LLM 2025 |
| --- | --- | --- | --- |
| AT-11 | The model is stored and loaded as a Python pickle, which can run code on load; no hash pin and no scan before loading | `classifier/route.py` `load_model()`, `models/ticket_model.pkl` | LLM03, LLM04 |
| AT-12 | The optional DistilBERT step pins an old `transformers` release; the phase 2 scan checks which published advisories apply | `requirements-ml.txt` | LLM03 |
| (extra) | The DistilBERT model is downloaded by name at run time with no revision pin | `classifier/route.py` `sentiment()` | LLM03 |

## Phase 6 fixes

Each fix follows a playbook in the CS54 remediation plan. A fix counts as closed only when its attack test passes **and** the AI-BOM rescan no longer raises the signal.

| ID | Playbook | Fix | Proof |
| --- | --- | --- | --- |
| AT-11 | PB-11 | The pickle file is gone. The model is saved as JSON weights (`models/ticket_router.model.json`) and predicted in plain Python, so loading it cannot run code. The router also refuses any file whose SHA-256 does not match the approved one, so a swapped file is caught before it is read. Predictions match the old model on all 22 sample tickets. | `test_at11_loading_a_tampered_model_file_runs_no_code`, `test_at11_model_file_with_wrong_hash_is_refused`, `test_at11_approved_model_still_loads_and_routes` |
| AT-12 | PB-12 | `transformers` moved from 4.37.2 to 5.24.0, which matches none of the 24 advisories in the 2026-11-24 snapshot (5.10.0, the first fix for the newest one, was yanked). The DistilBERT download needs a reviewed commit hash and runs with remote code off. | the CS54 attack runner's dependency check; `test_at12_distilbert_download_needs_a_pinned_revision` |

Not tested here: whether DistilBERT still works with transformers 5.24.0. That needs the optional 1 GB install, so run it on your Mac.
