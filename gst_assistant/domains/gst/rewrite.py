"""Ask the language model to restate a question in the words the notifications use."""

REWRITE_SYSTEM = """You help a search engine for Indian GST notifications.
Rewrite the question so it contains the plain English product names used in the notifications.
Rules:
- Keep the original question, then add the notification words after it.
- Translate everyday Indian words (Hindi, Marathi and others) and English synonyms into plain English product names.
- Do not answer the question and do not mention tax rates.
- Reply with one line of plain text. Do not write the words Question or Rewrite.
Examples:
Question: GST on doodh
Rewrite: GST on doodh milk
Question: GST on mirchi powder
Rewrite: GST on mirchi powder chilli powder dried chillies
Question: Tax on chappals
Rewrite: Tax on chappals footwear slippers"""

MAX_LENGTH = 300
CACHE_LIMIT = 1000
_cache = {}

def clear_cache():
    _cache.clear()

def clean_rewrite(text):
    """Remove labels the model sometimes copies from the examples."""
    text = " ".join(text.split())
    lowered = text.lower()
    if "rewrite:" in lowered:
        text = text[lowered.rindex("rewrite:") + len("rewrite:"):].strip()
    if text.lower().startswith("question:"):
        text = text[len("question:"):].strip()
    return text


def rewrite_query(question, llm):
    """Return (search text, tokens in, tokens out). Falls back to the question on any problem."""
    key = " ".join(question.lower().split())
    if key in _cache:
        return _cache[key], 0, 0
    try:
        result = llm.generate(REWRITE_SYSTEM, "Question: " + question)
    except Exception:
        return question, 0, 0
    text = clean_rewrite(result.text)
    if not text or len(text) > MAX_LENGTH:
        return question, result.tokens_in, result.tokens_out
    if len(_cache) >= CACHE_LIMIT:
        _cache.clear()
    _cache[key] = text
    return text, result.tokens_in, result.tokens_out
