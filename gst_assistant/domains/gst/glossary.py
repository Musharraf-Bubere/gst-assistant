"""Everyday Indian trade words mapped to the words used in the notifications."""
import json
import re

GLOSSARY_PATH = "gst_assistant/domains/gst/glossary.json"


def load_glossary(path=GLOSSARY_PATH):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def expand_query(question, glossary):
    """Add the notification words for any everyday word found in the question."""
    words = re.findall(r"[a-z0-9]+", question.lower())
    extra = []
    for word in words:
        meaning = glossary.get(word)
        if meaning and meaning not in extra:
            extra.append(meaning)
    if not extra:
        return question
    return question + " " + " ".join(extra)
