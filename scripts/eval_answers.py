import json
import re
import sys
import time

from gst_assistant.core.llm import get_llm
from gst_assistant.domains.gst.answer import Searcher, answer_question, load_records

path = sys.argv[1] if len(sys.argv) > 1 else "eval/questions.json"
with open(path, encoding="utf-8") as file:
    questions = json.load(file)

searcher = Searcher(load_records())
llm = get_llm()


def value_ok(expected, text):
    if expected == "exempt":
        return "exempt" in text.lower()
    number = expected.rstrip("%")
    return re.search(r"\b" + re.escape(number) + r"(\.0)?\s*%", text) is not None


passed = 0
failed = []
tokens_in = 0
tokens_out = 0
for item in questions:
    try:
        answer = answer_question(item["question"], searcher, llm)
    except Exception as error:
        print("ERROR", item["id"], str(error)[:120])
        failed.append(item["id"])
        continue
    tokens_in += answer.tokens_in
    tokens_out += answer.tokens_out

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
    time.sleep(1)

print()
print("answer pipeline:", passed, "of", len(questions), "| failed:", ", ".join(failed) or "none")
print("tokens in:", tokens_in, "| tokens out:", tokens_out)
