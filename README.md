# FlashSearch - Wikipedia Crawler & Inverted Index Search Engine

A Python-based web scraper and full-text search engine that crawls Wikipedia articles and builds an inverted index for fast document retrieval.

## Features

- **Web Crawler**: Scrapes Wikipedia articles starting from any topic
- **Text Preprocessing**: Uses spaCy for lemmatization, stop word removal, and tokenization
- **Inverted Index**: Efficient full-text search index structure
- **Search Engine**: Query documents with relevance ranking based on token frequency

## Project Structure

```
FlashSearch/
├── crawler.py           # Wikipedia web scraper
├── preprocess.py        # Text preprocessing with spaCy
├── invertedindex.py     # Inverted index and search functionality
├── tokenize_json.py     # Test tokenizer script
├── wiki_data.json       # Scraped Wikipedia data
└── README.md            # This file
```

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Required Libraries
```bash
pip install requests beautifulsoup4 spacy
python -m spacy download en_core_web_sm
```

## Usage

### 1. Crawl Wikipedia
```bash
python crawler.py
```
This will scrape 20 Wikipedia articles starting from "Computer science" and save data to `wiki_data.json`.

### 2. Build Inverted Index and Search
```bash
python invertedindex.py
```
This creates an inverted index and runs example searches.

### 3. Test Tokenization
```bash
python tokenize_json.py
```
This tests the preprocessing pipeline on the first document.

## How It Works

### Crawler (crawler.py)
- Sends HTTP requests to Wikipedia pages
- Parses HTML using BeautifulSoup
- Extracts titles and content from articles
- Follows random links to discover new pages
- Saves data in JSON format

### Preprocessing (preprocess.py)
- Loads spaCy's English language model
- Tokenizes text into individual words
- Converts words to their base form (lemmatization)
- Removes punctuation, whitespace, and stop words
- Returns cleaned tokens for indexing

### Inverted Index (invertedindex.py)
- Maps each token to the documents containing it
- Tracks token frequency in each document
- Provides `search(query)` function for full-text search
- Ranks results by relevance (token frequency)

## Example Searches

```python
from invertedindex import search, display_results

# Search for documents about "computer"
results = search("computer")
display_results(results, "computer")

# Search with multiple terms
results = search("scientific research")
display_results(results, "scientific research")
```

## Performance

- **Index Size**: 526 unique tokens
- **Documents**: 20 Wikipedia articles
- **Search Time**: O(k) where k is number of matching documents

## Technologies Used

- **BeautifulSoup**: HTML parsing
- **Requests**: HTTP requests
- **spaCy**: NLP and text processing
- **Python Collections**: Efficient data structures (defaultdict)

## Future Enhancements

- [ ] TF-IDF ranking algorithm
- [ ] Boolean query support (AND, OR, NOT)
- [ ] Phrase search
- [ ] Web UI for searching
- [ ] Persistent database (SQLite/PostgreSQL)
- [ ] Pagination for large result sets

## Author

Created as a demonstration of web scraping and information retrieval concepts.

## License

MIT License - Feel free to use for educational purposes.
