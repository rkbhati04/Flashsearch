import requests
from bs4 import BeautifulSoup
import json
import time
import random

def crawl_wikipedia(start_url, max_pages=20):
    # This list will hold all our scraped data
    scraped_data = []
    
    # We use a 'set' to make sure we don't visit the same page twice
    visited_urls = set()
    current_url = start_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f" Starting crawl at: {start_url}")

    while len(scraped_data) < max_pages:
        if current_url in visited_urls:
            print("Already visited, stopping or picking new link...")
            break

        try:
            # 1. SEND REQUEST (Knock on the door)
            response = requests.get(current_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print("Failed to load page")
                break

            # 2. PARSE HTML (Open the door)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 3. SCRAPE DATA
            # Wikipedia titles are always in an <h1 id="firstHeading"> tag
            title = soup.find(id="firstHeading").text
            
            # The main text is usually in paragraphs <p>
            paragraphs = soup.find_all('p')
            content = " ".join([p.text for p in paragraphs])
            
            # Clean up empty pages
            if not content: 
                break

            # Save to our list
            page_data = {
                "id": len(scraped_data) + 1,
                "url": current_url,
                "title": title,
                "content": content[:500] + "..." # Saving just first 500 chars for preview
            }
            scraped_data.append(page_data)
            visited_urls.add(current_url)
            
            print(f" Scraped [{len(scraped_data)}/{max_pages}]: {title}")

            # 4. CRAWL (Find the next path)
            # Find all links that start with "/wiki/" and are not special files
            all_links = soup.find_all('a', href=True)
            wiki_links = [link['href'] for link in all_links if link['href'].startswith('/wiki/') and ':' not in link['href']]

            if wiki_links:
                # Pick a random link to follow next
                next_link = random.choice(wiki_links)
                current_url = "https://en.wikipedia.org" + next_link
            else:
                print("No more links found!")
                break
            
            # 5. (Wait a bit so we don't crash their server)
            time.sleep(1)

        except Exception as e:
            print(f"Error: {e}")
            break

    # 6. SAVE TO FILE
    with open('wiki_data.json', 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, indent=4, ensure_ascii=False)
    
    print(" Done! Data saved to wiki_data.json")

# Start the crawler
crawl_wikipedia("https://en.wikipedia.org/wiki/Computer_science")