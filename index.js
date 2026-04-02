import axios from 'axios';
import * as cheerio from 'cheerio';
import fs from 'node:fs';

async function fetchPage(url, headers) {
    try {
        const response = await axios.get(url, { headers });
        return response.data;
    } catch (error) {
        console.error(`Error fetching ${url}: ${error.message}`);
        return null;
    }
}

function extractLinks(html) {
    const $ = cheerio.load(html);
    const links = [];
    $('a.link-title').each((index, element) => {
        const href = $(element).attr('href');
        if (href) links.push(href);
    });
    return links;
}

function processLink(href) {
    let temp = href.replace(/.*?myanimelist\.net/, '');
    temp = temp.replace(/\/[^/]*?$/, '');
    return `.data.image a[href^="${temp}/"]:before{content: var(--R18);}`;
}

function readExistingEntries(filePath) {
    const entries = new Set();
    if (fs.existsSync(filePath)) {
        const fileContent = fs.readFileSync(filePath, 'utf-8');
        const lines = fileContent.split('\n');
        for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed) entries.add(trimmed);
        }
    }
    return entries;
}

function writeEntries(filePath, entries) {
    const content = Array.from(entries).join('\n') + '\n';
    fs.writeFileSync(filePath, content, 'utf-8');
}

async function scrapeR18Data(baseUrl, filePath, headers) {
    let page = 1;
    const existingEntries = readExistingEntries(filePath);
    const validEntries = new Set();

    while (true) {
        console.log(`Fetching page ${page} of ${baseUrl}...`);
        const url = `${baseUrl}?page=${page}`;
        const html = await fetchPage(url, headers);

        if (!html) break;

        const links = extractLinks(html);
        if (links.length === 0) {
            console.log("No more pages found. Exiting.");
            break;
        }

        for (const link of links) {
            const newEntry = processLink(link);
            validEntries.add(newEntry);
        }

        page++;
    }

    const newEntries = new Set([...validEntries].filter(x => !existingEntries.has(x)));
    const removedEntries = new Set([...existingEntries].filter(x => !validEntries.has(x)));

    if (newEntries.size > 0) {
        console.log(`Adding new entries:\n`, Array.from(newEntries));
    }
    if (removedEntries.size > 0) {
        console.log(`Removing invalid entries:\n`, Array.from(removedEntries));
    }

    writeEntries(filePath, validEntries);

    console.log(`New entries added to ${filePath}`);
    console.log(`Invalid entries removed from ${filePath}\n-------------------`);
}

async function main() {
    const headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    };

    await scrapeR18Data(
        "https://myanimelist.net/anime/genre/12/Hentai",
        'data/R18Anime.css',
        headers
    );

    await scrapeR18Data(
        "https://myanimelist.net/manga/genre/12/Hentai",
        'data/R18Manga.css',
        headers
    );

    console.log("Scraping completed.");
}

main();