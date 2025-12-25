import os
import json
import random
import flask
import telebot
import difflib
import unicodedata
from datetime import datetime, timedelta, date
from collections import defaultdict

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = flask.Flask(__name__)

with open("names.json", "r", encoding="utf-8") as f:
    namedays = json.load(f)

with open("namedays.json", "r", encoding="utf-8") as f:
    NAME_MEANINGS = json.load(f)

def _safe_load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

RANDOM_MEANINGS = _safe_load_json("random.json", {})
GIFT_WISHES = _safe_load_json("gift.json", [])

MONTH_KEY_NAMES = {
    "01": "Január", "02": "Február", "03": "Marec", "04": "Apríl",
    "05": "Máj", "06": "Jún", "07": "Júl", "08": "August",
    "09": "September", "10": "Október", "11": "November", "12": "December",
}

MONTH_GENITIVE = {
    "Január": "Januára", "Február": "Februára", "Marec": "Marca",
    "Apríl": "Apríla", "Máj": "Mája", "Jún": "Júna",
    "Júl": "Júla", "August": "Augusta", "September": "Septembra",
    "Október": "Októbra", "November": "Novembra", "December": "Decembra",
}

MONTH_ABBR = {
    "Január": "JAN", "Február": "FEB", "Marec": "MAR", "Apríl": "APR",
    "Máj": "MAJ", "Jún": "JUN", "Júl": "JUL", "August": "AUG",
    "September": "SEP", "Október": "OKT", "November": "NOV", "December": "DEC",
}

WEEKDAYS = ["Po", "Ut", "St", "Št", "Pi", "So", "Ne"]

FALLBACK_TEXT = (
    "Pôvod: Neznámy\n"
    "Význam: Význam tohto mena sa v dostupných prameňoch nenašiel. "
    "Možno je čas zapísať ho do histórie."
)

def split_names(names):
    cleaned = names.replace(" a ", ", ").replace(" - ", ", ").replace(".", "")
    return [n.strip().lower() for n in cleaned.split(",") if n.strip()]

def normalize_name(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    )

def find_similar_name(name, candidates):
    matches = difflib.get_close_matches(name, candidates, n=1, cutoff=0.75)
    return matches[0] if matches else None

def get_single_name_meaning(names_str):
    mena = split_names(names_str)
    if len(mena) != 1:
        return ""
    meno = mena[0]
    data = NAME_MEANINGS.get(meno)
    if data:
        return (
            f"\n\nPôvod: {data['origin']}\n"
            f"Význam: {data['meaning']}"
        )
    return f"\n\n{FALLBACK_TEXT}"

def _format_meaning(name, data):
    if not data:
        return f"{name.capitalize()}\n\n{FALLBACK_TEXT}"
    return (
        f"{name.capitalize()}\n\n"
        f"Pôvod: {data.get('origin')}\n"
        f"Význam: {data.get('meaning')}"
    )

name_to_date = defaultdict(list)
for date_key, names in namedays.items():
    for name in split_names(names):
        name_to_date[name].append(date_key)

normalized_names = {normalize_name(n): n for n in name_to_date.keys()}

def next_nameday_info(name):
    today = date.today()
    dates = name_to_date.get(name)
    if not dates:
        return None, None

    upcoming = []
    for dkey in dates:
        d, m = dkey.split("-")
        mnum = next(k for k, v in MONTH_KEY_NAMES.items() if v == m)
        nd = date(today.year, int(mnum), int(d))
        if nd < today:
            nd = date(today.year + 1, int(mnum), int(d))
        upcoming.append(nd)

    next_day = min(upcoming)
    delta = (next_day - today).days

    if delta == 0:
        countdown = "dnes"
    elif delta == 1:
        countdown = "zajtra"
    else:
        countdown = f"o {delta} dní"

    return next_day, countdown
def help_text():
    return (
        "Meninový bot 🎉\n\n"
        "📅 Meniny\n"
        "/meniny – dnešné meniny\n"
        "/meniny zajtra – zajtrajšie meniny\n"
        "/meniny vcera – včerajšie meniny\n"
        "/meniny tyzden – meniny na 7 dní dopredu\n"
        "/meniny 13-07 – meniny k dátumu\n\n"
        "🔎 Podľa mena\n"
        "/meniny Daniel – meniny\n"
        "/vyznam Daniel – význam mena\n\n"
        "🎲 Doplnky\n"
        "/random – náhodné meno\n"
        "/gift – malé prianie\n\n"
        "ℹ️ Môj účel\n"
        "/meninar"
    )


@bot.message_handler(commands=["start", "help", "pomoc"])
def help_cmd(message):
    bot.send_message(message.chat.id, help_text())

@bot.message_handler(commands=["meninar"])
def about_cmd(message):
    bot.send_message(
        message.chat.id,
        "👋 Ahoj!\n\n"
        "Som meninový bot 🎉\n"
        "Pomáham rýchlo zistiť, kto má meniny, kedy sú tie tvoje "
        "a čo tvoje meno znamená.\n\n"
        "Skús napríklad:\n"
        "• /meniny\n"
        "• /meniny zajtra\n"
        "• /vyznam tvoje_meno\n\n"
        "Alebo len klikni na moje meno a objav, čo všetko viem 😊"
    )


@bot.message_handler(commands=["meniny"])
def handle_meniny(message):
    now = datetime.now()

    if now.month == 12 and now.day == 25:
        bot.send_message(
            message.chat.id,
            "🎄 Veselé Vianoce! Prajeme pokoj, radosť a pohodu."
        )

    if now.month == 1 and now.day == 1:
        bot.send_message(
            message.chat.id,
            "🎆 Šťastný nový rok! Nech je plný zdravia a úspechov."
        )

    parts = message.text.split(maxsplit=1)
    query = parts[1].strip().lower() if len(parts) > 1 else ""

    if query in ["tyzden", "týždeň", "7", "7dni"]:
        dnes = date.today()
        vystup = []
        for i in range(7):
            d = dnes + timedelta(days=i)
            key = f"{d.day:02d}-{MONTH_KEY_NAMES[str(d.month).zfill(2)]}"
            mena = namedays.get(key, "—")
            vystup.append(f"{WEEKDAYS[d.weekday()]} {d.day}.{d.month}. – {mena}")
        bot.send_message(message.chat.id, "\n".join(vystup))
        return

    if not query or query == "dnes":
        d = now
        label = "Dnes"
    elif query == "zajtra":
        d = now + timedelta(days=1)
        label = "Zajtra"
    elif query == "vcera":
        d = now - timedelta(days=1)
        label = "Včera"
    else:
        bot.send_message(message.chat.id, "Neznámy príkaz.")
        return

    key = f"{d.day:02d}-{MONTH_KEY_NAMES[d.strftime('%m')]}"
    mena = namedays.get(key)
    if not mena:
        bot.send_message(message.chat.id, "Tento dátum nemá meniny.")
        return

    vyznam = get_single_name_meaning(mena)
    bot.send_message(message.chat.id, f"{label} ({key}): {mena}{vyznam}")

@bot.message_handler(commands=["vyznam", "meaning"])
def meaning_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return

    meno = parts[1].strip().lower()
    data = NAME_MEANINGS.get(meno)

    if data:
        nd, countdown = next_nameday_info(meno)
        line = ""
        if nd:
            line = f"\n\nMeniny: {nd.day:02d} {MONTH_ABBR[MONTH_KEY_NAMES[f'{nd.month:02d}']]} ({countdown})"
        bot.send_message(
            message.chat.id,
            f"{meno.capitalize()}{line}\n\n"
            f"Pôvod: {data['origin']}\n"
            f"Význam: {data['meaning']}"
        )
    else:
        bot.send_message(message.chat.id, f"{meno.capitalize()}\n\n{FALLBACK_TEXT}")

@bot.message_handler(commands=["random"])
def random_cmd(message):
    if not RANDOM_MEANINGS:
        return
    meno = random.choice(list(RANDOM_MEANINGS.keys()))
    bot.send_message(message.chat.id, _format_meaning(meno, RANDOM_MEANINGS.get(meno)))

@bot.message_handler(commands=["blahozelanie", "prianie", "zelanie"])
def gift_cmd(message):
    if not GIFT_WISHES:
        return
    parts = message.text.split(maxsplit=1)
    meno = parts[1].strip() if len(parts) > 1 else message.from_user.first_name
    text = random.choice(GIFT_WISHES)
    bot.send_message(message.chat.id, text.replace("{meno}", meno))

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("!meniny"))
def group_meniny(message):
    now = datetime.now()
    key = f"{now.day:02d}-{MONTH_KEY_NAMES[now.strftime('%m')]}"
    bot.send_message(message.chat.id, f"Dnes ({key}): {namedays.get(key, '—')}")

@app.route("/" + TOKEN, methods=["POST"])
def telegram_webhook():
    update = telebot.types.Update.de_json(
        flask.request.get_data().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot beží"

if os.environ.get("RENDER"):
    bot.delete_webhook(drop_pending_updates=True)
    bot.set_webhook(url=f"https://meniny-bot.onrender.com/{TOKEN}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
