import json
from preprocess import preprocess

with open("wiki_data.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

for doc in documents:   # just test one doc
    text = doc["title"] + " " + doc["content"]
    tokens = preprocess(text)
    print(tokens[:20])
