import json

from gst_assistant.core.hybrid import HybridIndex
from gst_assistant.core.search import KeywordIndex
from gst_assistant.core.vector_search import VectorIndex
from gst_assistant.domains.gst.answer import card_text, embed_text, load_records

with open("eval/questions.json", encoding="utf-8") as file:
    questions = {q["id"]: q for q in json.load(file)}

records = load_records()
keyword = KeywordIndex(records, card_text)
vector = VectorIndex(records, embed_text, cache_path="data/processed/vectors.npy")
indexes = {"keyword": keyword, "vector": vector, "hybrid": HybridIndex([keyword, vector])}

for question_id in ["q19", "q22"]:
    item = questions[question_id]
    wanted = item["expected_ids"][0]
    print(question_id, item["question"], "| wanted:", wanted)
    for name, index in indexes.items():
        ids = [r["id"] for r, score in index.search(item["question"], top_k=50)]
        position = ids.index(wanted) + 1 if wanted in ids else None
        print("  ", name.ljust(8), "position of the right card:", position or "not in top 50")
