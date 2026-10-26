"""Semantic (meaning-based) search with local embeddings."""
import os

import numpy as np
from fastembed import TextEmbedding

MODEL_NAME = "BAAI/bge-small-en-v1.5"


class VectorIndex:
    def __init__(self, records, text_of, cache_path=None):
        self.records = records
        self.model = TextEmbedding(model_name=MODEL_NAME)
        self.vectors = self._load_or_build(text_of, cache_path)

    def _embed(self, texts):
        vectors = np.array(list(self.model.embed(texts)))
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    def _load_or_build(self, text_of, cache_path):
        if cache_path and os.path.exists(cache_path):
            vectors = np.load(cache_path)
            if len(vectors) == len(self.records):
                return vectors
        vectors = self._embed([text_of(r) for r in self.records])
        if cache_path:
            np.save(cache_path, vectors)
        return vectors

    def search(self, query, top_k=5):
        query_vector = self._embed([query])[0]
        scores = self.vectors @ query_vector
        ranked = np.argsort(-scores)[:top_k]
        return [(self.records[i], float(scores[i])) for i in ranked]
