"""Build the editable PowerPoint version of slides.html (same layout, Cobalt Grid look).

Needs python-pptx and Pillow (not in the project environment; any Python with both works):
    python build_pptx.py
Reads the figure cut-outs in figures/ (cut from slides.html at 2x) and writes
spatial_reasoning_week2.pptx next to this script. All text is editable; the two bar charts
are native PowerPoint charts; spot maps and toy-grid diagrams are images.
Coordinates are written in the HTML's 1920 x 1080 px space and converted here.
"""

from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

HERE = Path(__file__).parent
FIG = HERE / "figures"
OUT = HERE / "spatial_reasoning_week2.pptx"

# ---- palette (two inks on paper; tints are cobalt blended onto the cream) ----
INK, SOFT, PAPER = "1F2BE0", "5560E5", "F0EBDE"
FAINT = "CAC8DE"     # 18% cobalt on cream (row dividers)
TINT = "A3A4DF"      # ~45% cobalt on cream (synthetic cells)
DIM = "6E74DF"       # 66% cobalt on cream (secondary text)
GRIDLINE = "DBD8DE"  # 10% cobalt on cream (graph paper)
SERIF, SANS, MONO = "Georgia", "Calibri", "Consolas"

px = lambda v: Emu(int(round(v * 6350)))          # 1920 px = 13.333 in  # noqa: E731
rgb = lambda h: RGBColor.from_string(h)             # noqa: E731

prs = Presentation()
prs.slide_width, prs.slide_height = px(1920), px(1080)
BLANK = prs.slide_layouts[6]

# graph-paper background, generated once
BG = HERE / "figures" / "_graph_paper.png"
img = Image.new("RGB", (1920, 1080), "#" + PAPER)
d = ImageDraw.Draw(img)
for x in range(0, 1920, 40):
    d.line([(x, 0), (x, 1080)], fill="#" + GRIDLINE)
for y in range(0, 1080, 40):
    d.line([(0, y), (1920, y)], fill="#" + GRIDLINE)
img.save(BG)


# ---------------------------------------------------------------- helpers
def text(slide, x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line=None):
    """paras: list of paragraphs; a paragraph is a list of runs (text, style dict) or a single run tuple."""
    tb = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if line:
            p.line_spacing = line
        runs = para if isinstance(para, list) else [para]
        for t, st in runs:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = st.get("font", SANS)
            f.size = Pt(st.get("size", 24) / 2)
            f.color.rgb = rgb(st.get("color", INK))
            f.italic = st.get("italic", False)
            f.bold = st.get("bold", False)
            if st.get("spc"):
                r._r.get_or_add_rPr().set("spc", str(st["spc"]))
            if st.get("space_before"):
                p.space_before = Pt(st["space_before"] / 2)
    return tb


def S(size, font=SANS, **kw):
    return dict(size=size, font=font, **kw)


def serif(size, **kw):
    return S(size, SERIF, **kw)


def mono(size, **kw):
    return S(size, MONO, **kw)


def caps(size=16, **kw):
    return S(size, SANS, bold=True, spc=int(size * 8.5), **kw)


def rect(slide, x, y, w, h, fill=None, line=INK, lw=1.5, dash=False):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, px(x), px(y), px(w), px(h))
    s.shadow.inherit = False
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(lw * 0.75)
        if dash:
            s.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    else:
        s.line.fill.background()
    return s


def hline(slide, x, y, w, color=INK, lw=1.5):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, px(x), px(y), px(x + w), px(y))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(lw * 0.75)
    return c


def vline(slide, x, y, h, color=FAINT, lw=1):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, px(x), px(y), px(x), px(y + h))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(lw * 0.75)
    return c


def dot(slide, x, y, d=15, fill=INK, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, px(x), px(y), px(d), px(d))
    s.shadow.inherit = False
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(1.5)
    else:
        s.line.fill.background()
    return s


def pill(slide, x_right, y, label, kind="line"):
    """Status label; x_right is the right edge. kind: solid | line | dash."""
    w = len(label) * 11.4 + 30
    rect(slide, x_right - w, y, w, 36, fill=INK if kind == "solid" else PAPER, dash=(kind == "dash"))
    text(slide, x_right - w, y, w, 36, [(label.upper(), caps(15, color=PAPER if kind == "solid" else INK))],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return w


def picture(slide, name, x, y, w, h):
    slide.shapes.add_picture(str(FIG / f"{name}.png"), px(x), px(y), px(w), px(h))


def fade(slide):
    """Fade transition between slides (python-pptx has no API for it)."""
    tr = etree.SubElement(slide._element, qn("p:transition"))
    tr.set("spd", "med")
    etree.SubElement(tr, qn("p:fade"))


def base(n, cite=None, chrome=None):
    slide = prs.slides.add_slide(BLANK)
    slide.shapes.add_picture(str(BG), 0, 0, prs.slide_width, prs.slide_height)
    hline(slide, 80, 28, 1760)
    hline(slide, 80, 1056.5, 1760)
    if chrome:
        text(slide, 80, 44, 900, 24, [(chrome[0].upper(), mono(17, spc=100))])
        text(slide, 940, 44, 900, 24, [(chrome[1].upper(), mono(17, spc=100))], align=PP_ALIGN.RIGHT)
    if cite:
        text(slide, 80, 1018, 1500, 24, [(cite, mono(16, color=DIM))])
    text(slide, 1640, 1018, 200, 24, [(f"{n:02d} / 08", mono(16))], align=PP_ALIGN.RIGHT)
    fade(slide)
    return slide


def topbar(slide, runs, right=None, kind=None):
    """Takeaway title: runs = [(text, italic?)]; right = tag text or pill label."""
    text(slide, 80, 88, 1440, 128,
         [[(t, serif(54, italic=it, color=SOFT if it else INK)) for t, it in runs]], anchor=MSO_ANCHOR.BOTTOM, line=0.95)
    if right and kind:
        pill(slide, 1840, 172, right, kind)
    elif right:
        text(slide, 1440, 186, 400, 24, [(right.upper(), caps(16))], align=PP_ALIGN.RIGHT)
    hline(slide, 80, 227, 1760)


def abc(slide, items, y=914):
    hline(slide, 80, y, 1760)
    w = 1760 / 3
    for i, (k, v) in enumerate(items):
        x = 80 + i * w + (24 if i else 0)
        if i:
            vline(slide, 80 + i * w, y + 10, 66)
        text(slide, x, y + 20, 140, 24, [(k.upper(), caps(14))])
        text(slide, x + 150, y + 14, w - 190, 70, [(v, S(21))], line=1.05)


def legend(slide, x, y, items):
    """items: (label, style) with style k=solid, m=mid, f=faint, o=outline."""
    fills = {"k": (INK, None), "m": ("9A9CE0", None), "f": ("D3D0E2", None), "o": (PAPER, INK)}
    for label, st in items:
        f, l = fills[st]
        dot(slide, x, y + 4, 15, f, l)
        w = len(label) * 10.2 + 20
        text(slide, x + 24, y, w, 24, [(label, mono(17))])
        x += 24 + w + 18


# ================================================================ 1 · title
s = base(1, chrome=("SPACE-MEL DC9 — Spatial reasoning", "Week 2 · 2–8 November 2026"))
text(s, 80, 130, 1120, 400, [[("Grounding spatial questions in ", serif(100)),
                              ("tested, µm‑scale", serif(100, italic=True, color=SOFT)),
                              (" operations", serif(100))]], line=0.93)
text(s, 80, 560, 1040, 100, [("Can an LLM answer spatial questions about melanoma tissue when its answers are "
                              "grounded in quantitative spatial analysis?", serif(31))], line=1.1)
hline(s, 80, 730, 1080)
stats = [("39,483", "spots kept by the paper's QC\n(paper: 39,481)", "Reproduced", "solid"),
         ("21 / 21", "tests pass for three\nspatial operations", "Tested · synthetic", "line"),
         ("14 / 15", "benchmark questions\nwith a reference answer", "Preliminary", "dash")]
for i, (n, l, st, kind) in enumerate(stats):
    x = 80 + i * 360 + (28 if i else 0)
    if i:
        vline(s, 80 + i * 360, 744, 210)
    text(s, x, 748, 330, 84, [(n, serif(72))])
    text(s, x, 842, 320, 56, [(ln, S(20)) for ln in l.split("\n")], line=1.0)
    pill(s, x + len(st) * 11.4 + 30, 912, st, kind)
picture(s, "cover", 1250, 100, 560, 840)
dot(s, 1250, 954, 13)
text(s, 1270, 950, 560, 24, [("Patient A24 · PRAME > 1.5 (provisional)", mono(16))])
text(s, 80, 1018, 900, 24, [("Aitor · supervised by Myles Tan", mono(16))])

# ================================================================ 2 · paper vs project
s = base(2, cite="Kreuger et al. 2026, Cancer Res 86(17):4400–4413 · roderickslieker/NevusMelanomaVisium · docs/paper_worksheet/")
topbar(s, [("The paper shows ", 0), ("where", 1), (" immune cells sit; this project builds tools to ", 0), ("measure", 1), (" it", 0)],
       "Kreuger et al. 2026")
cols = [(80, "Published", "Not re-claimed", "line",
         [("A", "More immune cells around melanoma than nevus, few inside", "IMC protein · Fig. 5A–B, 5D"),
          ("B", "Distances measured once, in pixels, lesions pooled", "Fig. 4E"),
          ("C", "Nevus / melanoma spot labels inferred from expression", "STdeconvolve topics, K = 15 · not public")]),
        (1020, "This project", "Method", "solid",
         [("1", "Spatial operations in µm, per patient and section", "src/space_mel/operations.py"),
          ("2", "Every operation tested against known answers", "tests/test_operations.py"),
          ("3", "Natural-language questions with reference answers", "02_spatial_operations/benchmark/")])]
for x0, head, st, kind, rows in cols:
    text(s, x0, 258, 500, 50, [(head, serif(40))])
    pill(s, x0 + 820, 266, st, kind)
    hline(s, x0, 318, 820)
    y = 318
    for n, h4, src in rows:
        text(s, x0, y + 30, 60, 50, [(n, serif(44))])
        text(s, x0 + 70, y + 30, 740, 90, [(h4, serif(34))], line=1.0)
        text(s, x0 + 70, y + 112, 740, 24, [(src, mono(16, color=DIM))])
        y += 160
        hline(s, x0, y, 820, FAINT, 1)
a = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, px(925), px(560), px(985), px(560))
a.line.color.rgb = rgb(INK); a.line.width = Pt(2)
a.line._get_or_add_ln().append(etree.fromstring('<a:tailEnd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" type="triangle" w="med" len="med"/>'))
rect(s, 80, 880, 1760, 100, fill=INK, line=None)
text(s, 120, 880, 260, 100, [("THE CONTRIBUTION", caps(16, color=PAPER))], anchor=MSO_ANCHOR.MIDDLE)
text(s, 400, 880, 1400, 100, [("A checkable reasoning framework — not a new biological finding.", serif(36, color=PAPER))],
     anchor=MSO_ANCHOR.MIDDLE)

# ================================================================ 3 · data structure
s = base(3, cite="GEO GSE298774 · Space Ranger 2.1.1 · QC thresholds: Kreuger et al. 2026, Methods · A2 excluded (no barcode file)")
topbar(s, [("One GEO sample can hold several patients, so everything runs ", 0), ("per patient, in µm", 1)], "GSE298774 · Visium")
picture(s, "shared", 80, 250, 860, 520)
legend(s, 80, 778, [("A24", "k"), ("A22", "m"), ("neither patient", "f")])
text(s, 520, 778, 420, 24, [("· one capture area, GSM9022967", mono(17, color=DIM))])
chain = [("Capture area", "one GEO sample · 11 hold 19 patients", "GSM9022967", "line"),
         ("Patient / section", "unit of analysis · 18 usable", "A24", "solid"),
         ("Tissue region", "no independent label → provisional", "PRAME > 1.5", "dash"),
         ("Spot", "55 µm · centres 100 µm apart", "6,059 in A24", "line")]
for i, (h4, sm, eg, kind) in enumerate(chain):
    y = 250 + i * 130
    col = PAPER if kind == "solid" else INK
    rect(s, 1010, y, 830, 100, fill=INK if kind == "solid" else PAPER, dash=(kind == "dash"))
    text(s, 1034, y + 12, 560, 46, [(h4, serif(36, color=col))])
    text(s, 1034, y + 60, 560, 28, [(sm, S(19, color=col))])
    text(s, 1500, y + 36, 316, 28, [(eg, mono(18, color=col))], align=PP_ALIGN.RIGHT)
    if i < 3:
        vline(s, 1050, y + 100, 22, INK, 1.5)
        t = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, px(1043), px(y + 120), px(14), px(10))
        t.rotation = 180; t.fill.solid(); t.fill.fore_color.rgb = rgb(INK); t.line.fill.background(); t.shadow.inherit = False
hline(s, 1010, 790, 830)
for i, (n, l) in enumerate([("> 500", "genes per spot,\n< 30% MT (paper QC)"), ("µm", "from the 100 µm spot grid,\nnever pixels"),
                            ("0", "links between\ndifferent sections")]):
    x = 1010 + i * 277 + (20 if i else 0)
    if i:
        vline(s, 1010 + i * 277, 800, 140)
    text(s, x, 804, 250, 64, [(n, S(54, "Cambria") if n == "0" else serif(54))])
    text(s, x, 876, 250, 60, [(ln, S(18)) for ln in l.split("\n")], line=1.0)

# ================================================================ 4 · QC
s = base(4, cite="Maps: solid = removed (≤ 500 genes), faint = kept · notebooks/03_explore_GSE298774.ipynb · cluster names provisional")
topbar(s, [("QC reproduces the paper's count, but removes ", 0), ("low‑RNA tissue", 1), (", not the lesion", 0)], "Reproduced", "solid")
text(s, 80, 250, 620, 24, [("% SPOTS KEPT · 18 PATIENTS", caps(16))])
rows = [("B38ex", 1861, 1855), ("B1", 3952, 3931), ("A24", 6165, 6059), ("D20", 1089, 1056), ("A22", 4326, 4081),
        ("A21", 2260, 1934), ("B4", 6415, 5419), ("D3", 1501, 1208), ("A23", 2782, 2143), ("A16", 5195, 2768),
        ("B38_2", 2100, 1094), ("A7", 2892, 1289), ("B13", 3614, 1536), ("A34", 4151, 1631), ("A17", 2274, 863),
        ("B15", 3171, 1069), ("B14", 2206, 669), ("B8", 5780, 878)]
cd = CategoryChartData()
cd.categories = [r[0] for r in rows]
cd.add_series("% kept", [round(100 * a / b, 1) for _, b, a in rows])
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, px(70), px(278), px(650), px(540), cd)
ch = gf.chart
ch.has_title = False
ch.has_legend = False
ch.font.name, ch.font.size = MONO, Pt(8)
ch.font.color.rgb = rgb(INK)
plot = ch.plots[0]
plot.gap_width = 55
plot.has_data_labels = True
dl = plot.data_labels
dl.number_format, dl.number_format_is_linked = '0"%"', False
dl.position = XL_LABEL_POSITION.OUTSIDE_END
dl.font.size, dl.font.name = Pt(8), MONO
ser = plot.series[0]
ser.format.fill.solid(); ser.format.fill.fore_color.rgb = rgb(INK)
ca, va = ch.category_axis, ch.value_axis
ca.reverse_order = True
ca.format.line.color.rgb = rgb(INK)
ca.has_major_gridlines = False
va.maximum_scale, va.minimum_scale = 112, 0
va.visible = False
va.has_major_gridlines = False
for i, (pid, sub) in enumerate([("A24", "106 of 6,165 removed"), ("B4", "996 of 6,415 removed"), ("A16", "2,427 of 5,195 removed")]):
    x = 770 + i * 367
    pct = {"A24": "1.7%", "B4": "15.5%", "A16": "46.7%"}[pid]
    text(s, x, 248, 180, 46, [(pid, serif(36))])
    text(s, x + 157, 248, 180, 46, [(pct, serif(36))], align=PP_ALIGN.RIGHT)
    hline(s, x, 296, 337)
    text(s, x, 302, 337, 22, [(sub, mono(15))])
    picture(s, f"qc{pid}", x, 316, 337, 420)
text(s, 770, 772, 320, 24, [("A24 CLUSTERING AFTER QC", caps(16))])
text(s, 770, 800, 320, 22, [("IFN-γ / T-cell cluster, 265 spots", mono(15))])
bx, bw = 1098, 742
for frac, fill, lab, col in [(0.63, INK, "63% stay together", PAPER), (0.25, "B6B7E0", "25% → antibody", INK), (0.12, "DFDCE3", "12%", INK)]:
    rect(s, bx, 772, bw * frac, 40, fill=fill, lw=1)
    text(s, bx + 12, 772, bw * frac - 14, 40, [(lab, mono(16, color=col))], anchor=MSO_ANCHOR.MIDDLE)
    bx += bw * frac
abc(s, [("Tested", "Paper thresholds, all 18 patients"), ("Shows", "39,483 kept vs 39,481; melanocytic clusters lose 0%"),
        ("Open", "500 genes may be too strict for dermis, fat, blood")])

# ================================================================ 5 · operations
s = base(5, cite="x-axis: neighbours per spot · touching spots are 99.8–101.2 µm apart, so “touching” uses r = 150 µm · src/space_mel/operations.py · tests/")
topbar(s, [("Three spatial operations return the known answer: ", 0), ("21 of 21 tests pass", 1)], "Tested · synthetic", "solid")
ops = [(80, "op1", "Spots within a radius", "spots_within_radius", "neighbours of the ringed spot within 100 µm", "6"),
       (681, "op2", "Distance to a region", "distance_to_region", "ringed spot to the nearest spot of region R", "200 µm"),
       (1283, "op3", "Neighbourhood fraction", "neighbourhood_fraction", "neighbours of the ringed spot in category C", "4 / 6")]
for x, img_name, h3, call, q, v in ops:
    text(s, x, 250, 557, 44, [(h3, serif(36))])
    text(s, x, 296, 557, 22, [(call, mono(16, color=DIM))])
    picture(s, img_name, x, 318, 557, 280)
    hline(s, x, 604, 557)
    text(s, x, 614, 320, 54, [(q, S(19))], line=1.0)
    text(s, x + 297, 604, 260, 70, [(v, serif(56))], align=PP_ALIGN.RIGHT)
text(s, 80, 720, 760, 24, [("EDGE CASES THE TESTS PIN DOWN", caps(16))])
cx = 80
for lab, val in [("exactly at r", "counted"), ("no neighbours", "empty · NaN"), ("the spot itself", "excluded"),
                 ("two sections", "never linked"), ("bad input", "error")]:
    w = max(len(lab) * 9.4, len(val) * 9.6) + 30
    rect(s, cx, 752, w, 62, fill=PAPER)
    text(s, cx + 14, 760, w - 20, 22, [(lab, mono(15))])
    text(s, cx + 14, 783, w - 20, 24, [(val, S(18))])
    cx += w + 12
text(s, 900, 720, 940, 24, [("ON REAL A24 COORDINATES, R MUST SIT BETWEEN GRID RINGS", caps(16))])
nb = {"100": {0: 832, 1: 4930, 2: 297}, "150": {1: 8, 2: 16, 3: 103, 4: 190, 5: 295, 6: 5447}}
for j, rad in enumerate(["100", "150"]):
    x = 900 + j * 494
    text(s, x, 764, 446, 24, [(f"r = {rad} µm" + (" · used for “touching”" if rad == "150" else ""), mono(17))])
    cd = CategoryChartData()
    cd.categories = [str(k) for k in range(7)]
    cd.add_series("% of spots", [round(100 * nb[rad].get(k, 0) / 6059, 1) for k in range(7)])
    ch = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, px(x - 10), px(790), px(466), px(160), cd).chart
    ch.has_title = False
    ch.has_legend = False
    ch.font.name, ch.font.size = MONO, Pt(7.5)
    ch.font.color.rgb = rgb(INK)
    p = ch.plots[0]
    p.gap_width = 40
    p.has_data_labels = True
    p.data_labels.number_format, p.data_labels.number_format_is_linked = '[>=1]0"%";;;', False
    p.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    p.series[0].format.fill.solid(); p.series[0].format.fill.fore_color.rgb = rgb(INK)
    ch.value_axis.visible = False
    ch.value_axis.has_major_gridlines = False
    ch.value_axis.maximum_scale, ch.value_axis.minimum_scale = 105, 0
    ch.category_axis.format.line.color.rgb = rgb(INK)

# ================================================================ 6 · benchmark
s = base(6, cite="02_spatial_operations/benchmark/benchmark.csv · docs/02_benchmark.md")
topbar(s, [("A first benchmark: ", 0), ("15 questions", 1), (", 9 tasks asked in two wordings", 0)], "Preliminary · new", "dash")
bench = [("Spots within\na radius", "spots_within_radius", "5", [("B01", "t"), ("B02", "t"), ("B03", "a"), ("B04", "a"), ("B13", "t")],
          "“Which spots touch spot AACTGCCGCTACATCT-1?”", "A24 · touching = within 150 µm"),
         ("Distance to\na region", "distance_to_region", "6", [("B05", "t"), ("B06", "t"), ("B07", "a"), ("B08", "a"), ("B14", "t"), ("B15", "w")],
          "“How far is spot GACGCTCGAGGAGTGC-1 from the nevus?”", "B15 · needs a per-spot nevus label"),
         ("Neighbourhood\nfraction", "neighbourhood_fraction", "4", [("B09", "t"), ("B10", "t"), ("B11", "a"), ("B12", "a")],
          "“What fraction of the spots touching AACTGCCGCTACATCT-1 are CXCL9-high?”", "A24 · CXCL9-high = CXCL9 > 2")]
for i, (h3, call, cnt, cells, eg, sm) in enumerate(bench):
    x = 80 + i * 601
    hline(s, x, 262, 557)
    text(s, x, 280, 400, 90, [(ln, serif(36)) for ln in h3.split("\n")], line=0.95)
    text(s, x + 397, 262, 160, 110, [(cnt, serif(96))], align=PP_ALIGN.RIGHT)
    text(s, x, 372, 400, 22, [(call, mono(16, color=DIM))])
    for k, (lab, kind) in enumerate(cells):
        cxx = x + k * 96
        fill = {"a": INK, "t": TINT, "w": PAPER}[kind]
        rect(s, cxx, 412, 86, 86, fill=fill, line=INK if kind == "w" else None, dash=(kind == "w"))
        text(s, cxx + 7, 470, 76, 22, [(lab, mono(15, color=PAPER if kind == "a" else INK))])
    text(s, x, 524, 557, 120, [(eg, serif(29))], line=1.05)
    text(s, x, 650, 557, 22, [(sm, mono(15))])
kx = 80
for lab, kind in [("answered · A24", "a"), ("answered · synthetic", "t"), ("awaiting independent annotation", "w")]:
    rect(s, kx, 800, 22, 22, fill={"a": INK, "t": TINT, "w": PAPER}[kind], line=INK if kind == "w" else None, dash=(kind == "w"))
    w = len(lab) * 10.2 + 10
    text(s, kx + 32, 799, w, 24, [(lab, mono(17))])
    kx += 32 + w + 30
abc(s, [("Recorded", "Inputs, operation, parameters + units, assumptions"), ("Checked", "By hand (toy) and brute force (A24): all match"),
        ("Not yet", "Signature enrichment; no LLM has been run")])

# ================================================================ 7 · worked examples
s = base(7, cite="benchmark.csv rows B01, B07, B11 · recomputed in presentation_week2/make_figure_data.py and asserted equal to the table")
topbar(s, [("Three worked reference answers, ", 0), ("computed by tested code", 1)], "Checked twice", "line")
picture(s, "a24map", 80, 244, 540, 500)
legend(s, 80, 752, [("PRAME > 1.5", "k"), ("CXCL9 > 2", "o"), ("other", "f")])
exs = [("B01 · synthetic", "“Which spots are within 100 µm of spot r0c0?”", "ex1", "6 spots", "exact · count by hand"),
       ("B07 · A24", "“How far is GACGCTCGAGGAGTGC-1 from the nearest PRAME-high spot?”", "ex2", "265.3 µm", "region is provisional"),
       ("B11 · A24", "“What fraction of the spots touching AACTGCCGCTACATCT-1 are CXCL9-high?”", "ex3", "1 / 6", "= 0.17 · provisional category")]
hline(s, 690, 244, 1150)
for i, (idl, q, img_name, v, sm) in enumerate(exs):
    y = 244 + i * 195
    w = len(idl) * 9.6 + 20
    rect(s, 690, y + 62, w, 26, fill=PAPER)
    text(s, 690, y + 62, w, 26, [(idl, mono(15))], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    parts = q.split("r0c0")
    runs = [(parts[0], serif(30))] + ([("r0c0", mono(28)), (parts[1], serif(30))] if len(parts) > 1 else [])
    text(s, 690, y + 98, 600, 90, [runs], line=1.0)
    picture(s, img_name, 1322, y + 13, 250, 170)
    text(s, 1600, y + 50, 250, 64, [(v, serif(50))])
    text(s, 1600, y + 122, 240, 44, [(sm, mono(15))])
    hline(s, 690, y + 195, 1150, FAINT, 1)
abc(s, [("Tested", "Operations vs an independent calculation"), ("Shows", "Exact answer given the stated definition"),
        ("Open", "Is PRAME > 1.5 a defensible tumour proxy?")])

# ================================================================ 8 · limitations, next, ask
s = base(8, cite="Status note: docs/status_note_week2.md · all code and figures in spatial-reasoning/")
topbar(s, [("The main blocker is ", 0), ("ground truth for regions", 1)], "Limitations · next step")
lims = [("No independent nevus / melanoma label per spot", "regions are expression thresholds · B15 waits"),
        ("The 500-gene threshold leaves holes around the lesion", "A16 loses 47% · B8, B14, A17 keep < 900 spots"),
        ("Signature enrichment not implemented yet", "“is gene X higher near region Y?”"),
        ("Real-data examples cover one patient only", "A24, one threshold per gene")]
hline(s, 80, 250, 848)
for i, (h4, hint) in enumerate(lims):
    y = 250 + i * 112
    text(s, 80, y + 22, 50, 46, [(str(i + 1), serif(36))])
    text(s, 142, y + 22, 786, 44, [(h4, serif(31))])
    text(s, 142, y + 66, 786, 24, [(hint, mono(16, color=DIM))])
    hline(s, 80, y + 112, 848, FAINT, 1)
rect(s, 992, 250, 848, 214, fill=PAPER)
text(s, 1022, 274, 780, 24, [("MOST IMPORTANT NEXT STEP", caps(16))])
text(s, 1022, 306, 790, 60, [("Independent region labels for A24", serif(46))])
text(s, 1022, 374, 790, 70, [("From a pathologist on the H&E, or from the authors. Unblocks B15 and any tumour / nevus validation.", S(21))],
     line=1.05)
for i, (lab, t) in enumerate([("then 02", "Gentler or per-patient QC threshold"), ("then 03", "Benchmark on a second patient (B4)"),
                              ("later", "First LLM test: does it pick the right operation?")]):
    x = 992 + i * 288
    hline(s, x, 486, 272)
    text(s, x, 496, 272, 22, [(lab, mono(15))])
    text(s, x, 520, 272, 60, [(t, S(19))], line=1.0)
rect(s, 80, 846, 1760, 136, fill=INK, line=None)
text(s, 104, 866, 240, 22, [("Feedback needed", mono(15, color=PAPER))])
text(s, 104, 890, 240, 84, [("Three decisions", serif(36, color=PAPER))], line=0.95)
for i, (lab, q) in enumerate([("Q1 · labels", "Who could give per-spot ground truth: the authors or a pathologist?"),
                              ("Q2 · QC", "Relax 500 genes for low-RNA tissue, or drop B8, B14, A17?"),
                              ("Q3 · benchmark", "Is this format right before adding more questions?")]):
    x = 360 + i * 493
    vline(s, x, 846, 136, "8D93E9", 1)
    text(s, x + 24, 866, 450, 22, [(lab, mono(15, color=PAPER))])
    text(s, x + 24, 892, 450, 80, [(q, S(21, color=PAPER))], line=1.05)

prs.save(OUT)
print("wrote", OUT)
