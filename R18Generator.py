from bs4 import BeautifulSoup
import requests
import re
import os

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
    return soup.find_all("a", class_="link-title")

def process_link(link):
    temp = re.sub(r'(?:.*?myanimelist\.net)', '', link.get('href'))
    temp = re.sub(r'\/[^\/]*?$', '', temp)
    return f'.data.image a[href^="{temp}/"]:before{{content: var(--R18);}}'

def read_existing_entries(file_path):
    entries = set()
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                entries.add(line.strip())
    return entries

def write_entries(file_path, entries):
    with open(file_path, 'w') as f:
        for entry in entries:
            f.write(entry + '\n')

def scrape_r18_data(base_url, file_path, headers):
    page = 1
    existing_entries = read_existing_entries(file_path)
    valid_entries = set()

    while True:
        print(f"Fetching page {page} of {base_url}...")
        url = f"{base_url}?page={page}"
        html = fetch_page(url, headers)
        if not html:
            break

        links = extract_links(html)
        if not links:
            print("No more pages found. Exiting.")
            break

        for link in links:
            new_entry = process_link(link)
            valid_entries.add(new_entry)

        page += 1

    new_entries = valid_entries - existing_entries
    removed_entries = existing_entries - valid_entries

    if new_entries:
        print(f"Adding new entries: {new_entries}")
    if removed_entries:
        print(f"Removing invalid entries: {removed_entries}")

    all_valid_entries = existing_entries.intersection(valid_entries).union(new_entries)
    write_entries(file_path, all_valid_entries)

    print(f"New entries added to {file_path}")
    print(f"Invalid entries removed from {file_path}")

def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    scrape_r18_data(
        base_url="https://myanimelist.net/anime/genre/12/Hentai",
        file_path='R18Anime.css',
        headers=headers
    )

    scrape_r18_data(
        base_url="https://myanimelist.net/manga/genre/12/Hentai",
        file_path='R18Manga.css',
        headers=headers
    )

    print("Scraping completed.")

if __name__ == "__main__":
    main()
