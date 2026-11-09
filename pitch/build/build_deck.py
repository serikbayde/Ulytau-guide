"""Сборка Ulytau_Gid_Pitch.pptx (python-pptx). Запуск: python3 pitch/build/build_deck.py"""
import json, pathlib
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn
from lxml import etree

ROOT = pathlib.Path(__file__).resolve().parents[2]
A = ROOT / "pitch/assets"
NOTES = json.load(open(ROOT / "pitch/build/notes_kk.json", encoding="utf-8"))
CREDITS = json.load(open(ROOT / "pitch/build/photo_meta.json", encoding="utf-8"))

NAVY, OCHRE, SKY, CREAM, WHITE = "0F1B2D", "D9A441", "4FA3D9", "F7F1E6", "FFFFFF"
NAVY2 = "1B2A41"   # чуть светлее фона — для карточек на тёмном
MUTED_D, MUTED_L = "A9B4C4", "5B6575"
H, B = "Montserrat", "Inter"
BOT = "@yelulytaubot"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
SW, SH = 13.333, 7.5
M = 0.75                      # поля
BLANK = prs.slide_layouts[6]

def rgb(h): return RGBColor.from_string(h)

def bg(slide, color):
    f = slide.background.fill; f.solid(); f.fore_color.rgb = rgb(color)

def pic(slide, path, x, y, w=None, h=None):
    kw = {}
    if w is not None: kw["width"] = Inches(w)
    if h is not None: kw["height"] = Inches(h)
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kw)

def text(slide, x, y, w, h, runs, size=20, color=NAVY, font=B, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=None, line=None):
    """runs: str | list of paragraphs; paragraph = str | list of (text, {opts})"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"): setattr(tf, side, 0)
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if line: p.line_spacing = line
        if spacing: p.space_after = Pt(spacing)
        for t, o in ([(para, {})] if isinstance(para, str) else para):
            r = p.add_run(); r.text = t
            f = r.font; f.name = o.get("font", font); f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold); f.italic = o.get("italic", False)
            f.color.rgb = rgb(o.get("color", color))
            if "track" in o:   # межбуквенный интервал
                r._r.get_or_add_rPr().set("spc", str(o["track"]))
    return tb

def box(slide, x, y, w, h, fill, line=None, radius=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, lw=1.25):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.shadow.inherit = False
    if fill: s.fill.solid(); s.fill.fore_color.rgb = rgb(fill)
    else: s.fill.background()
    if line: s.line.color.rgb = rgb(line); s.line.width = Pt(lw)
    else: s.line.fill.background()
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    return s

def label(slide, txt, dark):
    text(slide, M, 0.62, 8, 0.4, [[(txt, {"track": 300})]], size=14, font=H, bold=True, color=OCHRE)

def title(slide, txt, dark, y=0.98, size=44, w=11.8):
    text(slide, M, y, w, 1.2, txt, size=size, font=H, bold=True, color=WHITE if dark else NAVY, line=1.0)

TOTAL = 14
def idx(): return len(prs.slides._sldIdLst)
def num(slide, n, dark):
    n = idx()
    text(slide, SW - M - 1.0, SH - 0.5, 1.0, 0.3, f"{n:02d} / {TOTAL}", size=10, font=H,
         color=MUTED_D if dark else MUTED_L, align=PP_ALIGN.RIGHT)

def icon(name, color): return A / "icons" / f"{name}_{color}.png"

def icon_badge(slide, x, y, d, name, fill, color):
    box(slide, x, y, d, d, fill, shape=MSO_SHAPE.OVAL)
    pad = d * 0.24; pic(slide, icon(name, color), x + pad, y + pad, w=d - 2 * pad)

def notes(slide, n):
    slide.notes_slide.notes_text_frame.text = NOTES[str(idx())]

def gradient_rect(slide, x, y, w, h, color, a1, a2, angle=90):
    """Прозрачный градиент (для читаемости поверх фото)."""
    s = box(slide, x, y, w, h, color, shape=MSO_SHAPE.RECTANGLE)
    spPr = s._element.spPr
    for el in spPr.findall(qn("a:solidFill")): spPr.remove(el)
    g = etree.SubElement(spPr, qn("a:gradFill")); g.set("rotWithShape", "1")
    gs = etree.SubElement(g, qn("a:gsLst"))
    for pos, a in ((0, a1), (100000, a2)):
        st = etree.SubElement(gs, qn("a:gs")); st.set("pos", str(pos))
        c = etree.SubElement(st, qn("a:srgbClr")); c.set("val", color)
        al = etree.SubElement(c, qn("a:alpha")); al.set("val", str(int(a * 1000)))
    lin = etree.SubElement(g, qn("a:lin")); lin.set("ang", str(angle * 60000)); lin.set("scaled", "0")
    # gradFill должен идти до a:ln
    ln = spPr.find(qn("a:ln"))
    if ln is not None: spPr.remove(g); ln.addprevious(g)
    return s

def credits_line():
    seen, parts = set(), []
    used = ["File:Горы Улытау 2.jpg", "File:Жошы хан кесенесі.jpg", "File:Aulietau-Akmeshit.jpg", "File:Ulutay 1.jpg",
            "File:Dombauyl.jpg", "File:Ulutay 2.jpg", "File:Terekti-Aulie 1.jpg", "File:Alasha-Khan Mausoleum-1.jpg"]
    by = {m["title"]: m for m in CREDITS}
    for t in used:
        m = by[t]; parts.append(f"{t[5:].rsplit('.',1)[0]} — {m['artist']}, {m['lic']}")
    return ("Суреттер: " + "; ".join(parts) + " · Wikimedia Commons. Иконкалар: Lucide (ISC). "
            "Телефон экрандары — боттың нақты мәтіндерінен жасалған макет.")

# ───────────────────────── 1. Титул ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
pic(s, A / "photos/s01_title_ulytau.jpg", 0, 0, w=SW)
text(s, M, 0.62, 10, 0.4, [[("PIZZA PITCH  ·  ULYTAU HUB  ·  14 ҚАРАША 2026", {"track": 250})]],
     size=14, font=H, bold=True, color=OCHRE)
text(s, M, 3.55, 11.5, 1.4, "Ұлытау гид", size=88, font=H, bold=True, color=WHITE)
text(s, M, 4.95, 11.5, 0.6, "Ұлы даланың жүрегі — қалтаңызда", size=30, font=B, color=WHITE)
box(s, M, 5.85, 0.9, 0.06, OCHRE, shape=MSO_SHAPE.RECTANGLE)
text(s, M, 6.1, 11.5, 0.45, [[("Telegram-бот  ", {"bold": True, "color": OCHRE}), (BOT + "   ·   ", {}),
     ("[КОМАНДА АТАУЫ]  ·  [Аты-жөні 1]  ·  [Аты-жөні 2]", {})]], size=18, color=WHITE)
notes(s, 1)

# ───────────────────────── 2. Хук ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
pic(s, A / "photos/s02_hook_zhoshy.jpg", 0, 0, w=SW)
text(s, M, 1.95, 6.4, 3.8, [[("Ұлытауға", {"color": WHITE})], [("келдіңіз.", {"color": WHITE})], [("Ал енді", {"color": OCHRE})],
     [("қайда барасыз?", {"color": OCHRE})]], size=50, font=H, bold=True, line=1.05)
text(s, M, SH - 0.82, 6, 0.3, "Жошы хан кесенесі, Ұлытау облысы", size=12, color=MUTED_D)
num(s, 2, True); notes(s, 2)

# ───────────────────────── 3. Мәселе ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, CREAM)
label(s, "МӘСЕЛЕ", False); title(s, "Ұлытауда туристке жол табу қиын", False)
cols = [("search-x", "Ақпарат шашыраңқы", "Ондаған сайт пен парақшаға тараған"),
        ("languages", "Тіл кедергісі", "Үш тіл бір жерде — сирек кездеседі"),
        ("route", "Дайын маршрут жоқ", "Қанша шақырым, қанша сағат — белгісіз")]
cw, gap = 3.6, (SW - 2 * M - 3 * 3.6) / 2
for i, (ic, t, d) in enumerate(cols):
    x = M + i * (cw + gap)
    box(s, x, 2.45, cw, 3.7, WHITE, radius=0.08)
    icon_badge(s, x + 0.45, 2.8, 1.0, ic, NAVY, "ochre")
    text(s, x + 0.45, 4.0, cw - 0.7, 0.9, t, size=24, font=H, bold=True, line=1.0)
    text(s, x + 0.45, 4.95, cw - 0.7, 1.1, d, size=20, color=MUTED_L, line=1.1)
text(s, M, 6.42, 11.8, 0.4, "[САУАЛНАМА ДЕРЕГІ: сауалнамаға қатысқан туристердің ...% Ұлытау туралы ақпарат табу қиын дейді]",
     size=14, color="B07D1E", font=B, bold=True)
num(s, 3, False); notes(s, 3)

# ───────────────────────── 4. Шешім ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
pic(s, A / "ornament_ochre.png", SW - 2.3, 0.0, w=2.3).rotation = 90
label(s, "ШЕШІМ", True)
text(s, M, 1.3, 7.3, 2.4, [[("Ұлытау гид — ", {"color": OCHRE})], [("Telegram ішіндегі", {})], [("қалта гиді", {})]],
     size=50, font=H, bold=True, color=WHITE, line=1.02)
text(s, M, 4.05, 6.9, 1.3, "Орындар, маршруттар және AI-гид. Үш тілде. Қосымша орнатпай-ақ.",
     size=24, color=MUTED_D, line=1.2)
text(s, M, 5.45, 6, 0.35, [[("КІМГЕ", {"track": 300})]], size=14, font=H, bold=True, color=OCHRE)
for i, (ic, t) in enumerate([("users", "Ішкі туристер"), ("footprints", "Зияратшылар"), ("plane", "Шетелдік қонақтар")]):
    x = M + i * 2.55
    box(s, x, 5.9, 2.4, 0.72, NAVY2, radius=0.5)
    pic(s, icon(ic, "ochre"), x + 0.18, 6.04, w=0.44)
    text(s, x + 0.72, 5.9, 1.65, 0.72, t, size=15, font=H, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE, line=0.95)
pic(s, A / "mockups/menu.png", 8.55, 0.42, h=6.66)
num(s, 4, True); notes(s, 4)

# ───────────────────────── 5. Қалай жұмыс істейді ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, CREAM)
label(s, "ҚАЛАЙ ЖҰМЫС ІСТЕЙДІ", False); title(s, "4 мүмкіндік — бір чатта", False)
cards = [("card_dombauyl.jpg", "map-pin", "Орындар", "14 орын · карта · дереккөз"),
         ("card_ulytau_park.jpg", "route", "Маршруттар", "1 күн · 2 күн · демалыс"),
         ("card_terekti.jpg", "bot", "AI-гид", "Тек тексерілген дерек бойынша"),
         ("card_alasha.jpg", "languages", "3 тіл", "Қазақша · Русский · English")]
cw = 2.74; gap = (SW - 2 * M - 4 * cw) / 3
for i, (ph, ic, t, d) in enumerate(cards):
    x = M + i * (cw + gap); y = 2.35
    box(s, x, y, cw, 4.3, WHITE, radius=0.06)
    pic(s, A / "photos" / ph, x, y, w=cw)
    icon_badge(s, x + 0.3, y + 1.6 - 0.45, 0.9, ic, OCHRE, "navy")
    text(s, x + 0.3, y + 2.2, cw - 0.45, 0.6, t, size=22, font=H, bold=True)
    text(s, x + 0.3, y + 2.85, cw - 0.5, 1.2, d, size=20, color=MUTED_L, line=1.1)
num(s, 5, False); notes(s, 5)

# ───────────────────────── 6. Демо ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
label(s, "ДЕМО", True)
text(s, M, 1.3, 7, 2.2, [[("Тікелей", {})], [("демо", {"color": OCHRE})]], size=80, font=H, bold=True, color=WHITE, line=0.95)
box(s, M, 3.95, 2.55, 2.55, CREAM, radius=0.08)
pic(s, A / "qr_dark.png", M + 0.15, 4.1, w=2.25)
text(s, M + 2.9, 4.1, 3.2, 2.4, [[("QR-ды сканерлеп,", {})], [("бірге көрейік!", {})],
     [(BOT, {"color": OCHRE, "bold": True, "font": H})]], size=24, color=WHITE, line=1.25, spacing=6)
p1 = pic(s, A / "mockups/place.png", 7.05, 0.75, h=6.35); p1.rotation = -4
p2 = pic(s, A / "mockups/ai.png", 9.75, 0.45, h=6.35); p2.rotation = 4
num(s, 6, True); notes(s, 6)

# ───────────────────────── 7. Техникалық құрылым ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, CREAM)
label(s, "ТЕХНИКАЛЫҚ ҚҰРЫЛЫМ", False); title(s, "Қалай жасалған", False)
def node(x, y, w, h, ic, t, d, fill=WHITE, tc=NAVY, dc=MUTED_L, icol="ochre", bfill=NAVY):
    box(s, x, y, w, h, fill, radius=0.12)
    icon_badge(s, x + 0.3, y + (h - 0.85) / 2, 0.85, ic, bfill, icol)
    text(s, x + 1.35, y + 0.3, w - 1.5, 0.5, t, size=21, font=H, bold=True, color=tc)
    text(s, x + 1.35, y + 0.78, w - 1.5, 0.6, d, size=16, color=dc)
def arrow(x1, y1, x2, y2, color=OCHRE):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color); c.line.width = Pt(3)
    ln = c.line._get_or_add_ln(); t = etree.SubElement(ln, qn("a:tailEnd")); t.set("type", "triangle")
    t.set("w", "med"); t.set("len", "med")
y0 = 2.75
node(M, y0 + 0.8, 3.0, 1.45, "send", "Telegram", "турист жазады")
node(4.4, y0 + 0.8, 3.45, 1.45, "cpu", "Python бот", "aiogram, 24/7")
node(8.6, y0, 3.98, 1.45, "database", "Деректер", "14 орын · 3 маршрут · 3 тіл, дереккөзімен")
node(8.6, y0 + 1.6, 3.98, 1.45, "sparkles", "Gemini AI", "тек осы деректер бойынша", fill=NAVY, tc=WHITE, dc=MUTED_D, bfill=OCHRE, icol="navy")
arrow(M + 3.0 + 0.08, y0 + 1.525, 4.4 - 0.1, y0 + 1.525)
arrow(7.85 + 0.08, y0 + 1.3, 8.6 - 0.1, y0 + 0.75)
arrow(7.85 + 0.08, y0 + 1.75, 8.6 - 0.1, y0 + 2.3)
# главный тезис
box(s, M, 5.95, SW - 2 * M, 0.95, NAVY, radius=0.2)
pic(s, icon("shield-check", "ochre"), M + 0.3, 6.12, w=0.6)
text(s, M + 1.1, 5.95, 10.6, 0.95, [[("AI тек тексерілген деректен жауап береді. ", {"bold": True, "color": WHITE}),
     ("Дерек жоқ болса — «білмеймін» дейді.", {"color": OCHRE, "bold": True})]], size=21, anchor=MSO_ANCHOR.MIDDLE)
# чипы
for i, c in enumerate(["65 автотест", "temperature 0.2", "сервер — 0 ₸"]):
    box(s, M + i * 2.45, 2.25, 2.25, 0.42, None, line=OCHRE, radius=0.5)
    text(s, M + i * 2.45, 2.25, 2.25, 0.42, c, size=14, font=H, bold=True, color="9A6B12", align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
num(s, 7, False); notes(s, 7)

# ───────────────────────── Дәлел (traction) ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
label(s, "ДӘЛЕЛ", True); title(s, "MVP дайын және жұмыс істеп тұр", True)
facts = [("14", "орын, әрқайсысы\nдереккөзімен"), ("3", "дайын\nмаршрут"), ("3", "тіл: қазақша,\nорысша, ағылшынша"), ("65", "автотест\nөтті")]
cw = (SW - 2 * M) / 4
for i, (n, d) in enumerate(facts):
    x = M + i * cw
    text(s, x, 2.3, cw - 0.2, 1.2, n, size=72, font=H, bold=True, color=OCHRE)
    box(s, x, 3.55, 0.7, 0.05, SKY, shape=MSO_SHAPE.RECTANGLE)
    text(s, x, 3.75, cw - 0.3, 0.9, d, size=20, color=WHITE, line=1.1)
for i, ph in enumerate(["[ҚОЛДАНУШЫЛАР: ботты ... адам байқап көрді]", "[ПІКІР: «...» — турист / гид]"]):
    x = M + i * 5.98
    box(s, x, 5.2, 5.85, 1.05, NAVY2, line=OCHRE, radius=0.15)
    text(s, x + 0.3, 5.2, 5.3, 1.05, ph, size=18, bold=True, color=OCHRE, anchor=MSO_ANCHOR.MIDDLE)
num(s, 0, True); notes(s, 0)

# ───────────────────────── 8. Нарық ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
pic(s, A / "photos/s08_market_aulietau.jpg", 0, 0, w=SW)
label(s, "НАРЫҚ", True); title(s, "Сұраныс бар және өсіп келеді", True)
stats = [(("21", " мың"), "турист Ұлытау облысының\nқонақ үйлерінде\n(2024, 9 ай)"),
         (("+9,9%", ""), "Қазақстанда ішкі туризм\nөсімі (2025)"),
         (("≈7,6", " млн"), "Telegram қолданушысы\nҚазақстанда (бағалау)")]
cw = (SW - 2 * M) / 3
for i, (n, d) in enumerate(stats):
    x = M + i * cw
    text(s, x, 2.85, cw, 1.3, [[(n[0], {}), (n[1], {"size": 34})]], size=72, font=H, bold=True, color=OCHRE)
    box(s, x, 4.25, 0.7, 0.05, SKY, shape=MSO_SHAPE.RECTANGLE)
    text(s, x, 4.5, cw - 0.2, 1.2, d, size=20, color=WHITE, line=1.1)
text(s, M, 5.95, 11.8, 0.4, "[САУАЛНАМА ДЕРЕГІ: сауалнамаға қатысқандардың ...% Telegram-ды күн сайын қолданады]",
     size=14, color=OCHRE, bold=True)
text(s, M, 6.55, 10.5, 0.5, "Дереккөздер: TravelPress.kz, 26.12.2024 · Inbusiness.kz / Ranking.kz, 17.03.2026 · "
     "Telegram — үшінші тарап бағалауы. Толығы: PITCH_SOURCES.md", size=11, color=MUTED_D)
num(s, 8, True); notes(s, 8)

# ───────────────────────── 9. Табыс моделі ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, CREAM)
pic(s, A / "ornament_ochre.png", 0.0, SH - 1.45, w=1.45).rotation = 270
label(s, "ТАБЫС МОДЕЛІ", False)
text(s, M, 0.98, 11.8, 1.5, [[("Туристке — тегін.", {})], [("Табыс — серіктестерден.", {"color": "B07D1E"})]],
     size=40, font=H, bold=True, line=1.0)
cards = [("handshake", "Комиссия", "Гид, қонақ үй, турфирма: әкелген әр клиент үшін"),
         ("landmark", "Облыспен серіктестік", "Туризм саласына цифрлық құрал ретінде"),
         ("megaphone", "Жергілікті жарнама", "Кафе, сувенир, көлік — бот ішінде")]
cw, gap = 3.6, (SW - 2 * M - 3 * 3.6) / 2
for i, (ic, t, d) in enumerate(cards):
    x = M + i * (cw + gap)
    box(s, x, 2.75, cw, 3.35, NAVY, radius=0.08)
    text(s, x + 0.45, 2.85, 1.5, 0.9, f"0{i+1}", size=36, font=H, bold=True, color=OCHRE)
    pic(s, icon(ic, "sky"), x + cw - 1.2, 3.0, w=0.75)
    text(s, x + 0.45, 3.85, cw - 0.7, 0.85, t, size=22, font=H, bold=True, color=WHITE, line=1.0)
    text(s, x + 0.45, 4.75, cw - 0.7, 1.2, d, size=20, color=MUTED_D, line=1.1)
text(s, 2.4, 6.4, 10.2, 0.45, "[САУАЛНАМА ДЕРЕГІ: сұралған гидтер мен қонақ үйлердің ...% серіктес болуға дайын]",
     size=14, color="B07D1E", bold=True)
num(s, 9, False); notes(s, 9)

# ───────────────────────── 10. Бәсекелестер ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
label(s, "БӘСЕКЕЛЕСТЕР", True); title(s, "Бәрі бір жерде — тек бізде", True)
cols = ["Ұлытау гид", "Google Maps", "2GIS", "Туристік портал", "Жеке гид"]
rows = [("Ұлытау орындары, тарихымен", "YPPYY"), ("Күндік дайын маршрут", "YNNPY"),
        ("Сұраққа AI жауабы", "YNNNN"), ("Қазақша · орысша · ағылшынша", "YPPPP"),
        ("Тегін және 24/7", "YYYYN")]
x0, y0, lw, cwid, rh = M, 2.3, 4.0, (SW - 2 * M - 4.0) / 5, 0.68
box(s, x0 + lw - 0.05, y0 - 0.12, cwid + 0.1, rh * (len(rows) + 1) + 0.24, NAVY2, line=OCHRE, radius=0.08)
for j, c in enumerate(cols):
    text(s, x0 + lw + j * cwid + 0.05, y0, cwid - 0.1, rh, c, size=14, font=H, bold=True,
         color=OCHRE if j == 0 else MUTED_D, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
for i, (r, v) in enumerate(rows):
    y = y0 + rh * (i + 1)
    box(s, x0, y, SW - 2 * M, 0.012, "2E3D57", shape=MSO_SHAPE.RECTANGLE)
    text(s, x0, y, lw - 0.2, rh, r, size=19, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    for j, ch in enumerate(v):
        cx = x0 + lw + j * cwid + cwid / 2; d = 0.42
        if ch == "Y":   icon_badge(s, cx - d / 2, y + (rh - d) / 2, d, "check", OCHRE if j == 0 else SKY, "navy")
        elif ch == "N": pic(s, icon("x", "white"), cx - 0.16, y + (rh - 0.32) / 2, w=0.32)
        else:           pic(s, icon("minus", "white"), cx - 0.16, y + (rh - 0.32) / 2, w=0.32)
text(s, M, 6.55, 11.8, 0.4, "—  ішінара.  Команданың бағалауы, 2026 ж. қараша. Туристік портал: vizit-ulytau.kz",
     size=12, color=MUTED_D)
num(s, 10, True); notes(s, 10)

# ───────────────────────── 11. Жоспарлар ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, CREAM)
label(s, "ЖОСПАРЛАР", False); title(s, "Келесі қадамдар", False)
steps = [("ҚАЗІР", "MVP дайын", "14 орын, 3 маршрут, AI-гид", "check", True),
         ("ҚЫС", "Жаңа орындар", "14 орыннан → 50+ орынға", "map-pin", False),
         ("КӨКТЕМ", "Брондау", "Гид, қонақ үй, көлік — ботта", "calendar-check", False),
         ("ЖАЗ", "Офлайн режим", "Интернетсіз карта мен мәтін", "wifi-off", False)]
cw = (SW - 2 * M) / 4; ly = 2.35
box(s, M + 0.45, ly + 0.43, SW - 2 * M - cw + 0.1, 0.06, OCHRE, shape=MSO_SHAPE.RECTANGLE)
for i, (when, t, d, ic, done) in enumerate(steps):
    x = M + i * cw
    icon_badge(s, x, ly, 0.92, ic, NAVY if done else OCHRE, "ochre" if done else "navy")
    text(s, x, ly + 1.25, cw - 0.3, 0.4, [[(when, {"track": 200})]], size=14, font=H, bold=True, color="9A6B12")
    text(s, x, ly + 1.65, cw - 0.25, 0.9, t, size=22, font=H, bold=True, line=1.0)
    text(s, x, ly + 2.55, cw - 0.35, 1.0, d, size=20, color=MUTED_L, line=1.1)
box(s, M, 6.0, SW - 2 * M, 0.8, NAVY, radius=0.3)
pic(s, icon("layers", "ochre"), M + 0.3, 6.13, w=0.54)
text(s, M + 1.05, 6.0, 10.6, 0.8, [[("Масштаб: ", {"bold": True, "color": OCHRE}),
     ("жаңа өңір — жаңа деректер файлы ғана. Код сол күйі қалады.", {"color": WHITE})]], size=20, anchor=MSO_ANCHOR.MIDDLE)
num(s, 11, False); notes(s, 11)

# ───────────────────────── Команда ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
label(s, "КОМАНДА", True); title(s, "Біз кімбіз", True)
team = [("code", "[Аты-жөні 1]", "[Рөлі: бағдарламашы — бот, AI-гид]", "[Құзыреті: Python, ...; жетістіктері]"),
        ("presentation", "[Аты-жөні 2]", "[Рөлі: деректер, дизайн, питч]", "[Құзыреті: ...; жетістіктері]")]
cw = (SW - 2 * M - 0.4) / 2
for i, (ic, n, r, c) in enumerate(team):
    x = M + i * (cw + 0.4)
    box(s, x, 2.3, cw, 3.4, NAVY2, radius=0.08)
    box(s, x + 0.45, 2.75, 1.6, 1.6, "2E3D57", line=OCHRE, shape=MSO_SHAPE.OVAL, lw=2)
    text(s, x + 0.45, 2.75, 1.6, 1.6, "[ФОТО]", size=14, font=H, bold=True, color=MUTED_D, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 2.35, 2.8, cw - 2.6, 0.6, n, size=26, font=H, bold=True, color=WHITE)
    text(s, x + 2.35, 3.45, cw - 2.6, 0.9, r, size=20, color=OCHRE, line=1.05)
    text(s, x + 0.45, 4.65, cw - 0.8, 0.9, c, size=18, color=MUTED_D, line=1.1)
text(s, M, 6.05, 11.8, 0.5, "[Ментор / кеңесші, бар болса]  ·  [Мектеп / оқу орны]", size=18, color=MUTED_D)
num(s, 0, True); notes(s, 0)

# ───────────────────────── 12. Рахмет ─────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
pic(s, A / "photos/s12_final_ulytau.jpg", 0, 0, w=SW)
text(s, M, 0.55, 7, 1.3, "Рахмет!", size=72, font=H, bold=True, color=WHITE)
text(s, M, 1.95, 7, 0.5, [[("БІЗ СҰРАЙМЫЗ", {"track": 300})]], size=14, font=H, bold=True, color=OCHRE)
asks = [("handshake", "Серіктестік", "облыстың туризм саласымен"),
        ("database", "Деректер", "«Ұлытау» қорық-мұражайынан"),
        ("landmark", "Пилот", "облыс әкімдігімен бірге")]
for i, (ic, t, d) in enumerate(asks):
    y = 2.5 + i * 0.95
    icon_badge(s, M, y, 0.7, ic, OCHRE, "navy")
    text(s, M + 0.95, y, 6.5, 0.7, [[(t + "  ", {"bold": True, "font": H, "color": WHITE}), (d, {"color": "DDE3EC"})]],
         size=22, anchor=MSO_ANCHOR.MIDDLE)
text(s, M, 5.4, 8.3, 0.8, ["[КОМАНДА АТАУЫ]  ·  [телефон / e-mail]"],
     size=16, color=WHITE)
box(s, 9.55, 1.15, 3.0, 3.55, CREAM, radius=0.08)
pic(s, A / "qr_dark.png", 9.75, 1.3, w=2.6)
text(s, 9.55, 3.95, 3.0, 0.6, BOT, size=20, font=H, bold=True, color=NAVY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
gradient_rect(s, 0, SH - 1.05, SW, 1.05, NAVY, 0, 92, angle=90)
text(s, M, SH - 0.72, SW - 2 * M - 1.2, 0.6, credits_line(), size=8, color="C9D1DD", line=1.05)
num(s, 12, True); notes(s, 12)

out = ROOT / "pitch/Ulytau_Gid_Pitch.pptx"; prs.save(out); print("saved", out)
