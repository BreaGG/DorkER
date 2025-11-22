"""
AUTO-OSINT Google Dork Generator & Multi-Engine Search
Integrated with dork generators and interactive menu.


Save as: dorker.py
Run: pip install aiohttp aiofiles beautifulsoup4 colorama requests tqdm python-dateutil
Run: python dorker.py

Notes:
- Optional API keys: SERPAPI_KEY, BING_API_KEY as environment variables.
- For screenshots (optional), integrate Selenium/Playwright manually.
"""

import os
import re
import json
import time
import random
import asyncio
import logging
import aiohttp
import aiofiles
import hashlib
from datetime import datetime
from dateutil import parser as dateparser
from bs4 import BeautifulSoup
from collections import defaultdict
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)

# ---------------------------
# Configuration
# ---------------------------

HISTORY_DIR = "history"
EVIDENCE_DIR = "evidence"
REPORTS_DIR = "reports"
HTML_SNAPSHOT_DIR = os.path.join(EVIDENCE_DIR, "html")
TOP_URLS_DIR = os.path.join(EVIDENCE_DIR, "top_urls")

# Create folders
for d in (HISTORY_DIR, EVIDENCE_DIR, REPORTS_DIR, HTML_SNAPSHOT_DIR, TOP_URLS_DIR):
    os.makedirs(d, exist_ok=True)

# Async HTTP defaults
REQUEST_TIMEOUT = 20  # seconds
MAX_CONCURRENT_TASKS = 8
MIN_DELAY = 1.0  # second between requests (randomized)
MAX_DELAY = 3.0

# Optional API keys (read from env)
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
BING_API_KEY = os.environ.get("BING_API_KEY")

# User agents pool (small sample; extend as needed)
USER_AGENTS = [
    # Common desktop user agents
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
    " (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
]

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("auto-osint")

# ---------------------------
# Your original dork generators (kept intact)
# ---------------------------

def dorks_email(email):
    return {
        "Búsqueda exacta": [
            f'"{email}"'
        ],
        "Documentos": [
            f'filetype:pdf "{email}"',
            f'filetype:doc "{email}"',
            f'filetype:docx "{email}"',
            f'filetype:xls "{email}"',
            f'filetype:xlsx "{email}"',
            f'filetype:txt "{email}"',
            f'filetype:csv "{email}"',
        ],
        "Leaks / Exposiciones": [
            f'"{email}" "password"',
            f'"{email}" "contraseña"',
            f'"{email}" "login"',
            f'"{email}" "user"',
        ],
        "Sitios específicos": [
            f'site:pastebin.com "{email}"',
            f'site:github.com "{email}"',
            f'site:reddit.com "{email}"',
            f'site:linkedin.com "{email}"',
            f'site:twitter.com "{email}"',
        ],
        "Variaciones ofuscadas": [
            f'"{email.replace("@", " at ")}"',
            f'"{email.replace("@", " [at] ")}"',
            f'"{email.replace("@", "(at)")} "',
            f'"{email.replace("@", "[at]")}"',
        ],
    }


def dorks_usuario(username):
    return {
        "Perfiles / usernames": [
            f'"{username}"',
            f'"{username}" site:github.com',
            f'"{username}" site:gitlab.com',
            f'"{username}" site:twitter.com',
            f'"{username}" site:linkedin.com',
            f'"{username}" site:instagram.com',
        ],
        "Leaks": [
            f'"{username}" "password"',
            f'"{username}" "login"',
            f'"{username}" "credentials"',
        ],
        "Combinaciones útiles": [
            f'"{username}" "@gmail.com"',
            f'"{username}" "email"',
        ]
    }


def dorks_dominio(domain):
    return {
        "Información general": [
            f'site:{domain}',
            f'"{domain}"',
            f'"{domain}" -www',
        ],
        "Subdominios": [
            f'site:{domain} -www.{domain}',
            f'"*.{domain}"',
        ],
        "Documentos": [
            f'site:{domain} filetype:pdf',
            f'site:{domain} filetype:xls',
            f'site:{domain} filetype:doc',
        ],
        "Leaks": [
            f'"{domain}" "password"',
            f'"{domain}" "database"',
            f'"{domain}" "index of"',
        ]
    }


def dorks_subdominio(subdomain):
    domain = subdomain.split(".", 1)[-1]
    return {
        "Búsqueda básica": [
            f'site:{subdomain}',
            f'"{subdomain}"',
        ],
        "Infraestructura": [
            f'site:{subdomain} "server"',
            f'site:{subdomain} "Apache"',
            f'site:{subdomain} "nginx"',
            f'site:{subdomain} "port"',
        ],
        "Relación con el dominio": [
            f'"{subdomain}" "{domain}"',
            f'site:{domain} "{subdomain}"',
        ],
        "Archivos expuestos": [
            f'site:{subdomain} filetype:env',
            f'site:{subdomain} filetype:log',
            f'site:{subdomain} filetype:txt',
        ]
    }

# ---------------------------
# Utility helpers
# ---------------------------

def uid_for_query(query: str) -> str:
    """Stable short id for a query -> used for filenames."""
    h = hashlib.sha1(query.encode("utf-8")).hexdigest()
    return h[:12]

def safe_filename(s: str) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]', '_', s)[:200]

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def sleep_random():
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)

# ---------------------------
# Parsers for search engines (scrape-based)
# ---------------------------

async def fetch(session: aiohttp.ClientSession, url: str, headers=None, params=None):
    try:
        async with session.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT) as resp:
            text = await resp.text()
            return resp.status, text
    except Exception as e:
        logger.debug(f"fetch error for {url}: {e}")
        return None, None

def parse_duckduckgo_count(html: str):
    """
    DuckDuckGo does not provide an explicit total; instead, count number of result blocks.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = soup.select("a.result__a")
    # fallback: count result containers
    if not results:
        results = soup.select(".result")
    count = len(results)
    urls = []
    for a in results[:10]:
        href = a.get("href")
        if href:
            urls.append(href)
    return count, urls

def parse_brave_count(html: str):
    soup = BeautifulSoup(html, "html.parser")
    # Brave uses results with class "result" or "snippet" - fallback robust selection
    items = soup.select("a.result__link, a.result-link, .serp-item a, .result a")
    if not items:
        items = soup.select(".result")
    count = len(items)
    urls = []
    for a in items[:10]:
        href = a.get("href")
        if href:
            urls.append(href)
    return count, urls

def normalize_number_text(s: str) -> int:
    # Parse strings like "About 1,230 results" -> 1230
    if not s:
        return 0
    s = re.sub(r"[^\d]", "", s)
    try:
        return int(s)
    except:
        return 0

# ---------------------------
# Engines implementations
# ---------------------------

async def search_duckduckgo(session: aiohttp.ClientSession, query: str):
    """Scrape DuckDuckGo HTML and return (count_estimate, top_urls, raw_html)"""
    q = query
    url = "https://html.duckduckgo.com/html/"
    # Use the simple HTML endpoint which is more scrape-friendly
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    data = {"q": q}
    try:
        async with session.post(url, data=data, headers=headers, timeout=REQUEST_TIMEOUT) as resp:
            html = await resp.text()
            count, urls = parse_duckduckgo_count(html)
            return {"engine": "duckduckgo", "count": count, "top_urls": urls, "raw": html}
    except Exception as e:
        logger.warning(f"DuckDuckGo fetch error for q={q}: {e}")
        return {"engine": "duckduckgo", "count": 0, "top_urls": [], "raw": None}

async def search_brave(session: aiohttp.ClientSession, query: str):
    """Scrape Brave Search"""
    q = query
    # Brave search URL (simple)
    url = "https://search.brave.com/search"
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    params = {"q": q}
    status, html = None, None
    try:
        status, html = await fetch(session, url, headers=headers, params=params)
        if not html:
            return {"engine": "brave", "count": 0, "top_urls": [], "raw": None}
        count, urls = parse_brave_count(html)
        return {"engine": "brave", "count": count, "top_urls": urls, "raw": html}
    except Exception as e:
        logger.warning(f"Brave fetch error for q={q}: {e}")
        return {"engine": "brave", "count": 0, "top_urls": [], "raw": None}

async def search_serpapi(query: str):
    """Use SerpAPI if api key provided (Google)"""
    if not SERPAPI_KEY:
        return {"engine": "serpapi", "count": 0, "top_urls": [], "raw": None, "note": "no_key"}
    import requests
    url = "https://serpapi.com/search.json"
    params = {"q": query, "api_key": SERPAPI_KEY, "num": 10}
    try:
        r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        js = r.json()
        count = 0
        try:
            count = int(js.get("search_information", {}).get("total_results", 0))
        except:
            count = 0
        top_urls = []
        for i in js.get("organic_results", [])[:10]:
            u = i.get("link") or i.get("url")
            if u:
                top_urls.append(u)
        return {"engine": "serpapi", "count": count, "top_urls": top_urls, "raw": js}
    except Exception as e:
        logger.warning(f"SerpAPI error for q={query}: {e}")
        return {"engine": "serpapi", "count": 0, "top_urls": [], "raw": None}

async def search_bing_api(query: str):
    """Use Bing Web Search API if key present."""
    if not BING_API_KEY:
        return {"engine": "bing_api", "count": 0, "top_urls": [], "raw": None, "note": "no_key"}
    import requests
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 10}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
        js = r.json()
        count = js.get("webPages", {}).get("totalEstimatedMatches", 0) or 0
        top_urls = []
        for v in js.get("webPages", {}).get("value", [])[:10]:
            top_urls.append(v.get("url"))
        return {"engine": "bing_api", "count": int(count), "top_urls": top_urls, "raw": js}
    except Exception as e:
        logger.warning(f"Bing API error for q={query}: {e}")
        return {"engine": "bing_api", "count": 0, "top_urls": [], "raw": None}

# ---------------------------
# Orchestrator for queries
# ---------------------------

async def run_query_all_engines(session: aiohttp.ClientSession, query: str):
    """
    Run same query across multiple engines in parallel and collect responses.
    Engines: serpapi (if key), bing api (if key), duckduckgo (scrape), brave (scrape)
    """
    tasks = []
    # SerpAPI (sync wrapper)
    tasks.append(asyncio.get_event_loop().run_in_executor(None, asyncio.run, search_serpapi(query)))
    # Bing API (sync wrapper)
    tasks.append(asyncio.get_event_loop().run_in_executor(None, asyncio.run, search_bing_api(query)))
    # DuckDuckGo (async)
    tasks.append(search_duckduckgo(session, query))
    # Brave (async)
    tasks.append(search_brave(session, query))

    # Execute concurrently
    results = []
    # Using gather: but previous two tasks are coroutines or futures; handle safely
    try:
        res = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        logger.warning(f"gather error: {e}")
        res = []
    # Normalize results: some tasks might have returned exception objects
    for r in res:
        if isinstance(r, Exception):
            logger.warning(f"engine task exception: {r}")
            continue
        # r might be a dict already
        if isinstance(r, dict):
            results.append(r)
        else:
            # Unknown type: skip
            continue
    return results

# ---------------------------
# High-level orchestration for a list of dorks
# ---------------------------

async def process_dorks_parallel(dorks_list, concurrency=MAX_CONCURRENT_TASKS):
    """
    dorks_list: list of strings (queries)
    Returns dict: { query: {engine: result_dict, ...}, ... }
    """
    connector = aiohttp.TCPConnector(limit_per_host=4)
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT + 5)
    sem = asyncio.Semaphore(concurrency)
    results = {}

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        async def worker(q):
            async with sem:
                headers = {"User-Agent": random.choice(USER_AGENTS)}
                # small randomized sleep to avoid bursts
                await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                # run queries across engines
                res = await run_query_all_engines(session, q)
                # Save evidence (raw html where available)
                uid = uid_for_query(q)
                saved = []
                top_urls = {}
                for r in res:
                    engine = r.get("engine", "unknown")
                    raw = r.get("raw")
                    if raw:
                        try:
                            fn = safe_filename(f"{uid}_{engine}.html")
                            path = os.path.join(HTML_SNAPSHOT_DIR, fn)
                            # if raw is dict (JSON), dump prettified json
                            if isinstance(raw, dict):
                                async with aiofiles.open(path, "w", encoding="utf-8") as f:
                                    await f.write(json.dumps(raw, ensure_ascii=False, indent=2))
                            else:
                                async with aiofiles.open(path, "w", encoding="utf-8") as f:
                                    await f.write(raw)
                            saved.append(path)
                        except Exception as e:
                            logger.debug(f"save html error: {e}")
                    # collect top urls
                    top_urls[engine] = r.get("top_urls", [])[:10]
                # Also write top urls to file
                try:
                    top_fn = safe_filename(f"{uid}_topurls.json")
                    top_path = os.path.join(TOP_URLS_DIR, top_fn)
                    async with aiofiles.open(top_path, "w", encoding="utf-8") as f:
                        await f.write(json.dumps(top_urls, ensure_ascii=False, indent=2))
                except Exception as e:
                    logger.debug(f"save top urls error: {e}")

                # Count summary per engine
                summary = {r.get("engine", "unknown"): r.get("count", 0) for r in res}
                return q, {"summary": summary, "engines": {r.get("engine", "unknown"): r for r in res}, "saved_html": saved, "top_urls_file": top_path}

        # schedule tasks
        tasks = [worker(q) for q in dorks_list]
        for coro in asyncio.as_completed(tasks):
            try:
                q, out = await coro
                results[q] = out
                # log brief
                logger.info(Fore.CYAN + f"[+] Query done: {q} -> {out['summary']}")
            except Exception as e:
                logger.warning(f"worker error: {e}")
    return results

# ---------------------------
# History & variation tracking
# ---------------------------

def get_history_filepath(target_label: str):
    fn = safe_filename(f"history_{target_label}.json")
    return os.path.join(HISTORY_DIR, fn)

def load_previous_history(target_label: str):
    path = get_history_filepath(target_label)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_history(target_label: str, payload: dict):
    path = get_history_filepath(target_label)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def compute_differences(prev: dict, current: dict):
    """
    prev/current: dict mapping query -> summary(engine->count)
    Return mapping query -> {engine: (prev, current, diff, pct_change)}
    """
    diffs = {}
    for q, curr in current.items():
        prev_entry = prev.get(q, {})
        curr_summary = curr.get("summary", {})
        diffs[q] = {}
        for engine, curr_count in curr_summary.items():
            prev_count = prev_entry.get("summary", {}).get(engine, 0) if isinstance(prev_entry, dict) else 0
            diff = curr_count - prev_count
            pct = None
            try:
                pct = (diff / prev_count * 100) if prev_count else None
            except:
                pct = None
            diffs[q][engine] = {"prev": prev_count, "curr": curr_count, "diff": diff, "pct": pct}
    return diffs

# ---------------------------
# Report generator (Markdown)
# ---------------------------

def generate_markdown_report(target_label: str, dorks_results: dict, diffs: dict, metadata: dict):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%SZ")
    report_name = safe_filename(f"report_{target_label}_{timestamp}.md")
    report_path = os.path.join(REPORTS_DIR, report_name)

    lines = []
    lines.append(f"# OSINT AUTO-REPORT: {target_label}")
    lines.append(f"Generated: {timestamp} UTC")
    lines.append("")
    lines.append("## Metadata")
    for k, v in metadata.items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    lines.append("## Summary table (per query and engine)")
    for q, res in dorks_results.items():
        lines.append(f"### Query: `{q}`")
        lines.append("")
        lines.append("| Engine | Count | Prev | Diff | % change |")
        lines.append("|---|---:|---:|---:|---:|")
        engines = res.get("summary", {})
        for eng, cnt in engines.items():
            prev = diffs.get(q, {}).get(eng, {}).get("prev", "")
            diff = diffs.get(q, {}).get(eng, {}).get("diff", "")
            pct = diffs.get(q, {}).get(eng, {}).get("pct", None)
            pct_str = f"{pct:.1f}%" if isinstance(pct, (int, float)) else ""
            lines.append(f"| {eng} | {cnt} | {prev} | {diff} | {pct_str} |")
        lines.append("")
        # Top URLs
        topurls_file = res.get("top_urls_file")
        if topurls_file and os.path.exists(topurls_file):
            try:
                with open(topurls_file, "r", encoding="utf-8") as f:
                    topjson = json.load(f)
                lines.append("Top URLs by engine:")
                for eng, urls in topjson.items():
                    lines.append(f"- **{eng}**:")
                    for u in urls[:5]:
                        lines.append(f"  - {u}")
                lines.append("")
            except Exception:
                pass
    # Write file
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return report_path

# ---------------------------
# CLI + Integration
# ---------------------------

def print_banner():
    print(Fore.GREEN + "=" * 40)
    print(Fore.GREEN + "AUTO-OSINT DORK GENERATOR - AUTO MODE")
    print(Fore.GREEN + "=" * 40)

def mostrar_menu():
    print(Fore.CYAN + "\n=== MENÚ PRINCIPAL ===")
    print(Fore.YELLOW + "1." + Fore.WHITE + " Correos electrónicos")
    print(Fore.YELLOW + "2." + Fore.WHITE + " Usernames / aliases")
    print(Fore.YELLOW + "3." + Fore.WHITE + " Dominios")
    print(Fore.YELLOW + "4." + Fore.WHITE + " Subdominios")
    print(Fore.YELLOW + "5." + Fore.WHITE + " Salir")
    return input(Fore.GREEN + "\nElige una opción: ")

def export_dorks_to_txt(nome, dorks):
    archivo = f"dorks_{nome.replace('@','_').replace('.', '_')}.txt"
    with open(archivo, "w", encoding="utf-8") as f:
        f.write(f"GOOGLE DORKS PARA: {nome}\n")
        f.write("=" * 60 + "\n\n")
        for cat, contenido in dorks.items():
            f.write(f"### {cat} ###\n")
            for d in contenido:
                f.write(f"{d}\n")
            f.write("\n")
    print(Fore.GREEN + f"\n✔ Archivo exportado como: {archivo}\n")
    return archivo

def flatten_dorks_dict(dorks_dict):
    # returns list of strings (queries)
    L = []
    for cat, lista in dorks_dict.items():
        L.extend(lista)
    return L

# ---------------------------
# Main
# ---------------------------

def main():
    print_banner()
    while True:
        opcion = mostrar_menu()
        if opcion == "1":
            objetivo = input("Introduce el correo: ").strip()
            dorks = dorks_email(objetivo)
            target_label = f"email_{objetivo}"
        elif opcion == "2":
            objetivo = input("Introduce el username: ").strip()
            dorks = dorks_usuario(objetivo)
            target_label = f"user_{objetivo}"
        elif opcion == "3":
            objetivo = input("Introduce el dominio (ej: acme.com): ").strip()
            dorks = dorks_dominio(objetivo)
            target_label = f"domain_{objetivo}"
        elif opcion == "4":
            objetivo = input("Introduce el subdominio (ej: dev.acme.com): ").strip()
            dorks = dorks_subdominio(objetivo)
            target_label = f"sub_{objetivo}"
        elif opcion == "5":
            print(Fore.RED + "Saliendo...")
            break
        else:
            print(Fore.RED + "Opción inválida.")
            continue

        # Show and optionally export dorks
        print(Fore.CYAN + "\n=== RESULTADOS (DORKS GENERADOS) ===\n")
        for cat, lista in dorks.items():
            print(Fore.YELLOW + f"\n--- {cat} ---")
            for d in lista:
                print(Fore.WHITE + d)

        if input(Fore.GREEN + "\n¿Quieres exportar los dorks a un .txt? (s/n): ").lower() == "s":
            export_dorks_to_txt(objetivo, dorks)

        # Flatten queries
        queries = flatten_dorks_dict(dorks)

        # Confirm run
        if input(Fore.MAGENTA + "\nRun automatic multi-engine search for all dorks now? (y/n): ").lower() != "y":
            print(Fore.YELLOW + "Aborting auto search for now.")
            continue

        metadata = {
            "target": objetivo,
            "target_label": target_label,
            "generated_at": now_iso(),
            "engines_used": ["serpapi" if SERPAPI_KEY else None, "bing_api" if BING_API_KEY else None, "duckduckgo", "brave"]
        }

        # Load previous history
        prev_history = load_previous_history(target_label)

        # Run async search
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(process_dorks_parallel(queries, concurrency=MAX_CONCURRENT_TASKS))

        # Save current history (minimal summary)
        summary_for_history = {}
        for q, out in results.items():
            summary_for_history[q] = {"summary": out.get("summary", {}), "ts": now_iso()}

        # Compute diffs
        diffs = compute_differences(prev_history, summary_for_history)

        # Save history
        save_history(target_label, summary_for_history)

        # Generate report
        report_path = generate_markdown_report(target_label, results, diffs, metadata)

        print(Fore.GREEN + f"\n✔ Auto-search done. Report generated: {report_path}")
        print(Fore.GREEN + f"✔ Evidence (HTML) and top URLs saved under folder: {EVIDENCE_DIR}")
        print(Fore.CYAN + "You can inspect the history folder for previous runs.")

if __name__ == "__main__":
    main()
