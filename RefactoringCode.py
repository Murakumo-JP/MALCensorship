from bs4 import BeautifulSoup
import requests
import os
import re

def fetch_page(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    return [re.sub(r'\/[^\/]*?$', '', re.sub(r'(?:.*?myanimelist\.net)', '', a.get('href'))) for a in soup.find_all("a", class_="link-title")]

def read_existing_entries(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def write_entries(file_path, entries):
    with open(file_path, 'w') as f:
        f.write('\n'.join(entries) + '\n')

def scrape_r18_data(base_url, file_path, headers):
    page, valid_entries = 1, set()
    existing_entries = read_existing_entries(file_path)
    
    while True:
        url = f"{base_url}?page={page}"
        html = fetch_page(url, headers)
        if not html: break
        
        links = extract_links(html)
        if not links: break
        
        valid_entries.update(f'.data.image a[href^="{link}/"]:before{{content: var(--R18);}}' for link in links)
        page += 1

    new_entries = valid_entries - existing_entries
    removed_entries = existing_entries - valid_entries

    print(f"New entries added: {len(new_entries)}")
    print(f"Entries removed: {len(removed_entries)}")

    write_entries(file_path, valid_entries)

def main():
    headers = {'User-Agent': 'Mozilla/5.0'}
    scrape_r18_data("https://myanimelist.net/anime/genre/12/Hentai", 'R18Anime.css', headers)
    scrape_r18_data("https://myanimelist.net/manga/genre/12/Hentai", 'R18Manga.css', headers)
    print("Scraping completed.")

if __name__ == "__main__":
    main()
