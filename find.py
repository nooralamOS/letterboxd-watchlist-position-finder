#!/usr/bin/env python3
"""Find the position of a film in alazraq's Letterboxd watchlist."""

import concurrent.futures
import math
import re
import sys
import urllib.request
from html.parser import HTMLParser

USERNAME = "alazraq"
BASE_URL = f"https://letterboxd.com/{USERNAME}/watchlist"
FILMS_PER_PAGE = 28
MAX_WORKERS = 12


class WatchlistParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.films = []

    def handle_starttag(self, tag, attrs):
        if tag != "div":
            return
        attrs = dict(attrs)
        slug = attrs.get("data-item-slug")
        name = attrs.get("data-item-name")
        if slug and name:
            self.films.append({"name": name, "slug": slug})


def fetch_html(page: int) -> str:
    url = BASE_URL + "/" if page == 1 else f"{BASE_URL}/page/{page}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def parse_films(html: str) -> list[dict]:
    parser = WatchlistParser()
    parser.feed(html)
    return parser.films


def get_num_pages(html: str) -> int:
    m = re.search(r'js-watchlist-count">([\d,]+)&nbsp;films', html)
    if m:
        total = int(m.group(1).replace(",", ""))
        return math.ceil(total / FILMS_PER_PAGE)
    return 30  # safe fallback


def fetch_all_films(verbose: bool = True) -> list[dict]:
    """Fetch every watchlist page in parallel and return films in order."""
    html1 = fetch_html(1)
    num_pages = get_num_pages(html1)

    page_films: dict[int, list[dict]] = {1: parse_films(html1)}

    if verbose:
        print(f"Fetching {num_pages} pages in parallel", end="", flush=True)

    if num_pages > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            future_to_page = {ex.submit(fetch_html, p): p for p in range(2, num_pages + 1)}
            for future in concurrent.futures.as_completed(future_to_page):
                p = future_to_page[future]
                page_films[p] = parse_films(future.result())
                if verbose:
                    print(".", end="", flush=True)

    if verbose:
        print()

    all_films = []
    for p in range(1, num_pages + 1):
        all_films.extend(page_films.get(p, []))
    return all_films


def strip_year(name: str) -> str:
    return re.sub(r"\s*\(\d{4}\)\s*$", "", name).strip()


def score(film: dict, q: str) -> int:
    """Return match score: 3=exact name, 2=exact slug, 1=substring, 0=no match."""
    name_bare = strip_year(film["name"]).lower()
    name_full = film["name"].lower()
    slug = film["slug"].lower()
    q = q.lower().strip()
    if q == name_bare or q == name_full:
        return 3
    if q == slug or q == slug.replace("-", " "):
        return 2
    if q in name_bare or q in name_full:
        return 1
    return 0


def search(query: str, verbose: bool = True) -> list[tuple[int, dict, int]]:
    """Return (position, film, score) for all matches, sorted by score desc."""
    all_films = fetch_all_films(verbose=verbose)
    results = []
    for i, film in enumerate(all_films, 1):
        s = score(film, query)
        if s > 0:
            results.append((i, film, s))
    return sorted(results, key=lambda x: -x[2])


def main():
    query = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else ""
    if not query:
        query = input("Film name: ").strip()
    if not query:
        sys.exit("No film name provided.")

    results = search(query)

    if not results:
        print(f'\nNo match for "{query}" in watchlist.')
        return

    best_score = results[0][2]
    shown = [r for r in results if r[2] == best_score] if best_score >= 2 else results

    if len(shown) == 1:
        pos, film, _ = shown[0]
        print(f'\n"{strip_year(film["name"])}" is #\033[1m{pos}\033[0m in your watchlist.')
    else:
        print(f'\nFound {len(shown)} matches:')
        for pos, film, _ in shown:
            print(f'  #{pos:>4}  {film["name"]}')


if __name__ == "__main__":
    main()
