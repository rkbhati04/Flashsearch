"""
Indexer module — Builds the inverted index from the document corpus.
Supports both the new corpus.json and legacy wiki_data.json formats.
"""
import json
import os
from collections import defaultdict
from preprocess import preprocess


def build_index(json_file=None):
    """
    Build inverted index from documents in JSON file.

    Automatically detects data/KDMP.json, corpus.json (new) or wiki_data.json (legacy).

    Args:
        json_file (str): Path to JSON file containing documents

    Returns:
        tuple: (inverted_index, documents)
    """
    # Auto-detect data file
    if json_file is None:
        if os.path.exists("ag_news.json"):
            json_file = "ag_news.json"
        elif os.path.exists("data/KDMP.json"):
            json_file = "data/KDMP.json"
        elif os.path.exists("corpus.json"):
            json_file = "corpus.json"
        elif os.path.exists("wiki_data.json"):
            json_file = "wiki_data.json"
        else:
            raise FileNotFoundError(
                "No data file found. Run data_fetcher.py first, "
                "or ensure data/KDMP.json exists."
            )

    # Load documents
    with open(json_file, "r", encoding="utf-8") as f:
        raw_documents = json.load(f)

    print(f"Building index from {json_file} ({len(raw_documents)} documents)...")

    # If it's KDMP.json, transform it to expected format
    documents = []
    if "KDMP.json" in json_file:
        for i, item in enumerate(raw_documents):
            doc = {
                "id": i + 1,  # 1-indexed doc_id required by search_engine.py
                "title": f"Comment by {item.get('nickname', item.get('username', 'Unknown'))}",
                "content": item.get("comment", "")
            }
            # Optional: keep original metadata if you want
            doc.update(item)
            documents.append(doc)
    else:
        documents = raw_documents

    # Create inverted index: token -> {doc_id: frequency}
    inverted_index = defaultdict(lambda: defaultdict(int))

    for i, doc in enumerate(documents):
        doc_id = doc["id"]
        text = doc.get("title", "") + " " + doc.get("content", "")
        tokens = preprocess(text)

        for token in tokens:
            inverted_index[token][doc_id] += 1
            
        # Print progress every 10,000 documents
        if (i + 1) % 10000 == 0:
            print(f"  Processed {i + 1} / {len(documents)} documents...")

    print(f"Index built: {len(inverted_index)} unique tokens")
    return inverted_index, documents


def save_index(inverted_index, filename="index.json"):
    """
    Save inverted index to JSON file for persistence.

    Args:
        inverted_index: The inverted index dictionary
        filename (str): Output filename
    """
    # Convert defaultdict to regular dict for JSON serialization
    serializable_index = {
        token: dict(docs)
        for token, docs in inverted_index.items()
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(serializable_index, f, indent=2, ensure_ascii=False)

    print(f"Index saved to {filename}")


def load_index(filename="index.json"):
    """
    Load inverted index from JSON file.

    Args:
        filename (str): Index filename

    Returns:
        dict: The inverted index
    """
    with open(filename, "r", encoding="utf-8") as f:
        serializable_index = json.load(f)

    # Convert keys back to integers for doc_id
    inverted_index = defaultdict(lambda: defaultdict(int))
    for token, docs in serializable_index.items():
        for doc_id_str, freq in docs.items():
            inverted_index[token][int(doc_id_str)] = freq

    return inverted_index


if __name__ == "__main__":
    # Build and display index statistics
    inverted_index, documents = build_index()

    print(f"\nIndex Statistics:")
    print(f"  Total unique tokens: {len(inverted_index)}")
    print(f"  Total documents: {len(documents)}")

    # Show sample tokens
    print("\nSample token postings:")
    for sample in ["computer", "algorithm", "data", "network"]:
        postings = dict(inverted_index.get(sample, {}))
        print(f"  '{sample}' -> appears in {len(postings)} docs")

    # Save the index
    save_index(inverted_index)
