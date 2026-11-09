"""IMAGE_CREDITS.md и SPEAKER_SCRIPT_KZ.md из метаданных и заметок."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
meta = {m["title"]: m for m in json.load(open(ROOT / "pitch/build/photo_meta.json", encoding="utf-8"))}
use = [("s01_title_ulytau.jpg", "File:Горы Улытау 2.jpg", "1-слайд (титул). Төменгі жақтағы күн-уақыт белгісі кесіліп тасталды"),
       ("s02_hook_zhoshy.jpg", "File:Жошы хан кесенесі.jpg", "2-слайд (хук)"),
       ("s08_market_aulietau.jpg", "File:Aulietau-Akmeshit.jpg", "8-слайд (нарық), қатты күңгірттелген"),
       ("s12_final_ulytau.jpg", "File:Ulutay 1.jpg", "12-слайд (финал)"),
       ("card_dombauyl.jpg", "File:Dombauyl.jpg", "5-слайд, «Орындар» карточкасы"),
       ("card_ulytau_park.jpg", "File:Ulutay 2.jpg", "5-слайд, «Маршруттар» карточкасы"),
       ("card_terekti.jpg", "File:Terekti-Aulie 1.jpg", "5-слайд, «AI-гид» карточкасы"),
       ("card_alasha.jpg", "File:Alasha-Khan Mausoleum-1.jpg", "5-слайд, «3 тіл» карточкасы")]
L = ["# IMAGE_CREDITS — суреттер мен иконкалар", "",
     "Барлық фото Wikimedia Commons-тан алынды, лицензиясы әр файлдың бетінде тексерілді (9 қараша 2026).",
     "Барлығы **CC BY-SA 4.0**: авторын көрсету және өзгертілген нұсқаны сол лицензиямен тарату керек.",
     "Біз фотоларды кестеге сай кестік, күңгірттендірдік (градиент) — бұл өзгерту, сондықтан 12-слайдта",
     "«Суреттер:» жолында авторлар мен лицензия көрсетілген.", "",
     "| Файл (pitch/assets/photos) | Түпнұсқа | Автор | Лицензия | URL | Қай жерде |", "|---|---|---|---|---|---|"]
for f, t, where in use:
    m = meta[t]
    L.append(f"| `{f}` | {t[5:]} | {m['artist']} | [{m['lic']}]({m['licurl']}) | {m['page']} | {where} |")
L += ["", "## Иконкалар", "",
      "`pitch/assets/icons/*.svg|png` — [Lucide](https://lucide.dev) v0.460.0, лицензиясы **ISC** (еркін, атрибуция міндетті емес,",
      "бірақ 12-слайдта көрсетілген). SVG-ден PNG-ге біздің түстерімізбен `pitch/build/icons.js` арқылы айналдырылды.", "",
      "## Өзіміз жасаған графика", "",
      "- `pitch/assets/mockups/*.png` — Telegram экранының макеті (`pitch/build/mockups.py`). Мәтіндер `locales/kk.json`",
      "  және `data/places.json`-нан алынған. **AI-гидтің жауабы (`ai.png`) — `places.json`-дағы Жошы хан сипаттамасынан",
      "  құрастырылған мысал**, нақты скриншот емес. Финалға дейін боттың нақты жауабының скриншотымен ауыстырған дұрыс.",
      "- `pitch/assets/ornament_*.png` — стильдендірілген «қошқар мүйіз» өрнегі, өзіміз сызғанбыз (`ornament.js`).",
      "- `pitch/assets/qr_*.png` — `qrcode` кітапханасымен жасалған, `https://t.me/yelulytaubot` ашады (OpenCV-мен тексерілді).",
      "", "## Пайдаланылмаған, бірақ жүктелген", "",
      "Кеңгір су қоймасының еркін фотосы (File:Кенгирское водохранилище Вид сверху.png, Almaz Tleuliyev, CC BY-SA 4.0)",
      "табылды, бірақ Wikimedia сұраныс шектеуіне байланысты жүктелмеді — презентацияға қосылмады."]
(ROOT / "pitch/IMAGE_CREDITS.md").write_text("\n".join(L) + "\n", encoding="utf-8")

notes = json.load(open(ROOT / "pitch/build/notes_kk.json", encoding="utf-8"))
names = {1: "Титул", 2: "Хук", 3: "Мәселе", 4: "Шешім", 5: "Қалай жұмыс істейді", 6: "Тікелей демо",
         7: "Техникалық құрылым", 8: "Нарық", 9: "Табыс моделі", 10: "Бәсекелестер", 11: "Жоспарлар", 12: "Рахмет! / Біз сұраймыз"}
S = ["# SPEAKER_SCRIPT_KZ — «Ұлытау гид», Pizza Pitch, 14 қараша", "",
     "Жалпы уақыт: **≈5 мин 50 с** (демо — 1,5 мин). Спикер 1 — мәселе, нарық, ақша; Спикер 2 — өнім, демо, техника.",
     "Мәтін слайдтардың «Заметки докладчика» бөлімінде де бар. Жаттап алмаңыз — өз сөзіңізбен айтыңыз.", "",
     "| Слайд | Уақыт | Кім |", "|---|---|---|"]
for i in range(1, 13):
    first = notes[str(i)].split("\n")[0].replace("⏱ ", "")
    t, who = first.split(" · ", 1)
    S.append(f"| {i}. {names[i]} | {t} | {who} |")
S.append("")
for i in range(1, 13):
    S += [f"## {i}. {names[i]}", "", notes[str(i)].replace("\n", "  \n"), ""]
S += ["---", "", "**Демо алдында:** DEMO_SCRIPT.md-дегі «30 минут бұрын» тізімін орындаңыз (жауаптарды жылыту, ботты",
      "қайта қоспау, интернет жоқ болса — видео). Бот: @yelulytaubot."]
(ROOT / "pitch/SPEAKER_SCRIPT_KZ.md").write_text("\n".join(S) + "\n", encoding="utf-8")
print("ok")
