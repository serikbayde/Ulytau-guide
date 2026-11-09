"""Мокапы экрана Telegram: тексты берутся из locales/kk.json и data/places.json."""
import json, html, re, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "pitch/assets/mockups"
kk = json.load(open(ROOT / "locales/kk.json", encoding="utf-8"))
places = json.load(open(ROOT / "data/places.json", encoding="utf-8"))["places"]
P = {p["id"]: p for p in places}
ICON = {"sacred": "🕌", "history": "🏛", "nature": "🏔", "city": "🏙"}

def tg(s):  # Telegram HTML (b/i) → безопасный HTML, переводы строк
    s = s.replace("\n", "<br>")
    return s

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:430px;height:900px;background:transparent;font-family:Inter,'Noto Color Emoji',sans-serif}
.phone{position:absolute;left:10px;top:10px;width:410px;height:880px;border-radius:62px;background:#0b0f16;padding:12px;box-shadow:0 0 0 2px #2b3445 inset}
.screen{position:relative;width:100%;height:100%;border-radius:50px;overflow:hidden;background:#cfe0c3;display:flex;flex-direction:column}
.screen:before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 20% 30%,#dbe9cf 0,transparent 40%),radial-gradient(circle at 80% 70%,#c3d9b4 0,transparent 45%)}
.status{position:relative;height:50px;display:flex;justify-content:space-between;align-items:flex-end;padding:0 34px 6px;font-weight:600;font-size:15px;background:#fff}
.island{position:absolute;left:50%;top:11px;width:120px;height:34px;border-radius:20px;background:#0b0f16;transform:translateX(-50%)}
.head{position:relative;display:flex;align-items:center;gap:10px;padding:8px 14px 10px;background:#fff;border-bottom:1px solid #e3e3e3}
.back{color:#3390ec;font-size:28px;line-height:1}
.ava{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#D9A441,#4FA3D9);display:flex;align-items:center;justify-content:center;font-size:21px}
.nm{font-weight:700;font-size:16px;color:#000}.st{font-size:13px;color:#8a8a8a}
.chat{position:relative;flex:1;padding:10px 10px 6px;display:flex;flex-direction:column;justify-content:flex-end;gap:6px;overflow:hidden}
.msg{max-width:88%;background:#fff;border-radius:16px 16px 16px 4px;padding:8px 11px 6px;font-size:14.2px;line-height:1.36;color:#111;box-shadow:0 1px 1px rgba(0,0,0,.12)}
.msg .t{float:right;font-size:11px;color:#9aa0a6;margin:6px 0 0 8px}
.me{align-self:flex-end;background:#e2fec7;border-radius:16px 16px 4px 16px}
.me .t{color:#5fae54}
.ikb{display:flex;flex-direction:column;gap:4px;max-width:88%;width:88%}
.ikb div{background:rgba(70,95,60,.42);color:#fff;font-weight:600;font-size:13.5px;text-align:center;padding:9px 6px;border-radius:10px}
.input{position:relative;display:flex;align-items:center;gap:8px;background:#fff;padding:8px 12px;border-top:1px solid #e3e3e3}
.input .f{flex:1;height:36px;border-radius:18px;background:#f1f1f1;color:#999;font-size:14px;display:flex;align-items:center;padding-left:14px}
.kb{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:6px;padding:8px 8px 30px;background:#f3f3f3}
.kb div{background:#fff;border-radius:9px;text-align:center;padding:12px 4px;font-size:14.5px;font-weight:500;box-shadow:0 1px 0 #c9c9c9}
.home{position:relative;height:26px;background:#fff}
.home:after{content:"";position:absolute;left:50%;bottom:8px;width:134px;height:5px;border-radius:3px;background:#111;transform:translateX(-50%)}
.cut{max-height:430px;overflow:hidden;-webkit-mask-image:linear-gradient(#000 85%,transparent)}
"""

def page(chat, bottom):
    return f"""<html><head><meta charset=utf-8><style>{CSS}</style></head><body><div class=phone><div class=screen>
<div class=status><span>9:41</span><span>5G · 100%</span></div><div class=island></div>
<div class=head><span class=back>‹</span><div class=ava>🏔</div><div><div class=nm>Ұлытау гид</div><div class=st>бот</div></div></div>
<div class=chat>{chat}</div>{bottom}</div></div></body></html>"""

KB = "<div class=kb>" + "".join(f"<div>{html.escape(kk[k])}</div>" for k in ["menu_places","menu_routes","menu_ask","menu_language"]) + "</div>"
INPUT = "<div class=input><span style='font-size:22px'>📎</span><div class=f>Хабарлама</div><span style='font-size:22px'>🎤</span></div><div class=home></div>"

# 1. Приветствие + меню
s1 = page(f"<div class='msg me'>/start<span class=t>9:40 ✓✓</span></div>"
          f"<div class=msg>{tg(kk['choose_language'])}<span class=t>9:40</span></div>"
          f"<div class=ikb><div>🇰🇿 Қазақша</div><div>🇷🇺 Русский</div><div>🇬🇧 English</div></div>"
          f"<div class=msg>{tg(kk['welcome'])}<span class=t>9:41</span></div>", KB)

# 2. Карточка места (Жошы хан) — тот же текст, что formatting.place_card
p = P["zhoshy_khan"]
card = (f"<b>{p['name']['kk']}</b><br>{kk['cat_'+p['category']]}<br><br>{html.escape(p['description']['kk'])}<br><br>"
        f"{kk['place_how_to_get']}<br>{html.escape(p['how_to_get']['kk'])}<br><br>"
        + kk['place_distance'].format(distance=p['distance_text']['kk']) + "<br><br>"
        f"{kk['place_tips']}<br>{html.escape(p['tips']['kk'])}")
s2 = page(f"<div class='msg me'>{kk['menu_places']}<span class=t>9:41 ✓✓</span></div>"
          f"<div class='msg cut'>{card}</div>"
          f"<div class=ikb><div>{kk['btn_open_map']}</div><div>{kk['btn_sources'].format(count=len(p['sources']))}</div><div>{kk['btn_back_places']}</div></div>",
          INPUT)

# 3. AI-гид. Ответ составлен ТОЛЬКО из places.json (zhoshy_khan, kk) — иллюстрация;
#    перед финалом замените реальным скриншотом.
q = "Жошы хан кесенесінде шынымен Жошы жерленген бе?"
ans = ("Дәстүр бойынша иә — кесене Шыңғыс ханның үлкен ұлы Жошының жерленген орны деп саналады.<br><br>"
       "1946 жылы Әлкей Марғұлан экспедициясы кесенені ашып, оң қолы жоқ адамның сүйегін тапқан.<br><br>"
       "Бірақ 2022 жылғы радиокөміртекті зерттеу мұнда дәл Жошының жерленгеніне күмән келтіреді.<br><br>"
       f"<i>{html.escape(kk['ai_footer'])}</i>")
s3 = page(f"<div class='msg me'>{kk['menu_ask']}<span class=t>9:42 ✓✓</span></div>"
          f"<div class=msg>{tg(kk['ask_intro'])}<span class=t>9:42</span></div>"
          f"<div class='msg me'>{q}<span class=t>9:42 ✓✓</span></div>"
          f"<div class=msg>{ans}<span class=t>9:42</span></div>", INPUT)

for name, s in [("menu", s1), ("place", s2), ("ai", s3)]:
    (OUT / f"{name}.html").write_text(s, encoding="utf-8")
subprocess.run(["node", "-e", f"""
const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();
const p=await b.newPage({{viewport:{{width:430,height:900}},deviceScaleFactor:3}});
for(const n of ['menu','place','ai']){{await p.goto('file://{OUT}/'+n+'.html');await p.waitForTimeout(300);
await p.screenshot({{path:'{OUT}/'+n+'.png',omitBackground:true}});}}await b.close();}})();"""], check=True)
for n in ["menu","place","ai"]: (OUT / f"{n}.html").unlink()
print("ok")
