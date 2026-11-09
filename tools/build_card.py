#!/usr/bin/env python3
"""Render dark_mode.svg and light_mode.svg: the neofetch-style card.

Layout: ascii art on the left, dotted-leader fields on the right, live
stats from cache/stats.json, and a blinking prompt cursor at the bottom.
Run fetch_stats.py first. Pure stdlib, deterministic output.
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = (ROOT / "assets" / "ascii-art.txt").read_text().splitlines()
STATS = json.loads((ROOT / "cache" / "stats.json").read_text())

FONT = 13
LINE = 17
CHAR = 7.8  # advance of one monospace cell at FONT px
PAD = 24
ART_W = 340  # right column starts after this
VALUE_X = 610  # where field values begin

IDENTITY = [
    ("Role", "Platform & Cloud Engineer"),
    ("Host", "Copenhagen, Denmark"),
    ("OS", "Linux Mint + Windows"),
    ("Langs", "Python, SQL, TypeScript"),
    ("Data", "dbt, DuckDB, Airflow, Databricks"),
    ("Cloud", "Azure, AWS, Terraform"),
    ("CI/CD", "GitHub Actions"),
    ("Hobbies", "FPL, DnD, LEGO"),
]
CONTACT = [
    ("Email", "theofilosan@gmail.com"),
    ("LinkedIn", "theophilos-anastasiadis"),
    ("Portfolio", "theofilosan.github.io"),
]

THEMES = {
    "dark": {
        "bg": "#101521", "border": "#30394c", "text": "#edf4eb",
        "muted": "#aab9be", "key": "#ed91d6", "value": "#79d6f0",
        "head": "#8df3c0", "dots": "#44546f", "cursor": "#8df3c0",
        "art": ["#8df3c0", "#8df3c0", "#79d6f0", "#79d6f0", "#ed91d6",
                "#ed91d6", "#79d6f0", "#79d6f0", "#8df3c0", "#8df3c0",
                "#ed91d6", "#ed91d6", "#79d6f0", "#aab9be", "#8df3c0"],
    },
    "light": {
        "bg": "#f6f8fa", "border": "#d0d7de", "text": "#1f2328",
        "muted": "#57606a", "key": "#b0449b", "value": "#0a6f8f",
        "head": "#1a7f37", "dots": "#9aa7b4", "cursor": "#1a7f37",
        "art": ["#1a7f37", "#1a7f37", "#0a6f8f", "#0a6f8f", "#b0449b",
                "#b0449b", "#0a6f8f", "#0a6f8f", "#1a7f37", "#1a7f37",
                "#b0449b", "#b0449b", "#0a6f8f", "#57606a", "#1a7f37"],
    },
}


def esc(text):
    return html.escape(str(text), quote=True)


def stat_rows():
    left = [("Repos", STATS["repos"])]
    right = []
    if STATS.get("commits_year") is not None:
        left.append(("Commits 1y", STATS["commits_year"]))
    if STATS.get("contributions_year") is not None:
        right.append(("Contribs 1y", STATS["contributions_year"]))
    rows = []
    for i in range(max(len(left), len(right), 1)):
        rows.append((left[i] if i < len(left) else None,
                     right[i] if i < len(right) else None))
    return rows


def field(y, key, value, theme, x=ART_W + 30, vx=VALUE_X):
    dots = "." * max(2, int((vx - x - (len(key) + 2) * CHAR) / CHAR))
    return (
        f'<text x="{x}" y="{y}" class="key">{esc(key)}:</text>'
        f'<text x="{x + (len(key) + 1) * CHAR}" y="{y}" class="dots">{esc(" " + dots)}</text>'
        f'<text x="{vx}" y="{y}" class="value">{esc(value)}</text>'
    )


def header(y, label, theme, x=ART_W + 30, width=500):
    rule = "─" * max(4, int((width - (len(label) + 4) * CHAR) / CHAR))
    return f'<text x="{x}" y="{y}" class="head">{esc(label)} <tspan class="dots">{esc(rule)}</tspan></text>'


def render(theme_name):
    t = THEMES[theme_name]
    rows = []
    rows.append(("title", None))
    rows.append(("divider", None))
    rows += [("field", f) for f in IDENTITY]
    rows.append(("blank", None))
    rows.append(("contact", None))
    rows += [("field", f) for f in CONTACT]
    rows.append(("blank", None))
    rows.append(("stats", None))
    rows += [("statline", s) for s in stat_rows()]
    rows.append(("blank", None))
    rows.append(("prompt", None))

    height = PAD * 2 + LINE * len(rows) + 6
    width = 894
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'font-family="\'IBM Plex Mono\',Consolas,Menlo,monospace" font-size="{FONT}" role="img" '
        f'aria-label="Theo Anastasiadis - Platform and Cloud Engineer, Copenhagen">',
        "<style>",
        f".key{{fill:{t['key']};}} .value{{fill:{t['value']};}} .head{{fill:{t['head']};font-weight:bold;}}",
        f".dots{{fill:{t['dots']};}} .muted{{fill:{t['muted']};}} text{{white-space:pre;}}",
        "</style>",
        f'<rect width="{width}" height="{height}" fill="{t["bg"]}" rx="14" stroke="{t["border"]}"/>',
    ]

    # ascii art, one tspan per line, palette cycles down the rows
    art = ['<text font-size="13">']
    for i, line in enumerate(ART):
        color = t["art"][i % len(t["art"])]
        art.append(f'<tspan x="{PAD}" y="{PAD + 13 + i * LINE}" fill="{color}">{esc(line)}</tspan>')
    art.append("</text>")
    out.append("".join(art))

    y = PAD + 13
    for kind, payload in rows:
        if kind == "title":
            out.append(f'<text x="{ART_W + 30}" y="{y}" class="head">theo@github</text>')
        elif kind == "divider":
            out.append(header(y, "", t))
        elif kind == "field":
            out.append(field(y, payload[0], payload[1], t))
        elif kind == "contact":
            out.append(header(y, "Contact", t))
        elif kind == "stats":
            out.append(header(y, "GitHub Stats", t))
        elif kind == "statline":
            left, right = payload
            parts = []
            if left:
                parts.append(field(y, left[0], left[1], t, vx=VALUE_X))
            if right:
                parts.append(field(y, right[0], right[1], t, x=VALUE_X + 40, vx=VALUE_X + 220))
            out.append("".join(parts))
        elif kind == "prompt":
            out.append(
                f'<text x="{ART_W + 30}" y="{y}" class="value">&gt; '
                f'<tspan fill="{t["cursor"]}">█'
                f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
                f'dur="1.1s" repeatCount="indefinite"/></tspan></text>'
            )
        y += LINE

    out.append("</svg>")
    return "\n".join(out) + "\n"


for name in THEMES:
    (ROOT / f"{name}_mode.svg").write_text(render(name))
    print(f"wrote {name}_mode.svg")
