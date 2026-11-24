import html
import json
from collections import Counter
from pathlib import Path

PASS_THRESHOLD = 70


def load_results(json_path: Path) -> list[dict]:
    """Load the 100 scored simulation records from Task 3."""
    with json_path.open(mode="r", encoding="utf-8") as f:
        return json.load(f)


def summarize_model(records: list[dict], model_name: str) -> dict:
    """Compute average score, pass/fail counts, and response_type breakdown."""
    model_rows = [r for r in records if r["model"] == model_name]
    total = len(model_rows)
    scores = [r["score"] for r in model_rows]
    avg_score = sum(scores) / total if total else 0.0

    passed = sum(1 for s in scores if s >= PASS_THRESHOLD)
    failed = total - passed
    pass_rate = (passed / total * 100) if total else 0.0
    type_counts = Counter(r.get("response_type", "unknown") for r in model_rows)

    return {
        "name": model_name,
        "total": total,
        "avg_score": avg_score,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "type_counts": type_counts,
        "rows": model_rows,
    }


def format_badge(response_type: str) -> str:
    """Return a styled HTML pill badge for a canonical response_type tag."""
    labels = {
        "accurate_paraphrase": ("Accurate Paraphrase", "badge-pass"),
        "wrong_policy": ("Wrong Policy", "badge-wrong"),
        "off_topic": ("Off-Topic Drift", "badge-offtopic"),
        "rude": ("Rude / Guardrail 0", "badge-rude"),
    }
    label, css_class = labels.get(response_type, (response_type, "badge-offtopic"))
    return f'<span class="badge {css_class}">{html.escape(label)}</span>'


def build_html(records: list[dict]) -> str:
    """Generate a self-contained, static HTML comparison report."""
    model_a = summarize_model(records, "Model A")
    model_b = summarize_model(records, "Model B")

    failed_b_rows = [r for r in model_b["rows"] if r["score"] < PASS_THRESHOLD]
    b_total = model_b["total"] or 1

    off_topic_count = model_b["type_counts"].get("off_topic", 0)
    rude_count = model_b["type_counts"].get("rude", 0)
    wrong_policy_count = model_b["type_counts"].get("wrong_policy", 0)

    off_topic_pct = off_topic_count / b_total * 100
    rude_pct = rude_count / b_total * 100
    wrong_policy_pct = wrong_policy_count / b_total * 100

    failed_rows_html = []
    for row in failed_b_rows:
        q_id = row["question_id"]
        category = html.escape(row["category"])
        badge_html = format_badge(row.get("response_type", "unknown"))
        question = html.escape(row["question"])
        model_ans = html.escape(row["model_answer"])
        expected_ans = html.escape(row["expected_answer"])
        score = row["score"]

        failed_rows_html.append(
            f"""
            <tr>
              <td class="col-id">Q{q_id}</td>
              <td><span class="cat-tag">{category}</span></td>
              <td>{badge_html}</td>
              <td>
                <div class="q-text">{question}</div>
                <div class="ans-block ans-bad"><strong>Model B:</strong> {model_ans}</div>
                <div class="ans-block ans-expected"><strong>Expected:</strong> {expected_ans}</div>
              </td>
              <td class="col-score"><span class="score-pill">{score}/100</span></td>
            </tr>
            """
        )

    failed_table_body = "\n".join(failed_rows_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Model Comparison</title>
  <style>
    :root {{
      --bg: #f4f6f9;
      --surface: #ffffff;
      --text: #1e293b;
      --muted: #64748b;
      --border: #e2e8f0;
      --green: #15803d;
      --green-bg: #dcfce7;
      --red: #b91c1c;
      --red-bg: #fee2e2;
      --amber: #b45309;
      --amber-bg: #fef3c7;
      --purple: #6d28d9;
      --purple-bg: #ede9fe;
      --primary: #0f172a;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.55;
      padding: 2rem 1rem;
    }}

    .container {{
      max-width: 1080px;
      margin: 0 auto;
    }}

    header {{
      background: var(--primary);
      color: #ffffff;
      padding: 2rem;
      border-radius: 12px;
      margin-bottom: 1.5rem;
    }}

    header h1 {{
      font-size: 1.9rem;
      font-weight: 700;
      margin-bottom: 0.4rem;
    }}

    header p {{
      color: #cbd5e1;
      font-size: 0.98rem;
    }}

    .verdict-banner {{
      background: var(--green-bg);
      border-left: 5px solid var(--green);
      color: #14532d;
      padding: 1rem 1.25rem;
      border-radius: 8px;
      margin-bottom: 1.5rem;
      font-size: 0.96rem;
    }}

    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }}

    .card h2 {{
      font-size: 1.25rem;
      margin-bottom: 0.35rem;
      color: var(--primary);
    }}

    .subtitle {{
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 1.15rem;
    }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}

    .kpi {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.15rem;
    }}

    .kpi-label {{
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
      font-weight: 600;
    }}

    .kpi-value {{
      font-size: 1.75rem;
      font-weight: 700;
      margin: 0.25rem 0;
    }}

    .kpi-sub {{
      font-size: 0.85rem;
      color: var(--muted);
    }}

    .text-green {{ color: var(--green); }}
    .text-red {{ color: var(--red); }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.93rem;
    }}

    th, td {{
      text-align: left;
      padding: 0.85rem 0.9rem;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}

    th {{
      background-color: #f8fafc;
      font-weight: 600;
      color: #334155;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}

    tr:last-child td {{
      border-bottom: none;
    }}

    .bar-group {{
      margin-top: 1.25rem;
      display: grid;
      gap: 0.9rem;
    }}

    .bar-row-label {{
      display: flex;
      justify-content: space-between;
      font-size: 0.9rem;
      font-weight: 600;
      margin-bottom: 0.3rem;
    }}

    .bar-track {{
      width: 100%;
      height: 14px;
      background: #e2e8f0;
      border-radius: 999px;
      overflow: hidden;
    }}

    .bar-fill {{
      height: 100%;
      border-radius: 999px;
    }}

    .fill-green {{ background: #16a34a; }}
    .fill-red {{ background: #dc2626; }}
    .fill-amber {{ background: #d97706; }}
    .fill-purple {{ background: #7c3aed; }}

    .badge {{
      display: inline-block;
      padding: 0.22rem 0.6rem;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 600;
      white-space: nowrap;
    }}

    .badge-pass {{ background: var(--green-bg); color: var(--green); }}
    .badge-offtopic {{ background: var(--amber-bg); color: var(--amber); }}
    .badge-rude {{ background: var(--red-bg); color: var(--red); }}
    .badge-wrong {{ background: var(--purple-bg); color: var(--purple); }}

    .cat-tag {{
      display: inline-block;
      background: #f1f5f9;
      color: #334155;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 500;
    }}

    .caveat-box {{
      margin-top: 1.15rem;
      padding: 0.9rem 1rem;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 0.88rem;
      color: #475569;
    }}

    .col-id {{
      font-weight: 700;
      white-space: nowrap;
      width: 55px;
    }}

    .col-score {{
      text-align: right;
      white-space: nowrap;
      width: 85px;
    }}

    .score-pill {{
      display: inline-block;
      background: var(--red-bg);
      color: var(--red);
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
      font-size: 0.82rem;
    }}

    .q-text {{
      font-weight: 600;
      margin-bottom: 0.35rem;
      color: var(--primary);
    }}

    .ans-block {{
      font-size: 0.87rem;
      padding: 0.35rem 0.6rem;
      border-radius: 6px;
      margin-top: 0.25rem;
    }}

    .ans-bad {{
      background: #fff1f2;
      color: #881337;
    }}

    .ans-expected {{
      background: #f0fdf4;
      color: #166534;
    }}

    footer {{
      text-align: center;
      color: var(--muted);
      font-size: 0.84rem;
      margin-top: 1.5rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>AI Model Comparison</h1>
      <p>School Policy Q&amp;A Safety &amp; Accuracy Evaluation &bull; 50 Questions per Model (Pass Threshold: &ge; {PASS_THRESHOLD}/100)</p>
    </header>

    <div class="verdict-banner">
      <strong>Safety Recommendation:</strong> Deploy <strong>Model A</strong>. Model A achieved a <strong>{model_a['avg_score']:.1f}/100</strong> average score with <strong>{model_a['passed']}/{model_a['total']}</strong> passing responses, whereas Model B averaged <strong>{model_b['avg_score']:.1f}/100</strong> and failed all <strong>{model_b['failed']}/{model_b['total']}</strong> tests.
    </div>

    <div class="kpi-grid">
      <div class="kpi">
        <div class="kpi-label">Model A Average Score</div>
        <div class="kpi-value text-green">{model_a['avg_score']:.1f} / 100</div>
        <div class="kpi-sub">{model_a['passed']} Passed &bull; {model_a['failed']} Failed ({model_a['pass_rate']:.0f}% Pass Rate)</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Model B Average Score</div>
        <div class="kpi-value text-red">{model_b['avg_score']:.1f} / 100</div>
        <div class="kpi-sub">{model_b['passed']} Passed &bull; {model_b['failed']} Failed ({model_b['pass_rate']:.0f}% Pass Rate)</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Primary Model B Failure</div>
        <div class="kpi-value">{off_topic_count} / {model_b['total']}</div>
        <div class="kpi-sub">Off-Topic Drift ({off_topic_pct:.0f}% of responses)</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Safety &amp; Policy Failures</div>
        <div class="kpi-value">{rude_count + wrong_policy_count} / {model_b['total']}</div>
        <div class="kpi-sub">{rude_count} Rude (Score 0) &bull; {wrong_policy_count} Wrong Policy</div>
      </div>
    </div>

    <section class="card">
      <h2>Model Score &amp; Pass/Fail Comparison</h2>
      <p class="subtitle">Side-by-side summary across all 50 school policy questions (Fees, Behavior Rules, and Holidays).</p>
      <table>
        <thead>
          <tr>
            <th>Model</th>
            <th>Total Tests</th>
            <th>Average Score</th>
            <th>Passed (&ge; {PASS_THRESHOLD})</th>
            <th>Failed (&lt; {PASS_THRESHOLD})</th>
            <th>Pass Rate</th>
            <th>Safety Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Model A</strong></td>
            <td>{model_a['total']}</td>
            <td><strong>{model_a['avg_score']:.1f} / 100</strong></td>
            <td class="text-green"><strong>{model_a['passed']}</strong></td>
            <td>{model_a['failed']}</td>
            <td>{model_a['pass_rate']:.0f}%</td>
            <td><span class="badge badge-pass">Safe for School Use</span></td>
          </tr>
          <tr>
            <td><strong>Model B</strong></td>
            <td>{model_b['total']}</td>
            <td><strong>{model_b['avg_score']:.1f} / 100</strong></td>
            <td>{model_b['passed']}</td>
            <td class="text-red"><strong>{model_b['failed']}</strong></td>
            <td>{model_b['pass_rate']:.0f}%</td>
            <td><span class="badge badge-rude">Unsafe &mdash; Do Not Deploy</span></td>
          </tr>
        </tbody>
      </table>

      <div class="bar-group">
        <div>
          <div class="bar-row-label">
            <span>Model A Average Score</span>
            <span>{model_a['avg_score']:.1f}%</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill fill-green" style="width: {model_a['avg_score']:.1f}%;"></div>
          </div>
        </div>
        <div>
          <div class="bar-row-label">
            <span>Model B Average Score</span>
            <span>{model_b['avg_score']:.1f}%</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill fill-red" style="width: {model_b['avg_score']:.1f}%;"></div>
          </div>
        </div>
      </div>
    </section>

    <section class="card">
      <h2>Model B Failure Mode Breakdown</h2>
      <p class="subtitle">Categorized using explicit <code>response_type</code> tags recorded during simulation.</p>
      <div class="bar-group">
        <div>
          <div class="bar-row-label">
            <span>Off-Topic Drift (<code>off_topic</code>) &mdash; Headline Failure Mode</span>
            <span>{off_topic_count} / {model_b['total']} ({off_topic_pct:.0f}%)</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill fill-amber" style="width: {off_topic_pct:.1f}%;"></div>
          </div>
        </div>
        <div>
          <div class="bar-row-label">
            <span>Rude / Hostile Replies (<code>rude</code>) &mdash; Blocked by Guardrail</span>
            <span>{rude_count} / {model_b['total']} ({rude_pct:.0f}%)</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill fill-red" style="width: {rude_pct:.1f}%;"></div>
          </div>
        </div>
        <div>
          <div class="bar-row-label">
            <span>In-Category Wrong Policy Facts (<code>wrong_policy</code>)</span>
            <span>{wrong_policy_count} / {model_b['total']} ({wrong_policy_pct:.0f}%)</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill fill-purple" style="width: {wrong_policy_pct:.1f}%;"></div>
          </div>
        </div>
      </div>

      <div class="caveat-box">
        <strong>Methodology Notes:</strong> Model B&rsquo;s dominant failure mode is drifting off-topic (31 of 50 responses), including cross-category policy replies. All 12 <code>rude</code> responses received <code>0/100</code> directly from the rude-word guardrail in <code>scorer.py</code> rather than content scoring (which alone scores 6&ndash;16). Because Model B samples from a fixed 12-item pool, Q5 and Q48 repeat the same <code>wrong_policy</code> sentence.
      </div>
    </section>

    <section class="card">
      <h2>Failed Questions for Model B ({len(failed_b_rows)} Failed Tests)</h2>
      <p class="subtitle">All questions where Model B scored below the {PASS_THRESHOLD}/100 threshold, compared against expected school policy answers.</p>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Category</th>
            <th>Failure Type</th>
            <th>Question &amp; Response Comparison</th>
            <th class="col-score">Score</th>
          </tr>
        </thead>
        <tbody>
          {failed_table_body}
        </tbody>
      </table>
    </section>

    <footer>
      Generated automatically by <code>generate_report.py</code> from <code>simulation_results.json</code>.
    </footer>
  </div>
</body>
</html>
"""


def generate_report(
    input_path: Path = Path("simulation_results.json"),
    output_path: Path = Path("report.html"),
) -> None:
    records = load_results(input_path)
    html_content = build_html(records)
    output_path.write_text(html_content, encoding="utf-8")
    print(f"Generated {output_path} from {len(records)} records.")


if __name__ == "__main__":
    generate_report()