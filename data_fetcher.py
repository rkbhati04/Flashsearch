"""
Wikipedia Data Fetcher — Uses MediaWiki API instead of web scraping.
Fetches substantive articles from curated CS-related categories.
Includes retry logic with exponential backoff for rate limiting.
"""
import requests
import json
import time
import sys

API_URL = "https://en.wikipedia.org/w/api.php"

# Persistent session with proper User-Agent (required by Wikipedia API policy)
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "FlashSearch/1.0 (https://github.com/rkbhati04/Flashsearch; rkbhat0105@gmail.com) python-requests"
})

# Curated categories — broad coverage of CS and tech topics
CATEGORIES = [
    "Computer_science", "Artificial_intelligence", "Machine_learning",
    "Data_structures", "Algorithms", "Operating_systems",
    "Computer_networking", "Database_management_systems",
    "Programming_languages", "Software_engineering", "Cryptography",
    "Computer_security", "Web_development", "Cloud_computing",
    "Distributed_computing", "Computer_graphics",
    "Natural_language_processing", "Computer_architecture",
    "Compilers", "Information_retrieval", "Data_mining",
    "Computer_vision", "Robotics", "Computational_complexity_theory",
    "Graph_theory", "Internet_protocols", "Linux",
    "Free_software", "Python_(programming_language)",
    "Java_(programming_language)",
    # Additional categories for more coverage
    "Computer_programming", "World_Wide_Web", "Computer_networks",
    "Theoretical_computer_science", "Computing",
    "Formal_methods", "Parallel_computing", "Computer_hardware",
    "Human%E2%80%93computer_interaction", "Software",
    "Internet", "Cybernetics", "Automation",
    "Electronic_design_automation", "History_of_computing",
    "Computer_engineers", "Programming_paradigms",
    "Type_theory", "Logic_in_computer_science",
    "Numerical_analysis", "Mathematical_optimization",
]

MIN_CONTENT_LENGTH = 300
MAX_CONTENT_LENGTH = 3000
MAX_RETRIES = 3
BASE_DELAY = 2  # seconds between requests


def api_get(params, retries=MAX_RETRIES):
    """Make an API request with retry + exponential backoff."""
    for attempt in range(retries):
        try:
            response = SESSION.get(API_URL, params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            wait = BASE_DELAY * (2 ** attempt)
            if attempt < retries - 1:
                print(f"    Retry {attempt+1}/{retries} in {wait}s... ({type(e).__name__})")
                time.sleep(wait)
            else:
                print(f"  [!] Failed after {retries} retries: {e}")
                return None


def get_category_members(category, limit=100):
    """Fetch article titles from a Wikipedia category."""
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": min(limit, 500),
        "cmtype": "page",
        "format": "json",
    }
    data = api_get(params)
    if data:
        return [m["title"] for m in data.get("query", {}).get("categorymembers", [])]
    return []


def get_article_extracts(titles_batch):
    """Fetch plain-text extracts for a batch of articles (max 20 per request)."""
    params = {
        "action": "query",
        "titles": "|".join(titles_batch),
        "prop": "extracts",
        "explaintext": True,
        "exlimit": len(titles_batch),
        "format": "json",
    }
    data = api_get(params)
    if not data:
        return []

    articles = []
    pages = data.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if page_id == "-1":
            continue
        extract = page.get("extract", "")
        if len(extract) >= MIN_CONTENT_LENGTH:
            articles.append({
                "title": page["title"],
                "content": extract[:MAX_CONTENT_LENGTH],
            })
    return articles


def fetch_corpus(target_count=1000, output_file="corpus.json"):
    """Main — fetches articles from all categories until target is reached."""
    all_articles = []
    seen_titles = set()

    print(f"=== FlashSearch Data Fetcher ===")
    print(f"Target: {target_count} articles from {len(CATEGORIES)} categories\n")

    for i, category in enumerate(CATEGORIES):
        if len(all_articles) >= target_count:
            break

        remaining = target_count - len(all_articles)
        fetch_limit = min(remaining + 50, 200)

        print(f"[{i+1}/{len(CATEGORIES)}] {category} (have {len(all_articles)}/{target_count})")

        time.sleep(BASE_DELAY)  # Rate limit between categories
        titles = get_category_members(category, limit=fetch_limit)

        new_titles = [t for t in titles if t not in seen_titles]
        seen_titles.update(new_titles)

        if not new_titles:
            print(f"  Skipped (no new articles)")
            continue

        print(f"  {len(new_titles)} new titles, fetching...")

        batch_size = 20
        category_articles = []

        for j in range(0, len(new_titles), batch_size):
            batch = new_titles[j:j + batch_size]
            articles = get_article_extracts(batch)
            category_articles.extend(articles)
            time.sleep(BASE_DELAY)  # Rate limit between batches

            if len(all_articles) + len(category_articles) >= target_count:
                break

        all_articles.extend(category_articles)
        print(f"  +{len(category_articles)} articles (total: {len(all_articles)})")

    # Assign sequential IDs and trim
    for idx, article in enumerate(all_articles):
        article["id"] = idx + 1
    all_articles = all_articles[:target_count]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)

    print(f"\n=== Done ===")
    print(f"Saved {len(all_articles)} articles to {output_file}")
    print(f"File size: {len(json.dumps(all_articles)) / 1024:.1f} KB")
    return all_articles


if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    fetch_corpus(target_count=target)
