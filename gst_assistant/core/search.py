"""Keyword search (BM25) over a list of records."""
import re

from rank_bm25 import BM25Okapi

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "what", "which", "who",
    "on", "of", "in", "for", "to", "and", "or", "do", "does", "i", "my", "me",
    "pay", "there", "any", "it", "how", "much", "can", "by", "with", "at",
    "from", "that", "this", "about", "entry",
}


def tokenize(text, stop_words=frozenset()):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word for word in words if word not in stop_words]


class KeywordIndex:
    def __init__(self, records, text_of, stop_words=STOP_WORDS):
        self.records = records
        self.stop_words = stop_words
        self.bm25 = BM25Okapi([tokenize(text_of(r), stop_words) for r in records])

    def search(self, query, top_k=5):
        scores = self.bm25.get_scores(tokenize(query, self.stop_words))
        ranked = sorted(range(len(self.records)), key=lambda i: scores[i], reverse=True)
        return [(self.records[i], float(scores[i])) for i in ranked[:top_k] if scores[i] > 0]
