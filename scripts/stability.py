import json
import sys
import time

from gst_assistant.core.llm import get_llm
from gst_assistant.domains.gst import rewrite
from gst_assistant.domains.gst.answer import Searcher, build_search_query, load_records

PAUSE_SECONDS = 4

path = sys.argv[1] if len(sys.argv) > 1 else "eval/fresh.json"
repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 5
with open(path, encoding="utf-8") as file:
    questions = json.load(file)
top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 5

searcher = Searcher(load_records())
llm = get_llm()

total_hits = 0
total_runs = 0
for item in questions:
    if not item["expected_ids"]:
        continue
    hits = 0
    failures = 0
    searches = set()
    for _ in range(repeats):
        rewrite.clear_cache()
        query, tokens_in, tokens_out = build_search_query(item["question"], searcher, llm, "both")
        if tokens_in == 0:
            failures += 1
        searches.add(query)
        retrieved = [r["id"] for r, score in searcher.hybrid.search(query, top_k=top_k)]
        if all(card_id in retrieved for card_id in item["expected_ids"]):
            hits += 1
        time.sleep(PAUSE_SECONDS)
    total_hits += hits
    total_runs += repeats
    print(
        str(hits) + "/" + str(repeats), item["id"], item["question"],
        "| different searches:", len(searches), "| rewrite failures:", failures,
    )

print()
print("right card in the top 5:", total_hits, "of", total_runs, "runs")
