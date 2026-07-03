#!/usr/bin/env python3
"""Export the Letterboxd watchlist to watchlist.json for the static site."""

import json
import os
from datetime import datetime, timezone

from find import USERNAME, fetch_all_films

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, "watchlist.json")


def main():
    films = fetch_all_films(verbose=True)
    if not films:
        raise SystemExit("Fetched 0 films — refusing to overwrite watchlist.json.")

    data = {
        "username": USERNAME,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(films),
        "films": [{"name": f["name"], "slug": f["slug"]} for f in films],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {len(films)} films to {OUT}")


if __name__ == "__main__":
    main()
