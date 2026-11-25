# School AI Policy Assistant — Evaluation & Comparison Report

Live report: https://muhammadadeel-se.github.io/school-ai-simulation/

---

## 1. Project Goal

Before introducing an AI assistant to answer questions from students and parents, the school needs to verify that the AI gives **accurate, on-topic, and polite** information about school policies.

This project evaluates two candidate AI models—**Model A** and **Model B**—against **50 real-world school policy questions** covering three everyday topics:
* **Fees** (monthly due dates, sibling discounts, payment rules)
* **Behavior Rules** (mobile phones, late arrivals, sports uniforms)
* **Holidays** (winter break, summer vacation, public holidays)

Each model's answers are automatically scored from **0 to 100**, saved to `simulation_results.json`, and published as an easy-to-read static webpage (`report.html`).

---

## 2. How to Interpret the Report Scores (For School Staff)

You do not need any technical background to read the comparison report. Every answer is graded on a **0 to 100 scale**, with **70/100 set as the minimum passing score**:

| Score Range | Result | What It Means for the School |
| :--- | :--- | :--- |
| **70 – 100** | **Pass (Safe)** | The AI answered the right policy question accurately and politely. Safe for students and parents. |
| **1 – 69** | **Fail (Unsafe)** | The AI drifted off-topic, answered a different policy rule, or gave incorrect school information. |
| **0** | **Blocked (Rude)** | The AI used insulting language (such as *"stupid"* or *"idiot"*) and was immediately blocked by the safety filter. |

### Final Evaluation Verdict

| Metric | Model A (Recommended) | Model B (Do Not Deploy) |
| :--- | :--- | :--- |
| **Average Score** | **92.9 / 100** | **7.0 / 100** |
| **Passed Questions (`>= 70`)** | **50 / 50 (100%)** | **0 / 50 (0%)** |
| **Failed Questions (`< 70`)** | **0 / 50 (0%)** | **50 / 50 (100%)** |
| **Recommendation** | **Safe for school use** | **Unsafe — reject** |

### What Model B's Failure Labels Mean
In the report's **Failed Questions** table, each Model B failure is tagged with why it failed:
* **Off-Topic Drift (`off_topic` — 31 of 50 responses, 62%):** Model B's main failure mode. Instead of answering the question asked, it gave an unrelated remark or quoted a rule from a different topic (for example, talking about mobile phones when asked about tuition fees).
* **Rude / Guardrail 0 (`rude` — 12 of 50 responses, 24%):** Model B insulted the user and received `0/100` immediately from the rude-word check.
* **Wrong Policy (`wrong_policy` — 7 of 50 responses, 14%):** Model B stayed on the right topic but stated the opposite of actual school policy (for example, claiming students can use mobile phones freely during lectures).

### Transparency & Methodological Notes
* **Repeated Simulation Example:** Because `Model B` draws from a fixed 12-item simulation pool, **Q5** and **Q48** repeat the exact same `wrong_policy` sentence.
* **Rude-Word Guardrail Dependency:** All 12 `rude` entries received `0` strictly from the rude-word filter rather than content scoring (which alone scores 6–16 due to minor common-word overlap).
* **Missing or Null Scores:** If any record has a missing or `null` score, `generate_report.py` excludes it from average score calculations (so averages are never distorted) and conservatively lists it as a failure in Model B's table so unverified answers are never treated as safe.

---

## 3. How to Run the Simulation & Report Scripts Locally

No third-party packages or internet connection are required—everything runs using **Python 3** standard libraries only.

> **Note on `scorer.py`:** You do **not** need to run or edit `scorer.py` on its own. It holds the 0–100 grading logic and rude-word filter, and `run_tests.py` calls it automatically behind the scenes.

1. **Clone the repository and open the folder:**
   ```bash
   git clone [https://github.com/muhammadadeel-se/school-ai-simulation.git](https://github.com/muhammadadeel-se/school-ai-simulation.git)
   cd school-ai-simulation
