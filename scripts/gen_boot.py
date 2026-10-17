"""Generates assets/boot.svg: an animated dmesg-style terminal."""
import sys
from html import escape

G, D, C, Y, W, M = "#3fb950", "#8b949e", "#79c0ff", "#e3b341", "#e6edf3", "#d2a8ff"
W_DOTS = 46  # column where OK/up lands

def dots(label, status, col=G):
    pad = W_DOTS - len(label)
    return [(W, label + " "), (D, "." * pad + " "), (col, status)]

def ts(t):
    return (D, f"[{t:>9.6f}] ")

lines = [
    [ts(0.0), (W, "js0nnn firmware "), (M, "v2026.10"), (W, " — booting")],
    [ts(0.000412)] + dots("cpu0: STM32 F4 / H7", "OK"),
    [ts(0.000418)] + dots("cpu1: ESP32 / Arduino", "OK"),
    [ts(0.000903)] + dots("edge: Raspberry Pi 5 / Jetson Orin Nano", "OK"),
    [ts(0.001207)] + dots("rf: LoRa SX1262, TI mmWave AWR1642 / AWR6843", "OK"),
    [ts(0.001550)] + dots("rtos: FreeRTOS scheduler started", "OK"),
    [ts(0.002010)] + dots("bus: UART SPI I2C DMA ADC PWM", "up", C),
    [ts(0.003300), (C, "role: "), (W, "Software Development Intern @ SGF Labs")],
    [ts(0.003301), (C, "edu:  "), (W, "B.Tech CSE (AI & ML), VIT, class of 2027")],
    [ts(0.004000), (W, "probing projects:")],
    [ts(0.004100), (Y, "  ade9000-stm32h755           "), (D, "driver           "), (G, "[ OK ]")],
    [ts(0.004200), (Y, "  diy-power-quality-analyzer  "), (D, "power-quality    "), (G, "[ OK ]")],
    [ts(0.004300), (Y, "  tm-seat-v1                  "), (D, "driver-safety    "), (G, "[ OK ]")],
    [ts(0.004400), (Y, "  led-matrix-32x128           "), (D, "display          "), (G, "[ OK ]")],
    [ts(0.004500), (Y, "  pc-based-oscilloscope       "), (D, "instrumentation  "), (G, "[ OK ]")],
    [ts(0.004600), (Y, "  bench-psu                   "), (D, "instrumentation  "), (G, "[ OK ]")],
    [ts(0.005000), (C, "pub: "), (W, "2 mounted "), (D, "(Elsevier SoftwareX '26, IEEE AIIoT '24)")],
    [ts(0.006000), (G, "ready.")],
]

FS, LH, PADX, TOP = 14, 21, 20, 66
cmd = "$ dmesg | grep js0nnn"
width = 720
login_y = TOP + LH * (len(lines) + 2) + 6
height = login_y + 22
t_cmd = 1.1                      # typing time for the command
step = 0.16                      # delay between log lines
t_login = t_cmd + 0.3 + step * len(lines) + 0.2

out = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t">
<title id="t">js0nnn boot log: STM32, ESP32, Arduino, Raspberry Pi, Jetson, TI mmWave and FreeRTOS OK; Software Development Intern at SGF Labs; projects ade9000-stm32h755, diy-power-quality-analyzer, tm-seat-v1, led-matrix-32x128, pc-based-oscilloscope and bench-psu; 2 publications.</title>
<style>
text{{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;font-size:{FS}px;white-space:pre}}
.l{{opacity:0;animation:on .01s forwards}}
@keyframes on{{to{{opacity:1}}}}
#tc{{animation:type {t_cmd}s steps({len(cmd)}) .3s both}}
@keyframes type{{from{{width:0}}to{{width:{len(cmd)*8.6+4:.0f}px}}}}
.cur{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.l,.cur{{animation:none;opacity:1}}#tc{{animation:none;width:{len(cmd)*8.6+4:.0f}px}}}}
</style>
<defs><clipPath id="c"><rect id="tc" x="{PADX}" y="{TOP-LH+4}" width="0" height="{LH}"/></clipPath></defs>
<rect width="{width}" height="{height}" rx="10" fill="#0d1117" stroke="#30363d"/>
<rect width="{width}" height="34" rx="10" fill="#161b22"/><rect y="24" width="{width}" height="10" fill="#161b22"/>
<line x1="0" y1="34" x2="{width}" y2="34" stroke="#30363d"/>
<circle cx="22" cy="17" r="6" fill="#ff5f56"/><circle cx="42" cy="17" r="6" fill="#ffbd2e"/><circle cx="62" cy="17" r="6" fill="#27c93f"/>
<text x="{width//2}" y="22" fill="{D}" text-anchor="middle" style="font-size:12px">js0nnn@github: ~</text>
<text x="{PADX}" y="{TOP}" clip-path="url(#c)"><tspan fill="{G}">$ </tspan><tspan fill="{W}">{escape(cmd[2:])}</tspan></text>
''']
for i, segs in enumerate(lines):
    y = TOP + LH * (i + 1) + 6
    delay = t_cmd + 0.3 + step * i
    spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for c, s in segs)
    out.append(f'<text class="l" style="animation-delay:{delay:.2f}s" x="{PADX}" y="{y}" xml:space="preserve">{spans}</text>\n')
out.append(f'<text class="l" style="animation-delay:{t_login:.2f}s" x="{PADX}" y="{login_y}"><tspan fill="{G}">js0nnn login: </tspan><tspan class="cur" fill="{W}">█</tspan></text>\n</svg>\n')
open(sys.argv[1], "w").write("".join(out))
