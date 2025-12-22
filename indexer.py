"""
Indexer module - Builds the inverted index from documents
"""
import json
from collections import defaultdict
from preprocess import preprocess


def build_index(json_file="wiki_data.json"):
    """
    Build inverted index from documents in JSON file.
    
    Args:
        json_file (str): Path to JSON file containing documents
    
    Returns:
        tuple: (inverted_index, documents)
    """
    # Load documents
    with open(json_file, "r", encoding="utf-8") as f:
        documents = json.load(f)
    
    # Create inverted index
    inverted_index = defaultdict(lambda: defaultdict(int))
    
    # Build the index
    for doc in documents:
        doc_id = doc["id"]
        
        # combine title + content
        text = doc["title"] + " " + doc["content"]
        
        # tokenize
        tokens = preprocess(text)
        
        # update index
        for token in tokens:
            inverted_index[token][doc_id] += 1
    
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
    
    print("Index Statistics:")
    print(f"Total unique tokens: {len(inverted_index)}")
    print(f"Total documents: {len(documents)}")
    
    print("\nSample tokens:")
    print("exam →", dict(inverted_index["exam"]))
    print("computer →", dict(inverted_index["computer"]))
    
    # Save the index
    save_index(inverted_index)
