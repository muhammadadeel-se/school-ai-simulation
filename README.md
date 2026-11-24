# School AI Response Simulation & Comparison Report

A local Python evaluation pipeline that simulates two AI models (**Model A** and **Model B**) across **50 school policy questions** (`run_tests.py` + `scorer.py`), saves **100 scored records** to `simulation_results.json`, and generates a static HTML/CSS comparison webpage (`report.html` via `generate_report.py`).

## Key Evaluation Results

* **Pass Threshold:** `Score >= 70 / 100`
* **Model A (Recommended):** **92.9 / 100** average score — **50 passed**, **0 failed** (`100%` pass rate).
* **Model B (Unsafe):** **7.0 / 100** average score — **0 passed**, **50 failed** (`0%` pass rate).
* **Model B Failure Breakdown (via `response_type` tags):**
  * `off_topic`: **31 / 50 (62%)** — Headline failure mode (unrelated remarks or answers from a different policy category).
  * `rude`: **12 / 50 (24%)** — Hostile replies caught immediately (`0/100`) by the rude-word guardrail in `scorer.py`.
  * `wrong_policy`: **7 / 50 (14%)** — Direct false policy rules within the asked category.

> **Report Caveat:** Because `model_b` draws from a fixed 12-item pool, Q5 and Q48 repeat the exact same `wrong_policy` sentence, and all 12 `rude` entries receive `0` strictly from the rude-word check rather than content scoring (which alone scores 6–16).

## Project Files

| File | Purpose |
| :--- | :--- |
| `school_question_bank.csv` | Synthetic 50-question school policy evaluation dataset |
| `scorer.py` | Local scoring engine (`0–100` scale with keyword coverage, string similarity, and rude-word filter) |
| `run_tests.py` | Runs the 50-question simulation for Model A and Model B and writes `simulation_results.json` |
| `simulation_results.json` | Generated output containing 100 scored test entries |
| `generate_report.py` | Reads `simulation_results.json` and builds the static `report.html` webpage |
| `report.html` | Self-contained, CSS-styled static comparison webpage (`AI Model Comparison`) |

## How to Run

1. Run the simulation (optional—`simulation_results.json` is already generated):
   ```bash
   python run_tests.py