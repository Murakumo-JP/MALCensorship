from bs4 import BeautifulSoup
import requests
import re
import os

animelist = []
page = 1

file_path = 'R18Anime.css'

if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        existing_lines = set(line.strip() for line in f)
else:
    existing_lines = set()

while True:
    request = requests.get(f"https://myanimelist.net/anime/genre/12/Hentai?page={page}")
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
        if new_entry not in existing_lines:
            animelist.append(new_entry)
            existing_lines.add(new_entry)

with open(file_path, 'w') as f:
    for index in animelist:
        f.write(index + '\n')

print(animelist)