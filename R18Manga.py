from bs4 import BeautifulSoup
import requests
import re
import os

animelist = []
page = 1

file_path = 'R18Manga.css'

if not os.path.exists(file_path):
    open(file_path, 'w').close()

existing_entries = set()
with open(file_path, 'r') as f:
    for line in f:
        existing_entries.add(line.strip())

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

while True:
    print(f"Fetching page {page}...")
    request = requests.get(f"https://myanimelist.net/manga/genre/12/Hentai?page={page}", headers=headers)
    soup = BeautifulSoup(request.text, 'html.parser')
    links = soup.find_all("a", class_="link-title")

    if links:
        page += 1
    else:
        print("No more pages found. Exiting.")
        break

    for link in links:
        temp = re.sub(r'(?:.*?myanimelist\.net)', '', link.get('href'))
        temp = re.sub(r'\/[^\/]*?$', '', temp)
        new_entry = f'.data.image a[href^="{temp}/"]:before{{content: var(--R18);}}'
        
        if new_entry not in existing_entries:
            print(f"Adding new entry: {new_entry}")
            animelist.append(new_entry)
            existing_entries.add(new_entry)

with open(file_path, 'a') as f:
    for index in animelist:
        f.write(index + '\n')

print("Scraping completed. New entries added to R18Manga.css")