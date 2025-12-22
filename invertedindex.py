import json
from collections import defaultdict
from preprocess import preprocess


with open("wiki_data.json", "r", encoding="utf-8") as f:
    documents = json.load(f)


inverted_index = defaultdict(lambda: defaultdict(int))


for doc in documents:
    doc_id = doc["id"]
    
    # combine title + content
    text = doc["title"] + " " + doc["content"]
    
    # tokenize
    tokens = preprocess(text)
    
    # update index
    for token in tokens:
        inverted_index[token][doc_id] += 1


# 1. Search function
def search(query):
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
    
    # Find documents for each token
    doc_scores = defaultdict(int)
    
    for token in query_tokens:
        if token in inverted_index:
            # Add up frequencies for matching documents
            for doc_id, frequency in inverted_index[token].items():
                doc_scores[doc_id] += frequency
    
    if not doc_scores:
        return []
    
    # Sort by frequency (highest first)
    sorted_results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get document details
    results = []
    for doc_id, score in sorted_results:
        doc = documents[doc_id - 1]  # doc_id is 1-indexed
        results.append({
            "doc_id": doc_id,
            "title": doc["title"],
            "score": score,
            "preview": doc["content"][:100] + "..."
        })
    
    return results


def display_results(results, query):
    """Display search results in a formatted way."""
    if not results:
        print(f"\nNo results found for '{query}'")
        return
    
    print(f"\n{'='*70}")
    print(f"Search Results for: '{query}' ({len(results)} documents found)")
    print(f"{'='*70}\n")
    
    for i, result in enumerate(results, 1):
        print(f"[{i}] Doc #{result['doc_id']}: {result['title']}")
        print(f"    Score: {result['score']}")
        print(f"    Preview: {result['preview']}")
        print()


# 2. Test the search function
if __name__ == "__main__":
    print("Index Statistics:")
    print(f"Total unique tokens: {len(inverted_index)}")
    print(f"Total documents: {len(documents)}")
    
    print("\nSample token queries:")
    print("exam →", dict(inverted_index["exam"]))
    print("computer →", dict(inverted_index["computer"]))
    
    print("\n" + "="*70)
    print("SEARCH EXAMPLES")
    print("="*70)
    
    # Example searches
    results1 = search("computer")
    display_results(results1, "computer")
    
    results2 = search("research")
    display_results(results2, "research")
    
    results3 = search("science")
    display_results(results3, "science")


