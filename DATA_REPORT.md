# DATA_REPORT — данные бота «Ұлытау гид»

Дата сбора: **9 ноября 2026**. Файлы: `data/places.json` (14 мест), `data/routes.json` (3 маршрута).

## 1. Как собирались данные (важно прочитать)

- **Источник фактов — веб-поиск.** Факты взяты из выдержек поисковой выдачи, у каждой есть ссылка на страницу.
  В среде, где собирались данные, открыть сами страницы было нельзя: сетевая политика блокировала
  kazakhstan.travel, ulytaureserve.kz, wikipedia.org и другие сайты. Поэтому **перед демо стоит
  открыть ссылки и сверить ключевые цифры** (чек-лист в разделе 4).
- **Координаты** сверялись минимум по двум независимым источникам. Если второго источника нет,
  у места стоит `"verified": false`, а в `verification_note` написано, что проверить.
- **Расстояния.** Если расстояние взято из источника, в карточке написано «по данным источников».
  Иначе это расстояние **по прямой, рассчитанное по координатам** от центра Жезказгана
  (47.7833, 67.7000). По дороге выйдет больше.
- **Легенды** везде помечены как легенды: семь святых на Аулиетау, Заратуштра, погребение Едиге и т. п.
- **Казахский текст** написан грамотно, со всеми буквами (ә, ғ, қ, ң, ө, ұ, ү, һ, і). Всё же
  рекомендую, чтобы носитель языка вычитал тексты перед сценой: это 5–10 минут работы.
- **Советы (tips)** бывают двух видов: взятые из источников (см. раздел 5) и общие рекомендации
  по безопасности и этикету. Общие советы не выдаются за факты.

## 2. Сводная таблица

| # | id | Место (ru) | Категория | Координаты (lat, lon) | verified | От Жезказгана |
|---|----|-----------|-----------|----------------------|----------|---------------|
| 1 | `zhoshy_khan` | Мавзолей Жошы хана | сакральное | 48.1549, 67.8210 | ✅ | 45–55 км (источники) |
| 2 | `dombauyl` | Мавзолей Домбауыл | сакральное | 48.1933, 67.8447 | ❌ | 50–55 км (источники) |
| 3 | `alasha_khan` | Мавзолей Алаша хана | сакральное | 48.3675, 67.8431 | ✅ | ≈66 км по прямой |
| 4 | `aulietau` | Гора Аулиетау (Акмешит) | природа | 48.6439, 66.9461 | ✅ | 130 км до с. Улытау + 5 км |
| 5 | `terekti_aulie` | Петроглифы Теректы-Аулие | история | 48.2125, 68.6139 | ✅ | 80–90 км (источники) |
| 6 | `bolgan_ana` | Мавзолей Болган-ана | сакральное | 47.4667, 68.0083 | ❌ | ≈50 км (музей-заповедник) |
| 7 | `ulytau_village` | Село Улытау и музей-заповедник | история | 48.6547, 67.0078 | ✅ | 130 км (музей-заповедник) |
| 8 | `unity_monument` | Монумент единства народа Казахстана | история | 48.5822, 67.0894 | ❌ | ≈120 км по трассе |
| 9 | `edige_tau` | Гора Едиге | природа | 48.5769, 66.8163 | ❌ | ≈110 км по прямой |
| 10 | `ayakkamyr` | Городище и мавзолей Аяккамыр | история | 48.1147, 66.9939 | ❌ | ≈64 км по прямой |
| 11 | `karsakpay` | Карсакпай и дом-музей Сатпаева | история | 47.8333, 66.7500 | ✅ | ≈71 км по прямой |
| 12 | `zhezkazgan_museum` | Жезказганский историко-археологический музей | город | 47.7833, 67.7000 (центр города!) | ❌ | в городе |
| 13 | `kengir_reservoir` | Кенгирское водохранилище | природа | 47.7956, 67.7328 | ❌ | ≈3 км |
| 14 | `ulytau_national_park` | Нацпарк «Ұлытау» | природа | 48.6360, 66.9030 | ❌ | ≈130 км |

Итого: **6 мест проверены (✅), 8 — с пометкой «проверить» (❌).**

## 3. Места: источники и статус проверки

### 1. Мавзолей Жошы хана — ✅
- Координаты по двум источникам: wildticketasia (48.1553, 67.8175) и qazaqstan3d.kz (48.1545, 67.8244).
  Расхождение около 0,5 км, в данных — среднее.
- Расстояние в источниках разное: 45 км (inform.kz, archaeology.kz, oq.gov.kz), 50 км (welcome.kz, wildticketasia),
  55 км (altynorda.kazakhstan.travel).
- Остальные факты: вскрытие экспедицией Маргулана в 1946 году (newtimes.kz); радиоуглеродное исследование 2022 года
  (Radiocarbon / Cambridge); строительство новой дороги с 2024 года (welcome.kz, 24.kz).
- Источники:
  - https://wildticketasia.com/1316-jochi-khan-mausoleum.html
  - https://qazaqstan3d.kz/en/place/view?id=72
  - https://archaeology.kz/en/heritages/120-zhoshy-han-kesenesi
  - https://www.inform.kz/ru/chto-izvestno-o-syne-chingizhana-dzhuchi-i-ego-mavzolee-v-kazahstane_a3559481
  - https://oq.gov.kz/en/abai/zhoshy-khan-kesenesi
  - https://welcome.kz/en/info-cities/ulytau-region/jochi-mausoleum
  - https://newtimes.kz/politika/211623-mongoly-proveli-obriad-u-mogily-zhoshy-khana-v-kazakhstane
  - https://www.cambridge.org/core/product/3B95527C5CB2DA08DC98D6136F0E5EFC/core-reader

### 2. Мавзолей Домбауыл — ❌
- Координаты есть только у wildticketasia (N48°11'36" E67°50'41"). Они совпадают с описанием «5–6 км к северу
  от мавзолея Жошы хана» (eurasia.travel, welcome.kz): по расчёту получается 4,6 км. Второго источника
  с координатами нет. В листе UNESCO (6913) указано N48°31' E67°17', но это, видимо, точка всей номинации.
- Датировка спорная: VIII–IX вв. (туристические сайты) против 1000–1300 гг. (госреестр).
- Источники:
  - https://wildticketasia.com/1311-dombaul-mausoleum.html
  - https://eurasia.travel/kazakhstan/karaganda/dombaul-mausoleum/
  - https://welcome.kz/en/info-cities/ulytau-region/dombauyl
  - https://archaeology.kz/en/heritages/119-dombauyl-dini-guryptyq-qurylysy
  - https://kazakhstan.travel/en/tourist-spot/77/mausoleums-of-jochi-khan-alasha-khan-and-dombauyl
  - https://whc.unesco.org/en/tentativelists/6913/

### 3. Мавзолей Алаша хана — ✅
- Координаты совпадают в двух источниках: wildticketasia (N48°22'03" E67°50'35") и aroundus (48.36747, 67.84300).
- Датировка расходится: X–XI вв. (e-history), XI–XII вв., XIII в. (tourstokazakhstan). В описании перечислены все варианты.
- Источники:
  - https://wildticketasia.com/1309-alasha-khan-mausoleum.html
  - https://aroundus.com/p/11829486-alasha-khan-mausoleum
  - https://kazakhstan.travel/en/attractions/389
  - https://archaeology.kz/en/heritages/108-alasha-han-kesenesi
  - https://e-history.kz/en/map/view/93
  - https://tourstokazakhstan.com/en/sights/karaganda-region-ulytau-district/mausoleum-of-alash-khan.html
  - https://www.ancient-history-sites.com/sites/alasha-khan-mausoleum/

### 4. Гора Аулиетау (Акмешит) — ✅
- Координаты: wildticketasia (N48°38'38" E66°56'47") и Wikipedia, вершина Акмешит (48°38′39″N 66°56′46″E), совпадают.
- Высота в источниках разная: 1131 м (Wikipedia, wildticketasia), 1133 м (kazakhstan.travel), 1135 м (ulytaureserve.kz).
- Источники:
  - https://wildticketasia.com/854-aulie-mount-aulietau.html
  - https://en.wikipedia.org/wiki/Ulytau_(range)
  - https://kazakhstan.travel/en/where-to-go/region/19/ulytau-region
  - https://kazakhstan.travel/en/publications/161/ulytau-region
  - https://ulytaureserve.kz/en/311-route-akmechet-auliyetau.html
  - https://ulytaureserve.kz/en/12-tourist-routes.html

### 5. Петроглифы Теректы-Аулие — ✅
- Координаты из трёх источников, расхождение не больше ~100 м. Расстояние в источниках 80–90 км.
- Источники:
  - https://wildticketasia.com/859-terekty-aulie-karaganda-region-kazakhstan.html
  - https://pages.vassar.edu/central-asia-sites/?p=256
  - https://wildticketasia.com/1338-necropolis-terekty-aulie-monument.html
  - https://archaeology.kz/en/heritages/137-terekti-aulie-petroglifteri
  - https://e-history.kz/en/seo-materials/show/30486
  - https://bulletin-ecology.kaznu.kz/index.php/1-eco/en/article/view/196

### 6. Мавзолей Болган-ана — ❌
- Координаты только из wildticketasia (47°28'00" N 68°00'30" E). У соседнего мазара Кулан-ана на том же сайте
  координаты почти такие же, поэтому они, возможно, приблизительные. Косвенно согласуются с описанием
  «10 км выше устья Каракенгира» (устье по Wikipedia: 47°22′42″N 67°59′29″E).
- Датировка расходится: XI–XII вв. на туристическом сайте, XIV–XV вв. в музее-заповеднике и 1401–1500 гг. в реестре.
- Урочище Каражар, легенды и находки (останки знатной женщины, золотая чаша, серьги) взяты из выдержек
  kazpravda / stud.kz. stud.kz — студенческая презентация, слабый источник, **проверить по kazpravda**.
- Источники:
  - https://ulytaureserve.kz/en/9-historical-and-cultural-monuments-of-the-ulytau-reserve-museum.html
  - https://archaeology.kz/en/heritages/116-bolgan-ana-kesenesi
  - https://wildticketasia.com/1339-bolgan-ana-mausoleum.html
  - https://kazpravda.kz/n/bolgan-ana-legenda-i-simvol/
  - https://stud.kz/prezentatsiya/id/28500
  - https://ulytaureserve.kz/en/museum-news-eng/573-archaeological-research-in-the-bolgan-ana-mausoleum
  - https://en.wikipedia.org/wiki/Karakengir

### 7. Село Улытау и музей-заповедник — ✅
- Координаты: Wikipedia (48°39′17″N 67°00′28″E) и Who's On First (≈48.655, 67.006).
- Расстояние: 130 км по трассе по данным музея-заповедника. Другие сайты пишут 120 и 150 км.
- Источники:
  - https://en.wikipedia.org/wiki/Ulytau_(village)
  - https://spelunker.whosonfirst.org/id/1326717465/geojson
  - https://ulytaureserve.kz/en/12-tourist-routes.html
  - https://e-history.kz/en/historical-education/show/12958
  - https://en.tengrinews.kz/tv/features/ulytau/127
  - https://kazpravda.kz/n/dobro-pozhalovat-v-ulytau/

### 8. Монумент единства народа Казахстана — ❌
- Координаты (N48°34'56" E67°05'22") и высота (20/22 м) есть только в одном источнике (wildticketasia).
  Внутренне координаты согласуются с «≈10 км от села Улытау»: по расчёту ровно 10,0 км.
- Год 1992 указан на двух страницах kazakhstan.travel. То, что это «географический центр Казахстана», —
  общепринятое мнение, а не геодезическая точка.
- Источники:
  - https://wildticketasia.com/1315-monument-of-unity-and-cohesion-of-the-people-of-kazakhstan.html
  - https://kazakhstan.travel/en/publications/161/ulytau-region
  - https://kazakhstan.travel/en/where-to-go/region/19/ulytau-region
  - https://www.guide.kz/en/road01_11.shtml

### 9. Гора Едиге — ❌
- Координаты (N48°34'36.95" E66°48'58.56") и высота 1063 м есть только в одном источнике (wildticketasia).
- Расстояние от с. Улытау: 35 км по данным музея-заповедника и gov.kz, 17 км по данным wildticketasia.
  Расчёт по координатам даёт 16,5 км по прямой. **Проверить по топокарте.**
- Источники:
  - https://wildticketasia.com/853-mount-edyge-karaganda-region-kazakhstan.html
  - https://ulytaureserve.kz/en/9-historical-and-cultural-monuments-of-the-ulytau-reserve-museum.html
  - https://www.gov.kz/memleket/entities/qazalem/activities/27973?lang=en
  - https://www.pressreader.com/kazakhstan/tengri/20160501/281552290098975

### 10. Городище и мавзолей Аяккамыр — ❌
- Координаты (N48°06'53" E66°59'38") есть только в одном источнике (wildticketasia).
- Расстояние от с. Жезды: 7 км до городища (wildticketasia), 9 км до мавзолея (archaeology.kz).
- Источники:
  - https://wildticketasia.com/1333-ayakkamyr-settlement-ancient-city.html
  - https://archaeology.kz/en/heritages/110-ayaqqamyr-kesenesi
  - https://kazpravda.kz/n/dva-ayakkamyra/

### 11. Карсакпай и дом-музей К. Сатпаева — ✅
- Координаты: Wikipedia (47°50′N 66°45′E) и NGA GeoNames (47°50′12″N 66°43′35″E). Расхождение ≈1,8 км,
  для посёлка это допустимо.
- Первая медь — октябрь 1928 г. (bizmedia.kz: пуск печи 16.10.1928, первая плавка 19.10.1928; kazakhmys.kz).
- Начало работы Сатпаева в Карсакпае: 1927 г. (aroundus); семья жила там с 1928 по июнь 1941 г. (e-history).
- Дорожное расстояние от Жезказгана в источниках **не найдено**.
- Источники:
  - https://en.wikipedia.org/wiki/Karsakpay
  - https://geonames.nga.mil/geon-ags/rest/services/RESEARCH/GIS_OUTPUT/MapServer/0/2162106/htmlPopup?f=html
  - https://aroundus.com/p/8376556-karsakpay
  - https://www.kazakhmys.kz/en/news/90-years-since-copper-in-karsakpay-was-first-mined
  - https://bizmedia.kz/2026-10-19-karsakpajskij-medeplavilnyj-zavod-98-let-istorii-truda-i-tradiczij
  - https://e-history.kz/en/news/show/7191
  - https://e-history.kz/en/calendar/show/27729
  - https://24.kz/ru/news/culture/647609-kak-vyglyadit-dom-muzej-kanysha-satpaeva

### 12. Жезказганский историко-археологический музей — ❌
- **Координат музея нет:** в данных стоит центр города. Кнопка «Открыть на карте» ведёт в центр Жезказгана.
  Нужно поставить точку по адресу.
- Адрес (ул. Алашахана, 22, бывш. Некрасова) и телефон +7 (7102) 73-77-53 взяты из одного источника (wildticketasia).
- Часы работы **не найдены**.
- Дата открытия 10.05.1978 и переименование в 1997 г. (artessere, weproject); новые экспозиции с ИИ (kazpravda);
  сундуки конца XIX в. (24.kz).
- Источники:
  - https://wildticketasia.com/1192-jezkazgan-historical-and-archaeological-museum.html
  - https://artessere.com/zhezkazgan-zhezkazgan-historical-and-archaeological-museum
  - https://weproject.media/articles/detail/kuda-shodit-esli-vi-vpervie-v-zhezkazgane/
  - https://kazpravda.kz/n/preobrazhenie/
  - https://24.kz/ru/news/social/699706-vystavku-starinnykh-sundukov-podgotovili-v-zhezkazganskom-muzee
  - https://en.wikipedia.org/wiki/Jezkazgan

### 13. Кенгирское водохранилище — ❌
- Координаты (47.79556, 67.73278) только из одного источника (aroundus). Это точка у города, а само
  водохранилище тянется примерно на 33 км.
- Год 1952 подтверждают несколько источников. По одной версии, строительство начали в 1940 году,
  прервали войной и возобновили в 1946-м.
- Размеры (33 км × 1,6 км, 37 км², 0,319 км³) нашлись в одной выдержке. Объём 319 млн м³ подтверждает второй источник.
- Купальный сезон «с мая по август» — со слов работницы прибрежной гостиницы, которые приводит СМИ.
- Источники:
  - https://informburo.kz/stati/69-let-zezkazganu-prosloe-i-nastoyashhee-odnoi-iz-bogateisix-mednyx-provincii-mira
  - https://bizmedia.kz/2024-04-10-kengirskoe-vodohranilishhe-vozle-zhezkazgana-vernut-kazahstanu
  - https://tengrinews.kz/kazakhstan_news/kengirskoe-vodohranilische-vernut-v-sobstvennost-gosudarstva-549251/
  - https://kazpravda.kz/n/kengirskoe-vodohranilishche-vozvrashchaetsya-v-gossobstvennost/
  - https://24.kz/ru/news/ekologiya/708944-taza-kazakstan-v-zhezkazgane-proshla-aktsiya-chistye-vodojomy
  - https://aroundus.com/p/8376570-qenggir-bogeni
  - https://en.wikipedia.org/wiki/Karakengir

### 14. Нацпарк «Ұлытау» — ❌
- Координаты (48.636, 66.903) — условная точка парка из одного источника (internationalparks.org; там же указан
  год создания 2023, что противоречит постановлению 2021 года).
- Постановление № 867 от 07.12.2021, в силе с 01.01.2022, 14-й нацпарк страны (inform.kz, gov.kz, Astana Times).
- Площадь: 58 900 га по Astana Times, 58 912 га по UNDP. Заказник занимает 19 300 га.
- Источники:
  - https://astanatimes.com/2021/12/kazakhstan-creates-new-national-park-in-karaganda-region-to-step-up-ecosystem-conservation-efforts/
  - https://www.inform.kz/en/kazakhstan-establishes-new-national-park_a3871875
  - https://www.gov.kz/memleket/entities/karaganda-tabigat/press/news/details/303880?lang=ru
  - https://www.undp.org/kazakhstan/stories/women-ulytau-are-shaping-future-their-region
  - https://www.internationalparks.org/kazakhstan/Ulytau
  - https://www.traveldojo.com/ulytau-national-park

## 4. Чек-лист ручной проверки (по приоритету)

1. [ ] **Музей Жезказгана:** поставить точные координаты по адресу ул. Алашахана, 22, позвонить и узнать часы работы.
   Сейчас карта открывает центр города.
2. [ ] **Мавзолей Домбауыл:** проверить точку на Google Maps или 2ГИС (ожидается ≈4–6 км к северу от мавзолея Жошы хана).
3. [ ] **Мавзолей Болган-ана:** проверить точку (ожидается ≈10 км выше слияния Каракенгира и Сарысу) и находки по статье kazpravda.
4. [ ] **Гора Едиге:** уточнить расстояние от с. Улытау (17 или 35 км).
5. [ ] **Монумент единства:** проверить точку на трассе Жезды — Улытау.
6. [ ] **Аяккамыр**, **Кенгирское водохранилище**, **нацпарк**: проверить точку на карте.
7. [ ] **Дороги:** состояние дороги к мавзолеям Жошы хана, Домбауыл и Алаша хана (асфальт строится с 2024 года).
   Дорожное расстояние Жезказган — Карсакпай.
8. [ ] Попросить носителя вычитать казахские тексты (`places.json`, `routes.json`, `locales/kk.json`).

Если место проверено, поставьте в `data/places.json` `"verified": true` и обновите `verification_note`.
Бот сам перестанет показывать пометку «данные уточняются».

## 5. Маршруты (`data/routes.json`)

| Маршрут | Длительность | Места |
|--------|-------------|-------|
| Мавзолеи долины Каракенгир | 1 день | Жошы хан → Домбауыл → Алаша хан → музей → водохранилище |
| Улытау — сердце страны | 2 дня | Аяккамыр → монумент Единства → с. Улытау (ночлег) → Аулиетау / нацпарк → гора Едиге |
| Медный край и древние петроглифы | выходные (сб–вс) | сб: музей → Карсакпай → водохранилище; вс: Теректы-Аулие (опц. Болган-ана) |

- Время в пути — **оценки**. Расстояние берётся из источников или по прямой ×1,3. Средняя скорость:
  ≈60 км/ч по трассе и ≈35–40 км/ч по степным участкам.
- Расстояния, которых в источниках нет и которые оценены: Домбауыл → Алаша хан (25 км),
  Жезказган → Карсакпай (≈95 км), крюк к Аяккамыру (≈85 км от Жезказгана), с. Улытау → гора Едиге.
- Из источников: Жезказган — Улытау 130 км; подъём на Аулиетау ≈3 ч; Домбауыл в 5–6 км от Жошы хана;
  Теректы-Аулие в 80–90 км.

## 6. Советы: что из источников, а что — общие рекомендации

**Из источников:**
- лучший сезон — весна и осень, в мае и сентябре ≈+5…+20 °C (traveldojo);
- нанять местного гида; уважать пастбища (traveldojo);
- портал vizit-ulytau.kz с информацией о гостиницах и транспорте (kazpravda);
- подъём на Аулиетау ≈3 ч, набор ≈500 м (kazakhstan.travel);
- купальный сезон на водохранилище с мая по август (со слов местной жительницы в СМИ);
- до мавзолея Жошы хана можно доехать на машине или с турами, к нему ведёт дорога с указателями (welcome.kz).

**Общие рекомендации (не факты):** взять воду и головной убор; одеваться скромно и говорить тихо на святых местах;
женщинам покрыть голову в мавзолее; не трогать петроглифы и кладку; заправиться в Жезказгане;
брать тёплую одежду в горы; фотографировать при утреннем или вечернем свете.

## 7. Что рассматривалось, но не вошло

- **Хан Ордасы** (место избрания ханов, ≈17 км от Улытау, у с. Амангельды). Координаты не найдены.
- **Городище Баскамыр.** Координат нет, описания противоречат друг другу.
- **Мемориал Кенгирского восстания 1954 г.** Слишком мало данных о самом мемориале.
- **«Дом-музей Сатпаева в Жезказгане».** Не подтвердился: дом-музей находится в Карсакпае (место № 11).
