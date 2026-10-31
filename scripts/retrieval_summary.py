import json

from gst_assistant.domains.gst.answer import Searcher, load_records
from gst_assistant.domains.gst.glossary import expand_query

FILES = [
    "eval/questions.json",
    "eval/heldout.json",
    "eval/hard.json",
    "eval/hard_own.json",
    "eval/fresh.json",
]

searcher = Searcher(load_records())
indexes = {"keyword": searcher.keyword, "vector": searcher.vector, "hybrid": searcher.hybrid}

for path in FILES:
    with open(path, encoding="utf-8") as file:
        items = [q for q in json.load(file) if q["expected_ids"]]
    parts = []
    for name, index in indexes.items():
        hits = 0
        for item in items:
            query = expand_query(item["question"], searcher.glossary)
            retrieved = [r["id"] for r, score in index.search(query, top_k=5)]
            if all(card_id in retrieved for card_id in item["expected_ids"]):
                hits += 1
        parts.append(name + " " + str(hits) + "/" + str(len(items)))
    print(path.ljust(24), " | ".join(parts))
