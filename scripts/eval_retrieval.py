import sys

import json

from gst_assistant.core.hybrid import HybridIndex
from gst_assistant.core.search import KeywordIndex
from gst_assistant.core.vector_search import VectorIndex
from gst_assistant.domains.gst.answer import build_keyword_index, embed_text, load_records
from gst_assistant.domains.gst.glossary import expand_query, load_glossary

path = sys.argv[1] if len(sys.argv) > 1 else "eval/questions.json"
with open(path, encoding="utf-8") as file:
    questions = json.load(file)

records = load_records()
glossary = load_glossary()
keyword = build_keyword_index(records)
vector = VectorIndex(records, embed_text, cache_path="data/processed/vectors.npy")
indexes = {
    "keyword": keyword,
    "vector": vector,
    "hybrid": HybridIndex([keyword, vector]),
}

summary = {}
for name, index in indexes.items():
    print("==", name.upper(), "==")
    misses = []
    checked = 0
    for item in questions:
        if not item["expected_ids"]:
            continue
        checked += 1
        retrieved = [r["id"] for r, score in index.search(expand_query(item["question"], glossary), top_k=5)]
        found = all(i in retrieved for i in item["expected_ids"])
        if not found:
            misses.append(item["id"])
            print("MISS", item["id"], item["question"])
            print("      expected:", item["expected_ids"])
            print("      got:     ", retrieved)
    summary[name] = (checked - len(misses), checked, misses)
    print()

print("SUMMARY (retrieval hit rate, top 5)")
for name, (hits, checked, misses) in summary.items():
    print(name.ljust(8), hits, "of", checked, "| missed:", ", ".join(misses) or "none")
