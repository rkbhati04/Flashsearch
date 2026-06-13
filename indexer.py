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

    Automatically detects corpus.json (new) or wiki_data.json (legacy).

    Args:
        json_file (str): Path to JSON file containing documents

    Returns:
        tuple: (inverted_index, documents)
    """
    # Auto-detect data file
    if json_file is None:
        if os.path.exists("corpus.json"):
            json_file = "corpus.json"
        elif os.path.exists("wiki_data.json"):
            json_file = "wiki_data.json"
        else:
            raise FileNotFoundError(
                "No data file found. Run data_fetcher.py first, "
                "or ensure corpus.json / wiki_data.json exists."
            )

    # Load documents
    with open(json_file, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"Building index from {json_file} ({len(documents)} documents)...")

    # Create inverted index: token -> {doc_id: frequency}
    inverted_index = defaultdict(lambda: defaultdict(int))

    for doc in documents:
        doc_id = doc["id"]
        text = doc.get("title", "") + " " + doc.get("content", "")
        tokens = preprocess(text)

        for token in tokens:
            inverted_index[token][doc_id] += 1

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
