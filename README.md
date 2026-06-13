# FlashSearch

A full-text search engine with **TF-IDF ranking** over a corpus of **250+ Wikipedia articles** on computer science topics. Features an NLP preprocessing pipeline, boolean query support, and a modern search UI.

## Features

- **TF-IDF Ranking** — log-normalized term frequency × inverse document frequency scoring
- **NLP Pipeline** — spaCy-powered tokenization, lemmatization, and stopword removal
- **Inverted Index** — O(1) token lookup with precomputed IDF values
- **LRU Cache** — bounded, eviction-based cache for repeated queries (sub-millisecond cache hits)
- **Boolean Queries** — AND (all terms match) and OR (any term matches)
- **Search UI** — dark-mode interface with real-time search, result highlighting, and pagination
- **REST API** — 6 endpoints for search, document retrieval, and statistics
- **Dockerized** — production-ready container with gunicorn

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Browser (Search UI)                                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │  index.html + app.js + style.css                  │  │
│  │  Debounced search · AND/OR toggle · Pagination    │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │ fetch()                          │
├──────────────────────┼──────────────────────────────────┤
│  Flask API Server    │                                  │
│  ┌───────────────────▼───────────────────────────────┐  │
│  │  /api/search      POST  (AND query)               │  │
│  │  /api/search/or   POST  (OR query)                │  │
│  │  /api/document/<id> GET (full document)           │  │
│  │  /api/stats       GET  (index + cache stats)      │  │
│  │  /api/health      GET  (health check)             │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                  │
│  ┌───────────────────▼───────────────────────────────┐  │
│  │  SearchEngine (TF-IDF + LRU Cache)                │  │
│  │  ┌──────────┐  ┌────────────┐  ┌──────────────┐  │  │
│  │  │ Preprocess│→│Inverted Idx│→│TF-IDF Scoring │  │  │
│  │  │ (spaCy)  │  │ (token→doc)│  │ (log-TF×IDF) │  │  │
│  │  └──────────┘  └────────────┘  └──────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.8+

### Installation
```bash
git clone https://github.com/rkbhati04/Flashsearch.git
cd Flashsearch

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Run
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

### Fetch More Data (Optional)
```bash
python data_fetcher.py 500    # Fetches ~500 Wikipedia CS articles
```

## Project Structure

```
FlashSearch/
├── app.py               # Flask server (API + UI)
├── search_engine.py      # TF-IDF search engine with LRU cache
├── indexer.py            # Inverted index builder
├── preprocess.py         # spaCy NLP pipeline
├── data_fetcher.py       # Wikipedia API data fetcher
├── crawler.py            # Original web scraper (legacy)
├── corpus.json           # Article corpus (250+ docs)
├── templates/
│   └── index.html        # Search UI
├── static/
│   ├── style.css         # UI styles
│   └── app.js            # Frontend logic
├── Dockerfile            # Container config
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deployment config
└── README.md
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Search UI |
| `GET` | `/api` | API docs |
| `GET` | `/api/stats` | Index + cache statistics |
| `POST` | `/api/search` | AND search (JSON: `{"query": "..."}`) |
| `POST` | `/api/search/or` | OR search (JSON: `{"query": "..."}`) |
| `GET` | `/api/document/<id>` | Full document by ID |
| `GET` | `/api/health` | Health check |

### Example Response
```json
{
  "query": "machine learning",
  "search_type": "AND",
  "total_matches": 12,
  "results_count": 12,
  "latency_ms": 3.42,
  "cached": false,
  "results": [
    {
      "doc_id": 3,
      "title": "Machine learning",
      "score": 18.4523,
      "preview": "Machine learning is a subset of artificial intelligence..."
    }
  ]
}
```

## Tech Stack

- **Python** — Core language
- **Flask** — Web framework and API server
- **spaCy** — NLP preprocessing (tokenization, lemmatization, stopword removal)
- **TF-IDF** — Information retrieval ranking algorithm
- **Docker** — Containerization
- **Gunicorn** — Production WSGI server

## Docker

```bash
docker build -t flashsearch .
docker run -p 5000:5000 flashsearch
```

## License

MIT License
