import json
import re

from rank_bm25 import BM25Okapi

with open("data/processed/records.json", encoding="utf-8") as file:
    records = json.load(file)


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


corpus = [tokenize(r["hsn_text"] + " " + r["description"]) for r in records]
bm25 = BM25Okapi(corpus)


def search(query, top_k=3):
    scores = bm25.get_scores(tokenize(query))
    ranked = sorted(range(len(records)), key=lambda i: scores[i], reverse=True)
    return [records[i] for i in ranked[:top_k] if scores[i] > 0]


def show_rate(record):
    if record["treatment"] == "exempt":
        return "exempt"
    return str(record["gst_rate"]) + "%"


for query in ["pan masala", "2401", "ginger", "fresh ginger", "tomatoes"]:
    print("QUERY:", query)
    for record in search(query):
        print("  ", show_rate(record), "|", record["id"], "|", record["hsn_text"][:25], "|", record["description"][:50])
