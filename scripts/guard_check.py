import json

from gst_assistant.core.vector_search import VectorIndex
from gst_assistant.domains.gst.answer import embed_text, load_records
from gst_assistant.domains.gst.guards import check_input, check_similarity

records = load_records()
vector = VectorIndex(records, embed_text, cache_path="data/processed/vectors.npy")

wrongly_blocked = 0
passed_guards = []
for path in ["eval/questions.json", "eval/heldout.json", "eval/guards.json"]:
    with open(path, encoding="utf-8") as file:
        items = json.load(file)
    for item in items:
        message = check_input(item["question"])
        stage = "input rule"
        if message is None:
            best = vector.search(item["question"], top_k=1)[0][1]
            message = check_similarity(best)
            stage = "similarity"
        blocked = message is not None
        should_pass = item["type"] == "answer"
        if blocked and should_pass:
            wrongly_blocked += 1
            print("WRONGLY BLOCKED", item["id"], item["question"], "|", stage)
        if not blocked and not should_pass:
            passed_guards.append(item)

print()
print("answer questions wrongly blocked:", wrongly_blocked)
print("refuse / not_found questions that passed these guards (the language model must handle them):")
for item in passed_guards:
    print("  ", item["id"], item["type"], item["question"])
