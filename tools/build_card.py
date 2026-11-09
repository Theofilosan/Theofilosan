#!/usr/bin/env python3
"""Render dark_mode.svg and light_mode.svg: the neofetch-style card.

Layout: ascii art on the left, dotted-leader fields on the right, live
stats from cache/stats.json, and a blinking prompt cursor at the bottom.
Run fetch_stats.py first. Pure stdlib, deterministic output.
"""
import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = (ROOT / "assets" / "ascii-art.txt").read_text().splitlines()

FONT = 13
LINE = 17
CHAR = 7.8  # advance of one monospace cell at FONT px
PAD = 24
ART_W = 340  # right column starts after this
VALUE_X = 610  # where field values begin

# ASCII portrait generated from his GitHub profile photo (luminance-mapped,
# subject dense / background empty). Static snapshot - update by re-running
# the conversion if the avatar changes.
PORTRAIT = """         ..::::------:.
       .::. ...:::::----:    -.
      -:.  ..:-------:::-=-+%-
     =:...:::-------::--+%@@.
:=+=++--:::--:::::::==::@@#+.
  -*@@@@%##=--+--=*%@. +@*=+=
    ==*@@@@  +%+@@@@+  #=-++=
    =::-=##  %*#@**%-.--:++*:
    .+-::::--%+=:.:----=++++-.
     .+====--==---:-==+++++.++=-
      .**+++++++++=+++=:-++=:++==
     :--=+-:-+*+==++=:.::=+*-.*++:
    .-::-=:==-::-++-.:::-++=+ ++==.-::
    :::::++-:-=++=:::--=++=+=:*=-+*+-:
     +==--==++=-::---=+++===.++=-+*==-
    .=-+++=---====+++++=---=.=*+=++=*+
    .- .--....-----::==----=-.*++*+*=:
     -.:.     :. . .:-=+====+:++*++*=-
     -=..    .:::::--==-::::-+*#*=+**+""".splitlines()
PORTRAIT_FONT = 10.5
PORTRAIT_LINE = 13
PORTRAIT_CHAR = 6.3


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
    rows.append(("blank", None))
    rows.append(("prompt", None))

    width = 894
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="@HEIGHT@" '
        f'font-family="\'IBM Plex Mono\',Consolas,Menlo,monospace" font-size="{FONT}" role="img" '
        f'aria-label="Theo Anastasiadis - Platform and Cloud Engineer, Copenhagen">',
        "<style>",
        f".key{{fill:{t['key']};}} .value{{fill:{t['value']};}} .head{{fill:{t['head']};font-weight:bold;}}",
        f".dots{{fill:{t['dots']};}} .muted{{fill:{t['muted']};}} text{{white-space:pre;}}",
        "</style>",
        f'<rect width="{width}" height="@HEIGHT@" fill="{t["bg"]}" rx="14" stroke="{t["border"]}"/>',
    ]

    # THEO wordmark: text lines with the palette gradient, then the
    # Squirtle sprite as crisp-edged pixel rects, then PRESS START.
    wordmark = [l for l in ART if l.strip() and "PRESS" not in l]
    art = ['<text font-size="13">']
    for i, line in enumerate(wordmark):
        color = t["art"][i % len(t["art"])]
        art.append(f'<tspan x="{PAD}" y="{PAD + 13 + i * LINE}" fill="{color}">{esc(line)}</tspan>')
    art.append("</text>")
    out.append("".join(art))

    pw_w = max(len(l) for l in PORTRAIT) * PORTRAIT_CHAR
    wm_w = max(len(l) for l in wordmark) * CHAR
    p_x = PAD + max(0, int((wm_w - pw_w) / 2))
    p_y = PAD + 13 + len(wordmark) * LINE + 4
    portrait = [f'<text font-size="{PORTRAIT_FONT}" fill="{t["head"]}">']
    for i, line in enumerate(PORTRAIT):
        portrait.append(f'<tspan x="{p_x}" y="{p_y + i * PORTRAIT_LINE}">{esc(line)}</tspan>')
    portrait.append("</text>")
    out.append("".join(portrait))

    press_y = p_y + len(PORTRAIT) * PORTRAIT_LINE + 20
    out.append(f'<text x="{PAD}" y="{press_y}" class="muted">PRESS START</text>')


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
        elif kind == "prompt":
            out.append(
                f'<text x="{ART_W + 30}" y="{y}" class="value">&gt; '
                f'<tspan fill="{t["cursor"]}">█'
                f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
                f'dur="1.1s" repeatCount="indefinite"/></tspan></text>'
            )
        y += LINE

    out.append("</svg>")
    height = max(PAD * 2 + LINE * len(rows) + 6, press_y + 14 + PAD)
    return "\n".join(out).replace("@HEIGHT@", str(height)) + "\n"


for name in THEMES:
    (ROOT / f"{name}_mode.svg").write_text(render(name))
    print(f"wrote {name}_mode.svg")
