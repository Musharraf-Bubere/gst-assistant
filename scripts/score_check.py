import json

from gst_assistant.core.vector_search import VectorIndex
from gst_assistant.domains.gst.answer import embed_text, load_records

records = load_records()
vector = VectorIndex(records, embed_text, cache_path="data/processed/vectors.npy")

rows = []
for path in ["eval/questions.json", "eval/heldout.json", "eval/guards.json"]:
    with open(path, encoding="utf-8") as file:
        for item in json.load(file):
            top_score = vector.search(item["question"], top_k=1)[0][1]
            rows.append((top_score, item["type"], item["id"], item["question"]))

for top_score, kind, question_id, question in sorted(rows):
    print(round(top_score, 3), kind.ljust(10), question_id, question)
