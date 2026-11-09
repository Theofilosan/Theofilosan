#!/usr/bin/env python3
"""Render pacman_dark.svg / pacman_light.svg: an arcade critter eating the
year's contribution graph, serpentine, with two ghosts in tow.

Contribution data comes from the public contributions page
(github.com/users/<name>/contributions) - no token needed. Pure stdlib.
"""
import datetime as dt
import html
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
USER = "Theofilosan"

DUR = 30.0          # seconds per loop
CELL, GAP = 10, 3
STEP = CELL + GAP
COLS, ROWS = 53, 7
PAD = 14
TOP = 34            # room for the title line

THEMES = {
    "dark": {
        "bg": "#101521", "border": "#30394c", "text": "#aab9be",
        "levels": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
        "pac": "#f5d90a", "ghost1": "#ed91d6", "ghost2": "#79d6f0",
    },
    "light": {
        "bg": "#f6f8fa", "border": "#d0d7de", "text": "#57606a",
        "levels": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
        "pac": "#d4a017", "ghost1": "#b0449b", "ghost2": "#0a6f8f",
    },
}


def fetch_days():
    url = f"https://github.com/users/{USER}/contributions"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "profile-card")
    with urllib.request.urlopen(req, timeout=30) as res:
        page = res.read().decode()
    days = []
    for tag in re.findall(r"<td[^>]+ContributionCalendar-day[^>]*>", page):
        date = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        level = re.search(r'data-level="(\d)"', tag)
        if date and level:
            days.append((dt.date.fromisoformat(date.group(1)), int(level.group(1))))
    if not days:
        raise SystemExit("no contribution cells found - page format changed?")
    days.sort()
    return days


def grid(days):
    """Map each day to (col, row); column 0 starts on the first Sunday."""
    first = days[0][0]
    sunday = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    out = []
    for date, level in days:
        col = (date - sunday).days // 7
        row = (date.weekday() + 1) % 7
        if col < COLS:
            out.append((col, row, level))
    return out


def serpentine():
    """Waypoints through every cell center, row by row, alternating direction."""
    pts = []
    for row in range(ROWS):
        cols = range(COLS) if row % 2 == 0 else range(COLS - 1, -1, -1)
        for col in cols:
            pts.append((PAD + col * STEP + CELL // 2, TOP + row * STEP + CELL // 2))
    return pts


def arrival_times(pts):
    """Fraction of the loop at which the critter reaches each waypoint."""
    dist = [0.0]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        dist.append(dist[-1] + abs(x2 - x1) + abs(y2 - y1))
    total = dist[-1]
    return [d / total for d in dist]


def pacman(color, bg):
    mouth_open = "M0,0 L16,-9 L16,9 Z"
    mouth_shut = "M0,0 L16,-1.5 L16,1.5 Z"
    return (
        f'<g><circle r="9" fill="{color}"/>'
        f'<path d="{mouth_open}" fill="{bg}">'
        f'<animate attributeName="d" values="{mouth_open};{mouth_shut};{mouth_open}" '
        f'dur="0.28s" repeatCount="indefinite"/></path>'
        f'<animateMotion dur="{DUR}s" repeatCount="indefinite" rotate="auto"><mpath href="#route"/></animateMotion>'
        f'</g>'
    )


def ghost(color, delay):
    skirt = "".join(f'<rect x="{x}" y="3" width="3" height="4" fill="{color}"/>'
                    for x in (-8, -2, 4))
    return (
        f'<g><rect x="-8" y="-4" width="16" height="8" rx="8" fill="{color}"/>'
        f'<rect x="-8" y="-1" width="16" height="5" fill="{color}"/>{skirt}'
        f'<circle cx="-3" cy="-2" r="2" fill="#fff"/><circle cx="4" cy="-2" r="2" fill="#fff"/>'
        f'<animateMotion dur="{DUR}s" begin="{delay}s" repeatCount="indefinite" rotate="auto">'
        f'<mpath href="#route"/></animateMotion></g>'
    )


def render(theme_name):
    t = THEMES[theme_name]
    days = fetch_days()
    cells = grid(days)
    total = sum(1 for _, _, lv in cells if lv > 0)
    pts = serpentine()
    times = arrival_times(pts)

    # waypoint lookup for arrival times at each contributing cell
    at = {}
    idx = 0
    for row in range(ROWS):
        cols = range(COLS) if row % 2 == 0 else range(COLS - 1, -1, -1)
        for col in cols:
            at[(col, row)] = times[idx]
            idx += 1

    path_d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    width = PAD * 2 + COLS * STEP - GAP
    height = TOP + ROWS * STEP - GAP + PAD

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'font-family="\'IBM Plex Mono\',Consolas,Menlo,monospace" role="img" '
        f'aria-label="Pac-Man eating {total} contributions from the last year">',
        f'<rect width="{width}" height="{height}" fill="{t["bg"]}" rx="14" stroke="{t["border"]}"/>',
        f'<text x="{PAD}" y="22" font-size="12" fill="{t["text"]}">'
        f'{total} contributions in the last year - chomp chomp</text>',
        f'<path id="route" d="{path_d}" fill="none"/>',
    ]
    for col, row, level in cells:
        x, y = PAD + col * STEP, TOP + row * STEP
        color = t["levels"][level]
        if level > 0:
            start = at[(col, row)]
            out.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}">'
                f'<animate attributeName="opacity" values="1;0" keyTimes="0;{start:.5f}" '
                f'calcMode="discrete" dur="{DUR}s" repeatCount="indefinite"/></rect>'
            )
        else:
            out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
    out.append(pacman(t["pac"], t["bg"]))
    out.append(ghost(t["ghost1"], "-0.55"))
    out.append(ghost(t["ghost2"], "-1.05"))
    out.append("</svg>")
    return "\n".join(out) + "\n"


for name in THEMES:
    svg = render(name)
    (ROOT / f"pacman_{name}.svg").write_text(svg)
    print(f"wrote pacman_{name}.svg ({len(svg)} bytes)")
