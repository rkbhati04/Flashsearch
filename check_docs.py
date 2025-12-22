import json

with open('wiki_data.json', encoding='utf-8') as f:
    docs = json.load(f)

print("Documents scraped:")
for i, doc in enumerate(docs):
    print(f"{i+1}. {doc['title']}")

print("\n\nSearching for 'exam' and 'computer' in full text:")
for i, doc in enumerate(docs):
    text = (doc['title'] + " " + doc['content']).lower()
    if 'exam' in text:
        print(f"'exam' found in Doc {i+1}: {doc['title']}")
    if 'computer' in text:
        print(f"'computer' found in Doc {i+1}: {doc['title']}")
