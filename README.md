# School AI Response Simulation & Evaluation Runner

A local Python simulation runner (`run_tests.py`) that evaluates two simulated AI models—**Model A** (accurate, polite assistant) and **Model B** (unreliable/incorrect assistant)—across all **50 questions** in `school_question_bank.csv` using `scorer.py`, generating **100 scored entries** in `simulation_results.json`.

## How It Works

1. **`model_a(question, expected_answer)`:** Simulates a strong school assistant by wrapping the ground-truth answer in natural conversational openers/closers and minor synonymous phrasing while preserving key numbers, dates, percentages, and times.
2. **`model_b(question, expected_answer)`:** Simulates a flawed assistant by returning wrong policy figures, off-topic school answers, or occasional rude responses (exercising `scorer.py`'s zero-score guardrail).
3. **`run_simulation()`:** Iterates through all 50 questions, scores both models' outputs on a `0–100` scale via `score_answer()`, and exports all **100 records** to `simulation_results.json`.

## Project Files

| File | Purpose |
| :--- | :--- |
| `run_tests.py` | Runs the 50-question simulation for Model A and Model B and writes `simulation_results.json` |
| `scorer.py` | Local scoring engine (`0–100` scale with keyword coverage, string similarity, and rude-word filter) |
| `school_question_bank.csv` | Synthetic 50-question school policy evaluation dataset |
| `simulation_results.json` | Generated output containing 100 scored test entries |

## JSON Output Schema

Each of the 100 entries in `simulation_results.json` follows this structure:

```json
{
  "question_id": 1,
  "category": "Fees",
  "model": "Model A",
  "question": "Could you please clarify, when are monthly tuition fees due for new students?",
  "expected_answer": "Monthly tuition fees are due by the 10th of each month.",
  "model_answer": "Certainly! Monthly tuition fees must be paid by the 10th of each month.",
  "score": 88
}