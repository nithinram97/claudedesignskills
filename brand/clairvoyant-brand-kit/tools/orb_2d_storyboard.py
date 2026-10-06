import math, os, re, cairosvg

OUT = "/home/claude/orb_storyboard"
os.makedirs(OUT, exist_ok=True)
W, H, CAP = 1280, 720, 96
FLOOR = 610
SLATE, BODY, AMBER, ICE, BLUSH = "#2F4356", "#4A6884", "#F5B942", "#CFE3F5", "#F28B82"

DEFS = f'''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#05080C"/><stop offset="0.75" stop-color="#14222F"/><stop offset="1" stop-color="#1B2C3D"/></linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#0E1823"/><stop offset="1" stop-color="#05090D"/></linearGradient>
<radialGradient id="body" cx="0.38" cy="0.32" r="0.75">
 <stop offset="0" stop-color="#6D8BA8"/><stop offset="0.55" stop-color="{BODY}"/><stop offset="1" stop-color="#22374A"/></radialGradient>
<radialGradient id="bodyGlow" cx="0.4" cy="0.35" r="0.75">
 <stop offset="0" stop-color="#FFFFFF"/><stop offset="0.6" stop-color="#E4EEF7"/><stop offset="1" stop-color="#A9C2D9"/></radialGradient>
<radialGradient id="amberGlow"><stop offset="0" stop-color="{AMBER}" stop-opacity="0.9"/>
 <stop offset="0.35" stop-color="{AMBER}" stop-opacity="0.35"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>
<radialGradient id="iceGlow"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/>
 <stop offset="0.3" stop-color="{ICE}" stop-opacity="0.45"/><stop offset="1" stop-color="{ICE}" stop-opacity="0"/></radialGradient>
<linearGradient id="bar" x1="0" y1="1" x2="0" y2="0">
 <stop offset="0" stop-color="#0D1620"/><stop offset="1" stop-color="#5FA8E8"/></linearGradient>
<linearGradient id="barA" x1="0" y1="1" x2="0" y2="0">
 <stop offset="0" stop-color="#2A1F0E"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>
</defs>'''


def stage(grid=True, monoliths=True):
    s = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    if monoliths:
        for x, w, h in ((60, 70, 260), (210, 50, 340), (980, 80, 300), (1150, 60, 220), (560, 40, 380)):
            s.append(f'<rect x="{x}" y="{FLOOR-h}" width="{w}" height="{h}" fill="#0C1620" opacity="0.8"/>')
    s.append(f'<rect y="{FLOOR}" width="{W}" height="{H-FLOOR}" fill="url(#floor)"/>')
    if grid:
        vx = W / 2
        for i in range(-16, 17):
            x2 = vx + i * 140
            s.append(f'<line x1="{vx + i*28}" y1="{FLOOR}" x2="{x2}" y2="{H}" stroke="#3E6E9A" stroke-width="1" opacity="0.45"/>')
        y = FLOOR
        for k in range(7):
            y += 4 + k * k * 2.2
            s.append(f'<line x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}" stroke="#3E6E9A" stroke-width="1" opacity="0.4"/>')
    # motes
    import random
    random.seed(3)
    for _ in range(70):
        x, y, r = random.uniform(0, W), random.uniform(0, FLOOR - 20), random.uniform(1, 2.6)
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r*3:.1f}" fill="url(#amberGlow)"/><circle cx="{x:.0f}" cy="{y:.0f}" r="{r*0.6:.1f}" fill="{AMBER}"/>')
    return "".join(s)


def glow_dot(x, y, r, kind="amber"):
    g = "amberGlow" if kind == "amber" else "iceGlow"
    c = AMBER if kind == "amber" else "#FFFFFF"
    return f'<circle cx="{x}" cy="{y}" r="{r*4}" fill="url(#{g})"/><circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>'


def trail(pts, color=AMBER, w=5, dashed=False, opacity=1):
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    dash = ' stroke-dasharray="14 12"' if dashed else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w*4}" stroke-linecap="round" stroke-linejoin="round" opacity="{0.12*opacity}"{dash}/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w*2}" stroke-linecap="round" stroke-linejoin="round" opacity="{0.25*opacity}"{dash}/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"{dash}/>')


def bar(x, h, w=78, amber=False, label=None):
    y = FLOOR - h
    g = "barA" if amber else "bar"
    top = AMBER if amber else "#9FD0FF"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="url(#{g})" stroke="{top}" stroke-opacity="0.5"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="5" rx="2" fill="{top}"/>'
            f'<rect x="{x}" y="{FLOOR}" width="{w}" height="{h*0.35}" fill="url(#{g})" opacity="0.18" transform="translate(0 {2*FLOOR}) scale(1 -1) translate(0 {-2*FLOOR + 0})"/>')


def orb(cx, cy, r, eyes="open", look=(0, 0), mouth="smile", tilt=0, antenna="full",
        legs="stand", glow=False, sweat=False, scale_y=1.0):
    """cx, cy = body centre. Feet land at cy + 1.55 r."""
    s = []
    sk = SLATE
    fill = "url(#bodyGlow)" if glow else "url(#body)"
    if glow:
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r*2.6}" fill="url(#iceGlow)"/>')
    # legs + feet
    if legs == "stand":
        L = [((-0.3, 0.8), (-0.42, 1.45), -0.45), ((0.3, 0.8), (0.42, 1.45), 0.45)]
    elif legs == "run":
        L = [((-0.25, 0.8), (-0.75, 1.25), -0.85), ((0.25, 0.8), (0.45, 1.45), 0.55)]
    elif legs == "hop":
        L = [((-0.3, 0.8), (-0.48, 1.25), -0.5), ((0.3, 0.8), (0.48, 1.25), 0.5)]
    elif legs == "tuck":
        L = [((-0.28, 0.8), (-0.35, 1.12), -0.36), ((0.28, 0.8), (0.35, 1.12), 0.36)]
    else:  # dangle: one leg up hooked, one flailing
        L = [((-0.25, 0.8), (-0.85, 1.3), -0.95), ((0.25, -0.2), (0.75, -1.25), 0.85)]
    legc = "#E9F1F8" if glow else sk
    for (a, b, fx) in L:
        s.append(f'<line x1="{cx+a[0]*r}" y1="{cy+a[1]*r}" x2="{cx+b[0]*r}" y2="{cy+b[1]*r}" stroke="{legc}" stroke-width="{0.2*r}" stroke-linecap="round"/>')
        fy = b[1] + (0.08 if b[1] > 0 else -0.08)
        s.append(f'<ellipse cx="{cx+fx*r}" cy="{cy+fy*r}" rx="{0.27*r}" ry="{0.14*r}" fill="{legc}"/>')
    # antenna
    if antenna in ("full", "stalk"):
        ac = AMBER
        s.append(f'<path d="M {cx+0.3*r} {cy-0.85*r} Q {cx+0.38*r} {cy-1.3*r} {cx+0.75*r} {cy-1.5*r}" fill="none" stroke="{ac}" stroke-width="{0.075*r}" stroke-linecap="round"/>')
        if antenna == "full":
            s.append(glow_dot(cx + 0.78 * r, cy - 1.53 * r, 0.14 * r))
        else:
            for a in (-60, -20, 20):
                t = math.radians(a)
                x0, y0 = cx + 0.78 * r, cy - 1.53 * r
                s.append(f'<line x1="{x0+0.12*r*math.cos(t)}" y1="{y0+0.12*r*math.sin(t)}" x2="{x0+0.3*r*math.cos(t)}" y2="{y0+0.3*r*math.sin(t)}" stroke="{AMBER}" stroke-width="{0.04*r}" stroke-linecap="round"/>')
    # body
    s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*scale_y}" fill="{fill}"/>')
    if not glow:
        s.append(f'<path d="M {cx-0.62*r} {cy+0.72*r} A {r} {r} 0 0 0 {cx+0.85*r} {cy+0.5*r}" fill="none" stroke="#7FC4FF" stroke-width="{0.05*r}" opacity="0.55"/>')
    # eyes
    lx, ly = look
    for sx in (-1, 1):
        ex, ey = cx + sx * 0.38 * r, cy - 0.12 * r
        ink = "#0B1118"
        if eyes == "closed":
            s.append(f'<path d="M {ex-0.2*r} {ey+0.04*r} Q {ex} {ey-0.2*r} {ex+0.2*r} {ey+0.04*r}" fill="none" stroke="{ink}" stroke-width="{0.06*r}" stroke-linecap="round"/>')
            continue
        big = 1.18 if eyes == "wide" else 1.0
        s.append(f'<ellipse cx="{ex}" cy="{ey}" rx="{0.27*r*big}" ry="{0.31*r*big}" fill="#F4F7FA"/>')
        pr = 0.62 if eyes == "wide" else 1.0
        px, py = ex + lx * 0.09 * r, ey + ly * 0.1 * r
        s.append(f'<ellipse cx="{px}" cy="{py}" rx="{0.16*r*pr}" ry="{0.19*r*pr}" fill="{ink}"/>')
        s.append(f'<circle cx="{px+0.06*r*pr}" cy="{py-0.08*r*pr}" r="{0.055*r*pr}" fill="#FFFFFF"/>')
        s.append(f'<circle cx="{px-0.05*r*pr}" cy="{py+0.07*r*pr}" r="{0.025*r*pr}" fill="#FFFFFF"/>')
        if eyes == "determined":
            s.append(f'<line x1="{ex-0.26*r}" y1="{ey-0.36*r - sx*0.06*r}" x2="{ex+0.26*r}" y2="{ey-0.36*r + sx*0.06*r}" stroke="{ink}" stroke-width="{0.06*r}" stroke-linecap="round"/>')
    for sx in (-1, 1):
        s.append(f'<ellipse cx="{cx+sx*0.64*r}" cy="{cy+0.2*r}" rx="{0.14*r}" ry="{0.07*r}" fill="{BLUSH}" opacity="0.65"/>')
    ink = "#0B1118"
    if mouth == "smile":
        s.append(f'<path d="M {cx-0.16*r} {cy+0.27*r} Q {cx} {cy+0.42*r} {cx+0.16*r} {cy+0.27*r}" fill="none" stroke="{ink}" stroke-width="{0.055*r}" stroke-linecap="round"/>')
    elif mouth == "o":
        s.append(f'<ellipse cx="{cx}" cy="{cy+0.33*r}" rx="{0.07*r}" ry="{0.09*r}" fill="{ink}"/>')
    elif mouth == "panic":
        s.append(f'<path d="M {cx-0.18*r} {cy+0.33*r} q {0.06*r} {-0.07*r} {0.12*r} 0 t {0.12*r} 0 t {0.12*r} 0" fill="none" stroke="{ink}" stroke-width="{0.05*r}" stroke-linecap="round"/>')
    elif mouth == "grin":
        s.append(f'<path d="M {cx-0.2*r} {cy+0.24*r} Q {cx} {cy+0.52*r} {cx+0.2*r} {cy+0.24*r} Z" fill="{ink}"/>')
    elif mouth == "flat":
        s.append(f'<line x1="{cx-0.12*r}" y1="{cy+0.32*r}" x2="{cx+0.12*r}" y2="{cy+0.32*r}" stroke="{ink}" stroke-width="{0.05*r}" stroke-linecap="round"/>')
    if sweat:
        s.append(f'<path d="M {cx-0.95*r} {cy-0.55*r} q {-0.08*r} {0.16*r} 0 {0.2*r} q {0.08*r} {-0.04*r} 0 {-0.2*r}" fill="#9FD0FF"/>')
        s.append(f'<path d="M {cx+1.0*r} {cy-0.35*r} q {-0.06*r} {0.12*r} 0 {0.15*r} q {0.06*r} {-0.03*r} 0 {-0.15*r}" fill="#9FD0FF"/>')
    return f'<g transform="rotate({tilt} {cx} {cy})">' + "".join(s) + "</g>"


def speed_lines(x, y, n=4, length=70, dx=-1, gap=16, color="#9FD0FF"):
    return "".join(f'<line x1="{x}" y1="{y+i*gap}" x2="{x+dx*length*(1-i*0.12)}" y2="{y+i*gap}" stroke="{color}" stroke-width="3" stroke-linecap="round" opacity="{0.7-i*0.12}"/>' for i in range(n))


def note_arrow(x1, y1, x2, y2, text=None):
    s = (f'<path d="M {x1} {y1} Q {(x1+x2)/2} {min(y1,y2)-60} {x2} {y2}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="6 7" opacity="0.6"/>'
         f'<circle cx="{x2}" cy="{y2}" r="4" fill="#FFFFFF" opacity="0.7"/>')
    return s


def caption(num, tc, title, action, camera):
    return (f'<rect y="{H}" width="{W}" height="{CAP}" fill="#0A0F15"/>'
            f'<rect y="{H}" width="{W}" height="2" fill="{AMBER}" opacity="0.7"/>'
            f'<text x="28" y="{H+40}" font-family="DejaVu Sans" font-weight="bold" font-size="26" fill="{AMBER}">{num:02d}</text>'
            f'<text x="78" y="{H+40}" font-family="DejaVu Sans" font-weight="bold" font-size="22" fill="#FFFFFF" letter-spacing="2">{title}</text>'
            f'<text x="{W-28}" y="{H+40}" font-family="DejaVu Sans Mono" font-size="18" fill="#9CACBC" text-anchor="end">{tc}</text>'
            f'<text x="78" y="{H+70}" font-family="DejaVu Sans" font-size="16" fill="#C9D3DD">{action}</text>'
            f'<text x="{W-28}" y="{H+70}" font-family="DejaVu Sans" font-size="14" fill="#7F92A6" text-anchor="end" font-style="italic">{camera}</text>')


def save(num, tc, title, action, camera, body, name):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H+CAP}" viewBox="0 0 {W} {H+CAP}">'
           + DEFS + '<g>' + body + '</g>' + caption(num, tc, title, action, camera) + '</svg>')
    path = f"{OUT}/{num:02d}_{name}.png"
    cairosvg.svg2png(bytestring=svg.encode(), write_to=path)
    return path


R = 70
FEET = lambda r: FLOOR - 1.55 * r   # body centre y when standing on the floor


def on(y_top, r):  # body centre y when standing on a surface at y_top
    return y_top - 1.55 * r


panels = []

# 1 — idle
b = stage() + orb(460, FEET(R), R, look=(0.3, -0.4), mouth="smile")
b += "".join(f'<path d="M {460+0.78*R+dx} {FEET(R)-1.53*R-30} l {6*s} -12" stroke="{AMBER}" stroke-width="3" stroke-linecap="round"/>' for dx, s in ((-18, -1), (0, 0), (18, 1)))
b += '<text x="560" y="300" font-family="DejaVu Sans" font-size="30" fill="#FFFFFF" opacity="0.85">?</text>'
panels.append((1, "0:00 – 0:01", "IDLE", "Orb idles on the empty grid. His antenna tip starts to twitch on its own.", "Wide, eye level, slow push-in", b, "idle"))

# 2 — spark escapes
cx, cy = 400, FEET(R)
tip = (cx + 0.78 * R, cy - 1.53 * R)
b = stage()
b += trail([tip, (560, 280), (720, 240), (880, 200)], w=4)
b += glow_dot(880, 200, 13)
b += orb(cx, cy, R, eyes="wide", look=(1, -1), mouth="o", antenna="stalk", tilt=-6)
b += speed_lines(860, 190, 3, 50, -1, 10, AMBER)
panels.append((2, "0:01 – 0:02", "THE SPARK ESCAPES", "The tip pops off and zips away, drawing an amber line behind it. Orb is stunned.", "Whip-pan follows the spark, then snaps back to Orb", b, "spark-escapes"))

# 3 — chase
bars3 = [(600, 70), (720, 120), (840, 175)]
b = stage()
for x, h in bars3:
    b += bar(x, h)
b += f'<rect x="960" y="{FLOOR-40}" width="78" height="40" rx="4" fill="url(#bar)" opacity="0.6"/>'
b += trail([(560, 470), (640, 520 - 70 - 20), (760, FLOOR - 120 - 25), (880, FLOOR - 175 - 25), (1000, FLOOR - 230), (1080, 330)], w=4)
b += glow_dot(1080, 330, 13)
b += orb(380, FEET(R), R, eyes="determined", look=(1, 0), mouth="flat", antenna="stalk", legs="run", tilt=10)
b += speed_lines(290, 470, 4, 80)
panels.append((3, "0:02 – 0:04", "THE CHASE", "Orb waddles after it. Bars grow out of the floor under the line as it climbs.", "Side-on tracking shot, camera keeps pace with Orb", b, "chase"))

# 4 — climb
bars4 = [(240, 70), (360, 120), (480, 175), (600, 230), (720, 290)]
b = stage()
for x, h in bars4:
    b += bar(x, h)
b += trail([(279, FLOOR - 95), (399, FLOOR - 145), (519, FLOOR - 200), (639, FLOOR - 255), (759, FLOOR - 315), (900, 230)], w=4)
b += glow_dot(900, 230, 12)
r4 = 52
b += note_arrow(519, on(FLOOR - 175, r4) + 1.2 * r4, 640, FLOOR - 236)
b += orb(560, on(FLOOR - 175, r4) - 70, r4, eyes="determined", look=(1, -0.5), mouth="grin", antenna="stalk", legs="hop", tilt=8)
panels.append((4, "0:04 – 0:05", "CLIMBING THE CHART", "He hops bar to bar like stairs, gaining on the spark with every jump.", "Camera cranes up as he climbs", b, "climb"))

# 5 — stumble
b = stage()
bars5 = [(160, 120), (280, 175), (400, 230), (520, 150), (640, 300), (760, 360)]
for i, (x, h) in enumerate(bars5):
    b += bar(x, h)
b += f'<text x="559" y="{FLOOR-160}" font-family="DejaVu Sans" font-size="15" fill="#FF8A80" text-anchor="middle">DIP</text>'
b += trail([(199, FLOOR - 145), (319, FLOOR - 200), (439, FLOOR - 255), (559, FLOOR - 175), (679, FLOOR - 325), (799, FLOOR - 385), (920, 190)], w=4)
b += glow_dot(920, 190, 11)
r5 = 50
# hanging off the left edge of the tall bar after misjudging the dip
hx, hy = 640 - 0.55 * r5, FLOOR - 300 + 1.05 * r5
b += orb(hx, hy, r5, eyes="wide", look=(1, -1), mouth="panic", antenna="stalk", legs="dangle", tilt=-18, sweat=True)
b += f'<text x="{hx-120}" y="{hy-40}" font-family="DejaVu Sans" font-size="40" font-weight="bold" fill="#FFFFFF" opacity="0.8">!!</text>'
panels.append((5, "0:05 – 0:07", "THE STUMBLE", "A dip bar throws off his rhythm. He slips and dangles by one foot, then scrambles up.", "Tight on Orb, a beat of held breath", b, "stumble"))

# 6 — the edge
b = stage()
bars6 = [(140, 90), (240, 140), (340, 190), (440, 130), (540, 260), (640, 330)]
for i, (x, h) in enumerate(bars6):
    b += bar(x, h, w=70, amber=(i == len(bars6) - 1))
b += trail([(175, FLOOR - 110), (275, FLOOR - 160), (375, FLOOR - 210), (475, FLOOR - 150), (575, FLOOR - 280), (675, FLOOR - 350)], w=4)
b += trail([(675, FLOOR - 350), (840, 200), (1010, 130), (1120, 95)], w=3, opacity=0.8)
b += glow_dot(1120, 95, 10)
r6 = 34
b += orb(690, on(FLOOR - 330, r6), r6, eyes="open", look=(1, -1), mouth="o", antenna="stalk")
b += f'<text x="900" y="420" font-family="DejaVu Sans" font-size="16" fill="#7F92A6" font-style="italic">no more bars. no more data.</text>'
panels.append((6, "0:07 – 0:09", "THE EDGE", "Top of the tallest bar. The spark has flown past the end of the chart into empty space.", "Wide reveal: tiny Orb, huge void", b, "edge"))

# 7 — foresight (the climax beat)
b = stage(monoliths=False)
b += bar(300, 330, w=220, amber=True)
r7 = 72
ox, oy = 410, on(FLOOR - 330, r7)
b += orb(ox, oy, r7, eyes="closed", mouth="smile", antenna="stalk", glow=True)
gx, gy = 1010, 150
b += trail([(ox + 60, oy - 90), (650, 160), (820, 110), (gx, gy)], w=4, dashed=True)
b += f'<circle cx="{gx}" cy="{gy}" r="26" fill="none" stroke="{AMBER}" stroke-width="3" stroke-dasharray="7 6"/>'
b += f'<text x="{gx}" y="{gy+58}" font-family="DejaVu Sans" font-size="15" fill="{AMBER}" text-anchor="middle">where it WILL be</text>'
b += glow_dot(1180, 330, 11)
b += f'<path d="M 1180 330 Q 1150 220 {gx+30} {gy+14}" fill="none" stroke="{AMBER}" stroke-width="2" stroke-dasharray="3 8" opacity="0.6"/>'
b += f'<text x="1180" y="370" font-family="DejaVu Sans" font-size="14" fill="#9CACBC" text-anchor="middle">where it is</text>'
panels.append((7, "0:09 – 0:10", "FORESIGHT", "He stops chasing. Eyes close, body glows, a dashed forecast line projects to where the spark will be.", "Slow push-in, everything else dims", b, "foresight"))

# 8 — leap
b = stage(monoliths=False)
b += bar(160, 330, w=200, amber=True)
b += trail([(300, 250), (480, 140), (650, 110)], w=4, dashed=True, opacity=0.55)
b += f'<path d="M 300 250 Q 420 120 600 140" fill="none" stroke="{ICE}" stroke-width="22" opacity="0.15" stroke-linecap="round"/>'
b += f'<path d="M 300 250 Q 420 120 600 140" fill="none" stroke="#FFFFFF" stroke-width="5" opacity="0.8" stroke-linecap="round"/>'
b += orb(690, 160, 62, eyes="determined", look=(1, -0.3), mouth="grin", antenna="stalk", legs="tuck", glow=True, tilt=22)
b += glow_dot(940, 150, 12)
b += speed_lines(990, 150, 3, 60, 1, 12, AMBER)
panels.append((8, "0:10 – 0:11", "LEAP OF FAITH", "He jumps off the last bar into empty space, riding the dashed line. The spark curves in to meet him.", "Slow motion, camera arcs with the jump", b, "leap"))

# 9 — the catch
b = stage(monoliths=False)
cx9, cy9 = 640, 330
for i in range(16):
    a = math.radians(i * 22.5)
    r1, r2 = 150, 330 + (i % 2) * 90
    b += f'<line x1="{cx9+r1*math.cos(a)}" y1="{cy9+r1*math.sin(a)}" x2="{cx9+r2*math.cos(a)}" y2="{cy9+r2*math.sin(a)}" stroke="{AMBER if i%2 else ICE}" stroke-width="{6 if i%2 else 3}" opacity="0.55" stroke-linecap="round"/>'
b += f'<circle cx="{cx9}" cy="{cy9-120}" r="220" fill="url(#amberGlow)"/>'
b += orb(cx9, cy9, 100, eyes="closed", mouth="grin", antenna="full", legs="tuck", glow=True)
b += f'<circle cx="{cx9}" cy="{cy9}" r="250" fill="none" stroke="#FFFFFF" stroke-width="4" opacity="0.6"/>'
panels.append((9, "0:11", "THE CATCH", "Spark and Orb meet in mid-air. It snaps back onto his antenna. Flash, and a shockwave ring.", "Freeze-frame for 4 frames, then smash cut", b, "catch"))

# 10 — the reveal (the scene drew the logo)
S, CX, CY = 2.6, 640, 330
X = lambda x: CX + (x - 190) * S
Y = lambda y: CY + (y - 140) * S
b = stage(monoliths=False)
arc = f'M {X(236)} {Y(84)} A {56*S} {56*S} 0 1 0 {X(236)} {Y(146)}'
b += f'<path d="{arc}" fill="none" stroke="{ICE}" stroke-width="{12*S*2.2}" opacity="0.14"/>'
b += f'<path d="{arc}" fill="none" stroke="#FFFFFF" stroke-width="{12*S}"/>'
b += f'<path d="M {X(225)} {Y(91)} A {42*S} {42*S} 0 1 0 {X(225)} {Y(139)}" fill="none" stroke="#FFFFFF" stroke-width="{2*S}" opacity="0.8"/>'
b += f'<line x1="{X(152)}" y1="{Y(150)}" x2="{X(228)}" y2="{Y(150)}" stroke="#FFFFFF" stroke-width="{2*S}"/>'
for (bx, bh, a) in ((158, 18, 0), (174, 26, 0), (190, 34, 0), (206, 44, 1)):
    b += f'<rect x="{X(bx)}" y="{Y(150-bh)}" width="{10*S}" height="{bh*S}" fill="{AMBER if a else "url(#bar)"}" stroke="#9FD0FF" stroke-opacity="0.4"/>'
b += trail([(X(211), Y(106)), (X(256), Y(88))], w=3 * S)
b += f'<path d="M {X(148)} {Y(168)} L {X(190)} {Y(210)} L {X(232)} {Y(168)}" fill="none" stroke="#FFFFFF" stroke-width="{6*S}" stroke-linecap="round" stroke-linejoin="round"/>'
b += f'<line x1="{X(158)}" y1="{Y(218)}" x2="{X(222)}" y2="{Y(218)}" stroke="#FFFFFF" stroke-width="{6*S}" stroke-linecap="round"/>'
b += orb(X(262), Y(80), 16, eyes="closed", mouth="grin", antenna="full", legs="stand")
labels = [((X(118), Y(70)), "his catch shockwave → the C"), ((X(108), Y(142)), "the bars he climbed →"),
          ((X(300), Y(112)), "the spark's trail → breakout line")]
for (lx, ly), t in labels:
    b += f'<text x="{lx}" y="{ly}" font-family="DejaVu Sans" font-size="15" fill="#9CACBC" font-style="italic" text-anchor="middle">{t}</text>'
panels.append((10, "0:11 – 0:13", "THE REVEAL", "Camera pulls back: the shockwave breaks open where the trail passes through. The chase drew the logo.", "Fast pull-back, ease out", b, "reveal"))

# 11 — melt into the mark
b = stage(monoliths=False)
b += b10 if False else ""
mark = open("/home/claude/out/clairvoyant-mark-dark.svg").read()
inner = re.search(r"<title>.*?</title>(.*)</svg>", mark, re.S).group(1)
vb = re.search(r'viewBox="([^"]+)"', mark).group(1).split()
mw, mh = float(vb[2]), float(vb[3])
sc = 2.6
b += f'<g transform="translate({640 - mw*sc/2} {340 - mh*sc/2}) scale({sc}) translate({-float(vb[0])} {-float(vb[1])})">{inner}</g>'
dot_x, dot_y = 640 - mw * sc / 2 + (130 - float(vb[0])) * sc, 340 - mh * sc / 2 + (34 - float(vb[1])) * sc
b += f'<circle cx="{dot_x}" cy="{dot_y}" r="70" fill="url(#iceGlow)"/>'
b += orb(dot_x + 30, dot_y - 30, 18, eyes="closed", mouth="smile", antenna="stalk", legs="tuck", glow=True, scale_y=0.8)
for i in range(8):
    a = math.radians(200 + i * 18)
    b += f'<circle cx="{dot_x+90*math.cos(a)}" cy="{dot_y+90*math.sin(a)}" r="{3+i%3}" fill="#FFFFFF" opacity="0.7"/>'
panels.append((11, "0:13 – 0:14", "MELT INTO THE MARK", "Orb glows white and folds himself into the breakout point. The scene resolves into the clean mark.", "Locked off, front-on", b, "melt"))

# 12 — title card
b = f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
lock = open("/home/claude/out/clairvoyant-lockup-stacked-dark.svg").read()
inner = re.search(r"<title>.*?</title>(.*)</svg>", lock, re.S).group(1)
vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', lock).group(1).split()]
sc = 470 / vb[3]
b += f'<circle cx="640" cy="330" r="380" fill="url(#iceGlow)" opacity="0.18"/>'
b += f'<g transform="translate({640 - vb[2]*sc/2} {70}) scale({sc}) translate({-vb[0]} {-vb[1]})">{inner}</g>'
b += f'<text x="640" y="640" font-family="DejaVu Sans" font-size="22" fill="#9CACBC" text-anchor="middle" letter-spacing="3">We don’t chase the number. We see where it’s going.</text>'
panels.append((12, "0:14 – 0:16", "TITLE", "Official stacked lockup, dark variant. Tagline fades in under the wordmark.", "Hold 2s, fade to black", b, "title"))

paths = [save(*p) for p in panels]
print("\n".join(paths))

# contact sheet
from PIL import Image
ims = [Image.open(p).convert("RGB") for p in paths]
tw, th = 640, int(640 * (H + CAP) / W)
cols, rows = 2, (len(ims) + 1) // 2
sheet = Image.new("RGB", (cols * tw + 30, rows * th + (rows + 1) * 10), (6, 9, 13))
for i, im in enumerate(ims):
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (10 + (i % 2) * (tw + 10), 10 + (i // 2) * (th + 10)))
sheet.save("/home/claude/orb_storyboard_sheet.png")
