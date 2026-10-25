import json

from gst_assistant.core.search import KeywordIndex
from gst_assistant.domains.gst.answer import card_text, load_records

with open("eval/questions.json", encoding="utf-8") as file:
    questions = json.load(file)

records = load_records()
index = KeywordIndex(records, card_text)

found_count = 0
checked = 0
for item in questions:
    if not item["expected_ids"]:
        continue
    checked += 1
    retrieved = [r["id"] for r, score in index.search(item["question"], top_k=5)]
    found = all(i in retrieved for i in item["expected_ids"])
    found_count += found
    print("OK  " if found else "MISS", item["id"], item["question"])
    if not found:
        print("      expected:", item["expected_ids"])
        print("      got:     ", retrieved)

print()
print("retrieval hit rate:", found_count, "of", checked)
