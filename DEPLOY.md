# DEPLOY — бот 24/7 на Oracle Cloud Always Free (Ubuntu + systemd)

Бот работает через **long polling**: он сам обращается к Telegram, и входящие порты открывать не нужно.
Хватит самой маленькой бесплатной машины (боту нужно ~100 МБ RAM).

Время: ~30–40 минут, если аккаунт Oracle уже есть.

---

## Шаг 0. Подготовка на своём компьютере

- Архив проекта `ulytau_guide.zip` или репозиторий на GitHub.
- Токен бота от @BotFather и ключ Gemini из https://aistudio.google.com/apikey.
- **Остановите локальную копию бота.** Если одновременно работают две копии с одним токеном, Telegram выдаёт
  ошибку `TelegramConflictError: terminated by other getUpdates request`.

## Шаг 1. Аккаунт Oracle Cloud

1. Зарегистрируйтесь на https://www.oracle.com/cloud/free/. Банковская карта нужна только для проверки.
2. **Home region** выбирается один раз и навсегда; ресурсы Always Free доступны только в нём.
   Выберите ближайший регион.

## Шаг 2. Создать виртуальную машину

1. Консоль Oracle → **Compute → Instances → Create instance**.
2. **Image:** `Canonical Ubuntu 24.04` (в нём Python 3.12 — подходит).
3. **Shape** (обе с пометкой *Always Free-eligible*):
   - `VM.Standard.E2.1.Micro` (AMD, 1 ГБ RAM) — для бота достаточно;
   - или `VM.Standard.A1.Flex` (ARM Ampere), например 1 OCPU и 6 ГБ RAM. Если пишет *Out of capacity*,
     возьмите E2.1.Micro или попробуйте позже.
4. **Networking:** оставьте VCN по умолчанию с публичным IPv4 (нужен для SSH).
5. **SSH keys:** нажмите *Generate a key pair for me* и **скачайте приватный ключ**
   (или вставьте свой публичный ключ).
6. **Create**. Через 1–2 минуты появится *Public IP address*.

## Шаг 3. Подключиться по SSH

На своём компьютере (Linux/macOS; на Windows — PowerShell):

```bash
chmod 600 ~/Downloads/ssh-key.key
```

```bash
ssh -i ~/Downloads/ssh-key.key ubuntu@<PUBLIC_IP>
```

## Шаг 4. Подготовить сервер

```bash
sudo apt update && sudo apt -y upgrade
```

```bash
sudo apt -y install python3-venv python3-pip git unzip
```

Если у машины 1 ГБ RAM (E2.1.Micro), добавьте swap на 1 ГБ — так `pip install` не упрётся в память:

```bash
sudo fallocate -l 1G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
```

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Создайте системного пользователя без права входа — бот будет работать от его имени:

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin ulytau
```

## Шаг 5. Загрузить код

**Вариант А — архив.** На своём компьютере:

```bash
scp -i ~/Downloads/ssh-key.key ulytau_guide.zip ubuntu@<PUBLIC_IP>:~
```

На сервере (архив содержит папку `ulytau_guide/`):

```bash
sudo unzip ~/ulytau_guide.zip -d /opt/
```

**Вариант Б — GitHub:**

```bash
sudo git clone https://github.com/<ваш-аккаунт>/ulytau_guide.git /opt/ulytau_guide
```

## Шаг 6. Установить зависимости

```bash
sudo python3 -m venv /opt/ulytau_guide/.venv
```

```bash
sudo /opt/ulytau_guide/.venv/bin/pip install -r /opt/ulytau_guide/requirements.txt
```

## Шаг 7. Секреты (.env)

```bash
sudo cp /opt/ulytau_guide/.env.example /opt/ulytau_guide/.env
```

```bash
sudo nano /opt/ulytau_guide/.env
```

Впишите `BOT_TOKEN=...` и `GEMINI_API_KEY=...`, затем сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`.

Создайте папку `var/` (там хранится выбранный язык пользователей), отдайте папку проекта пользователю `ulytau`
и закройте `.env` от чтения посторонними:

```bash
sudo mkdir -p /opt/ulytau_guide/var
```

```bash
sudo chown -R ulytau:ulytau /opt/ulytau_guide
```

```bash
sudo chmod 600 /opt/ulytau_guide/.env
```

## Шаг 8. Пробный запуск

```bash
sudo -u ulytau /opt/ulytau_guide/.venv/bin/python /opt/ulytau_guide/bot.py
```

Ожидаемый лог:

```
INFO ulytau_guide: AI-гид: модель gemini-3.5-flash, запасные: gemini-3.5-flash-lite, gemini-3.1-flash-lite
INFO ulytau_guide: Подключено к Telegram как @<имя_бота>
INFO ulytau_guide: Бот запущен. Остановка: Ctrl+C
INFO aiogram.dispatcher: Start polling
```

Напишите боту `/start` в Telegram и проверьте меню. Затем остановите бота: `Ctrl+C`.

## Шаг 9. systemd — работа 24/7

В проекте уже есть готовый юнит `deploy/ulytau-guide.service`. Он перезапускает бота при падении
(`Restart=always`), запускает его после загрузки сервера и ограничивает права процесса.

```bash
sudo cp /opt/ulytau_guide/deploy/ulytau-guide.service /etc/systemd/system/
```

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl enable --now ulytau-guide
```

Проверка:

```bash
systemctl status ulytau-guide
```

Должно быть `Active: active (running)`. Логи в реальном времени:

```bash
journalctl -u ulytau-guide -f
```

Проверьте автозапуск после перезагрузки:

```bash
sudo reboot
```

Через минуту подключитесь снова и выполните `systemctl status ulytau-guide`.

## Шаг 10. Обновление бота

Загрузите новые файлы (архивом или `git pull` в `/opt/ulytau_guide`), затем:

```bash
sudo chown -R ulytau:ulytau /opt/ulytau_guide
```

```bash
sudo systemctl restart ulytau-guide
```

Если менялся `requirements.txt`, перед перезапуском выполните `sudo /opt/ulytau_guide/.venv/bin/pip install -r /opt/ulytau_guide/requirements.txt`.

Тесты можно запустить прямо на сервере:

```bash
sudo /opt/ulytau_guide/.venv/bin/pip install -r /opt/ulytau_guide/requirements-dev.txt
```

```bash
cd /opt/ulytau_guide && sudo -u ulytau .venv/bin/python -m pytest -q -p no:cacheprovider
```

---

## Важно: правило Oracle о «простаивающих» машинах

Oracle может **остановить простаивающую Always Free машину** («reclamation of idle compute instances»).
Простаивающей считается машина, у которой за 7 дней загрузка CPU (95-й перцентиль), сеть и, для A1, память
ниже ~20%. Telegram-бот почти не нагружает сервер, поэтому под правило может попасть.

- До демо 14 ноября это не успеет произойти, если развернуть бота сейчас (нужно 7 дней простоя).
- Для работы дольше: по отзывам пользователей, правило не применяется к аккаунтам, переведённым на
  **Pay As You Go**, а ресурсы Always Free при этом остаются бесплатными. Поставьте бюджет-алерт на 1 $.
  Перед переходом проверьте условия на официальной странице:
  https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm
- Если машину всё же остановили, её можно снова запустить в консоли (Instances → Start). Бот поднимется сам:
  сервис включён через `systemctl enable`.

## Безопасность

- Входящие порты, кроме SSH (22), **не открывайте**: боту они не нужны.
- `.env` доступен только пользователю `ulytau` (`chmod 600`). Не коммитьте `.env` в Git (он в `.gitignore`).
- Если токен куда-то утёк: @BotFather → `/revoke` → новый токен в `.env` → `sudo systemctl restart ulytau-guide`.
  Ключ Gemini перевыпускается в AI Studio.

## Типичные проблемы

| Симптом в `journalctl` | Причина и решение |
|------------------------|-------------------|
| `TelegramConflictError: terminated by other getUpdates request` | Запущена вторая копия бота (например, на ноутбуке). Остановите её. |
| `Telegram отклонил BOT_TOKEN` | Неверный или отозванный токен — исправьте `.env`. |
| `Нет связи с Telegram ... Повтор через N с` | Нет интернета или DNS; бот сам переподключится. Проверьте `curl -I https://api.telegram.org`. |
| `Gemini (...) ошибка: 429 RESOURCE_EXHAUSTED` | Исчерпан лимит бесплатного тарифа (≈5 запросов в минуту на модель). Бот переключится на запасную модель; подождите минуту. |
| `GEMINI_API_KEY не задан` | Впишите ключ в `.env` и перезапустите сервис. |
| `status=226/NAMESPACE` | Нет папки `/opt/ulytau_guide/var` — создайте её (шаг 7). |
| `Permission denied` на файлах | Повторите `sudo chown -R ulytau:ulytau /opt/ulytau_guide`. |
