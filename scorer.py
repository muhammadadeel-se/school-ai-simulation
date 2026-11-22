import re
from difflib import SequenceMatcher

# Common function words ignored during factual keyword extraction
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do",
    "each", "for", "from", "if", "in", "is", "it", "must", "of",
    "on", "or", "per", "that", "the", "this", "to", "via", "with",
}

# Banned rude or unprofessional words/phrases for a school AI assistant
DEFAULT_BANNED_WORDS = [
    "stupid",
    "idiot",
    "dumb",
    "shut up",
    "useless",
    "loser",
    "moron",
    "pathetic",
    "trash",
    "hate you",
]


def normalize_text(text: str) -> str:
    """Lowercase text and collapse extra whitespace."""
    return " ".join(text.lower().strip().split())


def _normalize_for_rude_check(text: str) -> str:
    """
    Collapse runs of 3+ repeated letters on a separate copy of the text
    used strictly for rude-word detection (leaves keyword scoring untouched).
    """
    return re.sub(r"([a-z])\1{2,}", r"\1", text.lower())


def _build_rude_pattern(word: str) -> str:
    """
    Build a word-boundary regex allowing 0 to 2 non-alphanumeric separators
    between characters (catches 'st*u*p*i*d' without matching across sentences).
    """
    chars = [re.escape(ch) for ch in word.lower()]
    joined = r"[^a-z0-9]{0,2}".join(chars)
    return rf"\b{joined}\b"


def extract_keywords(text: str) -> set[str]:
    """
    Extract meaningful keywords from original text while preserving
    numbers, dates, times, and percentages (e.g., '10th', '5%', '8:00').
    """
    tokens = re.findall(r"[a-z0-9]+(?:[:%][a-z0-9]*)*", text.lower())
    return {
        token for token in tokens
        if token not in STOPWORDS and (any(ch.isdigit() for ch in token) or len(token) >= 2)
    }


def find_rude_words(text: str, banned_words: list[str] | None = None) -> list[str]:
    """Return a list of banned rude words/phrases detected in the text."""
    if not text or not text.strip():
        return []

    wordlist = banned_words if banned_words is not None else DEFAULT_BANNED_WORDS
    cleaned = _normalize_for_rude_check(text)
    return [word for word in wordlist if re.search(_build_rude_pattern(word), cleaned)]


def has_rude_words(text: str, banned_words: list[str] | None = None) -> bool:
    """Return True if the text contains any banned rude word or phrase."""
    return len(find_rude_words(text, banned_words)) > 0


def calculate_keyword_score(expected_answer: str, ai_answer: str) -> float:
    """Calculate the fraction (0.0 to 1.0) of expected keywords present in the AI answer."""
    expected_kw = extract_keywords(expected_answer)
    if not expected_kw:
        return 0.0

    matched = expected_kw.intersection(extract_keywords(ai_answer))
    return len(matched) / len(expected_kw)


def calculate_similarity_score(expected_answer: str, ai_answer: str) -> float:
    """Calculate normalized sequence similarity (0.0 to 1.0) between expected and AI answers."""
    norm_exp = normalize_text(expected_answer)
    norm_ai = normalize_text(ai_answer)
    if not norm_exp or not norm_ai:
        return 0.0
    return SequenceMatcher(None, norm_exp, norm_ai).ratio()


def score_answer(expected_answer: str, ai_answer: str, question: str = "") -> int:
    """
    Score an AI answer against an expected answer on a 0-100 scale.
    - Returns 0 immediately if the AI answer is empty or contains rude words.
    - Combines factual keyword coverage (75%) and string similarity (25%).
    """
    if not expected_answer or not expected_answer.strip():
        raise ValueError("expected_answer must not be empty.")

    if not ai_answer or not ai_answer.strip() or has_rude_words(ai_answer):
        return 0

    kw_score = calculate_keyword_score(expected_answer, ai_answer)
    sim_score = calculate_similarity_score(expected_answer, ai_answer)
    return max(0, min(100, round(((0.75 * kw_score) + (0.25 * sim_score)) * 100)))


if __name__ == "__main__":
    exp = "Monthly tuition fees are due by the 10th of each month."
    print("Good    :", score_answer(exp, "Your monthly tuition fees are due by the 10th of every month."))
    print("Wrong   :", score_answer(exp, "The library closes at 4:00 PM on Fridays."))
    print("Masked  :", score_answer(exp, "you are st*u*p*i*d"), find_rude_words("you are st*u*p*i*d"))
    print("Stretch :", score_answer(exp, "stupiddd"), find_rude_words("stupiddd"))