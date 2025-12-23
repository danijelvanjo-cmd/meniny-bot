import os
import json
import flask
import telebot
from datetime import datetime, timedelta, date
from collections import defaultdict

# =========================
# CONFIG
# =========================

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = flask.Flask(__name__)

# =========================
# LOAD DATA FILES
# =========================

with open("names.json", "r", encoding="utf-8") as f:
    namedays = json.load(f)

with open("namedays.json", "r", encoding="utf-8") as f:
    NAME_MEANINGS = json.load(f)

# =========================
# CONSTANTS
# =========================

MONTH_KEY_NAMES = {
    "01": "Januar", "02": "Februar", "03": "Marec", "04": "April",
    "05": "Maj", "06": "Jun", "07": "Jul", "08": "August",
    "09": "September", "10": "Oktober", "11": "November", "12": "December",
}

MONTH_GENITIVE = {
    "Januar": "Januara", "Februar": "Februara", "Marec": "Marca",
    "April": "Aprila", "Maj": "Maja", "Jun": "Juna",
    "Jul": "Jula", "August": "Avgusta", "September": "Septembra",
    "Oktober": "Oktobra", "November": "Novembra", "December": "Decembra",
}

WEEKDAYS = ["Po", "Ut", "St", "Št", "Pi", "So", "Ne"]

FALLBACK_MEANING = (
    "Origin: unknown\n"
    "Meaning: The origin of this name is unknown. "
    "Maybe it’s time for you to make history with it."
)

# =========================
# HELPERS
# =========================

def split_names(names: str):
    cleaned = (
        names.replace(" a ", ", ")
        .replace(" - ", ", ")
        .replace(".", "")
    )
    return [n.strip().lower() for n in cleaned.split(",") if n.strip()]

def get_first_name_meaning(names_str: str):
    names = split_names(names_str)
    if not names:
        return ""

    first = names[0]
    data = NAME_MEANINGS.get(first)

    if data:
        return f"\nOrigin: {data['origin']}\nMeaning: {data['meaning']}"
    return f"\n{FALLBACK_MEANING}"

# =========================
# BUILD NAME → DATE INDEX
# =========================

name_to_date = defaultdict(list)

for date_key, names in namedays.items():
    for name in split_names(names):
        name_to_date[name].append(date_key)

# =========================
# COMMANDS
# =========================

@bot.message_handler(commands=["start", "help"])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "📅 Name Days Bot\n\n"
        "/meniny → today\n"
        "/meniny zajtra | vcera\n"
        "/meniny DD-MM\n"
        "/meniny tyzden → next 7 days\n"
        "/meniny Name → dates + meaning\n\n"
        "/meaning Name → meaning only\n\n"
        "!meniny → group shortcut"
    )

# =========================
# MENINY
# =========================

@bot.message_handler(commands=["meniny"])
def handle_meniny(message):
    parts = message.text.split(maxsplit=1)
    query = parts[1].strip().lower() if len(parts) > 1 else ""

    # ---- 7 DAYS AHEAD ----
    if query in ["tyzden", "týždeň", "7", "7dni"]:
        today = date.today()
        lines = []

        for i in range(7):
            d = today + timedelta(days=i)
            key = f"{d.day:02d}-{MONTH_KEY_NAMES[str(d.month).zfill(2)]}"
            names = namedays.get(key, "Nobody")
            wd = WEEKDAYS[d.weekday()]
            lines.append(f"{wd} {d.day}.{d.month}. – {names}")

        bot.send_message(message.chat.id, "\n".join(lines))
        return

    now = datetime.now()
    label = "Today"

    # ---- TODAY / TOMORROW / YESTERDAY ----
    if not query or query in ["dnes", "today"]:
        d = now
    elif query == "zajtra":
        d = now + timedelta(days=1)
        label = "Tomorrow"
    elif query == "vcera":
        d = now - timedelta(days=1)
        label = "Yesterday"

    # ---- DATE LOOKUP ----
    elif any(sep in query for sep in [".", "-", "/"]):
        try:
            cleaned = query.replace("/", ".").replace("-", ".")
            day, month = cleaned.split(".")[:2]
            key = f"{day.zfill(2)}-{MONTH_KEY_NAMES[month.zfill(2)]}"
            names = namedays.get(key, "Nobody")
            meaning = get_first_name_meaning(names)
            bot.send_message(message.chat.id, f"{key}: {names}{meaning}")
            return
        except:
            bot.send_message(message.chat.id, "Invalid date format 😅")
            return

    # ---- NAME LOOKUP ----
    else:
        dates = name_to_date.get(query)
        if not dates:
            bot.send_message(message.chat.id, "Name not found 😕")
            return

        out = []
        for dkey in sorted(dates):
            day, month = dkey.split("-")
            out.append(f"{day}-{MONTH_GENITIVE.get(month, month)}")

        data = NAME_MEANINGS.get(query)
        if data:
            meaning = f"\nOrigin: {data['origin']}\nMeaning: {data['meaning']}"
        else:
            meaning = f"\n{FALLBACK_MEANING}"

        bot.send_message(
            message.chat.id,
            f"{query.capitalize()} name days: {', '.join(out)}{meaning}"
        )
        return

    key = f"{d.day:02d}-{MONTH_KEY_NAMES[d.strftime('%m')]}"
    names = namedays.get(key, "Nobody")
    meaning = get_first_name_meaning(names)
    bot.send_message(
        message.chat.id,
        f"{label} ({key}): {names}{meaning}"
    )

# =========================
# MEANING ONLY
# =========================

@bot.message_handler(commands=["meaning"])
def meaning_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Usage: /meaning Name")
        return

    name = parts[1].strip().lower()
    data = NAME_MEANINGS.get(name)

    if data:
        bot.send_message(
            message.chat.id,
            f"{name.capitalize()}\n"
            f"Origin: {data['origin']}\n"
            f"Meaning: {data['meaning']}"
        )
    else:
        bot.send_message(
            message.chat.id,
            f"{name.capitalize()}\n{FALLBACK_MEANING}"
        )

# =========================
# GROUP SHORTCUT
# =========================

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("!meniny"))
def group_meniny(message):
    now = datetime.now()
    key = f"{now.day:02d}-{MONTH_KEY_NAMES[now.strftime('%m')]}"
    names = namedays.get(key, "Nobody")
    meaning = get_first_name_meaning(names)
    bot.send_message(
        message.chat.id,
        f"Today ({key}): {names}{meaning}"
    )

# =========================
# WEBHOOK (UNCHANGED)
# =========================

@app.route("/" + TOKEN, methods=["POST"])
def telegram_webhook():
    update = telebot.types.Update.de_json(
        flask.request.get_data().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is alive"

if os.environ.get("RENDER"):
    bot.delete_webhook(drop_pending_updates=True)
    bot.set_webhook(url=f"https://meniny-bot.onrender.com/{TOKEN}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
