import random, math, cairosvg
exec(open("/tmp/claude-0/-home-claude/b526ec50-437e-5e03-99f2-649ee89e85be/scratchpad/beluga_lib.py").read())
W, H = 1600, 1000
random.seed(21)

DEFS3 = '''<defs>
<linearGradient id="towerFar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#22374C"/><stop offset="1" stop-color="#101B26"/></linearGradient>
<linearGradient id="towerMid" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2C4A66"/><stop offset="0.6" stop-color="#1B3047"/><stop offset="1" stop-color="#12202F"/></linearGradient>
<linearGradient id="towerNear" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1A2B3C"/><stop offset="1" stop-color="#0A121A"/></linearGradient>
<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8A86A" stop-opacity="0"/><stop offset="1" stop-color="#E8A86A" stop-opacity="0.35"/></linearGradient>
</defs>'''

def tower(x, w, top, layer, cap="#5FA8E8", lit=0.12):
    g = {"far": "url(#towerFar)", "mid": "url(#towerMid)", "near": "url(#towerNear)"}[layer]
    s = [f'<rect x="{x}" y="{top}" width="{w}" height="{H-top+20}" rx="{min(10, w*0.08)}" fill="{g}"/>']
    # glowing roof cap: the "top of the bar"
    capw = 6 if layer != "far" else 3
    s.append(f'<rect x="{x}" y="{top}" width="{w}" height="{capw}" rx="3" fill="{cap}" opacity="{0.95 if layer!="far" else 0.6}"/>')
    if layer != "far":
        s.append(f'<rect x="{x-6}" y="{top-14}" width="{w+12}" height="30" fill="{cap}" opacity="0.10"/>')
    # windows
    cols = max(2, int(w / 22))
    gx = w / cols
    y = top + 22
    while y < H:
        for c in range(cols):
            if random.random() < lit:
                col = "#F5B942" if random.random() < 0.35 else "#9FD0FF"
                s.append(f'<rect x="{x + c*gx + gx*0.3:.1f}" y="{y}" width="{gx*0.4:.1f}" height="8" fill="{col}" opacity="{0.5 if layer=="far" else 0.8}"/>')
        y += 22
    return "".join(s)

b = [f'<rect width="{W}" height="{H}" fill="url(#dusk)"/>', f'<circle cx="1350" cy="900" r="520" fill="url(#sun)"/>']
for _ in range(70):
    x, y = random.uniform(0, W), random.uniform(0, 320)
    b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{random.uniform(0.6,1.6):.1f}" fill="#FFFFFF" opacity="{random.uniform(0.3,0.8):.2f}"/>')
b.append(clouds())

# far skyline: a dense rising chart
x = -20
while x < W:
    w = random.uniform(38, 70)
    t = 820 - (x / W) * 420 + random.uniform(-60, 60)
    b.append(tower(x, w, t, "far", cap="#3E6E9A", lit=0.08))
    x += w + random.uniform(4, 14)
b.append(f'<rect width="{W}" height="{H}" fill="url(#haze)"/>')

# mid towers: the bars he weaves between (rising left to right)
mids = [(230, 95, 690), (370, 80, 610), (720, 100, 520), (1240, 120, 330, "#F5B942"), (1420, 110, 250)]
for m in mids:
    b.append(tower(m[0], m[1], m[2], "mid", cap=m[3] if len(m) > 3 else "#5FA8E8"))

# plane + Orb, banked a little into the turn
k = 0.44
ox, oy = 790, 470
r = 62
cx, cy = ox + 560 * k, oy - 0.82 * r
spark = (cx + 0.78 * r - 4, cy - 1.53 * r)
bank = -9
pc = (ox + 480 * k, oy + 100 * k)
rot = lambda p: (pc[0] + (p[0]-pc[0])*math.cos(math.radians(bank)) - (p[1]-pc[1])*math.sin(math.radians(bank)),
                 pc[1] + (p[0]-pc[0])*math.sin(math.radians(bank)) + (p[1]-pc[1])*math.cos(math.radians(bank)))
sx, sy = rot(spark)

# the trail: a smooth line that only ever climbs, threading the towers
pts = [(-20, 930), (120, 900), (300, 840), (470, 790), (600, 730), (690, 640), (780, 560), (880, 470), (980, 420), (sx - 60, sy + 22), (sx, sy)]
def smooth(p):
    d = f"M {p[0][0]:.1f} {p[0][1]:.1f}"
    for i in range(1, len(p)):
        x0, y0 = p[i-1]; x1, y1 = p[i]
        mx = (x0 + x1) / 2
        d += f" C {mx:.1f} {y0:.1f} {mx:.1f} {y1:.1f} {x1:.1f} {y1:.1f}"
    return d
d = smooth(pts)
for w, o in ((22, 0.10), (11, 0.25), (4.5, 1.0)):
    b.append(f'<path d="{d}" fill="none" stroke="#F5B942" stroke-width="{w}" stroke-linecap="round" opacity="{o}"/>')
# data points where the line passes each bar
for (px, py) in pts[1:-2:2]:
    b.append(glow_dot(px, py, 4))

# speed lines behind the plane
for i, (yy, L) in enumerate(((520, 240), (560, 180), (600, 300), (450, 150))):
    b.append(f'<line x1="{ox-40-i*12}" y1="{yy}" x2="{ox-40-i*12-L}" y2="{yy+L*0.16}" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.3"/>')
grp = beluga(ox, oy, k) + orb(cx, cy, r, eyes="squint", mouth="grin", tilt=-8, antenna="full", legs="sit")
b.append(f'<g transform="rotate({bank} {pc[0]:.1f} {pc[1]:.1f})">{grp}</g>')
b.append(f'<path d="M {sx-100} {sy+50} q -24 6 -48 0 M {sx-110} {sy+80} q -20 5 -40 0" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.6"/>')

# near towers: the line dips BEHIND these (depth), never down
for (x, w, t) in ((-30, 170, 760), (540, 120, 660), (1530, 120, 160)):
    b.append(tower(x, w, t, "near", cap="#5FA8E8", lit=0.06))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       + DEFS + DEFS2 + DEFS3 + "".join(b) + "</svg>")
cairosvg.svg2png(bytestring=svg.encode(), write_to="/home/claude/orb_beluga_bar_city.png")
print("ok")
