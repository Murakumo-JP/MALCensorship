import fs from "fs";
import fetch from "node-fetch";
import * as cheerio from "cheerio";

async function fetchPage(url, headers) {
  try {
    const res = await fetch(url, { headers });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  } catch (err) {
    console.error(`❌ Ошибка при загрузке ${url}: ${err.message}`);
    return null;
  }
}

function extractLinks(html) {
  const $ = cheerio.load(html);
  return $("a.link-title")
    .map((_, el) => $(el).attr("href"))
    .get()
    .filter(Boolean);
}

function formatEntry(link) {
  let path = link.replace(/.*?myanimelist\.net/, "");
  path = path.replace(/\/[^/]*?$/, "");
  return `.data.image a[href^="${path}/"]:before{content: var(--R18);}`;
}

function readEntries(filePath) {
  if (!fs.existsSync(filePath)) return new Set();
  return new Set(
    fs
      .readFileSync(filePath, "utf8")
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
  );
}

function writeEntries(filePath, entries) {
  const sorted = Array.from(entries).sort();
  fs.writeFileSync(filePath, sorted.join("\n") + "\n");
}

async function scrapeGenre(baseUrl, filePath, headers) {
  let page = 1;
  const existing = readEntries(filePath);
  const current = new Set();

  console.log(`\n=== 🔍 Начинаем парсинг: ${baseUrl} ===`);

  while (true) {
    const url = `${baseUrl}?page=${page}`;
    console.log(`→ Загружается страница ${page}...`);
    const html = await fetchPage(url, headers);
    if (!html) break;

    const links = extractLinks(html);
    if (links.length === 0) {
      console.log("⏹ Нет новых страниц. Парсинг завершён.");
      break;
    }

    links.forEach((link) => current.add(formatEntry(link)));
    page++;
  }

  const newEntries = [...current].filter((e) => !existing.has(e));
  const removedEntries = [...existing].filter((e) => !current.has(e));

  if (newEntries.length || removedEntries.length) {
    writeEntries(filePath, current);
    console.log(`✅ Файл обновлён: ${filePath}`);
  } else {
    console.log(`✅ ${filePath} — без изменений`);
  }
}


async function main() {
  const headers = {
    "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
      "AppleWebKit/537.36 (KHTML, like Gecko) " +
      "Chrome/124.0.0.0 Safari/537.36",
  };

  await scrapeGenre("https://myanimelist.net/anime/genre/12/Hentai", "R18Anime.css", headers);
  await scrapeGenre("https://myanimelist.net/manga/genre/12/Hentai", "R18Manga.css", headers);

  console.log("\n🎉 Парсинг завершён успешно.\n");
}

main().catch((err) => {
  console.error("🚨 Критическая ошибка:", err);
  process.exit(1);
});
