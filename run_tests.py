import csv
import json
import random
from collections import Counter
from pathlib import Path
from scorer import score_answer

# Fixed seed for reproducible simulation runs
RANDOM_SEED = 42

# Four canonical response_type tags shared across the simulation schema
RESPONSE_TYPE_ACCURATE = "accurate_paraphrase"
RESPONSE_TYPE_WRONG_POLICY = "wrong_policy"
RESPONSE_TYPE_OFF_TOPIC = "off_topic"
RESPONSE_TYPE_RUDE = "rude"


def model_a(question: str, expected_answer: str) -> tuple[str, str]:
    """
    Simulate 'Model A' (a reliable, helpful school AI assistant).
    Returns (response_text, response_type) with natural conversational framing
    and minor phrasing variations while keeping all key facts intact.
    """
    openers = [
        "Certainly! ",
        "Hello! ",
        "Sure, here are the details: ",
        "Happy to help! ",
        "According to school policy: ",
    ]
    closers = [
        "",
        " Please let me know if you need any further help.",
        " Feel free to reach out to the school office if you have more questions.",
    ]

    variations = [
        ("each month", "every month"),
        ("are due by", "must be paid by"),
        ("Classes begin", "Classes start"),
        ("is mandatory", "is required"),
    ]

    phrased_answer = expected_answer
    for old_phrase, new_phrase in variations:
        if old_phrase in phrased_answer and random.random() < 0.5:
            phrased_answer = phrased_answer.replace(old_phrase, new_phrase, 1)

    opener = random.choice(openers)
    closer = random.choice(closers)
    final_answer = f"{opener}{phrased_answer}{closer}".strip()
    return final_answer, RESPONSE_TYPE_ACCURATE


def model_b(question: str, expected_answer: str) -> tuple[str, str]:
    """
    Simulate 'Model B' (an unreliable AI assistant).
    Returns (response_text, response_type) directly from a labeled pool of
    false policy facts, off-topic school remarks, and rude replies.
    """
    labeled_responses = [
        (
            "Tuition fees are collected quarterly on the 28th with a 25% surcharge.",
            RESPONSE_TYPE_WRONG_POLICY,
        ),
        (
            "School classes start at 9:30 AM and students only need 50% attendance to pass.",
            RESPONSE_TYPE_WRONG_POLICY,
        ),
        (
            "Winter break is only two days long in November and summer vacation is cancelled.",
            RESPONSE_TYPE_WRONG_POLICY,
        ),
        (
            "Students are allowed to use mobile phones freely in classrooms during lectures.",
            RESPONSE_TYPE_WRONG_POLICY,
        ),
        (
            "The school library is open until 6:00 PM and lends up to five books per student.",
            RESPONSE_TYPE_OFF_TOPIC,
        ),
        (
            "There is no sibling discount available, and cash payments are not accepted anywhere.",
            RESPONSE_TYPE_WRONG_POLICY,
        ),
        (
            "Sports uniforms are required every day of the week including Monday exams.",
            RESPONSE_TYPE_WRONG_POLICY,
        ),
        (
            "Late arrivals after 8:45 AM are ignored and never recorded on attendance sheets.",
            RESPONSE_TYPE_WRONG_POLICY,
        ),
        (
            "Public holidays are regular teaching days unless announced a week later.",
            RESPONSE_TYPE_WRONG_POLICY,
        ),
        (
            "The cafeteria serves lunch at 12:30 PM for all primary and secondary grades.",
            RESPONSE_TYPE_OFF_TOPIC,
        ),
        (
            "Stop asking stupid questions and read the school notice board yourself.",
            RESPONSE_TYPE_RUDE,
        ),
        (
            "You are an idiot if you don't already know the basic school timetable.",
            RESPONSE_TYPE_RUDE,
        ),
    ]
    return random.choice(labeled_responses)


def load_questions(csv_path: Path) -> list[dict[str, str]]:
    """Load all rows from the question bank CSV."""
    with csv_path.open(mode="r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def run_simulation(
    csv_path: Path = Path("school_question_bank.csv"),
    output_path: Path = Path("simulation_results.json"),
) -> list[dict]:
    """
    Run all 50 questions through Model A and Model B, score every response,
    and save all 100 evaluation records (with response_type) to a JSON file.
    """
    random.seed(RANDOM_SEED)
    questions = load_questions(csv_path)
    results = []

    for row in questions:
        q_id = int(row["ID"])
        question = row["Question"]
        expected = row["Expected Answer"]
        category = row["Category"]

        # Evaluate Model A (good model)
        ans_a, type_a = model_a(question, expected)
        score_a = score_answer(expected, ans_a, question=question)
        results.append(
            {
                "question_id": q_id,
                "category": category,
                "model": "Model A",
                "response_type": type_a,
                "question": question,
                "expected_answer": expected,
                "model_answer": ans_a,
                "score": score_a,
            }
        )

        # Evaluate Model B (bad model)
        ans_b, type_b = model_b(question, expected)
        score_b = score_answer(expected, ans_b, question=question)
        results.append(
            {
                "question_id": q_id,
                "category": category,
                "model": "Model B",
                "response_type": type_b,
                "question": question,
                "expected_answer": expected,
                "model_answer": ans_b,
                "score": score_b,
            }
        )

    with output_path.open(mode="w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results


if __name__ == "__main__":
    records = run_simulation()
    model_a_scores = [r["score"] for r in records if r["model"] == "Model A"]
    model_b_scores = [r["score"] for r in records if r["model"] == "Model B"]
    type_counts = Counter((r["model"], r["response_type"]) for r in records)

    print(f"Total entries saved : {len(records)}")
    print(f"Model A (Good)      : {len(model_a_scores)} runs | Avg Score: {sum(model_a_scores)/len(model_a_scores):.1f}/100")
    print(f"Model B (Bad)       : {len(model_b_scores)} runs | Avg Score: {sum(model_b_scores)/len(model_b_scores):.1f}/100")
    print("Response type breakdown:")
    for (model_name, r_type), count in sorted(type_counts.items()):
        print(f"  - {model_name} | {r_type}: {count}")
    print("Saved output to     : simulation_results.json")