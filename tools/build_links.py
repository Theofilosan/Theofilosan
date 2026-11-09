#!/usr/bin/env python3
"""Render the retro link buttons: link_{portfolio,linkedin,email}_{dark,light}.svg.

Flat pixel buttons with a hard bottom edge, matching the card palette.
Pure stdlib, deterministic output.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

W, H = 300, 56

THEMES = {
    "dark": {"bg": "#101521", "text": "#edf4eb",
             "green": "#8df3c0", "cyan": "#79d6f0", "pink": "#ed91d6"},
    "light": {"bg": "#f6f8fa", "text": "#1f2328",
              "green": "#1a7f37", "cyan": "#0a6f8f", "pink": "#b0449b"},
}

BUTTONS = [
    ("portfolio", "PORTFOLIO", "green", "monitor"),
    ("linkedin", "LINKEDIN", "cyan", "in"),
    ("email", "EMAIL", "pink", "mail"),
]


def icon(kind, color):
    """Tiny 16x16 pixel glyph drawn at (18, 20)."""
    if kind == "monitor":
        return (
            f'<rect x="18" y="18" width="18" height="12" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<rect x="18" y="18" width="18" height="12" fill="{color}" opacity="0.18"/>'
            f'<rect x="24" y="32" width="6" height="3" fill="{color}"/>'
            f'<rect x="20" y="35" width="14" height="2" fill="{color}"/>'
        )
    if kind == "in":
        return (
            f'<rect x="18" y="18" width="18" height="18" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<text x="21.5" y="32" font-size="13" font-weight="bold" fill="{color}">in</text>'
        )
    # mail
    return (
        f'<rect x="18" y="20" width="18" height="13" fill="none" stroke="{color}" stroke-width="2"/>'
        f'<polyline points="18,21 27,28 36,21" fill="none" stroke="{color}" stroke-width="2"/>'
    )


def render(theme_name, name, label, accent, glyph):
    t = THEMES[theme_name]
    c = t[accent]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="'IBM Plex Mono',Consolas,Menlo,monospace" role="img" aria-label="{label}">
<rect x="1" y="1" width="{W - 2}" height="{H - 8}" rx="7" fill="{t['bg']}" stroke="{c}" stroke-width="2"/>
<rect x="1" y="{H - 9}" width="{W - 2}" height="8" rx="4" fill="{c}" opacity="0.45"/>
{icon(glyph, c)}
<text x="48" y="33" font-size="15" font-weight="bold" letter-spacing="2" fill="{c}">{label}</text>
</svg>
'''


for theme_name in THEMES:
    for name, label, accent, glyph in BUTTONS:
        out = ROOT / f"link_{name}_{theme_name}.svg"
        out.write_text(render(theme_name, name, label, accent, glyph))
        print(f"wrote {out.name}")
