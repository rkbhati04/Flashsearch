import json
import csv
import urllib.request
import os

def download_ag_news():
    url = 'https://raw.githubusercontent.com/mhjabreel/CharCnn_Keras/master/data/ag_news_csv/train.csv'
    csv_file = 'ag_news.csv'
    
    print("Downloading AG News dataset (120,000 articles) directly...")
    urllib.request.urlretrieve(url, csv_file)
    
    print("Download complete. Converting to FlashSearch format...")
    documents = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            # AG News CSV format: class_index, title, description
            if len(row) >= 3:
                documents.append({
                    "id": i + 1,
                    "title": row[1],
                    "content": row[2]
                })
                
            if (i + 1) % 20000 == 0:
                print(f"  Processed {i + 1} / 120000 articles...")

    output_file = "ag_news.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2)
        
    print(f"\nDone! Saved all articles to '{output_file}'.")
    
    # Clean up the CSV file
    if os.path.exists(csv_file):
        os.remove(csv_file)

if __name__ == "__main__":
    download_ag_news()
