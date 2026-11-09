"""Обрезка фото под слайды (Pillow) + затемняющий градиент для текста."""
import json, pathlib, sys
from PIL import Image, ImageDraw
ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = pathlib.Path(sys.argv[1])            # папка со скачанными 0.jpg, 1.jpg...
PH = ROOT / "pitch/assets/photos"
meta = json.load(open(ROOT / "pitch/build/photo_meta.json", encoding="utf-8"))
idx = {m["title"]: i for i, m in enumerate(meta)}
NAVY = (15, 27, 45)

def load(title):
    return Image.open(RAW / f"{idx[title]}.jpg").convert("RGB")

def crop(im, ratio, fx=0.5, fy=0.5, keep_h=1.0):
    """Обрезка под ratio; fx/fy — где центр кадра; keep_h<1 отрезает низ (дата на фото)."""
    w, h = im.size; h = int(h * keep_h); im = im.crop((0, 0, w, h))
    if w / h > ratio:
        nw = int(h * ratio); x = int((w - nw) * fx); return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio); y = int((h - nh) * fy); return im.crop((0, y, w, y + nh))

def grad(im, kind, strength=0.88, base=0.0):
    w, h = im.size
    mask = Image.new("L", (w, h), 0); d = ImageDraw.Draw(mask)
    for i in range(w if kind == "left" else h):
        if kind == "left":   t = max(0.0, 1 - i / (w * 0.62))
        else:                t = max(0.0, (i / h - 0.30) / 0.70)
        a = int(255 * min(1.0, base + strength * t ** 1.3))
        if kind == "left": d.line([(i, 0), (i, h)], fill=a)
        else:              d.line([(0, i), (w, i)], fill=a)
    return Image.composite(Image.new("RGB", (w, h), NAVY), im, mask)

def save(im, name, size):
    im = im.resize(size, Image.LANCZOS); im.save(PH / name, quality=88); print(name, im.size)

# фото на весь слайд (2400×1350, 16:9)
im = grad(crop(load("File:Горы Улытау 2.jpg"), 16/9, fy=0.35, keep_h=0.86), "bottom", 0.92, 0.12)
im = grad(im.transpose(Image.FLIP_TOP_BOTTOM), "bottom", 0.55, 0.0).transpose(Image.FLIP_TOP_BOTTOM)  # затемнить верх под надпись
save(im, "s01_title_ulytau.jpg", (2400, 1350))
# хук: слева тёмная панель под текст, справа фото мавзолея с плавным переходом
ph = crop(load("File:Жошы хан кесенесі.jpg"), 1.1, fx=0.62).resize((1485, 1350), Image.LANCZOS)
canvas = Image.new("RGB", (2400, 1350), NAVY); canvas.paste(ph, (915, 0))
m = Image.new("L", (2400, 1350), 0); dm = ImageDraw.Draw(m)
for x in range(2400):
    a = 255 if x < 915 else max(0, int(255 * (1 - (x - 915) / 620) ** 1.6)) if x < 1535 else 0
    dm.line([(x, 0), (x, 1350)], fill=a)
canvas = Image.composite(Image.new("RGB", (2400, 1350), NAVY), canvas, m)
save(canvas, "s02_hook_zhoshy.jpg", (2400, 1350))
save(grad(crop(load("File:Aulietau-Akmeshit.jpg"), 16/9, fy=0.5), "bottom", 0.35, 0.72), "s08_market_aulietau.jpg", (2400, 1350))
save(grad(crop(load("File:Ulutay 1.jpg"), 16/9, fy=0.6), "left", 0.92, 0.30), "s12_final_ulytau.jpg", (2400, 1350))
# карточки (1200×700)
for t, n in [("File:Dombauyl.jpg", "card_dombauyl.jpg"), ("File:Ulutay 2.jpg", "card_ulytau_park.jpg"),
             ("File:Terekti-Aulie 1.jpg", "card_terekti.jpg"), ("File:Alasha-Khan Mausoleum-1.jpg", "card_alasha.jpg")]:
    save(crop(load(t), 12/7, fy=0.55), n, (1200, 700))
