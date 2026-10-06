import math, random, cairosvg

src = open("/tmp/claude-0/-home-claude/b526ec50-437e-5e03-99f2-649ee89e85be/scratchpad/board.py").read()
src = src[:src.index("panels = []")]
# add a sitting pose: legs reach forward and down over the curve of the hump
src = src.replace('''    elif legs == "tuck":''', '''    elif legs == "sit":
        L = [((-0.25, 0.8), (-0.12, 1.5), 0.0), ((0.28, 0.8), (0.42, 1.45), 0.58)]
    elif legs == "tuck":''')
exec(src)

W, H = 1600, 1000
random.seed(4)

DEFS2 = '''<defs>
<linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#0B1622"/><stop offset="0.45" stop-color="#1E3A57"/>
 <stop offset="0.78" stop-color="#5B6F8A"/><stop offset="1" stop-color="#E8A86A"/></linearGradient>
<radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">
 <stop offset="0" stop-color="#FFE3B0" stop-opacity="1"/><stop offset="0.25" stop-color="#F5B942" stop-opacity="0.55"/>
 <stop offset="1" stop-color="#F5B942" stop-opacity="0"/></radialGradient>
<linearGradient id="hull" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#FFFFFF"/><stop offset="0.55" stop-color="#EEF3F8"/><stop offset="1" stop-color="#B9C7D6"/></linearGradient>
<linearGradient id="hullBelly" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#E3EAF1"/><stop offset="1" stop-color="#9FB0C2"/></linearGradient>
<linearGradient id="eng" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#F2F5F8"/><stop offset="1" stop-color="#8FA1B5"/></linearGradient>
<linearGradient id="wing" x1="0" y1="0" x2="1" y2="1">
 <stop offset="0" stop-color="#DCE4EC"/><stop offset="1" stop-color="#97A9BC"/></linearGradient>
<radialGradient id="cloud" cx="0.5" cy="0.6" r="0.5">
 <stop offset="0" stop-color="#C9D6E4" stop-opacity="0.55"/><stop offset="1" stop-color="#C9D6E4" stop-opacity="0"/></radialGradient>
</defs>'''


def clouds():
    s = []
    for (x, y, w, h, o) in ((180, 760, 520, 120, 0.9), (900, 820, 700, 140, 1), (1350, 700, 420, 100, 0.8),
                            (420, 300, 360, 70, 0.4), (1250, 260, 300, 60, 0.35), (60, 560, 300, 70, 0.6)):
        for k in range(5):
            cx = x + random.uniform(-w * 0.35, w * 0.35)
            cy = y + random.uniform(-h * 0.25, h * 0.2)
            s.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{w*random.uniform(0.3,0.5):.0f}" ry="{h*random.uniform(0.4,0.7):.0f}" fill="url(#cloud)" opacity="{o}"/>')
    return "".join(s)


def beluga(ox, oy, k):
    """A plain, unbranded Beluga-style freighter in side view, facing right.
    Drawn in a 0-1000 unit box, origin at the tail, scaled by k."""
    P = lambda x, y: f"{ox + x*k:.1f} {oy + y*k:.1f}"
    s = []
    # far wing + engine (behind the fuselage)
    s.append(f'<path d="M {P(470,212)} L {P(560,214)} L {P(700,150)} L {P(668,150)} Z" fill="#8597AB"/>')
    s.append(f'<rect x="{ox+600*k}" y="{oy+168*k}" width="{70*k}" height="{24*k}" rx="{12*k}" fill="#8193A7"/>')
    # tail: vertical fin, horizontal stabiliser and its endplate fins
    s.append(f'<path d="M {P(60,150)} L {P(10,25)} L {P(-30,25)} L {P(-10,175)} Z" fill="url(#hull)" stroke="#9FB0C2" stroke-width="{1.5*k}"/>')
    s.append(f'<path d="M {P(-45,178)} L {P(80,170)} L {P(84,186)} L {P(-40,192)} Z" fill="#C9D5E1"/>')
    for ex in (-42,):
        s.append(f'<path d="M {P(ex,190)} L {P(ex-4,128)} L {P(ex+14,128)} L {P(ex+18,190)} Z" fill="url(#hull)" stroke="#9FB0C2" stroke-width="{1.2*k}"/>')
    # fuselage: lower lobe
    s.append(f'<path d="M {P(-10,165)} C {P(60,190)} {P(150,214)} {P(260,218)} L {P(870,220)} '
             f'C {P(930,220)} {P(965,205)} {P(968,186)} C {P(968,170)} {P(950,160)} {P(920,158)} L {P(100,150)} Z" fill="url(#hullBelly)"/>')
    # the famous hump: the oversized upper deck
    s.append(f'<path d="M {P(-10,165)} C {P(80,100)} {P(230,8)} {P(380,0)} L {P(740,-4)} '
             f'C {P(880,-6)} {P(966,76)} {P(962,170)} C {P(962,190)} {P(940,196)} {P(900,192)} '
             f'L {P(200,190)} C {P(120,190)} {P(40,180)} {P(-10,165)} Z" fill="url(#hull)"/>')
    # cargo door seam and a soft highlight along the top
    s.append(f'<path d="M {P(870,22)} C {P(915,60)} {P(932,120)} {P(934,170)}" fill="none" stroke="#B7C5D3" stroke-width="{2*k}"/>')
    s.append(f'<path d="M {P(330,14)} L {P(740,8)}" stroke="#FFFFFF" stroke-width="{7*k}" stroke-linecap="round" opacity="0.8"/>')
    # cockpit tucked low under the hump, at the nose
    s.append(f'<path d="M {P(905,176)} L {P(948,178)} L {P(955,190)} L {P(912,190)} Z" fill="#1B2A3A"/>')
    s.append(f'<path d="M {P(912,180)} L {P(944,181)}" stroke="#7FC4FF" stroke-width="{2*k}" opacity="0.7"/>')
    # near wing + engines
    s.append(f'<path d="M {P(440,198)} L {P(600,200)} L {P(520,330)} L {P(470,330)} Z" fill="url(#wing)" stroke="#8597AB" stroke-width="{1.2*k}"/>')
    for (ex, ey) in ((505, 228), (470, 290)):
        s.append(f'<rect x="{ox+ex*k}" y="{oy+ey*k}" width="{95*k}" height="{32*k}" rx="{16*k}" fill="url(#eng)" stroke="#8597AB" stroke-width="{1.2*k}"/>')
        s.append(f'<ellipse cx="{ox+(ex+93)*k}" cy="{oy+(ey+16)*k}" rx="{6*k}" ry="{14*k}" fill="#2A394A"/>')
        s.append(f'<ellipse cx="{ox+(ex-4)*k}" cy="{oy+(ey+16)*k}" rx="{4*k}" ry="{9*k}" fill="#5D6E80"/>')
    # nav light + belly shadow line
    s.append(glow_dot(ox - 30 * k, oy + 30 * k, 3 * k))
    s.append(f'<path d="M {P(150,214)} L {P(870,218)}" stroke="#8597AB" stroke-width="{1.5*k}" opacity="0.6"/>')
    return "".join(s)


body = [f'<rect width="{W}" height="{H}" fill="url(#dusk)"/>']
body.append(f'<circle cx="1260" cy="840" r="420" fill="url(#sun)"/>')
for _ in range(60):                      # first stars
    x, y = random.uniform(0, W), random.uniform(0, 380)
    body.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{random.uniform(0.6,1.6):.1f}" fill="#FFFFFF" opacity="{random.uniform(0.3,0.8):.2f}"/>')
body.append(clouds())

# plane: only a little bigger than Orb
k = 0.44
ox, oy = 600, 540
# wind/speed lines
for i, (y, L) in enumerate(((560, 220), (600, 160), (640, 260), (470, 140))):
    body.append(f'<line x1="{ox-60-i*15}" y1="{y}" x2="{ox-60-i*15-L}" y2="{y}" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.35"/>')
body.append(beluga(ox, oy, k))

# Orb sitting on the hump, leaning back into the wind, loving it
r = 62
hump_top = oy + 0 * k
cx, cy = ox + 560 * k, hump_top - 0.82 * r
spark_x, spark_y = cx + 0.78 * r - 4, cy - 1.53 * r
# the spark's contrail streams back as a rising line
trail_pts = [(spark_x, spark_y)]
for i in range(1, 10):
    trail_pts.append((spark_x - 40 - i * 80, spark_y + 10 + i * 22 - (10 if i % 2 else 0)))
body.append(trail(list(reversed(trail_pts)), w=3, opacity=0.75))
body.append(orb(cx, cy, r, eyes="happy" if False else "closed", mouth="grin", tilt=-10, antenna="full", legs="sit"))
# cheeks puffed by the wind + a couple of motion ticks on his antenna
body.append(f'<path d="M {cx-1.25*r} {cy-0.9*r} q -20 6 -40 0 M {cx-1.3*r} {cy-0.6*r} q -18 5 -34 0" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.6"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       + DEFS + DEFS2 + "".join(body) + "</svg>")
cairosvg.svg2png(bytestring=svg.encode(), write_to="/home/claude/orb_on_beluga.png")
print("ok")
