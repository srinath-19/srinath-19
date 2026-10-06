"""Builds assets/terminal.svg — the animated terminal header of the profile README.

Edit the content below and re-run:  python scripts/build_terminal.py

Why a generator rather than a hand-written SVG: GitHub serves the SVG as an
<img>, so it renders in whatever monospace font the *viewer* has (Consolas is
0.55em wide, Menlo 0.6em…). Every glyph is therefore pinned to a fixed grid
with a per-character `x` list, and the typing effect slides a cover over the
text in `steps(n)` of that same grid — so the cursor lands on character
boundaries in any font. (`textLength` looks like the tool for this, but
renderers disagree on honouring it.) The banner is drawn as rects and paths
rather than block characters, so it has no font seams at all.
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"

# ── palette (shared with the portfolio site, srinath.io) ────────────────────
BG = "#0f1324"
BAR = "#171c35"
EDGE = "#2a3152"
FG = "#e6edf3"
DIM = "#7d8590"
LIME = "#cdfb52"
PINK = "#f756a3"
RED = "#d4423b"

FONT = (
    "'JetBrains Mono','Fira Code','SF Mono',SFMono-Regular,ui-monospace,"
    "Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
)
ADVANCE = 0.6  # monospace advance width as a fraction of font size

W = 960
PX = 28  # left padding

BANNER = [
    "███████╗██████╗ ██╗███╗   ██╗ █████╗ ████████╗██╗  ██╗",
    "██╔════╝██╔══██╗██║████╗  ██║██╔══██╗╚══██╔══╝██║  ██║",
    "███████╗██████╔╝██║██╔██╗ ██║███████║   ██║   ███████║",
    "╚════██║██╔══██╗██║██║╚██╗██║██╔══██║   ██║   ██╔══██║",
    "███████║██║  ██║██║██║ ╚████║██║  ██║   ██║   ██║  ██║",
    "╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝",
]

INFO = [  # neofetch-style key / value rows
    ("Role", "AI Software Engineer · ML · Backend"),
    ("Location", "SF Bay Area · open to relocation"),
    ("Edu", "M.S. CS (AI) · CU Boulder '26"),
    ("Focus", "agentic AI · RAG · LLM fine-tuning"),
    ("Stack", "Python · TypeScript · FastAPI · PyTorch"),
    ("Infra", "GCP · AWS · Docker · Kubernetes"),
    ("Paper", "IEEE 2024 · YOLOv8 harvest detection"),
    ("Status", "● open to full-time AI/ML & SWE roles"),
]

MOTTO = [
    "I'm the kind of engineer who sees someone doing the same boring thing twice",
    'and immediately thinks, "There has to be a way to automate this."',
]

PROMPT = [("srinath", LIME), ("@", DIM), ("github", PINK), (":", DIM), ("~", FG), ("$ ", DIM)]
PROMPT_LEN = sum(len(t) for t, _ in PROMPT)

css: list[str] = []
body: list[str] = []
_uid = 0


def width(chars: int, size: float) -> float:
    return round(chars * size * ADVANCE, 2)


def tspans(parts: list[tuple[str, str]], bold: bool = False) -> str:
    weight = ' font-weight="700"' if bold else ""
    return "".join(f'<tspan fill="{c}"{weight}>{escape(t)}</tspan>' for t, c in parts)


def grid(x: float, n: int, size: float) -> str:
    """Per-character x positions — pins every glyph to the monospace grid."""
    cw = size * ADVANCE
    return " ".join(f"{x + i * cw:g}" for i in range(n))


def line(x: float, y: float, parts, size: float, at: float, bold=False) -> str:
    """One row of text that appears at `at` seconds, pinned to the grid."""
    n = sum(len(t) for t, _ in parts)
    return (
        f'<text x="{grid(x, n, size)}" y="{y}" font-size="{size}" '
        f'class="o" style="animation-delay:{at}s">{tspans(parts, bold)}</text>'
    )


def typed(y: float, cmd: str, at: float, cps: float = 14) -> float:
    """A prompt that appears at `at`, then has `cmd` typed out. Returns the end time."""
    global _uid
    _uid += 1
    size = 14
    cw = size * ADVANCE
    start = at + 0.25
    dur = round(len(cmd) / cps, 2)
    end = round(start + dur, 2)
    x0 = round(PX + PROMPT_LEN * cw, 2)
    css.append(
        f"@keyframes ty{_uid}{{to{{transform:translateX({width(len(cmd), size)}px)}}}}"
        f".ty{_uid}{{animation:ty{_uid} {dur}s steps({len(cmd)}) {start}s forwards,"
        f"hide .01s linear {end + 0.15}s forwards}}"
    )
    body.append(
        f'<g class="o" style="animation-delay:{at}s">'
        + line(PX, y, PROMPT + [(cmd, FG)], size, at).replace(' class="o"', "", 1)
        + f'<g class="ty{_uid}">'
        f'<rect x="{x0}" y="{y - 14}" width="{round(cw, 2)}" height="18" fill="{LIME}"/>'
        f'<rect x="{round(x0 + cw, 2)}" y="{y - 15}" width="{W}" height="21" fill="{BG}"/>'
        "</g></g>"
    )
    return end


# ── 1. `neofetch` ───────────────────────────────────────────────────────────
t = typed(72, "neofetch", 0.4)

# banner — left column, drawn as geometry: █ is a filled cell, the box-drawing
# "shadow" characters are pairs of thin lines
CW, CH, BTOP = 9.0, 16.0, 94
XA, XB, YA, YB = CW * 0.33, CW * 0.67, CH * 0.38, CH * 0.62
STROKES = {
    "═": [[(0, YA), (CW, YA)], [(0, YB), (CW, YB)]],
    "║": [[(XA, 0), (XA, CH)], [(XB, 0), (XB, CH)]],
    "╗": [[(0, YA), (XB, YA), (XB, CH)], [(0, YB), (XA, YB), (XA, CH)]],
    "╔": [[(CW, YA), (XA, YA), (XA, CH)], [(CW, YB), (XB, YB), (XB, CH)]],
    "╝": [[(0, YB), (XB, YB), (XB, 0)], [(0, YA), (XA, YA), (XA, 0)]],
    "╚": [[(CW, YB), (XA, YB), (XA, 0)], [(CW, YA), (XB, YA), (XB, 0)]],
}
for i, row in enumerate(BANNER):
    y0 = BTOP + i * CH
    rects, path = [], []
    for j, ch in enumerate(row):
        x0 = PX + j * CW
        if ch == "█":
            rects.append(f'<rect x="{x0:g}" y="{y0:g}" width="{CW + 0.3:g}" height="{CH + 0.3:g}"/>')
        for stroke in STROKES.get(ch, []):
            path.append("M" + " L".join(f"{x0 + px:g} {y0 + py:g}" for px, py in stroke))
    body.append(
        f'<g class="o" style="animation-delay:{round(t + 0.25 + i * 0.07, 2)}s" filter="url(#glow)">'
        f'<g fill="url(#grad)">{"".join(rects)}</g>'
        f'<path d="{" ".join(path)}" fill="none" stroke="url(#grad)" stroke-width="1.2"/></g>'
    )
by = 108  # first text baseline level, shared with the info column
under = BTOP + len(BANNER) * CH + 34
body.append(line(PX, under, [("Srinath Muppala", FG)], 17, round(t + 0.8, 2), bold=True))
body.append(line(PX, under + 26, [("// I make computers do the boring stuff", DIM)], 13, round(t + 0.9, 2)))
body.append(line(PX, under + 46, [("// so humans can do the interesting stuff.", DIM)], 13, round(t + 1.0, 2)))

# info — right column
RX, rsize, rstep, ry = 556, 13, 21, by - 12
rows = [
    [("srinath", LIME), ("@", DIM), ("github", PINK)],
    [("─" * 14, DIM)],
] + [[(f"{k:<10}", PINK), (v, FG)] for k, v in INFO]
for i, parts in enumerate(rows):
    at = round(t + 0.35 + i * 0.09, 2)
    if parts[0][0].startswith("─"):  # a drawn rule — box glyphs gap on the grid
        y = ry + i * rstep - 4
        body.append(
            f'<line x1="{RX}" y1="{y}" x2="{RX + width(14, rsize)}" y2="{y}" stroke="{DIM}" '
            f'class="o" style="animation-delay:{at}s"/>'
        )
    elif parts[0][0].strip() == "Status":  # own tspan so only the dot pulses
        value = parts[1][0]
        parts = [parts[0], ("●", LIME), (value[1:], FG)]
        body.append(
            line(RX, ry + i * rstep, parts, rsize, at, bold=(i == 0))
            .replace(f'<tspan fill="{LIME}">●</tspan>', f'<tspan fill="{LIME}" class="pulse">●</tspan>')
        )
    else:
        body.append(line(RX, ry + i * rstep, parts, rsize, at, bold=(i == 0)))

blocks_y = ry + len(rows) * rstep - 4
swatches = [RED, PINK, "#febc2e", LIME, "#3fb950", "#58a6ff", "#bc8cff", FG]
at = round(t + 0.35 + len(rows) * 0.09, 2)
body.append(
    f'<g class="o" style="animation-delay:{at}s">'
    + "".join(f'<rect x="{RX + i * 26}" y="{blocks_y}" width="22" height="12" rx="2" fill="{c}"/>'
              for i, c in enumerate(swatches))
    + "</g>"
)

# ── 2. `cat motto.txt` ──────────────────────────────────────────────────────
y2 = blocks_y + 52
t2 = typed(y2, "cat motto.txt", round(at + 0.5, 2))
for i, m in enumerate(MOTTO):
    body.append(line(PX, y2 + 24 + i * 21, [(m, FG)], 14, round(t2 + 0.25 + i * 0.05, 2)))

# ── 3. idle prompt with blinking cursor ─────────────────────────────────────
y3 = y2 + 24 + len(MOTTO) * 21 + 12
t3 = round(t2 + 0.6, 2)
cx = round(PX + PROMPT_LEN * 14 * ADVANCE, 2)
body.append(
    f'<g class="o" style="animation-delay:{t3}s">'
    + line(PX, y3, PROMPT, 14, t3).replace(' class="o"', "", 1)
    + f'<rect x="{cx}" y="{y3 - 14}" width="{round(14 * ADVANCE, 2)}" height="18" fill="{LIME}" class="blink"/>'
    "</g>"
)

H = y3 + 30

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" xml:space="preserve" role="img" aria-labelledby="t d">
<title id="t">Srinath Muppala — AI Software Engineer</title>
<desc id="d">An animated terminal running neofetch: AI Software Engineer, ML and backend. San Francisco Bay Area, open to relocation. M.S. Computer Science (AI), CU Boulder. Focus: agentic AI, RAG, LLM fine-tuning. Open to full-time AI/ML and software engineering roles.</desc>
<defs>
<linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="{PX}" y1="0" x2="{PX + len(BANNER[0]) * CW}" y2="0">
<stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{LIME}"/>
</linearGradient>
<filter id="glow" x="-5%" y="-30%" width="110%" height="160%">
<feGaussianBlur stdDeviation="2.2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<clipPath id="win"><rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12"/></clipPath>
</defs>
<style>
text{{font-family:{FONT};white-space:pre}}
.o{{opacity:0;animation:show .18s ease-out forwards}}
@keyframes show{{to{{opacity:1}}}}
@keyframes hide{{to{{opacity:0}}}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.pulse{{animation:pulse 1.8s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.25}}}}
{"".join(css)}
</style>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="38" fill="{BAR}"/>
<line x1="0" y1="38" x2="{W}" y2="38" stroke="{EDGE}"/>
<circle cx="22" cy="19" r="6" fill="#ff5f57"/><circle cx="42" cy="19" r="6" fill="#febc2e"/><circle cx="62" cy="19" r="6" fill="#28c840"/>
<text x="{W / 2}" y="24" font-size="12" fill="{DIM}" text-anchor="middle">srinath@github: ~ — zsh</text>
{chr(10).join(body)}
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{EDGE}"/>
</svg>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(f"wrote {OUT} ({W}x{H}, {len(svg):,} bytes)")
