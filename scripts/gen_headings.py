"""Generates assets/headings/*.svg: powerline-style prompt bars used as section headings.
Usage: python3 gen_headings.py   (run from the repo root)"""
import re
from html import escape
from pathlib import Path

SECTIONS = {  # slug: (icon, path, command)
    "featured-projects": ("folder-code", "~/featured-projects", "ls -la"),
    "tech-arsenal":      ("tools",       "~/tech-arsenal",      "cat pinout"),
    "work":              ("briefcase",   "/var/log",            "cat work"),
    "lab":               ("camera",      "~/lab",               "ls"),
    "builds":            ("cpu",         "~/builds",            "tree -L 1"),
    "publications":      ("book",        "/mnt",                "mount | grep pub"),
    "ping":              ("send",        "~",                   "ping js0nnn"),
}
H, FS, CW = 32, 13, 8.0          # bar height, font size, assumed monospace char width
ARROW = 12                       # depth of the powerline arrow
SEGS = [("#238636", "#ffffff"), ("#1f6feb", "#ffffff"), ("#30363d", "#e6edf3")]

def icon_paths(name):
    svg = Path(f"assets/icons/{name}.svg").read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    return re.sub(r'(stroke|fill)="#[0-9a-fA-F]{6}"', r'\1="#ffffff"', inner)

def build(icon, path, cmd):
    texts = ["js0nnn", path, cmd]
    x, parts = 0.0, []
    for i, ((bg, fg), label) in enumerate(zip(SEGS, texts)):
        lead = 34 if i == 0 else ARROW + 10            # room for icon / incoming arrow
        w = lead + len(label) * CW + 14
        # body plus the arrow tip pointing into the next segment
        pts = f"{x},0 {x + w},0 {x + w + ARROW},{H / 2} {x + w},{H} {x},{H}"
        if i:
            pts += f" {x + ARROW},{H / 2}"
        parts.append(f'<polygon points="{pts}" fill="{bg}"/>')
        parts.append(f'<text x="{x + lead:.1f}" y="{H / 2}" fill="{fg}" dominant-baseline="central"'
                     f'{" font-weight=\"700\"" if i == 0 else ""}>{escape(label)}</text>')
        x += w
    width = x + ARROW + 22
    cursor = f'<rect class="cur" x="{x + ARROW + 8:.1f}" y="{H / 2 - 8}" width="8" height="16" fill="#3fb950"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{H}" viewBox="0 0 {width:.0f} {H}" role="img" aria-label="js0nnn {escape(path)} $ {escape(cmd)}">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-size:{FS}px}}
.cur{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.cur{{animation:none}}}}</style>
<clipPath id="r"><rect width="{width:.0f}" height="{H}" rx="6"/></clipPath>
<g clip-path="url(#r)">{"".join(parts)}</g>
<g transform="translate(10 {H / 2 - 9}) scale(0.75)">{icon_paths(icon)}</g>
{cursor}
</svg>
'''

BUTTONS = {  # slug: (icon, label, colour)
    "linkedin": ("brand-linkedin", "LinkedIn", "#0a66c2"),
    "say-hi":   ("message-circle", "Say hi",   "#238636"),
    "leetcode": ("brand-leetcode", "LeetCode", "#30363d"),
    "orcid":    ("brand-orcid",    "ORCID",    "#5e7d1c"),
    "resume":   ("download",       "Resume",   "#8957e5"),
}

def button(icon, label, bg):
    w = 34 + len(label) * CW + 16
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w + ARROW:.0f}" height="{H}" viewBox="0 0 {w + ARROW:.0f} {H}" role="img" aria-label="{escape(label)}">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-size:{FS}px}}</style>
<clipPath id="r"><rect width="{w + ARROW:.0f}" height="{H}" rx="6"/></clipPath>
<polygon clip-path="url(#r)" points="0,0 {w},0 {w + ARROW},{H / 2} {w},{H} 0,{H}" fill="{bg}"/>
<g transform="translate(10 {H / 2 - 9}) scale(0.75)">{icon_paths(icon)}</g>
<text x="34" y="{H / 2}" fill="#ffffff" font-weight="700" dominant-baseline="central">{escape(label)}</text>
</svg>
'''

if __name__ == "__main__":
    out = Path("assets/headings")
    out.mkdir(parents=True, exist_ok=True)
    for slug, spec in SECTIONS.items():
        (out / f"{slug}.svg").write_text(build(*spec))
    for slug, spec in BUTTONS.items():
        (out / f"btn-{slug}.svg").write_text(button(*spec))
