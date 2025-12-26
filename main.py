import os
import json
import random
import flask
import telebot
import difflib
import unicodedata
import re
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


RANDOM_MSGS = _safe_load_json("random.json", [])
GIFT_MSGS = _safe_load_json("gift.json", [])

FALLBACK_TEXT = (
    "Tento význam zatiaľ nemám uložený.\n"
    "Skús iné meno alebo napíš /help."
)

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
    "Január": "jan", "Február": "feb", "Marec": "mar", "Apríl": "apr",
    "Máj": "máj", "Jún": "jún", "Júl": "júl", "August": "aug",
    "September": "sep", "Október": "okt", "November": "nov", "December": "dec",
}

WEEKDAYS = ["Po", "Ut", "St", "Št", "Pi", "So", "Ne"]


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


# Build index: name -> list of date keys
name_to_date = defaultdict(list)
for date_key, names in namedays.items():
    for name in split_names(names):
        name_to_date[name].append(date_key)

# normalized -> canonical (for diacritics + typos)
normalized_names = {normalize_name(n): n for n in name_to_date.keys()}


def resolve_name(text):
    """
    Returns canonical keyname used in name_to_date (lowercase, no diacritics),
    or None if not found. Accepts diacritics and small typos.
    """
    q = (text or "").strip()
    if not q:
        return None

    q_low = q.lower()
    if q_low in name_to_date:
        return q_low

    q_norm = normalize_name(q_low)
    keyname = normalized_names.get(q_norm)
    if keyname:
        return keyname

    close = find_similar_name(q_norm, normalized_names.keys())
    return normalized_names.get(close) if close else None


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
        "🎉 Meninový bot 🎉\n\n"
        "📅 Meniny\n"
        "/meniny – dnešné meniny\n"
        "/meniny zajtra – zajtrajšie meniny\n"
        "/meniny vcera – včerajšie meniny\n"
        "/meniny tyzden – meniny na 7 dní dopredu\n"
        "/meniny 13-07 – meniny k dátumu\n\n"
        "🔎 Podľa mena\n"
        "/meniny Daniel – kedy má Daniel meniny\n"
        "/vyznam Daniel – význam mena\n\n"
        "🎲 Doplnky\n"
        "/random – náhodné meno\n"
        "/blahozelanie Igor – prianie pre Igora\n\n"
        "ℹ️ Info\n"
        "/meninar – o botovi\n"
        "/help | /pomoc | /info – tento zoznam"
    )


def _random_pick_from_random_json():
    """
    Your random.json is currently a dict (name -> info). If it is a list, also supported.
    Returns a text message.
    """
    if not RANDOM_MSGS:
        return "Nič tu nemám."

    # If it's a list of strings
    if isinstance(RANDOM_MSGS, list):
        return random.choice(RANDOM_MSGS)

    # If it's a dict (your case): pick a random name key
    if isinstance(RANDOM_MSGS, dict):
        raw_name = random.choice(list(RANDOM_MSGS.keys()))
        canon = resolve_name(raw_name)  # try map to calendar spelling
        display = raw_name.strip().capitalize()

        extra = ""
        if canon:
            nd, countdown = next_nameday_info(canon)
            if nd:
                month_name = MONTH_KEY_NAMES[f"{nd.month:02d}"]
                extra = f"\nMeniny: {nd.day:02d}. {MONTH_GENITIVE[month_name]} ({countdown})"

            meaning_data = NAME_MEANINGS.get(canon)
            if meaning_data:
                extra += f"\nPôvod: {meaning_data.get('origin')}\nVýznam: {meaning_data.get('meaning')}"

        return f"🎲 Náhodné meno: {display}{extra}"

    # fallback
    return "Nič tu nemám."


def _random_gift_template():
    if not GIFT_MSGS:
        return None
    if isinstance(GIFT_MSGS, list):
        return random.choice(GIFT_MSGS)
    return None


# ===== Commands =====

@bot.message_handler(commands=["start", "help", "pomoc", "info"])
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
        "Alebo len napíš meno (napr. Igor) a skúsim odpovedať 😊"
    )


@bot.message_handler(commands=["random"])
def random_cmd(message):
    bot.send_message(message.chat.id, _random_pick_from_random_json())


@bot.message_handler(commands=["blahozelanie", "gift"])
def blahozelanie_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Použitie: /blahozelanie Igor")
        return

    raw_name = parts[1].strip()
    if not raw_name:
        bot.send_message(message.chat.id, "Použitie: /blahozelanie Igor")
        return

    template = _random_gift_template()
    if not template:
        bot.send_message(message.chat.id, "Nemám uložené priania 😕")
        return

    # Keep user's diacritics for addressing, just make it look nice
    display_name = raw_name[:1].upper() + raw_name[1:]

    # Support both {meno} placeholder and plain templates
    wish = template.replace("{meno}", display_name)

    bot.send_message(
        message.chat.id,
        f"🎁 Blahoželanie pre meno: {display_name}\n\n{wish}"
    )


@bot.message_handler(commands=["meniny"])
def handle_meniny(message):
    now = datetime.now()
    parts = message.text.split(maxsplit=1)
    query_raw = parts[1].strip() if len(parts) > 1 else ""
    query = query_raw.lower()

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

    m = re.match(r"^\s*(\d{1,2})\s*[.\-/]\s*(\d{1,2})\s*$", query_raw)
    if m:
        dd = int(m.group(1))
        mm = int(m.group(2))
        if 1 <= mm <= 12 and 1 <= dd <= 31:
            key = f"{dd:02d}-{MONTH_KEY_NAMES[str(mm).zfill(2)]}"
            mena = namedays.get(key)
            if not mena:
                bot.send_message(message.chat.id, "Tento dátum nemá meniny.")
                return
            vyznam = get_single_name_meaning(mena)
            bot.send_message(
                message.chat.id,
                f"{dd:02d}. {MONTH_GENITIVE[MONTH_KEY_NAMES[str(mm).zfill(2)]]} ({key}): {mena}{vyznam}"
            )
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
        keyname = resolve_name(query_raw)
        if not keyname:
            bot.send_message(message.chat.id, "Neznámy príkaz alebo meno.")
            return

        nd, countdown = next_nameday_info(keyname)
        if not nd:
            bot.send_message(message.chat.id, "Neznámy príkaz alebo meno.")
            return

        key = f"{nd.day:02d}-{MONTH_KEY_NAMES[str(nd.month).zfill(2)]}"
        mena = namedays.get(key, "—")
        vyznam = get_single_name_meaning(keyname)

        bot.send_message(
            message.chat.id,
            f"{keyname.capitalize()}\n\n"
            f"Meniny: {nd.day:02d}. {MONTH_GENITIVE[MONTH_KEY_NAMES[str(nd.month).zfill(2)]]} ({countdown})\n"
            f"Dátum: {key}\n"
            f"V ten deň má meniny: {mena}{vyznam}"
        )
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
        bot.send_message(message.chat.id, "Použitie: /vyznam Daniel")
        return

    raw = parts[1].strip()
    keyname = resolve_name(raw)
    if not keyname:
        bot.send_message(message.chat.id, f"{raw.capitalize()}\n\n{FALLBACK_TEXT}")
        return

    data = NAME_MEANINGS.get(keyname)
    if data:
        nd, countdown = next_nameday_info(keyname)
        line = ""
        if nd:
            line = f"\n\nMeniny: {nd.day:02d} {MONTH_ABBR[MONTH_KEY_NAMES[f'{nd.month:02d}']]} ({countdown})"
        bot.send_message(
            message.chat.id,
            f"{keyname.capitalize()}{line}\n\n"
            f"Pôvod: {data['origin']}\n"
            f"Význam: {data['meaning']}"
        )
    else:
        bot.send_message(message.chat.id, f"{keyname.capitalize()}\n\n{FALLBACK_TEXT}")


# ===== Auto-reply: user types just a name =====
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def name_autoreply(message):
    text = message.text.strip()

    # ignore super short / super long
    if len(text) < 2 or len(text) > 30:
        return

    keyname = resolve_name(text)
    if not keyname:
        return  # silent ignore (so "ahoj" doesn't spam)

    nd, countdown = next_nameday_info(keyname)
    if not nd:
        return

    month_name = MONTH_KEY_NAMES[f"{nd.month:02d}"]
    date_str = f"{nd.day:02d}. {MONTH_GENITIVE[month_name]}"

    meaning_data = NAME_MEANINGS.get(keyname)
    meaning_block = ""
    if meaning_data:
        meaning_block = (
            f"\n\nPôvod: {meaning_data.get('origin')}\n"
            f"Význam: {meaning_data.get('meaning')}"
        )
    else:
        meaning_block = f"\n\n{FALLBACK_TEXT}"

    bot.send_message(
        message.chat.id,
        f"📅 {keyname.capitalize()}\n"
        f"Meniny: {date_str} ({countdown})"
        f"{meaning_block}"
    )


# ===== WEBHOOK + SETTINGS (DO NOT TOUCH) =====
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(
        flask.request.get_data().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def home():
    return "OK"


if __name__ == "__main__":
    webhook_url = os.environ.get("WEBHOOK_URL", "").strip()
    if not webhook_url.endswith("/"):
        webhook_url += "/"

    bot.remove_webhook()
    bot.set_webhook(url=webhook_url + TOKEN)

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
