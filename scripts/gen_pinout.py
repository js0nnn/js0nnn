"""Generates assets/pinout.svg: the tech stack drawn as an LQFP chip pinout. Usage: python3 gen_pinout.py <out.svg>"""
import sys
from html import escape

SIDES = {  # side: (group label, colour, pins)
    "left":   ("LANG",      "#79c0ff", ["C", "C++", "Python", "Java", "SQL", "QML"]),
    "right":  ("MCU / SBC", "#e3b341", ["STM32", "ESP32", "Arduino", "RPi 5", "Jetson", "TI mmWave"]),
    "top":    ("BUS / RF",  "#d2a8ff", ["UART", "SPI", "I2C", "DMA", "ADC", "PWM", "EXTI", "LoRa"]),
    "bottom": ("SW / TOOLS", "#3fb950", ["FreeRTOS", "Qt", "OpenCV", "YOLO", "CubeIDE", "ESP-IDF", "Linux", "Git"]),
}
W, H = 760, 560
CX, CY = W // 2, H // 2 + 6
BW, BH = 300, 230            # chip body
PIN_L, PIN_T = 26, 10        # pin length, thickness
METAL, BODY = "#8b949e", "#1c2128"

def spread(n, span):
    step = span / n
    return [-span / 2 + step * (i + 0.5) for i in range(n)]

out = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
<title id="t">Tech arsenal as a chip pinout. Languages: {", ".join(SIDES["left"][2])}. Hardware: {", ".join(SIDES["right"][2])}. Buses: {", ".join(SIDES["top"][2])}. Software and tools: {", ".join(SIDES["bottom"][2])}.</title>
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-size:13px}}
.p{{fill:{METAL};animation:lit .25s forwards}}
@keyframes lit{{to{{fill:var(--c)}}}}
.lb{{opacity:0;animation:on .25s forwards}}
@keyframes on{{to{{opacity:1}}}}
.pulse{{animation:pulse 2.4s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.25}}}}
@media (prefers-reduced-motion:reduce){{.p{{animation:none;fill:var(--c)}}.lb{{animation:none;opacity:1}}.pulse{{animation:none}}}}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="20" y="28" fill="#8b949e">$ cat /sys/firmware/js0nnn/pinout</text>
''']

n, k = 1, 0
def pin(x, y, w, h, colour, label, lx, ly, anchor, rotate=False):
    global n, k
    d = 0.4 + k * 0.08
    k += 1
    out.append(f'<rect class="p" style="--c:{colour};animation-delay:{d:.2f}s" x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="1.5"/>')
    tr = f' transform="rotate(-90 {lx:.1f} {ly:.1f})"' if rotate else ""
    out.append(f'<text class="lb" style="animation-delay:{d:.2f}s" x="{lx:.1f}" y="{ly:.1f}" fill="#e6edf3" text-anchor="{anchor}" dominant-baseline="middle"{tr}>{escape(label)}</text>\n')
    n += 1

side_order = ["left", "bottom", "right", "top"]
for side in side_order:
    name, colour, pins = SIDES[side]
    if side in ("left", "right"):
        offs = spread(len(pins), BH - 40)
        for o in offs:
            y = CY + o - PIN_T / 2
            if side == "left":
                pin(CX - BW / 2 - PIN_L, y, PIN_L, PIN_T, colour, pins[offs.index(o)], CX - BW / 2 - PIN_L - 10, CY + o, "end")
            else:
                pin(CX + BW / 2, y, PIN_L, PIN_T, colour, pins[offs.index(o)], CX + BW / 2 + PIN_L + 10, CY + o, "start")
    else:
        offs = spread(len(pins), BW - 30)
        for o in offs:
            x = CX + o - PIN_T / 2
            if side == "bottom":
                pin(x, CY + BH / 2, PIN_T, PIN_L, colour, pins[offs.index(o)], CX + o, CY + BH / 2 + PIN_L + 10, "end", rotate=True)
            else:
                pin(x, CY - BH / 2 - PIN_L, PIN_T, PIN_L, colour, pins[offs.index(o)], CX + o, CY - BH / 2 - PIN_L - 10, "start", rotate=True)

# group labels
for side, (x, y, a) in {"left": (CX - BW / 2 - 130, CY - BH / 2 - 8, "middle"), "right": (CX + BW / 2 + 130, CY - BH / 2 - 8, "middle"),
                        "top": (CX - BW / 2 - 60, CY - BH / 2 - 70, "middle"), "bottom": (CX + BW / 2 + 70, CY + BH / 2 + 80, "middle")}.items():
    name, colour, _ = SIDES[side]
    out.append(f'<text x="{x}" y="{y}" fill="{colour}" text-anchor="{a}" style="font-size:11px;letter-spacing:2px">{name}</text>\n')

bx, by = CX - BW / 2, CY - BH / 2
out.append(f'''<rect x="{bx}" y="{by}" width="{BW}" height="{BH}" rx="6" fill="{BODY}" stroke="#30363d"/>
<circle cx="{bx + 22}" cy="{by + 22}" r="7" fill="#0d1117" stroke="#30363d"/>
<circle class="pulse" cx="{bx + 22}" cy="{by + 22}" r="3" fill="#3fb950"/>
<text x="{CX}" y="{CY - 22}" fill="#e6edf3" text-anchor="middle" style="font-size:22px;font-weight:700;letter-spacing:3px">JS0NNN-H22</text>
<text x="{CX}" y="{CY + 6}" fill="#8b949e" text-anchor="middle">embedded + edge AI</text>
<text x="{CX}" y="{CY + 30}" fill="#8b949e" text-anchor="middle" style="font-size:11px">LQFP-{n - 1}  |  rev 2026.10</text>
<text x="{CX}" y="{CY + 72}" fill="#484f58" text-anchor="middle" style="font-size:10px">VIT  |  CSE (AI &amp; ML)</text>
</svg>
''')
with open(sys.argv[1], "w") as f:
    f.write("".join(out))
