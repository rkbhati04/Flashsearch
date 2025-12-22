"""
Search Engine module - Provides search functionality on inverted index
"""
import json
from collections import defaultdict
from preprocess import preprocess


class SearchEngine:
    """Full-text search engine using inverted index"""
    
    def __init__(self, inverted_index, documents):
        """
        Initialize search engine with index and documents.
        
        Args:
            inverted_index: The inverted index dictionary
            documents: List of document dictionaries
        """
        self.inverted_index = inverted_index
        self.documents = documents
    
    def search(self, query):
        """
        Search the inverted index for documents matching the query.
        
        Args:
            query (str): Search query (can be single word or multiple words)
        
        Returns:
            list: List of dictionaries with doc_id, title, score, and preview
        """
        # Preprocess the query
        query_tokens = preprocess(query)
        
        if not query_tokens:
            return []
        
        # Find documents for each token (AND search - all tokens must match)
        doc_scores = defaultdict(int)
        token_docs = []
        
        # Get documents matching each token
        for token in query_tokens:
            if token in self.inverted_index:
                token_docs.append(set(self.inverted_index[token].keys()))
            else:
                token_docs.append(set())
        
        # AND operation: only documents in ALL token sets
        if token_docs:
            matching_docs = set.intersection(*token_docs) if token_docs else set()
        else:
            matching_docs = set()
        
        # Score the matching documents
        for token in query_tokens:
            if token in self.inverted_index:
                for doc_id, frequency in self.inverted_index[token].items():
                    if doc_id in matching_docs:
                        doc_scores[doc_id] += frequency
        
        if not doc_scores:
            return []
        
        # Sort by frequency (highest first)
        sorted_results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get document details
        results = []
        for doc_id, score in sorted_results:
            doc = self.documents[doc_id - 1]  # doc_id is 1-indexed
            results.append({
                "doc_id": doc_id,
                "title": doc["title"],
                "score": score,
                "preview": doc["content"][:100] + "..."
            })
        
        return results
    
    def search_or(self, query):
        """
        OR search - documents matching ANY of the query terms.
        
        Args:
            query (str): Search query
        
        Returns:
            list: Sorted list of matching documents
        """
        query_tokens = preprocess(query)
        
        if not query_tokens:
            return []
        
        doc_scores = defaultdict(int)
        
        # OR operation: accumulate scores from all tokens
        for token in query_tokens:
            if token in self.inverted_index:
                for doc_id, frequency in self.inverted_index[token].items():
                    doc_scores[doc_id] += frequency
        
        if not doc_scores:
            return []
        
        sorted_results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_results:
            doc = self.documents[doc_id - 1]
            results.append({
                "doc_id": doc_id,
                "title": doc["title"],
                "score": score,
                "preview": doc["content"][:100] + "..."
            })
        
        return results
    
    def get_stats(self):
        """Get index statistics."""
        return {
            "total_tokens": len(self.inverted_index),
            "total_documents": len(self.documents)
        }


def display_results(results, query, search_type="AND"):
    """Display search results in a formatted way."""
    if not results:
        print(f"\nNo results found for '{query}' ({search_type} search)")
        return
    
    print(f"\n{'='*70}")
    print(f"Search Results for: '{query}' ({search_type} search)")
    print(f"Documents found: {len(results)}")
    print(f"{'='*70}\n")
    
    for i, result in enumerate(results, 1):
        print(f"[{i}] Doc #{result['doc_id']}: {result['title']}")
        print(f"    Relevance Score: {result['score']}")
        print(f"    Preview: {result['preview']}")
        print()


if __name__ == "__main__":
    from indexer import build_index
    
    # Build index and initialize search engine
    inverted_index, documents = build_index()
    engine = SearchEngine(inverted_index, documents)
    
    # Display statistics
    stats = engine.get_stats()
    print(f"Index Statistics:")
    print(f"Total unique tokens: {stats['total_tokens']}")
    print(f"Total documents: {stats['total_documents']}")
    
    # Example searches
    print("\n" + "="*70)
    print("SEARCH EXAMPLES")
    print("="*70)
    
    results = engine.search("computer")
    display_results(results, "computer", "AND")
    
    results = engine.search("research data")
    display_results(results, "research data", "AND")
    
    results = engine.search_or("research data")
    display_results(results, "research data", "OR")
