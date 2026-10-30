import json
import re
import sys
import time

from gst_assistant.core.llm import get_llm
from gst_assistant.core.logbook import LogBook
from gst_assistant.domains.gst.answer import Searcher, answer_question, load_records

PAUSE_SECONDS = 4

path = sys.argv[1] if len(sys.argv) > 1 else "eval/questions.json"
with open(path, encoding="utf-8") as file:
    questions = json.load(file)

searcher = Searcher(load_records())
llm = get_llm()
logbook = LogBook("data/eval_logs.db")


def value_ok(expected, text):
    if expected == "exempt":
        return "exempt" in text.lower()
    number = expected.rstrip("%")
    return re.search(r"\b" + re.escape(number) + r"(\.0)?\s*%", text) is not None


passed = 0
failed = []
errors = []
tokens_in = 0
tokens_out = 0
for item in questions:
    answer = answer_question(item["question"], searcher, llm, logbook=logbook)
    tokens_in += answer.tokens_in
    tokens_out += answer.tokens_out

    if answer.status == "error":
        errors.append(item["id"])
        print("ERROR", item["id"], answer.raw_text[:100])
        time.sleep(PAUSE_SECONDS)
        continue

    if item["type"] == "answer":
        right_card = all(card_id in answer.cited_ids for card_id in item["expected_ids"])
        right_value = value_ok(item["expected"], answer.text)
        ok = answer.status == "answered" and right_card and right_value
    else:
        ok = answer.status in ("refused", "not_found")

    print("PASS" if ok else "FAIL", item["id"], answer.status.ljust(10), item["question"])
    if ok:
        passed += 1
    else:
        failed.append(item["id"])
        print("      expected:", item["type"], item["expected_ids"], item["expected"])
        print("      cited:   ", answer.cited_ids)
        print("      answer:  ", (answer.raw_text or answer.text)[:200].replace("\n", " "))
    if answer.tokens_in:
        time.sleep(PAUSE_SECONDS)

scored = len(questions) - len(errors)
print()
print("answer pipeline:", passed, "of", scored, "scored | failed:", ", ".join(failed) or "none")
print("errors (not scored):", ", ".join(errors) or "none")
print("tokens in:", tokens_in, "| tokens out:", tokens_out)
