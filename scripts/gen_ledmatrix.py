"""Renders the GitHub contribution calendar as an animated MAX7219-style LED matrix SVG.

Usage:
  GITHUB_TOKEN=... python3 gen_ledmatrix.py <user> <out.svg>   # GraphQL (used in CI)
  python3 gen_ledmatrix.py <user> <out.svg>                     # public calendar page (local preview)
Standard library only.
"""
import json
import os
import re
import sys
import urllib.request

FONT = {
    "A": ".###.#...##...#######...##...##...#", "B": "####.#...##...#####.#...##...#####.",
    "C": ".###.#...##....#....#....#...#.###.", "D": "####.#...##...##...##...##...#####.",
    "E": "######....#....####.#....#....#####", "F": "######....#....####.#....#....#....",
    "G": ".###.#...##....#.####...##...#.####", "H": "#...##...##...#######...##...##...#",
    "I": ".###...#....#....#....#....#...###.", "J": "..###...#....#....#....#.#..#..##..",
    "K": "#...##..#.#.#..##...#.#..#..#.#...#", "L": "#....#....#....#....#....#....#####",
    "M": "#...###.###.#.##.#.##...##...##...#", "N": "#...##...###..##.#.##..###...##...#",
    "O": ".###.#...##...##...##...##...#.###.", "P": "####.#...##...#####.#....#....#....",
    "Q": ".###.#...##...##...##.#.##..#..##.#", "R": "####.#...##...#####.#.#..#..#.#...#",
    "S": ".#####....#.....###.....#....#####.", "T": "#####..#....#....#....#....#....#..",
    "U": "#...##...##...##...##...##...#.###.", "V": "#...##...##...##...##...#.#.#...#..",
    "W": "#...##...##...##.#.##.#.##.#.#.#.#.", "X": "#...##...#.#.#...#...#.#.#...##...#",
    "Y": "#...##...#.#.#...#....#....#....#..", "Z": "#####....#...#...#...#...#....#####",
    "0": ".###.#...##..###.#.###..##...#.###.", "1": "..#...##....#....#....#....#...###.",
    "2": ".###.#...#....#...#...#...#...#####", "3": "#####...#...#.....#.....##...#.###.",
    "4": "...#...##..#.#.#..#.#####...#....#.", "5": "######....####.....#....##...#.###.",
    "6": "..##..#...#....####.#...##...#.###.", "7": "#####....#...#...#...#....#....#...",
    "8": ".###.#...##...#.###.#...##...#.###.", "9": ".###.#...##...#.####....#...#..##..",
    " ": "." * 35, "/": "....#....#...#...#...#...#....#....",
    "-": "...............#####...............", ">": "#.....#.....#.....#...#...#...#....",
}

def fetch_graphql(user, token):
    q = {"query": "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{"
                  "totalContributions weeks{contributionDays{contributionCount contributionLevel}}}}}}",
         "variables": {"u": user}}
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps(q).encode(),
                                 headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    lv = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    weeks = [[lv[d["contributionLevel"]] for d in w["contributionDays"]] for w in cal["weeks"]]
    return weeks, cal["totalContributions"]

def fetch_public(user):
    with urllib.request.urlopen(f"https://github.com/users/{user}/contributions", timeout=20) as r:
        html = r.read().decode()
    days = re.findall(r'data-date="(\d{4}-\d\d-\d\d)" id="contribution-day-component-(\d)-(\d+)" data-level="(\d)"', html)
    ncol = max(int(c) for _, _, c, _ in days) + 1
    weeks = [[0] * 7 for _ in range(ncol)]
    for _, row, col, lvl in days:
        weeks[int(col)][int(row)] = int(lvl)
    m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
    return weeks, int(m.group(1).replace(",", "")) if m else None

def render(weeks, total):
    P, R = 14, 5                      # LED pitch and radius
    cols = len(weeks)
    pad, top = 24, 46
    gw = cols * P
    width = gw + 2 * pad
    band_y = top + 7 * P + 22
    height = band_y + 7 * P + 34
    alpha = [0.10, 0.45, 0.65, 0.85, 1.0]

    count = f"{total} CONTRIBUTIONS IN THE LAST YEAR" if total is not None else "CONTRIBUTIONS IN THE LAST YEAR"
    msg = f"   JS0NNN  >  {count}  >  FIRMWARE  -  EDGE AI  -  RF  -  HARDWARE   "
    text_cols = []
    for ch in msg.upper():
        g = FONT.get(ch, FONT[" "])
        for c in range(5):
            text_cols.append([g[r * 5 + c] == "#" for r in range(7)])
        text_cols.append([False] * 7)
    shift = len(text_cols)
    dur = shift * 0.07

    o = [f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t">
<title id="t">js0nnn contribution graph drawn as a red LED matrix{f", {total} contributions in the last year" if total is not None else ""}, with a scrolling LED marquee.</title>
<defs>
<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<circle id="d" r="{R}" fill="#ff3b30"/>
<clipPath id="band"><rect x="{pad}" y="{band_y - P // 2}" width="{gw}" height="{7 * P}"/></clipPath>
</defs>
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-size:12px}}
.c{{opacity:0;animation:on .2s forwards}}
@keyframes on{{to{{opacity:1}}}}
#mq{{animation:scroll {dur:.1f}s steps({shift}) infinite}}
@keyframes scroll{{from{{transform:translateX(0)}}to{{transform:translateX(-{shift * P}px)}}}}
@media (prefers-reduced-motion:reduce){{.c{{animation:none;opacity:1}}#mq{{animation:none;transform:translateX(-{3 * 6 * P}px)}}}}
</style>
<rect width="{width}" height="{height}" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="{pad}" y="27" fill="#8b949e">MAX7219 x {cols * 7 // 64 + 1}  |  js0nnn@github: contributions, last 52 weeks</text>
<circle cx="{width - pad - 4}" cy="23" r="4" fill="#3fb950"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>
''']
    for c, week in enumerate(weeks):
        o.append(f'<g class="c" style="animation-delay:{0.3 + c * 0.035:.3f}s">')
        for r, lvl in enumerate(week):
            x, y = pad + c * P + P // 2, top + r * P + P // 2
            f = ' filter="url(#glow)"' if lvl else ""
            o.append(f'<use xlink:href="#d" x="{x}" y="{y}" opacity="{alpha[lvl]}"{f}/>')
        o.append("</g>\n")
    o.append(f'<line x1="{pad}" y1="{band_y - P}" x2="{pad + gw}" y2="{band_y - P}" stroke="#30363d"/>\n')
    for c in range(cols):
        for r in range(7):
            o.append(f'<use xlink:href="#d" x="{pad + c * P + P // 2}" y="{band_y + r * P}" opacity="0.10"/>')
    o.append(f'\n<g clip-path="url(#band)"><g id="mq" filter="url(#glow)">')
    for rep in range(2):  # two copies so the loop is seamless
        for i, col in enumerate(text_cols):
            for r, lit in enumerate(col):
                if lit:
                    o.append(f'<use xlink:href="#d" x="{pad + (rep * shift + i) * P + P // 2}" y="{band_y + r * P}"/>')
    o.append(f'</g></g>\n<text x="{pad}" y="{height - 12}" fill="#8b949e">off</text>')
    for i, a in enumerate(alpha):
        o.append(f'<use xlink:href="#d" x="{pad + 34 + i * 16}" y="{height - 16}" opacity="{a}"/>')
    o.append(f'<text x="{pad + 34 + 5 * 16}" y="{height - 12}" fill="#8b949e">more</text>\n</svg>\n')
    return "".join(o)

if __name__ == "__main__":
    user, out = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", user):
        sys.exit("invalid GitHub username")
    token = os.environ.get("GITHUB_TOKEN")
    try:
        weeks, total = fetch_graphql(user, token) if token else fetch_public(user)
    except (OSError, KeyError, TypeError, ValueError) as e:
        print(f"GraphQL fetch failed ({type(e).__name__}), using public calendar", file=sys.stderr)
        weeks, total = fetch_public(user)
    weeks = weeks[-53:]
    weeks[0] = [0] * (7 - len(weeks[0])) + weeks[0]   # first week starts mid-week
    for w in weeks[1:]:
        w.extend([0] * (7 - len(w)))
    with open(out, "w") as f:
        f.write(render(weeks, total))
