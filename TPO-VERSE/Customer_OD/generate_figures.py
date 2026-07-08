#!/usr/bin/env python3
"""
Generate TikZ figure files for the H3 sales & marketing paper.

Creates a deterministic synthetic dataset over a pointy-top hexagonal grid
standing in for H3 resolution-8 cells (~0.74 km^2 each) covering a stylised
western Jakarta--Tangerang corridor, then writes the figure bodies to
figures/*.tex.  Run:  python3 generate_figures.py
"""

import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------
# Deterministic RNG (LCG) so figures are reproducible without numpy
# ----------------------------------------------------------------------------
class LCG:
    def __init__(self, seed=20250907):
        self.state = seed

    def next(self):
        self.state = (self.state * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return self.state / float(1 << 64)

rng = LCG()

# ----------------------------------------------------------------------------
# Hex grid geometry: pointy-top, odd-r offset coordinates
# ----------------------------------------------------------------------------
COLS, ROWS = 20, 13
SQ3 = math.sqrt(3.0)

def center(col, row, s):
    x = s * SQ3 * (col + 0.5 * (row % 2))
    y = s * 1.5 * row
    return x, y

def hex_corners(cx, cy, s):
    return [(cx + s * math.cos(math.radians(60 * k + 30)),
             cy + s * math.sin(math.radians(60 * k + 30))) for k in range(6)]

def offset_to_cube(col, row):
    x = col - (row - (row & 1)) // 2
    z = row
    y = -x - z
    return x, y, z

def hexdist(a, b):
    ax, ay, az = offset_to_cube(*a)
    bx, by, bz = offset_to_cube(*b)
    return max(abs(ax - bx), abs(ay - by), abs(az - bz))

# ----------------------------------------------------------------------------
# Synthetic population surface (persons per ~0.74 km^2 cell)
# ----------------------------------------------------------------------------
BLOBS = [
    # (col, row, amplitude, sigma)   -- stylised centres
    (12.5, 6.5, 16000, 2.3),   # CBD core
    (5.5,  8.0,  9500, 2.0),   # western sub-centre ("Tangerang side")
    (17.0, 8.5,  9000, 1.8),   # eastern sub-centre (under-served)
    (12.5, 2.5,  7000, 1.9),   # southern sub-centre
    (9.0,  5.0,  5200, 2.4),   # infill corridor
]
BASE = 1900.0

def coast_row(col):
    # Java Sea to the north (higher rows are north here); coastline dips
    return 11.4 - 0.16 * col if col < 10 else 12.4 - 0.05 * col

hexes = []           # list of dicts
noise = {}
for row in range(ROWS):
    for col in range(COLS):
        noise[(col, row)] = rng.next()

for row in range(ROWS):
    for col in range(COLS):
        if row > coast_row(col):
            continue                      # sea: cell not part of the spine
        pop = BASE
        for bc, br, amp, sg in BLOBS:
            d2 = (col - bc) ** 2 + ((row - br) * 1.05) ** 2
            pop += amp * math.exp(-d2 / (2 * sg * sg))
        pop *= 0.80 + 0.40 * noise[(col, row)]
        hexes.append({"col": col, "row": row, "pop": pop})

cells = {(h["col"], h["row"]): h for h in hexes}

# ----------------------------------------------------------------------------
# Stores: clustered in CBD / west / south, none in the eastern sub-centre
# ----------------------------------------------------------------------------
STORES = [
    # (col, row, monthly gross attractiveness, name)
    (12, 7, 1.00, "S01"), (13, 6, 0.85, "S02"), (11, 5, 0.90, "S03"),
    (14, 8, 0.70, "S04"), (12, 4, 0.75, "S05"),
    (5, 8, 0.85, "S06"),  (6, 7, 0.70, "S07"),  (4, 9, 0.60, "S08"),
    (12, 2, 0.80, "S09"), (14, 3, 0.65, "S10"),
    (8, 5, 0.70, "S11"),  (9, 8, 0.60, "S12"),
]
TAU = 1.55            # catchment decay length in cells

for h in hexes:
    rev = 0.0
    for sc, sr, amp, _ in STORES:
        d = hexdist((h["col"], h["row"]), (sc, sr))
        rev += amp * (h["pop"] / 1000.0) * 0.32 * math.exp(-(d * d) / (2 * TAU * TAU))
    h["rev"] = rev if rev >= 0.05 else 0.0     # IDR bn / month reaching this cell

# ----------------------------------------------------------------------------
# Classification: penetrated / under-penetrated / whitespace / low priority
# ----------------------------------------------------------------------------
pops = sorted(h["pop"] for h in hexes)
POP_HI = pops[int(0.60 * len(pops))]           # 60th percentile
revpc = [h["rev"] * 1e9 / h["pop"] for h in hexes if h["rev"] > 0]
revpc.sort()
RPC_T = revpc[int(0.40 * len(revpc))]          # 40th pct of positive rev/capita

for h in hexes:
    rpc = h["rev"] * 1e9 / h["pop"]
    if h["pop"] < POP_HI:
        h["cls"] = "low"
    elif h["rev"] == 0.0:
        h["cls"] = "white"
    elif rpc < RPC_T:
        h["cls"] = "under"
    else:
        h["cls"] = "pen"

# ----------------------------------------------------------------------------
# Irregular "kecamatan" districts (for the MAUP panel and gain curves)
# ----------------------------------------------------------------------------
DSEEDS = [
    # (col, row, weight) -- larger weight => bigger district
    (12.5, 6.0, 1.00), (5.0, 8.5, 1.45), (17.5, 8.0, 1.75),
    (12.0, 2.0, 1.30), (8.5, 5.5, 1.05), (2.5, 3.0, 2.30),
    (17.5, 2.5, 2.05), (9.5, 10.5, 1.35),
]
for h in hexes:
    best, bid = 1e9, -1
    for i, (sc, sr, w) in enumerate(DSEEDS):
        d = math.hypot(h["col"] - sc, h["row"] - sr) / w
        if d < best:
            best, bid = d, i
    h["dist"] = bid

dmean = {}
for i in range(len(DSEEDS)):
    ms = [h["pop"] for h in hexes if h["dist"] == i]
    dmean[i] = sum(ms) / len(ms)

# ----------------------------------------------------------------------------
# Colour bins (population)  -- blue sequential ramp, 7 steps
# ----------------------------------------------------------------------------
PBINS = [1500, 2500, 4000, 6000, 9000, 13000]                    # k thresholds
PCOLS = ["h3b100", "h3b200", "h3b300", "h3b400", "h3b500", "h3b600", "h3b700"]
PLABS = ["$<$1.5", "1.5--2.5", "2.5--4", "4--6", "6--9", "9--13", "$>$13"]

def pop_color(p):
    for i, t in enumerate(PBINS):
        if p < t:
            return PCOLS[i]
    return PCOLS[-1]

CLS_COL = {"pen": "clsPen", "under": "clsUnd", "white": "clsWhi", "low": "clsLow"}
CLS_LAB = {"pen": "Penetrated", "under": "Under-penetrated",
           "white": "Whitespace", "low": "Low priority"}

REVMAX = max(h["rev"] for h in hexes)

# ----------------------------------------------------------------------------
# TikZ writers
# ----------------------------------------------------------------------------
def hexpath(col, row, s):
    cx, cy = center(col, row, s)
    pts = " -- ".join("(%.3f,%.3f)" % p for p in hex_corners(cx, cy, s))
    return "%s -- cycle" % pts

def w(fname, body):
    with open(os.path.join(OUT, fname), "w") as f:
        f.write("% Auto-generated by generate_figures.py -- do not edit by hand\n")
        f.write(body)

def legend_swatches(x0, y0, items, boxw=0.42, boxh=0.26, dx=1.72, xs=None):
    """items: list of (color, label). Returns TikZ lines.
    xs: optional explicit x position per item (overrides uniform dx)."""
    out = []
    for i, (c, lab) in enumerate(items):
        x = xs[i] if xs else x0 + i * dx
        out.append("\\fill[%s, draw=inkM, line width=0.2pt] (%.3f,%.3f) "
                   "rectangle (%.3f,%.3f);" % (c, x, y0, x + boxw, y0 + boxh))
        out.append("\\node[anchor=west, font=\\scriptsize, text=inkS, inner sep=1pt] "
                   "at (%.3f,%.3f) {%s};" % (x + boxw + 0.05, y0 + boxh / 2, lab))
    return "\n".join(out)

def store_marks(s, label_first=False):
    out = []
    for sc, sr, _, name in STORES:
        cx, cy = center(sc, sr, s)
        out.append("\\node[store] at (%.3f,%.3f) {};" % (cx, cy))
    return "\n".join(out)

# ---- Figure: population choropleth + stores --------------------------------
def fig_population(s=0.30):
    L = ["\\begin{tikzpicture}"]
    for h in hexes:
        L.append("\\fill[%s, draw=white, line width=0.5pt] %s;"
                 % (pop_color(h["pop"]), hexpath(h["col"], h["row"], s)))
    L.append(store_marks(s))
    # coastline annotation
    cx, cy = center(2.2, 12.1, s)
    L.append("\\node[font=\\scriptsize\\itshape, text=inkM] at (%.3f,%.3f) "
             "{Java Sea (cells masked)};" % (cx + 1.1, cy - 0.72))
    # legend
    W = SQ3 * s * (COLS + 0.5)
    items = list(zip(PCOLS, PLABS))
    L.append(legend_swatches(0.1, -0.85, items, dx=W / 7.35))
    L.append("\\node[anchor=west, font=\\scriptsize, text=inkS] at (0.1,-1.30) "
             "{Population per cell (thousands)\\quad "
             "\\tikz{\\node[store, scale=0.9] at (0,0) {};}\\; existing store};")
    L.append("\\end{tikzpicture}")
    w("fig-population.tex", "\n".join(L) + "\n")

# ---- Figure: overlay = population fill + revenue bubbles + whitespace ------
def fig_overlay(s=0.30):
    L = ["\\begin{tikzpicture}"]
    for h in hexes:
        L.append("\\fill[%s!72!white, draw=white, line width=0.5pt] %s;"
                 % (pop_color(h["pop"]), hexpath(h["col"], h["row"], s)))
    # whitespace outline first (under bubbles)
    for h in hexes:
        if h["cls"] == "white":
            L.append("\\draw[clsWhi, line width=0.9pt, dash pattern=on 2pt off 1.4pt] %s;"
                     % hexpath(h["col"], h["row"], s))
    # revenue bubbles
    rmax = 0.62 * s
    for h in hexes:
        if h["rev"] > 0:
            cx, cy = center(h["col"], h["row"], s)
            r = rmax * math.sqrt(h["rev"] / REVMAX)
            L.append("\\fill[accOr, draw=white, line width=0.55pt] "
                     "(%.3f,%.3f) circle (%.3f);" % (cx, cy, r))
    L.append(store_marks(s))
    # annotation: call out the whitespace cluster on the map itself
    white = [h for h in hexes if h["cls"] == "white"]
    if white:
        wx = sum(center(h["col"], h["row"], s)[0] for h in white) / len(white)
        wy = sum(center(h["col"], h["row"], s)[1] for h in white) / len(white)
        L.append("\\node[anchor=south, font=\\scriptsize\\itshape, text=clsWhi!85!black, "
                 "align=center] (wlab) at (%.3f,%.3f) "
                 "{whitespace: population\\\\ with no revenue capture};"
                 % (wx - 1.05, wy + 1.15))
        L.append("\\draw[-{Stealth[length=2.2mm]}, clsWhi!85!black, line width=0.7pt] "
                 "(wlab.south) -- (%.3f,%.3f);" % (wx, wy + 0.28))
    # legend row 1: revenue bubble scale
    r1 = -0.80
    L.append("\\node[anchor=west, font=\\scriptsize, text=inkS] at (0.1,%.2f) "
             "{Monthly revenue captured (IDR bn):};" % r1)
    for i, v in enumerate([0.5, 1.5, 3.0]):
        x = 5.6 + i * 1.55
        r = rmax * math.sqrt(v / REVMAX)
        L.append("\\fill[accOr, draw=white, line width=0.55pt] (%.3f,%.2f) circle (%.3f);"
                 % (x, r1, r))
        L.append("\\node[anchor=west, font=\\scriptsize, text=inkS] at (%.3f,%.2f) {%.1f};"
                 % (x + 0.26, r1, v))
    # legend row 2: whitespace outline, store mark, fill meaning
    r2 = -1.45
    L.append("\\draw[clsWhi, line width=0.9pt, dash pattern=on 2pt off 1.4pt] "
             "(0.10,%.2f) rectangle +(0.34,0.26);" % (r2 - 0.13))
    L.append("\\node[anchor=west, font=\\scriptsize, text=inkS] at (0.54,%.2f) "
             "{whitespace cell};" % r2)
    L.append("\\node[store, scale=0.9] at (3.30,%.2f) {};" % r2)
    L.append("\\node[anchor=west, font=\\scriptsize, text=inkS] at (3.52,%.2f) "
             "{existing store};" % r2)
    L.append("\\node[anchor=west, font=\\scriptsize, text=inkS] at (6.10,%.2f) "
             "{cell fill: population (as in Fig.~\\ref{fig:population})};" % r2)
    L.append("\\end{tikzpicture}")
    w("fig-overlay.tex", "\n".join(L) + "\n")

# ---- Figure: classification map ---------------------------------------------
def fig_classification(s=0.30):
    L = ["\\begin{tikzpicture}"]
    for h in hexes:
        L.append("\\fill[%s, draw=white, line width=0.5pt] %s;"
                 % (CLS_COL[h["cls"]], hexpath(h["col"], h["row"], s)))
    L.append(store_marks(s))
    items = [(CLS_COL[k], CLS_LAB[k]) for k in ("pen", "under", "white", "low")]
    L.append(legend_swatches(0.1, -0.85, items, xs=[0.1, 2.45, 5.95, 8.35]))
    L.append("\\node[store, scale=0.9] at (0.31,-1.42) {};")
    L.append("\\node[anchor=west, font=\\scriptsize, text=inkS] at (0.54,-1.42) "
             "{existing store};")
    L.append("\\end{tikzpicture}")
    w("fig-classification.tex", "\n".join(L) + "\n")

# ---- Figure: MAUP two panels -------------------------------------------------
def district_borders(s):
    """Thick border segments between hexes of different districts."""
    segs = []
    # neighbour offsets for odd-r pointy-top, per row parity
    NBR = {
        0: [(+1, 0), (0, -1), (-1, -1), (-1, 0), (-1, +1), (0, +1)],
        1: [(+1, 0), (+1, -1), (0, -1), (-1, 0), (0, +1), (+1, +1)],
    }
    for h in hexes:
        c, r = h["col"], h["row"]
        cx, cy = center(c, r, s)
        corners = hex_corners(cx, cy, s)
        for k, (dc, dr) in enumerate(NBR[r % 2]):
            nb = cells.get((c + dc, r + dr))
            if nb is None or nb["dist"] != h["dist"]:
                # edge between corner k and k+1 faces neighbour direction k?
                # Map: for pointy-top with corners at 30+60k, edge k spans
                # corners k,k+1 and faces angle 60k+60.
                # Determine facing by angle to neighbour centre.
                if nb is None and (c + dc, r + dr) not in cells:
                    facing_sea = r + dr > coast_row(c + dc) or not \
                        (0 <= c + dc < COLS and 0 <= r + dr < ROWS)
                    if not facing_sea:
                        continue
                nx, ny = center(c + dc, r + dr, s)
                ang = math.degrees(math.atan2(ny - cy, nx - cx)) % 360
                k_edge = int(round((ang - 60) / 60.0)) % 6
                p1 = corners[k_edge % 6]
                p2 = corners[(k_edge + 1) % 6]
                segs.append("\\draw[inkP, line width=0.9pt] (%.3f,%.3f) -- (%.3f,%.3f);"
                            % (p1[0], p1[1], p2[0], p2[1]))
    return segs

def fig_maup(s=0.185):
    W = SQ3 * s * (COLS + 0.5)
    L = ["\\begin{tikzpicture}"]
    # panel (a): district-mean colouring
    L.append("\\begin{scope}")
    for h in hexes:
        L.append("\\fill[%s] %s;" % (pop_color(dmean[h["dist"]]),
                                     hexpath(h["col"], h["row"], s)))
    L.extend(district_borders(s))
    L.append("\\node[font=\\footnotesize, text=inkP, anchor=west] at (0,%.3f) "
             "{(a) Administrative aggregation};" % (ROWS * 1.5 * s + 0.42))
    L.append("\\end{scope}")
    # panel (b): true hex values
    L.append("\\begin{scope}[xshift=%.3fcm]" % (W + 0.7))
    for h in hexes:
        L.append("\\fill[%s, draw=white, line width=0.3pt] %s;"
                 % (pop_color(h["pop"]), hexpath(h["col"], h["row"], s)))
    L.append("\\node[font=\\footnotesize, text=inkP, anchor=west] at (0,%.3f) "
             "{(b) Same data on the H3 grid};" % (ROWS * 1.5 * s + 0.42))
    L.append("\\end{scope}")
    items = list(zip(PCOLS, PLABS))
    L.append(legend_swatches(0.1, -0.80, items, dx=(2 * W + 0.7) / 7.1))
    L.append("\\node[anchor=west, font=\\scriptsize, text=inkS] at (0.1,-1.24) "
             "{Population per cell (thousands); identical underlying data in both panels};")
    L.append("\\end{tikzpicture}")
    w("fig-maup.tex", "\n".join(L) + "\n")

# ---- Figure: k-ring cannibalization -----------------------------------------
def fig_kring(s=0.34):
    A, B = (4, 4), (8, 4)
    Lc, Rc = 12, 9
    L = ["\\begin{tikzpicture}"]
    for row in range(Rc):
        for col in range(Lc):
            da = hexdist((col, row), A)
            db = hexdist((col, row), B)
            ca = da <= 2
            cb = db <= 2
            if ca and cb:
                col_fill = "violet!38!white"
            elif ca:
                col_fill = "clsPen!42!white"
            elif cb:
                col_fill = "aqua!45!white"
            else:
                col_fill = "neu"
            L.append("\\fill[%s, draw=white, line width=0.6pt] %s;"
                     % (col_fill, hexpath(col, row, s)))
    for P, nm in ((A, "Store A"), (B, "Store B")):
        cx, cy = center(*P, s)
        L.append("\\node[store] at (%.3f,%.3f) {};" % (cx, cy))
        L.append("\\node[font=\\scriptsize\\bfseries, text=inkP, anchor=north] "
                 "at (%.3f,%.3f) {%s};" % (cx, cy - 0.24, nm))
    items = [("clsPen!42!white", "$k\\le2$ ring of A"),
             ("aqua!45!white", "$k\\le2$ ring of B"),
             ("violet!38!white", "shared cells (overlap)")]
    L.append(legend_swatches(0.1, -0.8, items, dx=2.9))
    L.append("\\end{tikzpicture}")
    w("fig-kring.tex", "\n".join(L) + "\n")

# ---- Figure: aperture-7 hierarchy -------------------------------------------
def fig_hierarchy():
    L = ["\\begin{tikzpicture}"]
    S = 1.9
    alpha = math.degrees(math.atan2(1, 5 * SQ3 / 3))  # ~19.107 deg
    def child_centers(scale, rot, origin=(0, 0)):
        pts = []
        for (q, r) in [(0, 0), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]:
            # axial to cartesian (pointy-top)
            x = scale * SQ3 * (q + r / 2.0)
            y = scale * 1.5 * r
            a = math.radians(rot)
            xr = x * math.cos(a) - y * math.sin(a) + origin[0]
            yr = x * math.sin(a) + y * math.cos(a) + origin[1]
            pts.append((xr, yr))
        return pts
    def hexagon_at(cx, cy, s, rot, style):
        pts = [(cx + s * math.cos(math.radians(60 * k + 30 + rot)),
                cy + s * math.sin(math.radians(60 * k + 30 + rot))) for k in range(6)]
        path = " -- ".join("(%.3f,%.3f)" % p for p in pts)
        L.append("\\%s %s -- cycle;" % (style, path))
    s1 = S / math.sqrt(7)
    s2 = s1 / math.sqrt(7)
    # children (res n+1)
    for (cx, cy) in child_centers(s1, alpha):
        hexagon_at(cx, cy, s1, alpha, "fill[h3b200, draw=white, line width=0.8pt]")
    # grandchildren inside the central child (res n+2)
    for (cx, cy) in child_centers(s2, 2 * alpha):
        hexagon_at(cx, cy, s2, 2 * alpha, "fill[h3b500, draw=white, line width=0.5pt]")
    # parent outline (res n)
    hexagon_at(0, 0, S, 0, "draw[inkP, line width=1.1pt]")
    L.append("\\node[font=\\scriptsize, text=inkP, anchor=west] at (2.2,1.45) "
             "{resolution $n$ (parent)};")
    L.append("\\draw[inkM, line width=0.4pt] (2.15,1.45) -- (%.3f,%.3f);"
             % (S * math.cos(math.radians(30)) * 0.97, S * math.sin(math.radians(30)) * 0.97))
    L.append("\\node[font=\\scriptsize, text=inkP, anchor=west] at (2.2,0.6) "
             "{resolution $n{+}1$ (7 children)};")
    L.append("\\node[font=\\scriptsize, text=inkP, anchor=west] at (2.2,-0.25) "
             "{resolution $n{+}2$};")
    L.append("\\end{tikzpicture}")
    w("fig-hierarchy.tex", "\n".join(L) + "\n")

# ---- pgfplots data: gain curves ---------------------------------------------
def gain_data():
    land = sorted(hexes, key=lambda h: -h["pop"])
    tot = sum(h["pop"] for h in hexes)
    n = len(land)
    hx_pts = [(0.0, 0.0)]
    acc = 0.0
    for i, h in enumerate(land):
        acc += h["pop"]
        hx_pts.append((100.0 * (i + 1) / n, 100.0 * acc / tot))
    # districts: rank by mean density, take whole districts
    ds = sorted(range(len(DSEEDS)), key=lambda i: -dmean[i])
    d_pts = [(0.0, 0.0)]
    a_acc, p_acc = 0, 0.0
    for i in ds:
        members = [h for h in hexes if h["dist"] == i]
        a_acc += len(members)
        p_acc += sum(h["pop"] for h in members)
        d_pts.append((100.0 * a_acc / n, 100.0 * p_acc / tot))
    return hx_pts, d_pts

def coords(pts, step=1):
    return " ".join("(%.2f,%.2f)" % p for p in pts[::step]) + \
        ("" if (len(pts) - 1) % step == 0 else " (%.2f,%.2f)" % pts[-1])

def fig_gain():
    hx, dd = gain_data()
    # area (in cells) needed for 50% / 75% of population
    def area_for(pts, target):
        for x, y in pts:
            if y >= target:
                return x
        return 100.0
    stats = {
        "hex50": area_for(hx, 50), "adm50": area_for(dd, 50),
        "hex75": area_for(hx, 75), "adm75": area_for(dd, 75),
    }
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  width=9.6cm, height=7.0cm,
  xlabel={Share of land area targeted (\%%)},
  ylabel={Share of population reached (\%%)},
  xmin=0, xmax=100, ymin=0, ymax=100,
  axis line style={base}, tick style={base},
  xlabel style={font=\small, text=inkS}, ylabel style={font=\small, text=inkS},
  ticklabel style={font=\scriptsize, text=inkM},
  grid=major, grid style={gridc},
  legend style={draw=none, fill=none, font=\small, at={(0.03,0.97)}, anchor=north west},
]
\addplot[clsPen, line width=1.6pt] coordinates {%(HX)s};
\addlegendentry{H3 res.\ 8 cells}
\addplot[inkM, line width=1.3pt, dash pattern=on 3.2pt off 2pt] coordinates {%(DD)s};
\addlegendentry{Administrative districts}
\addplot[gridc, line width=0.7pt, forget plot] coordinates {(0,50) (%(A50).1f,50)};
\addplot[clsPen!70!black, line width=0.7pt, forget plot] coordinates {(%(H50).1f,0) (%(H50).1f,50)};
\addplot[inkM, line width=0.7pt, forget plot] coordinates {(%(A50c).1f,0) (%(A50c).1f,50)};
\node[font=\scriptsize\bfseries, text=clsPen!70!black, anchor=south] at
  (axis cs:%(H50).1f,55) {%(H50).0f\%%};
\node[font=\scriptsize\bfseries, text=inkM, anchor=south] at
  (axis cs:%(A50c).1f,55) {%(A50c).0f\%%};
\node[font=\scriptsize, text=inkS, anchor=north west, align=left] at
  (axis cs:2,45) {50\%% of population\\ reached at:};
\end{axis}
\end{tikzpicture}
""" % {"HX": coords(hx, 4), "DD": coords(dd),
       "H50": stats["hex50"], "A50": stats["adm50"], "A50c": stats["adm50"]}
    w("fig-gain.tex", body.lstrip("\n"))
    return stats

# ---- pgfplots: scatter (population vs revenue) -------------------------------
def fig_scatter():
    groups = {k: [] for k in ("pen", "under", "white", "low")}
    for h in hexes:
        groups[h["cls"]].append((h["pop"] / 1000.0, h["rev"]))
    def cs(pts):
        return " ".join("(%.2f,%.3f)" % p for p in pts)
    # axis bounds sized to the actual data range -- fixed bounds previously
    # clipped every cell above ~19k population / IDR 3.4bn revenue, silently
    # dropping the highest-value "penetrated" cells from the plot.
    popmax = max(h["pop"] for h in hexes) / 1000.0
    revmax = max(h["rev"] for h in hexes)
    xmax = 5 * math.ceil(popmax / 5.0)
    ymax = 2 * math.ceil(revmax / 2.0)
    ymin = -0.036 * ymax
    white = groups["white"]
    wcx = sum(p for p, _ in white) / len(white)
    wcy = sum(r for _, r in white) / len(white)
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  width=10.2cm, height=7.2cm,
  xlabel={Population in cell (thousands)},
  ylabel={Monthly revenue captured (IDR bn)},
  xmin=0, xmax=%(XMAX).0f, ymin=%(YMIN).2f, ymax=%(YMAX).0f,
  axis line style={base}, tick style={base},
  xlabel style={font=\small, text=inkS}, ylabel style={font=\small, text=inkS},
  ticklabel style={font=\scriptsize, text=inkM},
  grid=major, grid style={gridc},
  legend style={draw=none, fill=none, font=\small, at={(0.03,0.97)}, anchor=north west},
  legend cell align=left,
]
\addplot[gridc, line width=0.9pt, forget plot] coordinates {(%(PH).2f,%(YMIN).2f) (%(PH).2f,%(YMAX).0f)};
\addplot[only marks, mark=*, mark size=1.9pt, clsLow, mark options={draw=white, line width=0.3pt}] coordinates {%(LOW)s};
\addlegendentry{Low priority}
\addplot[only marks, mark=*, mark size=2.1pt, clsPen, mark options={draw=white, line width=0.3pt}] coordinates {%(PEN)s};
\addlegendentry{Penetrated}
\addplot[only marks, mark=*, mark size=2.1pt, clsUnd, mark options={draw=white, line width=0.3pt}] coordinates {%(UND)s};
\addlegendentry{Under-penetrated}
\addplot[only marks, mark=triangle*, mark size=2.9pt, clsWhi, mark options={draw=white, line width=0.3pt}] coordinates {%(WHI)s};
\addlegendentry{Whitespace}
\node[font=\scriptsize, text=inkS, anchor=east, align=right] (wlab) at
  (axis cs:%(LX).1f,%(LY).2f)
  {Whitespace: high population,\\ zero captured revenue};
\draw[-{Stealth[length=1.8mm]}, clsWhi!85!black, line width=0.6pt]
  (axis cs:%(AX).1f,%(LY).2f) -- (axis cs:%(AX).1f,%(YLOW).2f)
  -- (axis cs:%(WCX).2f,%(YLOW).2f) -- (axis cs:%(WCX).2f,%(WCY).2f);
\end{axis}
\end{tikzpicture}
""" % {"XMAX": xmax, "YMAX": ymax, "YMIN": ymin,
       "LX": xmax - 1.0, "LY": ymax * 0.10, "YLOW": ymin * 0.85,
       "AX": xmax - 6.0,
       "WCX": wcx, "WCY": wcy + ymax * 0.012,
       "PH": POP_HI / 1000.0,
       "LOW": cs(groups["low"]), "PEN": cs(groups["pen"]),
       "UND": cs(groups["under"]), "WHI": cs(groups["white"])}
    w("fig-scatter.tex", body.lstrip("\n"))

# ---- pgfplots: bar comparison (media targeting efficiency) -------------------
def fig_bars(stats):
    KM2 = 0.737
    n = len(hexes)
    vals = {k: v / 100.0 * n * KM2 for k, v in stats.items()}
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  width=8.8cm, height=6.4cm,
  ybar, bar width=17pt,
  xlabel={Campaign reach target (share of corridor population)},
  ylabel={Geofenced area required (km$^2$)},
  symbolic x coords={50\%%, 75\%%}, xtick=data,
  ymin=0, ymax=%(YMAX).0f,
  axis line style={base}, tick style={base},
  xlabel style={font=\small, text=inkS}, ylabel style={font=\small, text=inkS},
  ticklabel style={font=\scriptsize, text=inkM},
  grid=major, grid style={gridc},
  legend style={draw=none, fill=none, font=\small, at={(0.05,0.95)}, anchor=north west},
  nodes near coords, every node near coord/.append style={font=\scriptsize, text=inkS},
  nodes near coords={\pgfmathprintnumber[fixed, precision=0]{\pgfplotspointmeta}},
]
\addplot[fill=clsPen, draw=none] coordinates {(50\%%,%(H50).1f) (75\%%,%(H75).1f)};
\addlegendentry{H3 res.\ 8 geofences}
\addplot[fill=inkM!52!white, draw=none] coordinates {(50\%%,%(A50).1f) (75\%%,%(A75).1f)};
\addlegendentry{Whole administrative districts}
\end{axis}
\end{tikzpicture}
""" % {"H50": vals["hex50"], "H75": vals["hex75"],
       "A50": vals["adm50"], "A75": vals["adm75"],
       "YMAX": max(vals.values()) * 1.3}
    w("fig-bars.tex", body.lstrip("\n"))
    return vals

# ----------------------------------------------------------------------------
# Emit everything + a stats report used in the paper's narrative
# ----------------------------------------------------------------------------
fig_population()
fig_overlay()
fig_classification()
fig_maup()
fig_kring()
fig_hierarchy()
stats = fig_gain()
fig_scatter()
vals = fig_bars(stats)

tot_pop = sum(h["pop"] for h in hexes)
tot_rev = sum(h["rev"] for h in hexes)
white = [h for h in hexes if h["cls"] == "white"]
under = [h for h in hexes if h["cls"] == "under"]
wpop = sum(h["pop"] for h in white)
upop = sum(h["pop"] for h in under)
arpu = tot_rev * 1e9 / sum(h["pop"] for h in hexes if h["rev"] > 0)
KM2 = 0.737

print("== dataset stats ==")
print("cells (land): %d  (~%.0f km2)" % (len(hexes), len(hexes) * KM2))
print("total pop: %.0f" % tot_pop)
print("total monthly revenue: IDR %.1f bn" % tot_rev)
print("POP_HI threshold: %.0f   RPC threshold: IDR %.0f /person/month" % (POP_HI, RPC_T))
print("class counts:", {k: sum(1 for h in hexes if h["cls"] == k)
                        for k in ("pen", "under", "white", "low")})
print("whitespace pop: %.0f  (%.1f%% of corridor)" % (wpop, 100 * wpop / tot_pop))
print("under-penetrated pop: %.0f" % upop)
print("ARPU in served cells: IDR %.0f /person/month" % arpu)
print("whitespace revenue opportunity at served ARPU: IDR %.2f bn/month" % (wpop * arpu / 1e9))
print("gain: 50%% pop -> hex %.1f%% area (%.0f km2) vs districts %.1f%% (%.0f km2)"
      % (stats["hex50"], vals["hex50"], stats["adm50"], vals["adm50"]))
print("gain: 75%% pop -> hex %.1f%% area (%.0f km2) vs districts %.1f%% (%.0f km2)"
      % (stats["hex75"], vals["hex75"], stats["adm75"], vals["adm75"]))
# cannibalization stat for the k-ring narrative
A, B = (4, 4), (8, 4)
shared = sum(1 for row in range(9) for col in range(12)
             if hexdist((col, row), A) <= 2 and hexdist((col, row), B) <= 2)
ring = sum(1 for row in range(9) for col in range(12) if hexdist((col, row), A) <= 2)
print("k-ring: %d shared cells of %d per store (%.0f%%)" % (shared, ring, 100 * shared / ring))
