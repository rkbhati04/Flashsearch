"""
Search Engine module — TF-IDF ranking, LRU cache, query timing.
"""
import math
import time
from collections import defaultdict, OrderedDict
from preprocess import preprocess


class LRUCache:
    """Bounded LRU cache to avoid unbounded memory growth."""

    def __init__(self, capacity=500):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    @property
    def stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 1),
            "size": len(self.cache),
            "capacity": self.capacity,
        }


class SearchEngine:
    """Full-text search engine with TF-IDF ranking."""

    def __init__(self, inverted_index, documents):
        """
        Initialize search engine with index and documents.

        Args:
            inverted_index: dict mapping token -> {doc_id: frequency}
            documents: list of document dicts with id, title, content
        """
        self.inverted_index = inverted_index
        self.documents = documents
        self.num_docs = len(documents)
        self.cache = LRUCache(capacity=500)

        # Precompute IDF for every token
        self.idf = {}
        for token, postings in inverted_index.items():
            df = len(postings)  # document frequency
            self.idf[token] = math.log((self.num_docs + 1) / (df + 1)) + 1  # smoothed IDF

    def _tfidf_score(self, token, doc_id):
        """Compute TF-IDF score for a token in a document."""
        tf = self.inverted_index.get(token, {}).get(doc_id, 0)
        if tf == 0:
            return 0.0
        # Log-normalized term frequency
        tf_norm = 1 + math.log(tf)
        return tf_norm * self.idf.get(token, 0)

    def search(self, query, limit=20, offset=0):
        """
        AND search — all query terms must appear in matching documents.
        Results ranked by TF-IDF score.

        Returns:
            dict with results, timing, and metadata
        """
        start_time = time.perf_counter()
        cache_key = ("AND", query, limit, offset)

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            elapsed = (time.perf_counter() - start_time) * 1000
            cached["latency_ms"] = round(elapsed, 2)
            cached["cached"] = True
            return cached

        query_tokens = preprocess(query)
        if not query_tokens:
            return self._empty_result(query, "AND", start_time)

        # Find documents containing ALL tokens (AND)
        token_doc_sets = []
        for token in query_tokens:
            if token in self.inverted_index:
                token_doc_sets.append(set(self.inverted_index[token].keys()))
            else:
                # Token not in index → no documents can match AND query
                return self._empty_result(query, "AND", start_time)

        matching_docs = set.intersection(*token_doc_sets) if token_doc_sets else set()

        # Score matching documents using TF-IDF
        doc_scores = {}
        for doc_id in matching_docs:
            score = sum(self._tfidf_score(token, doc_id) for token in query_tokens)
            doc_scores[doc_id] = score

        result = self._build_result(query, "AND", doc_scores, query_tokens, limit, offset, start_time)
        self.cache.put(cache_key, result)
        return result

    def search_or(self, query, limit=20, offset=0):
        """
        OR search — any query term can appear in matching documents.
        Results ranked by TF-IDF score.
        """
        start_time = time.perf_counter()
        cache_key = ("OR", query, limit, offset)

        cached = self.cache.get(cache_key)
        if cached is not None:
            elapsed = (time.perf_counter() - start_time) * 1000
            cached["latency_ms"] = round(elapsed, 2)
            cached["cached"] = True
            return cached

        query_tokens = preprocess(query)
        if not query_tokens:
            return self._empty_result(query, "OR", start_time)

        # Score ALL documents containing ANY token (OR)
        doc_scores = defaultdict(float)
        for token in query_tokens:
            if token in self.inverted_index:
                for doc_id in self.inverted_index[token]:
                    doc_scores[doc_id] += self._tfidf_score(token, doc_id)

        result = self._build_result(query, "OR", dict(doc_scores), query_tokens, limit, offset, start_time)
        self.cache.put(cache_key, result)
        return result

    def _build_result(self, query, search_type, doc_scores, query_tokens, limit, offset, start_time):
        """Build a structured result dict from scored documents."""
        if not doc_scores:
            return self._empty_result(query, search_type, start_time)

        # Sort by score descending
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        total_matches = len(sorted_docs)

        # Paginate
        page = sorted_docs[offset:offset + limit]

        results = []
        for doc_id, score in page:
            doc = self.documents[doc_id - 1]  # doc_id is 1-indexed
            preview = doc.get("content", "")[:200]
            results.append({
                "doc_id": doc_id,
                "title": doc["title"],
                "score": round(score, 4),
                "preview": preview + ("..." if len(doc.get("content", "")) > 200 else ""),
            })

        elapsed = (time.perf_counter() - start_time) * 1000
        return {
            "query": query,
            "search_type": search_type,
            "tokens": query_tokens,
            "total_matches": total_matches,
            "results_count": len(results),
            "limit": limit,
            "offset": offset,
            "latency_ms": round(elapsed, 2),
            "cached": False,
            "results": results,
        }

    def _empty_result(self, query, search_type, start_time):
        elapsed = (time.perf_counter() - start_time) * 1000
        return {
            "query": query,
            "search_type": search_type,
            "tokens": [],
            "total_matches": 0,
            "results_count": 0,
            "limit": 20,
            "offset": 0,
            "latency_ms": round(elapsed, 2),
            "cached": False,
            "results": [],
        }

    def get_stats(self):
        """Get index and cache statistics."""
        return {
            "total_tokens": len(self.inverted_index),
            "total_documents": self.num_docs,
            "cache": self.cache.stats,
        }


# ─── CLI testing ─────────────────────────────────────────────
def display_results(result):
    """Pretty-print search results in the terminal."""
    if not result["results"]:
        print(f"\nNo results for '{result['query']}' ({result['search_type']})")
        return

    print(f"\n{'='*70}")
    print(f"Query: '{result['query']}' ({result['search_type']})  |  "
          f"{result['total_matches']} matches  |  {result['latency_ms']}ms")
    print(f"{'='*70}\n")

    for i, r in enumerate(result["results"], 1):
        print(f"  [{i}] {r['title']}  (score: {r['score']})")
        print(f"      {r['preview'][:100]}...")
        print()


if __name__ == "__main__":
    from indexer import build_index

    inverted_index, documents = build_index()
    engine = SearchEngine(inverted_index, documents)

    stats = engine.get_stats()
    print(f"Index: {stats['total_tokens']} tokens, {stats['total_documents']} docs\n")

    # Run sample queries
    for q in ["machine learning", "computer science", "algorithm", "database"]:
        display_results(engine.search(q))
        # Second search should hit cache
        display_results(engine.search(q))
