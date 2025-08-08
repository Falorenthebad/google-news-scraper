import sys
import time
import urllib.parse
from typing import List, Dict, Optional
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://news.google.com"
SEARCH_TEMPLATE = (
    "https://news.google.com/search?q={query}&hl=en-US&gl=US&ceid=US%3Aen"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

def build_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"])
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update(HEADERS)
    return s

def build_search_url(query: str) -> str:
    q = urllib.parse.quote_plus(query.strip())
    return SEARCH_TEMPLATE.format(query=q)

def absolute_url(href: str) -> str:
    return urllib.parse.urljoin(BASE, href)

def fetch_html(session: requests.Session, url: str, timeout: float = 10.0) -> str:
    r = session.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text

def format_datetime_abs(dt_iso: Optional[str]) -> Optional[str]:
    if not dt_iso:
        return None
    try:
        if dt_iso.endswith("Z"):
            dt = datetime.fromisoformat(dt_iso.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(dt_iso)
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.strftime("%d %B %Y %H:%M:%S UTC")
    except Exception:
        return dt_iso

def clean_title(raw_title: str) -> str:
    if " - " in raw_title:
        return raw_title.split(" - ")[0].strip()
    return raw_title.strip()

def parse_results(html: str, limit: Optional[int] = None) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    items = []

    for art in soup.find_all("article"):
        a = art.find("a", href=True)
        if not a:
            continue

        href = a.get("href", "")
        raw_title = (a.get_text(" ", strip=True) or "").strip()
        if not raw_title:
            title_node = art.find("a", attrs={"aria-label": True})
            if title_node:
                raw_title = (title_node.get("aria-label") or "").strip()
        if not raw_title:
            continue

        title = clean_title(raw_title)
        url = absolute_url(href)

        publisher = None
        pub_div = art.select_one(".vr1PYe")
        if pub_div:
            publisher = pub_div.get_text(" ", strip=True) or None
        if not publisher:
            maybe_pub = art.find(attrs={"data-n-tid": True})
            if maybe_pub:
                txt = maybe_pub.get_text(" ", strip=True)
                publisher = txt if txt else None

        dt_iso = None
        time_el = art.find("time")
        if time_el:
            dt_iso = time_el.get("datetime")

        items.append({
            "title": title,
            "url": url,
            "publisher": publisher,
            "datetime_iso": dt_iso,
        })

        if limit is not None and len(items) >= limit:
            break

    return items

def prompt_user() -> Dict:
    try:
        query = input("Search term: ").strip()
        if not query:
            print("Search term cannot be empty.")
            sys.exit(1)
        raw_n = input("How many results? (press Enter for 5, max 100): ").strip()
        limit = int(raw_n) if raw_n else 5
        if limit > 100:
            limit = 100
        return {"query": query, "limit": limit}
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"Invalid input: {e}")
        sys.exit(1)

def main():
    user = prompt_user()
    session = build_session()

    search_url = build_search_url(user["query"])
    print(f"\nGoogle News search: {search_url}\n")

    try:
        html = fetch_html(session, search_url)
    except requests.HTTPError as e:
        print(f"HTTP error: {e}")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)

    time.sleep(0.8)

    results = parse_results(html, limit=user["limit"])

    if not results:
        print("No results found or page structure may have changed.")
        sys.exit(0)

    for i, item in enumerate(results, 1):
        print(f"{i}. {item['title']}")
        if item.get("publisher"):
            print(f"   Source    : {item['publisher']}")
        abs_dt = format_datetime_abs(item.get("datetime_iso"))
        if abs_dt:
            print(f"   Published : {abs_dt}")
        print(f"   Link      : {item['url']}")
        print("-" * 80)

if __name__ == "__main__":
    main()
