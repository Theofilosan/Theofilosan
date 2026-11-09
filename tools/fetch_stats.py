#!/usr/bin/env python3
"""Fetch the public GitHub numbers shown on the profile card.

Writes cache/stats.json. Uses GITHUB_TOKEN when present (rate limits and
the commits graph); without it, everything except the commits count still
works, since the REST endpoints used here are public.
"""
import json
import os
import pathlib
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
USER = "Theofilosan"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def get(url, headers=None):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "profile-card")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read())


def fetch_contributions():
    """Public contribution counts over the last year. Needs a token."""
    if not TOKEN:
        return {}
    query = (
        "{ user(login: \"%s\") { contributionsCollection { "
        "totalCommitContributions "
        "contributionCalendar { totalContributions } } } }" % USER
    )
    req = urllib.request.Request("https://api.github.com/graphql")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("User-Agent", "profile-card")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, json.dumps({"query": query}).encode(), timeout=30) as res:
            data = json.loads(res.read())
        coll = data["data"]["user"]["contributionsCollection"]
        return {
            "commits_year": coll["totalCommitContributions"],
            "contributions_year": coll["contributionCalendar"]["totalContributions"],
        }
    except Exception as exc:  # token missing scope, rate limit, network...
        print(f"graphql contributions lookup skipped: {exc}", file=sys.stderr)
        return {}


def main():
    user = get(f"https://api.github.com/users/{USER}")
    stats = {
        "fetched_at": time.strftime("%Y-%m-%d"),
        "repos": user["public_repos"],
    }
    stats.update(fetch_contributions())
    out = ROOT / "cache" / "stats.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
