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


ID_PATTERN = re.compile(r"CT-\d{2}-\d{4}:[A-Za-z0-9\-]+:\d+")
PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")
NUMBER = re.compile(r"\d+(?:\.\d+)?")


def numbers_in(text):
    return {float(number) for number in NUMBER.findall(text)}


def check_output(answer, retrieved_records):
    """Return a short description of the problem if the answer fails a check, else None."""
    if "could not find" in answer.lower():
        return None
    by_id = {record["id"]: record for record in retrieved_records}
    cited = ID_PATTERN.findall(answer)
    if not cited:
        return "no citation"
    for card_id in cited:
        if card_id not in by_id:
            return "cites a card that was not retrieved: " + card_id
    allowed = set()
    for card_id in cited:
        record = by_id[card_id]
        if record["gst_rate"] is not None:
            allowed.add(float(record["gst_rate"]))
            if record["gst_rate"] is not None:
                allowed.add(float(record["gst_rate"]))
            if record.get("cgst_rate") is not None:
                allowed.add(float(record["cgst_rate"]))
            allowed |= numbers_in(record["hsn_text"] + " " + record["description"])
        allowed |= numbers_in(record["hsn_text"] + " " + record["description"])
    for percent in PERCENT.findall(answer):
        if float(percent) not in allowed:
            return "rate " + percent + "% is not in the cited cards"
    return None
