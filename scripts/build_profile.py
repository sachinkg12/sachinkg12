#!/usr/bin/env python3
"""Regenerate assets/live.svg from the GitHub public API.

Pulls live signals for the profile owner (public repo count, total stars and
forks across non-fork repos, followers, and the latest HeapLens release) and
renders them into a self-contained SVG telemetry panel.

Standard library only -- no pip install needed in CI. Set GITHUB_TOKEN in the
environment to raise the API rate limit (the GitHub Actions runner provides one
automatically); it also works unauthenticated for local runs.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

USER = "sachinkg12"
RELEASE_REPO = "heaplens"          # repo whose latest release we surface
OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "live.svg",
)
API = "https://api.github.com"


def api_get(path):
    """GET an API path, returning parsed JSON (or None on 404)."""
    req = urllib.request.Request(API + path)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", f"{USER}-profile-builder")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def collect():
    user = api_get(f"/users/{USER}")
    if not user:
        raise SystemExit(f"could not fetch user {USER}")

    stars = forks = 0
    page = 1
    while True:
        repos = api_get(f"/users/{USER}/repos?per_page=100&page={page}&type=owner")
        if not repos:
            break
        for r in repos:
            if r.get("fork"):
                continue
            stars += r.get("stargazers_count", 0)
            forks += r.get("forks_count", 0)
        if len(repos) < 100:
            break
        page += 1

    rel = api_get(f"/repos/{USER}/{RELEASE_REPO}/releases/latest")
    release = rel.get("tag_name", "—") if rel else "—"

    return {
        "repos": user.get("public_repos", 0),
        "stars": stars,
        "forks": forks,
        "followers": user.get("followers", 0),
        "release": release,
    }


# --- SVG template -----------------------------------------------------------
# Placeholders are «TOKENS» so nothing collides with SVG/XML syntax.
TEMPLATE = r"""<svg width="1200" height="200" viewBox="0 0 1200 200" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Live open source telemetry">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1200" y2="200" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#08121f"/><stop offset="1" stop-color="#0a1a30"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#63e6ff"/><stop offset="0.5" stop-color="#82f1c3"/><stop offset="1" stop-color="#b894ff"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="1198" height="198" rx="20" fill="url(#bg)" stroke="#1d3a5f"/>

  <circle cx="64" cy="42" r="5" fill="#4ade80">
    <animate attributeName="fill-opacity" values="1;0.3;1" dur="2.2s" repeatCount="indefinite"/>
  </circle>
  <text x="80" y="47" font-family="'SFMono-Regular',ui-monospace,Consolas,Menlo,monospace" font-size="13" letter-spacing="2" fill="#c7d6ea">LIVE OPEN SOURCE TELEMETRY</text>
  <text x="1160" y="47" text-anchor="end" font-family="'SFMono-Regular',ui-monospace,Consolas,Menlo,monospace" font-size="12" fill="#55719a">updated «DATE» UTC</text>

  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
    «TILES»
  </g>
</svg>
"""

TILE = r"""<g>
      <rect x="«X»" y="78" width="«W»" height="98" rx="14" fill="#0c1a2e" stroke="#25456d"/>
      <rect x="«X»" y="78" width="«W»" height="4" rx="2" fill="«C»"/>
      <text x="«TX»" y="132" text-anchor="middle" font-size="«FS»" font-weight="700" fill="«C»">«V»</text>
      <text x="«TX»" y="160" text-anchor="middle" font-family="'SFMono-Regular',ui-monospace,Consolas,Menlo,monospace" font-size="12" fill="#8ba3c2">«L»</text>
    </g>"""


def render(data):
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    tiles_spec = [
        (str(data["repos"]), "public repos", "#63e6ff"),
        (str(data["stars"]), "total stars",  "#82f1c3"),
    ]
    # center N tiles across the 1200px panel; widen tiles when there are few
    n = len(tiles_spec)
    gap = 24
    tile_w = {1: 460, 2: 430, 3: 330}.get(n, 250)
    wide = tile_w >= 380
    start_x = (1200 - (n * tile_w + (n - 1) * gap)) // 2
    tiles = []
    for i, (value, label, color) in enumerate(tiles_spec):
        x = start_x + i * (tile_w + gap)
        tx = x + tile_w // 2
        # bigger number on wide tiles; shrink for longer strings (e.g. v1.0.21)
        if len(value) <= 5:
            fs = "44" if wide else "34"
        elif len(value) <= 7:
            fs = "36" if wide else "30"
        else:
            fs = "28" if wide else "24"
        tile = (TILE
                .replace("«X»", str(x))
                .replace("«W»", str(tile_w))
                .replace("«TX»", str(tx))
                .replace("«FS»", fs)
                .replace("«C»", color)
                .replace("«V»", value)
                .replace("«L»", label))
        tiles.append(tile)
    return (TEMPLATE
            .replace("«DATE»", date)
            .replace("«TILES»", "\n    ".join(tiles)))


def main():
    data = collect()
    svg = render(data)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH}: {data}", file=sys.stderr)


if __name__ == "__main__":
    main()
