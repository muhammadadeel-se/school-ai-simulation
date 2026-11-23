# School AI Response Simulation & Evaluation Runner

A local Python simulation runner (`run_tests.py`) that evaluates two simulated AI models—**Model A** (accurate, polite assistant) and **Model B** (unreliable/incorrect assistant)—across all **50 questions** in `school_question_bank.csv` using `scorer.py`, generating **100 scored entries** in `simulation_results.json`.

## How It Works

1. **`model_a(question, expected_answer)`:** Simulates a strong school assistant by wrapping the ground-truth answer in natural conversational openers/closers and minor synonymous phrasing while preserving key numbers, dates, percentages, and times. Returns `(response_text, "accurate_paraphrase")`.
2. **`model_b(question, expected_answer)`:** Simulates a flawed assistant by drawing from a labeled pool of wrong policy figures, off-topic school statements, and rude responses. Returns `(response_text, response_type)` directly without post-hoc inference.
3. **`run_simulation()`:** Iterates through all 50 questions, scores both models' outputs on a `0–100` scale via `score_answer()`, and exports all **100 records** to `simulation_results.json`.

## Canonical `response_type` Values

Every record in `simulation_results.json` carries one of four fixed `response_type` tags:
* `accurate_paraphrase` — Ground-truth policy answer with polite framing/paraphrasing (`Model A`)
* `wrong_policy` — Incorrect dates, fees, percentages, or school rules (`Model B`)
* `off_topic` — Unrelated school information that does not answer the question (`Model B`)
* `rude` — Hostile or unprofessional phrasing caught by the rude-word guardrail (`Model B`)

## Project Files

| File | Purpose |
| :--- | :--- |
| `run_tests.py` | Runs the 50-question simulation for Model A and Model B and writes `simulation_results.json` |
| `scorer.py` | Local scoring engine (`0–100` scale with keyword coverage, string similarity, and rude-word filter) |
| `school_question_bank.csv` | Synthetic 50-question school policy evaluation dataset |
| `simulation_results.json` | Generated output containing 100 scored test entries |

## JSON Output Schema

Each of the 100 entries in `simulation_results.json` follows this unified schema:

```json
{
  "question_id": 1,
  "category": "Fees",
  "model": "Model A",
  "response_type": "accurate_paraphrase",
  "question": "Could you please clarify, when are monthly tuition fees due for new students?",
  "expected_answer": "Monthly tuition fees are due by the 10th of each month.",
  "model_answer": "Certainly! Monthly tuition fees must be paid by the 10th of each month.",
  "score": 88
}