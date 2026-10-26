"""Combine several searches into one list with Reciprocal Rank Fusion (RRF)."""


def reciprocal_rank_fusion(result_lists, k=60, top_k=5):
    points = {}
    cards = {}
    for results in result_lists:
        for rank, (record, score) in enumerate(results, start=1):
            card_id = record["id"]
            cards[card_id] = record
            points[card_id] = points.get(card_id, 0) + 1 / (k + rank)
    best = sorted(points, key=points.get, reverse=True)[:top_k]
    return [(cards[card_id], points[card_id]) for card_id in best]


class HybridIndex:
    def __init__(self, indexes, pool=20):
        self.indexes = indexes
        self.pool = pool

    def search(self, query, top_k=5):
        result_lists = [index.search(query, top_k=self.pool) for index in self.indexes]
        return reciprocal_rank_fusion(result_lists, top_k=top_k)
