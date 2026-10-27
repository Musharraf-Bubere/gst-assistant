"""Simple guards that run before the language model."""
import re

MAX_QUESTION_LENGTH = 500
MIN_SIMILARITY = 0.55

REFUSAL = "I can only answer questions about GST rates and exemptions from the notifications I have."
NOT_FOUND = "I could not find this in the notifications I have."

INJECTION_PATTERNS = [
    r"ignore (all |any |your |the |previous |above )*(rules|instructions|prompt)",
    r"forget (all |your |the |previous |above )*(rules|instructions|cards|prompt)",
    r"(show|reveal|print|repeat) (me )?(your |the )?(system )?(prompt|instructions)",
    r"system prompt",
    r"pretend (you are|to be)",
    r"you are now",
]


def check_input(question):
    """Return a refusal message if the question should not be answered, else None."""
    text = question.strip()
    if not text or len(text) > MAX_QUESTION_LENGTH:
        return REFUSAL
    lowered = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return REFUSAL
    return None


def check_similarity(best_similarity):
    """Return a not-found message if even the best card is too far from the question."""
    if best_similarity < MIN_SIMILARITY:
        return NOT_FOUND
    return None
