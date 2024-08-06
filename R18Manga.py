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

while True:
    request = requests.get(f"https://myanimelist.net/manga/genre/12/Hentai?page={page}")
    soup = BeautifulSoup(request.text, 'html.parser')
    links = soup.find_all("a", class_="link-title")

    if links:
        page += 1
    else:
        break

    for link in links:
        temp = re.sub(r'(?:.*?myanimelist\.net)', '', link.get('href'))
        temp = re.sub(r'\/[^\/]*?$', '', temp)
        new_entry = f'.data.image a[href^="{temp}/"]:before{{content: var(--R18);}}'
        
        if new_entry not in existing_entries:
            animelist.append(new_entry)
            existing_entries.add(new_entry)

with open(file_path, 'a') as f:
    for index in animelist:
        f.write(index + '\n')

print(animelist)