import math, os, re
src = open("/tmp/claude-0/-home-claude/b526ec50-437e-5e03-99f2-649ee89e85be/scratchpad/board.py").read()
exec(src[:src.index("panels = []")])

OUT = "/home/claude/orb_grin_storyboard"
os.makedirs(OUT, exist_ok=True)

cx, R = 640, 110
cy = FLOOR - 1.55 * R
s = R / 62.0                       # logo units -> px (ring outer radius = body radius)
X = lambda x: cx + (x - 190) * s
Y = lambda y: cy + (y - 115) * s
INK, MOUTH, TONGUE = "#0B1118", "#3A1520", "#E86A6A"


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def legs(v=0.0, col=SLATE):
    """v=0: Orb's legs and feet. v=1: the logo's V stand and groundline."""
    out = []
    for sx, top_v, foot_v in ((-1, (X(148), Y(168)), (X(158), Y(218))), (1, (X(232), Y(168)), (X(222), Y(218)))):
        t0 = (cx + sx * 0.3 * R, cy + 0.8 * R)
        b0 = (cx + sx * 0.42 * R, cy + 1.45 * R)
        t1, b1 = top_v, (X(190), Y(210))
        tx, ty = t0[0] + (t1[0] - t0[0]) * v, t0[1] + (t1[1] - t0[1]) * v
        bx, by = b0[0] + (b1[0] - b0[0]) * v, b0[1] + (b1[1] - b0[1]) * v
        w = 0.2 * R + (6 * s - 0.2 * R) * v
        out.append(f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round"/>')
        # foot -> half of the groundline
        f0 = (cx + sx * 0.45 * R, cy + 1.53 * R)
        fx = f0[0] + ((X(190) + foot_v[0]) / 2 - f0[0]) * v
        fy = f0[1] + (foot_v[1] - f0[1]) * v
        rx = 0.27 * R + ((X(222) - X(158)) / 4 + 3 * s - 0.27 * R) * v
        ry = 0.14 * R + (3 * s - 0.14 * R) * v
        out.append(f'<ellipse cx="{fx:.1f}" cy="{fy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{col}"/>')
    return "".join(out)


def antenna(a=0.0, col=AMBER):
    """a=0: antenna on his head. a=1: the breakout line and point."""
    p0 = (cx + 0.3 * R, cy - 0.85 * R)
    p1 = (cx + 0.78 * R, cy - 1.53 * R)
    q0, q1 = (X(211), Y(106)), (X(258), Y(87))
    b = (p0[0] + (q0[0] - p0[0]) * a, p0[1] + (q0[1] - p0[1]) * a)
    e = (p1[0] + (q1[0] - p1[0]) * a, p1[1] + (q1[1] - p1[1]) * a)
    ctrl = (cx + 0.38 * R, cy - 1.3 * R)
    mid = ((b[0] + e[0]) / 2, (b[1] + e[1]) / 2)
    c = (ctrl[0] + (mid[0] - ctrl[0]) * a, ctrl[1] + (mid[1] - ctrl[1]) * a)
    w = 0.075 * R + (3 * s - 0.075 * R) * a
    r = 0.14 * R + (5 * s - 0.14 * R) * a
    return (f'<path d="M {b[0]:.1f} {b[1]:.1f} Q {c[0]:.1f} {c[1]:.1f} {e[0]:.1f} {e[1]:.1f}" fill="none" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
            + glow_dot(round(e[0], 1), round(e[1], 1), round(r, 1)))


def body():
    return f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#body)"/>' \
           f'<path d="M {cx-0.62*R} {cy+0.72*R} A {R} {R} 0 0 0 {cx+0.85*R} {cy+0.5*R}" fill="none" stroke="#7FC4FF" stroke-width="{0.05*R}" opacity="0.55"/>'


def eye_open(ex, ey, sc=1.0, look=(0, 0)):
    px, py = ex + look[0] * 0.09 * R * sc, ey + look[1] * 0.1 * R * sc
    return (f'<ellipse cx="{ex}" cy="{ey}" rx="{0.27*R*sc}" ry="{0.31*R*sc}" fill="#F4F7FA"/>'
            f'<ellipse cx="{px}" cy="{py}" rx="{0.16*R*sc}" ry="{0.19*R*sc}" fill="{INK}"/>'
            f'<circle cx="{px+0.06*R*sc}" cy="{py-0.08*R*sc}" r="{0.055*R*sc}" fill="#FFFFFF"/>')


def eye_happy(ex, ey, sc=1.0):
    return f'<path d="M {ex-0.2*R*sc} {ey+0.05*R*sc} Q {ex} {ey-0.22*R*sc} {ex+0.2*R*sc} {ey+0.05*R*sc}" fill="none" stroke="{INK}" stroke-width="{0.065*R}" stroke-linecap="round"/>'


def brow(ex, ey, slant, sc=1.0):
    dx, dy = 0.15 * R * sc * math.cos(math.radians(slant)), 0.15 * R * sc * math.sin(math.radians(slant))
    return f'<line x1="{ex-dx}" y1="{ey-dy}" x2="{ex+dx}" y2="{ey+dy}" stroke="{INK}" stroke-width="{0.06*R}" stroke-linecap="round"/>'


def blush(sc=1.0, dy=0.2):
    return "".join(f'<ellipse cx="{cx+sx*0.64*R}" cy="{cy+dy*R}" rx="{0.14*R*sc}" ry="{0.07*R*sc}" fill="{BLUSH}" opacity="0.7"/>' for sx in (-1, 1))


def ticks(x, y, n=3, ang=0, length=22, col="#FFFFFF"):
    out = []
    for i in range(n):
        a = math.radians(ang - 40 + i * 40)
        out.append(f'<line x1="{x+12*math.cos(a):.1f}" y1="{y+12*math.sin(a):.1f}" x2="{x+(12+length)*math.cos(a):.1f}" y2="{y+(12+length)*math.sin(a):.1f}" stroke="{col}" stroke-width="3" stroke-linecap="round" opacity="0.8"/>')
    return "".join(out)


def ring(col, width=None, interior=None, interior_op=1.0, gap_deg=34):
    """The open C: centre radius 56 units, stroke 12, gap facing right."""
    rr = 56 * s
    a0, a1 = math.radians(gap_deg), math.radians(360 - gap_deg)
    x0, y0 = cx + rr * math.cos(a0), cy - rr * math.sin(a0)
    x1, y1 = cx + rr * math.cos(a1), cy - rr * math.sin(a1)
    out = ""
    if interior:
        ri = 50 * s
        out += (f'<path d="M {cx+ri*math.cos(a0):.1f} {cy-ri*math.sin(a0):.1f} A {ri:.1f} {ri:.1f} 0 1 0 {cx+ri*math.cos(a1):.1f} {cy-ri*math.sin(a1):.1f} Z" '
                f'fill="{interior}" opacity="{interior_op}"/>')
    out += f'<path d="M {x0:.1f} {y0:.1f} A {rr:.1f} {rr:.1f} 0 1 0 {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{width or 12*s:.1f}"/>'
    return out


panels = []

# 1 — proud
b = stage(monoliths=False) + legs() + antenna() + body()
b += eye_open(cx - 0.38 * R, cy - 0.12 * R) + eye_open(cx + 0.38 * R, cy - 0.12 * R)
b += blush() + f'<path d="M {cx-0.16*R} {cy+0.27*R} Q {cx} {cy+0.42*R} {cx+0.16*R} {cy+0.27*R}" fill="none" stroke="{INK}" stroke-width="{0.055*R}" stroke-linecap="round"/>'
panels.append((1, "0:00", "PROUD", "Orb stands centre stage, chest out, looking straight at us.", "Locked off, front-on, medium shot", b, "proud"))

# 2 — cheeky smirk + wink
b = stage(monoliths=False) + legs() + antenna() + body()
b += eye_open(cx - 0.38 * R, cy - 0.12 * R, look=(0.6, 0)) + eye_happy(cx + 0.38 * R, cy - 0.1 * R)
b += brow(cx - 0.38 * R, cy - 0.5 * R, 8) + brow(cx + 0.38 * R, cy - 0.55 * R, -14)
b += blush()
b += (f'<path d="M {cx-0.22*R} {cy+0.24*R} Q {cx-0.02*R} {cy+0.52*R} {cx+0.5*R} {cy+0.12*R} Q {cx+0.1*R} {cy+0.3*R} {cx-0.22*R} {cy+0.24*R} Z" fill="{MOUTH}" stroke="{INK}" stroke-width="{0.04*R}" stroke-linejoin="round"/>'
      f'<ellipse cx="{cx+0.05*R}" cy="{cy+0.36*R}" rx="{0.12*R}" ry="{0.05*R}" fill="{TONGUE}"/>')
b += glow_dot(round(cx + 0.66 * R, 1), round(cy - 0.32 * R, 1), 5, "ice")
panels.append((2, "0:01", "CHEEKY", "A lopsided grin and a wink. The right corner of his smile starts to stretch.", "Tiny push-in", b, "cheeky"))

# 3 — wider...
b = stage(monoliths=False) + legs() + antenna() + body()
b += eye_happy(cx - 0.34 * R, cy - 0.46 * R, 0.8) + eye_happy(cx + 0.24 * R, cy - 0.52 * R, 0.8)
b += brow(cx - 0.34 * R, cy - 0.72 * R, 0, 0.8) + brow(cx + 0.24 * R, cy - 0.78 * R, -10, 0.8)
b += blush(0.9, -0.08)
b += (f'<path d="M {cx-0.62*R} {cy+0.0*R} Q {cx-0.15*R} {cy+0.98*R} {cx+0.97*R} {cy-0.2*R} Q {cx+0.25*R} {cy+0.18*R} {cx-0.62*R} {cy+0.0*R} Z" fill="{MOUTH}" stroke="{INK}" stroke-width="{0.04*R}" stroke-linejoin="round"/>'
      f'<ellipse cx="{cx+0.05*R}" cy="{cy+0.5*R}" rx="{0.3*R}" ry="{0.1*R}" fill="{TONGUE}"/>')
b += ticks(cx + 0.98 * R, cy - 0.22 * R, ang=-20)
panels.append((3, "0:01 – 0:02", "WIDER…", "The grin keeps growing, squeezing his eyes up. The corner reaches the edge of his face.", "Hold, slight camera shake", b, "wider"))

# 4 — pop! the smile breaks through: he IS the C
b = stage(monoliths=False) + legs() + antenna()
b += ring(SLATE, interior=MOUTH)
b += f'<ellipse cx="{cx}" cy="{cy+0.55*R}" rx="{0.5*R}" ry="{0.16*R}" fill="{TONGUE}"/>'
b += eye_open(cx - 0.3 * R, cy - 0.12 * R, 0.75, look=(0, 1)) + eye_open(cx + 0.12 * R, cy - 0.22 * R, 0.75, look=(0, 1))
b += "".join(f'<line x1="{x}" y1="{cy-0.55*R}" x2="{x}" y2="{cy-0.42*R}" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.6"/>' for x in (cx - 0.3 * R, cx + 0.12 * R))
b += ticks(cx + R * 0.95, cy, n=4, ang=0, length=34, col=AMBER)
b += f'<text x="{cx+1.35*R}" y="{cy-0.2*R}" font-family="DejaVu Sans" font-weight="bold" font-size="40" fill="#FFFFFF" opacity="0.85">POP!</text>'
panels.append((4, "0:02", "POP!", "The smile breaks through his cheek: his body is now the open C, the gap is his grin. His eyes tumble inside.", "Snap zoom-in on the pop", b, "pop"))

# 5 — eyes become bars
b = stage(monoliths=False) + legs(0.15) + antenna(0.55)
b += ring(mix(SLATE, "#DCE6EF", 0.5), interior=MOUTH, interior_op=0.45)
b += f'<line x1="{X(152)}" y1="{Y(150)}" x2="{X(228)}" y2="{Y(150)}" stroke="{mix(TONGUE, "#FFFFFF", 0.4)}" stroke-width="{2*s+2}" stroke-linecap="round"/>'
for bx, bh, col, eye in ((158, 18, "#F4F7FA", True), (174, 26, "#F4F7FA", True), (190, 34, mix(BLUSH, "#FFFFFF", 0.35), False), (206, 26, AMBER, False)):
    b += f'<rect x="{X(bx)}" y="{Y(150-bh)}" width="{10*s}" height="{bh*s}" rx="{2*s}" fill="{col}"/>'
    if eye:
        b += f'<circle cx="{X(bx+5)}" cy="{Y(150-bh)+6*s}" r="{2.6*s}" fill="{INK}"/><circle cx="{X(bx+5)+1.2*s}" cy="{Y(150-bh)+4.8*s}" r="{0.9*s}" fill="#FFFFFF"/>'
b += f'<path d="M {X(211)} {Y(124)} l 0 {-14}" stroke="{AMBER}" stroke-width="3" stroke-dasharray="3 4"/>'
panels.append((5, "0:02 – 0:03", "EYES TO BARS", "His eyes land as two bars (still peeking), his cheeks become the third, his tongue flattens into the baseline. The amber bar rises.", "Hold", b, "eyes-to-bars"))

# 6 — stand tall: antenna out through the gap, legs to V
b = stage(monoliths=False) + legs(0.75, mix(SLATE, "#FFFFFF", 0.7)) + antenna(0.92)
b += ring(mix(SLATE, "#FFFFFF", 0.85))
b += f'<path d="M {X(225)} {Y(91)} A {42*s} {42*s} 0 0 0 {X(190)-42*s*0.2:.1f} {Y(115)-42*s*0.98:.1f}" fill="none" stroke="#FFFFFF" stroke-width="{2*s}" opacity="0.7"/>'
b += f'<line x1="{X(152)}" y1="{Y(150)}" x2="{X(228)}" y2="{Y(150)}" stroke="#FFFFFF" stroke-width="{2*s}"/>'
for bx, bh, col in ((158, 18, "#FFFFFF"), (174, 26, "#FFFFFF"), (190, 34, "#FFFFFF"), (206, 44, AMBER)):
    b += f'<rect x="{X(bx)}" y="{Y(150-bh)}" width="{10*s}" height="{bh*s}" fill="{col}"/>'
b += ticks(X(232) + 10, Y(190), n=3, ang=20, col="#9FD0FF") + ticks(X(148) - 10, Y(190), n=3, ang=160, col="#9FD0FF")
panels.append((6, "0:03", "STAND TALL", "His antenna slides out through the gap as the breakout line. Legs swing into the V, feet merge into the groundline.", "Slow pull-back begins", b, "stand-tall"))

# 7 — the mark (exact logo geometry) with a parting wink-sparkle
b = f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
b += ring("#FFFFFF")
b += f'<path d="M {X(225)} {Y(91)} A {42*s} {42*s} 0 1 0 {X(225)} {Y(139)}" fill="none" stroke="#FFFFFF" stroke-width="{2*s}"/>'
b += f'<line x1="{X(152)}" y1="{Y(150)}" x2="{X(228)}" y2="{Y(150)}" stroke="#FFFFFF" stroke-width="{2*s}" stroke-linecap="round"/>'
for bx, bh, col in ((158, 18, "#FFFFFF"), (174, 26, "#FFFFFF"), (190, 34, "#FFFFFF"), (206, 44, AMBER)):
    b += f'<rect x="{X(bx)}" y="{Y(150-bh)}" width="{10*s}" height="{bh*s}" rx="{s}" fill="{col}"/>'
b += f'<line x1="{X(211)}" y1="{Y(106)}" x2="{X(256)}" y2="{Y(88)}" stroke="{AMBER}" stroke-width="{3*s}" stroke-linecap="round"/>'
b += glow_dot(round(X(258), 1), round(Y(87), 1), round(5 * s, 1))
b += f'<path d="M {X(148)} {Y(168)} L {X(190)} {Y(210)} L {X(232)} {Y(168)}" fill="none" stroke="#FFFFFF" stroke-width="{6*s}" stroke-linecap="round" stroke-linejoin="round"/>'
b += f'<line x1="{X(158)}" y1="{Y(218)}" x2="{X(222)}" y2="{Y(218)}" stroke="#FFFFFF" stroke-width="{6*s}" stroke-linecap="round"/>'
sx_, sy_ = X(258) + 14, Y(87) - 16
b += f'<path d="M {sx_} {sy_-16} L {sx_+4} {sy_-4} L {sx_+16} {sy_} L {sx_+4} {sy_+4} L {sx_} {sy_+16} L {sx_-4} {sy_+4} L {sx_-16} {sy_} L {sx_-4} {sy_-4} Z" fill="#FFFFFF"/>'
panels.append((7, "0:03 – 0:04", "THE MARK", "The clean Clairvoyant mark. A sparkle glints on the breakout point: the last trace of his wink.", "Locked off", b, "the-mark"))

# 8 — title
b = f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
lock = open("/home/claude/out/clairvoyant-lockup-stacked-dark.svg").read()
inner = re.search(r"<title>.*?</title>(.*)</svg>", lock, re.S).group(1)
vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', lock).group(1).split()]
sc = 520 / vb[3]
b += f'<circle cx="640" cy="330" r="380" fill="url(#iceGlow)" opacity="0.18"/>'
b += f'<g transform="translate({640 - vb[2]*sc/2} {90}) scale({sc}) translate({-vb[0]} {-vb[1]})">{inner}</g>'
panels.append((8, "0:04 – 0:06", "TITLE", "Official stacked lockup. Hold, then fade.", "Gentle push-in", b, "title"))

paths = [save(*p) for p in panels]
from PIL import Image
ims = [Image.open(p).convert("RGB") for p in paths]
tw, th = 640, int(640 * (H + CAP) / W)
sheet = Image.new("RGB", (2 * tw + 30, 4 * th + 50), (6, 9, 13))
for i, im in enumerate(ims):
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (10 + (i % 2) * (tw + 10), 10 + (i // 2) * (th + 10)))
sheet.save("/home/claude/orb_grin_storyboard_sheet.png")
print("\n".join(paths))
