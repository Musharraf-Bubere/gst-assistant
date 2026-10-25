"""Keyword search (BM25) over a list of records."""
import re

from rank_bm25 import BM25Okapi


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


class KeywordIndex:
    def __init__(self, records, text_of):
        self.records = records
        self.bm25 = BM25Okapi([tokenize(text_of(r)) for r in records])

    def search(self, query, top_k=5):
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(range(len(self.records)), key=lambda i: scores[i], reverse=True)
        return [(self.records[i], float(scores[i])) for i in ranked[:top_k] if scores[i] > 0]
