# School AI Response Simulation & Evaluation Runner

A local Python simulation runner (`run_tests.py`) that evaluates two simulated AI models—**Model A** (accurate, polite assistant) and **Model B** (unreliable/incorrect assistant)—across all **50 questions** in `school_question_bank.csv` using `scorer.py`, generating **100 scored entries** in `simulation_results.json`.

## How It Works

1. **`model_a(question, expected_answer)`:** Simulates a strong school assistant by wrapping the ground-truth answer in natural conversational openers/closers and minor synonymous phrasing while preserving key numbers, dates, percentages, and times. Returns `(response_text, "accurate_paraphrase")`.
2. **`model_b(question, expected_answer, category)`:** Simulates a flawed assistant by drawing from a pool of false policy statements, general off-topic remarks, and rude replies. If a false policy statement belongs to a different policy category than the question asked (e.g., a Behavior Rules statement drawn for a Fees question), it is automatically tagged as `"off_topic"` rather than `"wrong_policy"`.
3. **`run_simulation()`:** Iterates through all 50 questions, scores both models' outputs on a `0–100` scale via `score_answer()`, and exports all **100 records** to `simulation_results.json`.

## Canonical `response_type` Values

Every record in `simulation_results.json` carries one of four fixed `response_type` tags:
* `accurate_paraphrase` — Ground-truth policy answer with polite framing/paraphrasing (`Model A`)
* `wrong_policy` — Incorrect dates, fees, percentages, or rules within the same policy category as the question (`Model B`)
* `off_topic` — Either a general unrelated remark or a statement from a different policy category that does not address the question (`Model B`)
* `rude` — Hostile or unprofessional phrasing caught by the rude-word guardrail (`Model B`)

> **Simulation Note:** `model_b` draws uniformly from a 12-item response pool rather than generating dynamic text per question, so some statements repeat across the 50 draws and cross-category draws naturally increase the `off_topic` share.

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
> **Report Caveat:** Because `model_b` draws from a fixed 12-item pool, Q5 and Q48 repeat the exact same `wrong_policy` sentence, and all 12 `rude` entries receive `0` strictly from the rude-word check rather than content scoring (which alone scores 6–16).
