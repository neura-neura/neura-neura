import json
import os
import urllib.request
from pathlib import Path

USER = "neura-neura"
EXCLUDE = {"neura-neura", "blog", "blog-public"}
README = Path(__file__).resolve().parent.parent / "README.md"


def fetch_repos():
    repos = []
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "neura-profile-readme"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for page in (1, 2):
        url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed&page={page}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            batch = json.load(resp)
        if not batch:
            break
        repos += batch
    seen = {}
    for r in repos:
        if not r.get("fork") and r["name"] not in EXCLUDE:
            seen[r["name"]] = r
    return list(seen.values())


def line(r):
    stars = r.get("stargazers_count", 0)
    lang = r.get("language") or ""
    desc = (r.get("description") or "").strip()
    parts = f"[{r['name']}] (https://github.com/{USER}/{r['name']})"
    if stars:
        parts += f" — {stars} stars"
    if lang:
        parts += f" · {lang}"
    if desc:
        parts += f" · {desc}"
    return f"- {parts}"


def replace_section(text, marker, lines):
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    i, j = text.index(start), text.index(end)
    return text[: i + len(start)] + "\n" + "\n".join(lines) + "\n" + text[j:]


def main():
    repos = fetch_repos()
    popular = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:4]
    recent = sorted(repos, key=lambda r: r.get("pushed_at", ""), reverse=True)[:4]
    text = README.read_text()
    text = replace_section(text, "POPULAR-REPOS", [line(r) for r in popular])
    text = replace_section(text, "RECENT-REPOS", [line(r) for r in recent])
    README.write_text(text)
    print("Updated popular:", [r["name"] for r in popular])
    print("Updated recent:", [r["name"] for r in recent])


if __name__ == "__main__":
    main()
