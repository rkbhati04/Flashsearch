"""
Wikipedia Data Fetcher — Uses MediaWiki API instead of web scraping.
Fetches 1,000+ substantive articles from curated CS-related categories.
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

# Curated categories covering breadth of CS topics
CATEGORIES = [
    "Computer_science",
    "Artificial_intelligence",
    "Machine_learning",
    "Data_structures",
    "Algorithms",
    "Operating_systems",
    "Computer_networking",
    "Database_management_systems",
    "Programming_languages",
    "Software_engineering",
    "Cryptography",
    "Computer_security",
    "Web_development",
    "Cloud_computing",
    "Distributed_computing",
    "Computer_graphics",
    "Natural_language_processing",
    "Computer_architecture",
    "Compilers",
    "Information_retrieval",
    "Data_mining",
    "Computer_vision",
    "Robotics",
    "Computational_complexity_theory",
    "Graph_theory",
    "Internet_protocols",
    "Linux",
    "Free_software",
    "Python_(programming_language)",
    "Java_(programming_language)",
]

# Minimum content length to filter out stubs
MIN_CONTENT_LENGTH = 300
# Max content to store per article (chars)
MAX_CONTENT_LENGTH = 3000


def get_category_members(category, limit=100):
    """
    Fetch article titles from a Wikipedia category.
    Uses the MediaWiki API categorymembers endpoint.
    """
    titles = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": min(limit, 500),  # API max is 500
        "cmtype": "page",
        "format": "json",
    }

    try:
        response = SESSION.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        members = data.get("query", {}).get("categorymembers", [])
        titles = [m["title"] for m in members]
    except Exception as e:
        print(f"  [!] Error fetching category '{category}': {e}")

    return titles


def get_article_extracts(titles_batch):
    """
    Fetch plain-text extracts for a batch of articles (max 20 per request).
    Returns list of {title, content} dicts.
    """
    articles = []
    params = {
        "action": "query",
        "titles": "|".join(titles_batch),
        "prop": "extracts",
        "explaintext": True,  # Plain text, no HTML
        "exlimit": len(titles_batch),
        "format": "json",
    }

    try:
        response = SESSION.get(API_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
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
    except Exception as e:
        print(f"  [!] Error fetching extracts: {e}")

    return articles


def fetch_corpus(target_count=1000, output_file="corpus.json"):
    """
    Main function — fetches articles from all categories until target is reached.
    """
    all_articles = []
    seen_titles = set()

    print(f"=== FlashSearch Data Fetcher ===")
    print(f"Target: {target_count} articles from {len(CATEGORIES)} categories\n")

    for i, category in enumerate(CATEGORIES):
        if len(all_articles) >= target_count:
            break

        # Calculate how many more we need
        remaining = target_count - len(all_articles)
        fetch_limit = min(remaining + 50, 200)  # Fetch extra to account for stubs

        print(f"[{i+1}/{len(CATEGORIES)}] Category: {category} (have {len(all_articles)}/{target_count})")
        titles = get_category_members(category, limit=fetch_limit)
        
        # Filter out already-seen titles
        new_titles = [t for t in titles if t not in seen_titles]
        seen_titles.update(new_titles)
        
        if not new_titles:
            print(f"  Skipping — no new articles")
            continue

        print(f"  Found {len(new_titles)} new titles, fetching extracts...")

        # Fetch extracts in batches of 20 (API limit)
        batch_size = 20
        category_articles = []

        for j in range(0, len(new_titles), batch_size):
            batch = new_titles[j:j + batch_size]
            articles = get_article_extracts(batch)
            category_articles.extend(articles)

            # Respect rate limits
            time.sleep(0.5)

            if len(all_articles) + len(category_articles) >= target_count:
                break

        all_articles.extend(category_articles)
        print(f"  Added {len(category_articles)} articles (total: {len(all_articles)})")

    # Assign sequential IDs
    for idx, article in enumerate(all_articles):
        article["id"] = idx + 1

    # Trim to exact target
    all_articles = all_articles[:target_count]

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)

    print(f"\n=== Done ===")
    print(f"Saved {len(all_articles)} articles to {output_file}")
    print(f"File size: {len(json.dumps(all_articles)) / 1024:.1f} KB")

    return all_articles


if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    fetch_corpus(target_count=target)
