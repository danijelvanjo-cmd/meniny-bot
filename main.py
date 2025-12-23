import os
import json
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

FALLBACK_TEXT = (
    "Pôvod: neznámy\n"
    "Význam: Význam tohto mena sa v kronikách nenašiel. "
    "Možno je čas zapísať ho do histórie práve ty 🙂"
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
        return f"\nPôvod: {data['origin']}\nVýznam: {data['meaning']}"
    return f"\n{FALLBACK_TEXT}"

name_to_date = defaultdict(list)

for date_key, names in namedays.items():
    for name in split_names(names):
        name_to_date[name].append(date_key)

normalized_names = {normalize_name(name): name for name in name_to_date.keys()}

def help_text():
    return (
        "Meninový bot\n\n"
        "📅 MENINY\n"
        "/meniny – dnešné meniny\n"
        "/meniny zajtra – zajtrajšie meniny\n"
        "/meniny vcera – včerajšie meniny\n"
        "/meniny 17-01 – meniny k dátumu\n"
        "/meniny tyzden – meniny na 7 dní dopredu\n\n"
        "🔎 PODĽA MENA\n"
        "/meniny Daniel – meniny\n"
        "/meaning Daniel – význam mena\n\n"
        "👥 SKUPINY\n"
        "!meniny – dnešné meniny\n\n"
        "ℹ️ Tip:\n"
        "Nezáleží na diakritike ani drobných preklepoch."
    )

@bot.message_handler(commands=["start", "help", "pomoc"])
def help_cmd(message):
    bot.send_message(message.chat.id, help_text())

@bot.message_handler(commands=["meniny"])
def handle_meniny(message):
    parts = message.text.split(maxsplit=1)
    query = parts[1].strip().lower() if len(parts) > 1 else ""

    if query in ["tyzden", "týždeň", "7", "7dni"]:
        dnes = date.today()
        vystup = []
        for i in range(7):
            d = dnes + timedelta(days=i)
            key = f"{d.day:02d}-{MONTH_KEY_NAMES[str(d.month).zfill(2)]}"
            mena = namedays.get(key, "Nikto")
            wd = WEEKDAYS[d.weekday()]
            vystup.append(f"{wd} {d.day}.{d.month}. – {mena}")
        bot.send_message(message.chat.id, "\n".join(vystup))
        return

    now = datetime.now()
    label = "Dnes"

    if not query or query == "dnes":
        d = now
    elif query == "zajtra":
        d = now + timedelta(days=1)
        label = "Zajtra"
    elif query == "vcera":
        d = now - timedelta(days=1)
        label = "Včera"
    elif any(sep in query for sep in [".", "-", "/"]):
        try:
            cleaned = query.replace("/", ".").replace("-", ".")
            den, mesiac = cleaned.split(".")[:2]
            key = f"{den.zfill(2)}-{MONTH_KEY_NAMES[mesiac.zfill(2)]}"
            mena = namedays.get(key, "Nikto")
            vyznam = get_single_name_meaning(mena)
            bot.send_message(message.chat.id, f"{key}: {mena}{vyznam}")
            return
        except:
            bot.send_message(message.chat.id, "Zlý formát dátumu 😅")
            return
    else:
        norm = normalize_name(query)
        real_name = name_to_date.get(query)
        if not real_name:
            podobne = find_similar_name(norm, normalized_names.keys())
            if podobne:
                query = normalized_names[podobne]
                real_name = name_to_date.get(query)
        if not real_name:
            bot.send_message(message.chat.id, "Toto meno sa v kalendári nenašlo 😕")
            return
        vystup = []
        for dkey in sorted(real_name):
            den, mesiac = dkey.split("-")
            vystup.append(f"{den}-{MONTH_GENITIVE.get(mesiac, mesiac)}")
        data = NAME_MEANINGS.get(query)
        if data:
            vyznam = f"\nPôvod: {data['origin']}\nVýznam: {data['meaning']}"
        else:
            vyznam = f"\n{FALLBACK_TEXT}"
        bot.send_message(
            message.chat.id,
            f"{query.capitalize()} má meniny: {', '.join(vystup)}{vyznam}"
        )
        return

    key = f"{d.day:02d}-{MONTH_KEY_NAMES[d.strftime('%m')]}"
    mena = namedays.get(key, "Nikto")
    vyznam = get_single_name_meaning(mena)
    bot.send_message(message.chat.id, f"{label} ({key}): {mena}{vyznam}")

@bot.message_handler(commands=["meaning"])
def meaning_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Použitie: /meaning Meno")
        return
    meno = parts[1].strip().lower()
    norm = normalize_name(meno)
    data = NAME_MEANINGS.get(meno)
    if not data:
        podobne = find_similar_name(norm, [normalize_name(n) for n in NAME_MEANINGS.keys()])
        if podobne:
            meno = next(k for k in NAME_MEANINGS.keys() if normalize_name(k) == podobne)
            data = NAME_MEANINGS.get(meno)
    if data:
        bot.send_message(
            message.chat.id,
            f"{meno.capitalize()}\nPôvod: {data['origin']}\nVýznam: {data['meaning']}"
        )
    else:
        bot.send_message(message.chat.id, f"{meno.capitalize()}\n{FALLBACK_TEXT}")

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("!meniny"))
def group_meniny(message):
    now = datetime.now()
    key = f"{now.day:02d}-{MONTH_KEY_NAMES[now.strftime('%m')]}"
    mena = namedays.get(key, "Nikto")
    bot.send_message(message.chat.id, f"Dnes ({key}): {mena}")

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
