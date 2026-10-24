import json
import re

from rank_bm25 import BM25Okapi

with open("data/processed/rates_09-2025.json", encoding="utf-8") as file:
    records = json.load(file)


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


corpus = [tokenize(r["hsn_text"] + " " + r["description"]) for r in records]
bm25 = BM25Okapi(corpus)


def search(query, top_k=3):
    scores = bm25.get_scores(tokenize(query))
    ranked = sorted(range(len(records)), key=lambda i: scores[i], reverse=True)
    return [records[i] for i in ranked[:top_k] if scores[i] > 0]


for query in ["pan masala", "live horses", "2401", "ginger"]:
    print("QUERY:", query)
    for record in search(query):
        print("  ", record["gst_rate"], "% |", record["id"], "|", record["hsn_text"][:25], "|", record["description"][:50])
