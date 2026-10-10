"""Compose the README's hero image — a connector package, drawn as what it is.

Not shipped data. Writes docs/hero.svg, then rasterises it to docs/hero.png with
a headless Chromium (the README shows the PNG: GitHub's `<img>` view of an SVG
loads no fonts). Needs the Inter and DejaVu Sans Mono fonts for the PNG to match,
and Pillow to crop the screenshot. A slim sibling of integral-job-search's hero:
same sheet and palette, so the two read as one project.

The sheet carries no board names or counts on purpose: a PNG cannot follow the
repo, so whatever changes with the next connector stays off it.

Usage, from the repository root:

    uv run --with pillow python tools/hero.py
    CHROMIUM=/path/to/chrome uv run --with pillow python tools/hero.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT_SVG = ROOT / "docs" / "hero.svg"
OUT_PNG = ROOT / "docs" / "hero.png"
LOGO_SVG = ROOT / "docs" / "logo.svg"

#: The GitHub social-preview size, which the README shows scaled to its column.
W, H = 1280, 640

PAPER = "#f3eee3"
GRID = "#e4ddcd"
INK = "#1d2733"
DIM = "#6b6f76"
FRAME = "#9a958a"
TEAL = "#0f6e66"
SANS = "Inter, 'DejaVu Sans', sans-serif"
DISPLAY = "'Inter Display', Inter, sans-serif"
MONO = "'DejaVu Sans Mono', monospace"


def text(
    x: float,
    y: float,
    s: str,
    *,
    size: float,
    fill: str = INK,
    family: str = SANS,
    weight: int = 400,
    anchor: str = "start",
    spacing: float = 0,
    italic: bool = False,
) -> str:
    style = ' font-style="italic"' if italic else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
        f'letter-spacing="{spacing}"{style} xml:space="preserve">{escape(s)}</text>'
    )


def sheet() -> list[str]:
    """Grid, border with zone marks, registration marks — the family's drafting sheet."""
    out = [f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']
    for x in range(0, W, 20):
        width = 0.9 if x % 100 == 0 else 0.4
        out.append(
            f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{GRID}" stroke-width="{width}"/>'
        )
    for y in range(0, H, 20):
        width = 0.9 if y % 100 == 0 else 0.4
        out.append(
            f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{GRID}" stroke-width="{width}"/>'
        )
    out.append(
        f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" fill="none" stroke="{GRID}"/>'
    )
    out.append(
        f'<rect x="30" y="30" width="{W - 60}" height="{H - 60}" fill="none" '
        f'stroke="{FRAME}" stroke-width="1.5"/>'
    )
    zw = (W - 60) / 8
    for i in range(8):
        x = 30 + zw * i
        if i:
            out.append(f'<line x1="{x}" y1="16" x2="{x}" y2="30" stroke="{FRAME}"/>')
            out.append(f'<line x1="{x}" y1="{H - 30}" x2="{x}" y2="{H - 16}" stroke="{FRAME}"/>')
        for y in (27, H - 19):
            out.append(
                text(x + zw / 2, y, str(8 - i), size=9, fill=DIM, family=MONO, anchor="middle")
            )
    zh = (H - 60) / 4
    for i in range(4):
        y = 30 + zh * i
        if i:
            out.append(f'<line x1="16" y1="{y}" x2="30" y2="{y}" stroke="{FRAME}"/>')
            out.append(f'<line x1="{W - 30}" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{FRAME}"/>')
        for x in (23, W - 23):
            out.append(
                text(x, y + zh / 2 + 3, "ABCD"[i], size=9, fill=DIM, family=MONO, anchor="middle")
            )
    for cx, cy in ((48, 48), (48, H - 48)):
        out += [
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="{TEAL}"/>',
            f'<line x1="{cx - 11}" y1="{cy}" x2="{cx + 11}" y2="{cy}" stroke="{TEAL}"/>',
            f'<line x1="{cx}" y1="{cy - 11}" x2="{cx}" y2="{cy + 11}" stroke="{TEAL}"/>',
        ]
    return out


#: The logo tile's size on the sheet, and the room it takes left of the wordmark.
LOGO_SIZE = 84
LOGO_GAP = 20


def logo(x: float, y: float, size: float) -> str:
    """docs/logo.svg nested inline, so the PNG needs no second file."""
    inner = LOGO_SVG.read_text().strip()
    inner = inner[inner.index(">") + 1 : inner.rindex("</svg>")]
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 64 64">{inner}</svg>'


def wordmark() -> list[str]:
    return [
        logo(64, 50, LOGO_SIZE),
        f'<text x="{64 + LOGO_SIZE + LOGO_GAP}" y="122" font-family="{DISPLAY}" font-size="70" '
        f'font-weight="800" letter-spacing="-2"><tspan fill="{INK}">integral</tspan>'
        f'<tspan fill="{TEAL}">-connectors</tspan></text>',
        text(68, 164, "One package per job board. Four files, no code.", size=25, fill="#3b4652"),
        text(68, 192, "How integral-job-search reads a board's listings.", size=15, fill=DIM),
    ]


def title_block() -> list[str]:
    x, y, w, h = 842, 62, 376, 64
    half = w / 2 - 20
    cells = [(0.0, "PART OF", "integral-job-search"), (half, "THE RULE", "crawlers, never adverts")]
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" stroke="{FRAME}" '
        f'stroke-width="1.2"/>',
        f'<line x1="{x}" y1="{y + h / 2 + 4}" x2="{x + w}" y2="{y + h / 2 + 4}" stroke="{FRAME}"/>',
        f'<line x1="{x + half}" y1="{y + h / 2 + 4}" x2="{x + half}" y2="{y + h}" '
        f'stroke="{FRAME}"/>',
        text(x + 10, y + 14, "PROJECT", size=8, fill=DIM, family=MONO, spacing=1.5),
        text(x + 10, y + 30, "integral-connectors", size=14, weight=700, family=MONO),
    ]
    for cx, label, value in cells:
        out.append(text(x + cx + 10, y + 47, label, size=8, fill=DIM, family=MONO, spacing=1.5))
        out.append(text(x + cx + 10, y + 61, value, size=11, family=MONO, fill=TEAL if cx else INK))
    return out


def card(x: float, y: float, w: float, h: float, caption: str) -> list[str]:
    return [
        text(x, y - 10, caption, size=10, fill=TEAL, family=MONO, spacing=2),
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#faf7f0" '
        f'stroke="{FRAME}" stroke-width="1"/>',
    ]


def arrow(x1: float, x2: float, y: float, label: str) -> list[str]:
    return [
        f'<line x1="{x1}" y1="{y}" x2="{x2 - 6}" y2="{y}" stroke="{TEAL}" '
        f'stroke-width="1.4" stroke-dasharray="5 3"/>',
        f'<path d="M{x2 - 8},{y - 5} L{x2},{y} L{x2 - 8},{y + 5}" fill="none" '
        f'stroke="{TEAL}" stroke-width="1.4"/>',
        text((x1 + x2) / 2, y - 8, label, size=11, fill=TEAL, family=MONO, anchor="middle"),
    ]


#: The package, as its file tree: (indent, name, what it is for).
TREE = [
    (0, "connectors/<board>/", ""),
    (1, "connector.yaml", "what to fetch, where each field is"),
    (1, "meta.yaml", "site, maintainer, robots.txt policy"),
    (1, "fixture/list.html", "a recorded listing page"),
    (1, "fixture/detail.html", "one offer, bodies excerpted"),
]

#: A connector.yaml excerpt in a fictitious board's terms: (indent, key, value).
YAML = [
    (0, "list", ""),
    (1, "url_pattern", '"https://jobs.example.com/it"'),
    (1, "item", '".job-card"'),
    (1, "fields", ""),
    (2, "title", '{css: "h2"}'),
    (2, "company", '{css: ".employer"}'),
    (2, "location_raw", '{css: ".place"}'),
    (2, "detail_url", '{css: "a", attr: href}'),
]

FIELDS = ["title", "company", "location_raw", "detail_url", "text"]


def figure() -> list[str]:
    top = 262
    out: list[str] = []
    # The package.
    x, w, h = 64, 372, 228
    out += card(x, top, w, h, "THE PACKAGE")
    trunk = x + 26
    last = top + 28 + (len(TREE) - 1) * 42
    out.append(
        f'<line x1="{trunk}" y1="{top + 36}" x2="{trunk}" y2="{last - 4}" stroke="{FRAME}"/>'
    )
    for i, (indent, name, why) in enumerate(TREE):
        y = top + 28 + i * 42
        tx = x + 18 + indent * 26
        if indent:
            out.append(
                f'<line x1="{trunk}" y1="{y - 4}" x2="{tx - 6}" y2="{y - 4}" stroke="{FRAME}"/>'
            )
        out.append(text(tx, y, name, size=13, weight=700 if not indent else 600, family=MONO))
        if why:
            out.append(text(tx, y + 17, why, size=11.5, fill=DIM))
    # The connector, as data.
    x2, w2 = 494, 372
    out += arrow(x + w + 6, x2 - 6, top + 78, "")
    out += card(x2, top, w2, h, "CONNECTOR.YAML  ·  DATA, NOT A PROGRAM")
    for i, (indent, key, value) in enumerate(YAML):
        y = top + 30 + i * 25
        out.append(
            f'<text x="{x2 + 18 + indent * 18}" y="{y}" font-family="{MONO}" font-size="12.5" '
            f'xml:space="preserve"><tspan fill="{TEAL}">{escape(key)}:</tspan>'
            f'<tspan fill="{INK}"> {escape(value)}</tspan></text>'
        )
    # What comes out, and where it goes.
    x3 = 924
    out += arrow(x2 + w2 + 6, x3 - 6, top + 112, "")
    out.append(text(x3, top - 10, "FIELDS OUT", size=10, fill=TEAL, family=MONO, spacing=2))
    for i, name in enumerate(FIELDS):
        y = top + 20 + i * 36
        cw = len(name) * 7.6 + 28
        out += [
            f'<rect x="{x3}" y="{y - 13}" width="{cw}" height="26" rx="13" fill="#faf7f0" '
            f'stroke="{TEAL}" stroke-width="1.4"/>',
            text(x3 + cw / 2, y + 4.5, name, size=12.5, family=MONO, anchor="middle"),
        ]
    bx, by = 1060, top + 52
    out += [
        f'<path d="M{x3 + 132},{top + 92} C{x3 + 140},{top + 92} {bx - 30},{by + 40} '
        f'{bx - 4},{by + 40}" fill="none" stroke="{TEAL}" stroke-width="1.4" '
        f'stroke-dasharray="5 3"/>',
        f'<rect x="{bx}" y="{by}" width="156" height="80" rx="6" fill="{TEAL}"/>',
        text(bx + 78, by + 34, "integral-", size=15, weight=700, fill="#ffffff", anchor="middle"),
        text(bx + 78, by + 54, "job-search", size=15, weight=700, fill="#ffffff", anchor="middle"),
    ]
    return out


#: The guarantees a reviewer checks before a package is merged.
FEATURES = [
    ("no code", "single-element selectors only"),
    ("robots.txt", "checked, recorded in meta.yaml"),
    ("fixtures", "sampled for this, excerpted"),
    ("offline", "checked against recorded pages"),
    ("manifest", "generated, never hand-typed"),
]


def features() -> list[str]:
    x0, y, w, h, gap = 64, 536, 218, 50, 15
    out = []
    for i, (name, sub) in enumerate(FEATURES):
        x = x0 + i * (w + gap)
        out += [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#ebe4d6" '
            f'stroke="{FRAME}" stroke-width="0.8"/>',
            f'<rect x="{x}" y="{y}" width="4" height="{h}" rx="2" fill="{TEAL}"/>',
            text(x + 16, y + 21, name, size=13, weight=700, family=MONO, fill=TEAL),
            text(x + 16, y + 39, sub, size=12, fill="#3b4652"),
        ]
    return out


def svg() -> str:
    parts = sheet() + wordmark() + title_block() + figure() + features()
    body = "\n  ".join(parts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n  {body}\n</svg>\n'
    )


def chromium() -> str:
    for candidate in (
        os.environ.get("CHROMIUM"),
        "/opt/pw-browsers/chromium",
        shutil.which("chromium"),
        shutil.which("google-chrome"),
    ):
        if candidate and Path(candidate).exists():
            return candidate
    sys.exit("hero: no Chromium found; set CHROMIUM=/path/to/chrome")


def main() -> None:
    OUT_SVG.write_text(svg())
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "hero.html"
        page.write_text(f'<html><body style="margin:0;overflow:hidden">{svg()}</body></html>')
        subprocess.run(
            [
                chromium(),
                "--headless=new",
                "--no-sandbox",
                "--hide-scrollbars",
                "--force-device-scale-factor=2",
                f"--window-size={W},{H + 200}",
                f"--screenshot={OUT_PNG}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    # Headless Chromium's viewport is shorter than its window: shoot tall, then crop.
    from PIL import Image  # type: ignore[import-not-found, unused-ignore]

    with Image.open(OUT_PNG) as shot:
        shot.crop((0, 0, W * 2, H * 2)).save(OUT_PNG, optimize=True)
    print(f"wrote {OUT_SVG.relative_to(ROOT)} and {OUT_PNG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
