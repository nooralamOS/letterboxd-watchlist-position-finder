# Letterboxd Watchlist Position Finder

Find where a film sits in a Letterboxd watchlist — by number, not by scrolling.

## What's here

- **[find.py](find.py)** — CLI tool. Scrapes every page of the watchlist in parallel and prints the position of the film you searched for.

  ```sh
  python3 find.py "The Green Knight"
  ```

- **[server.py](server.py)** — small HTTP server that caches the watchlist in memory and serves a web UI at `http://localhost:8080`, with a JSON search API at `/api/search?q=...`.

  ```sh
  python3 server.py
  ```

- **[index.html](index.html)** — the web UI served by `server.py`.

- **[horror.html](horror.html)** — standalone page showing curated horror picks from the watchlist as a poster grid (posters via the TMDB API — paste your own [TMDB API key](https://www.themoviedb.org/settings/api) when prompted; it's kept in `localStorage`).

## Notes

- The watchlist username is set at the top of `find.py` (`USERNAME`).
- No dependencies beyond the Python 3 standard library.
