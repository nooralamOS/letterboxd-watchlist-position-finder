# Letterboxd Watchlist Position Finder

Find where a film sits in a Letterboxd watchlist — by number, not by scrolling.

**Live site:** https://nooralamos.github.io/letterboxd-watchlist-position-finder/

The site is fully static (GitHub Pages): search runs in the browser against
[watchlist.json](watchlist.json), a snapshot of the watchlist that a
[GitHub Action](.github/workflows/update-watchlist.yml) re-scrapes daily.

## What's here

- **[find.py](find.py)** — CLI tool. Scrapes every page of the watchlist in parallel and prints the position of the film you searched for.

  ```sh
  python3 find.py "The Green Knight"
  ```

- **[index.html](index.html)** — the web UI. Loads `watchlist.json` and searches it client-side, so it works on any static host. Serve locally with `python3 -m http.server`.

- **[export_watchlist.py](export_watchlist.py)** — scrapes the watchlist and writes `watchlist.json`. Run by the daily GitHub Action; run it manually to refresh immediately.

- **[server.py](server.py)** — (legacy/local) HTTP server that scrapes live and serves a search API at `http://localhost:8080`. Not used by the hosted site.

- **[horror.html](horror.html)** — standalone page showing curated horror picks from the watchlist as a poster grid (posters via the TMDB API — paste your own [TMDB API key](https://www.themoviedb.org/settings/api) when prompted; it's kept in `localStorage`).

## Notes

- The watchlist username is set at the top of `find.py` (`USERNAME`).
- No dependencies beyond the Python 3 standard library.
