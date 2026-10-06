import os, cairosvg
src = open("/tmp/claude-0/-home-claude/b526ec50-437e-5e03-99f2-649ee89e85be/scratchpad/board.py").read()
exec(src[:src.index("panels = []")])
OUTD = "/home/claude/kit/orb-character"
os.makedirs(OUTD, exist_ok=True)
poses = [
    ("neutral",    dict(eyes="open", mouth="smile")),
    ("happy",      dict(eyes="closed", mouth="grin")),
    ("surprised",  dict(eyes="wide", mouth="o", look=(0.5, -0.8))),
    ("determined", dict(eyes="determined", mouth="flat", look=(1, 0))),
    ("worried",    dict(eyes="wide", mouth="panic", sweat=True, look=(0, 1))),
    ("glowing",    dict(eyes="closed", mouth="smile", glow=True)),
    ("spark-gone", dict(eyes="wide", mouth="o", antenna="stalk", look=(1, -1))),
    ("running",    dict(eyes="determined", mouth="grin", legs="run", tilt=10, look=(1, 0))),
    ("jumping",    dict(eyes="wide", mouth="grin", legs="hop", look=(0.6, -0.6))),
]
r = 100
tiles = []
for name, kw in poses:
    g = orb(200, 230, r, **kw)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="420" viewBox="0 0 400 420">{DEFS}{g}</svg>'
    open(f"{OUTD}/orb-{name}.svg", "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=f"{OUTD}/orb-{name}.png", output_width=800)
    tiles.append((name, g))
# character sheet
cols = 3
W2, H2 = 1350, 1500
parts = [f'<rect width="{W2}" height="{H2}" fill="#0B121A"/>',
         f'<text x="40" y="60" font-family="DejaVu Sans" font-weight="bold" font-size="34" fill="#FFFFFF">ORB  ·  Clairvoyant mascot</text>',
         f'<text x="40" y="95" font-family="DejaVu Sans" font-size="18" fill="#9CACBC">Body slate #2F4356 (3D: #46647F) · eyes #F4F7FA / #0B1118 · blush #F28B82 · antenna + spark amber #F5B942</text>']
for i, (name, g) in enumerate(tiles):
    x, y = 40 + (i % cols) * 430, 130 + (i // cols) * 450
    parts.append(f'<rect x="{x}" y="{y}" width="410" height="430" rx="18" fill="#13202D"/>')
    parts.append(f'<g transform="translate({x+5} {y-20})">{g}</g>')
    parts.append(f'<text x="{x+205}" y="{y+412}" font-family="DejaVu Sans" font-size="20" fill="#F5B942" text-anchor="middle">{name}</text>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}">{DEFS}{"".join(parts)}</svg>'
cairosvg.svg2png(bytestring=svg.encode(), write_to="/home/claude/kit/orb-character/orb-character-sheet.png")
print("ok")
