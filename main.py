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

# =====================
# Boot / setup
# =====================

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise RuntimeError("Missing env var TOKEN")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = flask.Flask(__name__)

# --- Load JSON files (your repo files) ---
# names.json = calendar date -> names
# namedays.json = meanings dict (name -> {origin, meaning})
with open("names.json", "r", encoding="utf-8") as f:
    NAMEDAYS_BY_KEY = json.load(f)

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
    "Vaše meno sa tu nenachádza. Choďte a vytvorte preň vlastnú históriu.\n"
    "Skús iné meno alebo napíš /help."
)

WEEKDAYS = ["Po", "Ut", "St", "Št", "Pi", "So", "Ne"]

# =====================
# Month handling
# =====================
# Your names.json uses keys like "01-Januar" (ASCII months). Example: :contentReference[oaicite:2]{index=2}
# We'll use that format for lookups, but still display Slovak month genitive in messages.

MONTH_NUM_TO_KEYNAME = {
    1: "Januar",
    2: "Februar",
    3: "Marec",
    4: "April",
    5: "Maj",
    6: "Jun",
    7: "Jul",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "December",
}

# Allow parsing multiple spellings (so we never crash)
MONTH_KEYNAME_TO_NUM = {
    "januar": 1, "január": 1,
    "februar": 2, "február": 2,
    "marec": 3,
    "april": 4, "apríl": 4,
    "maj": 5, "máj": 5,
    "jun": 6, "jún": 6,
    "jul": 7, "júl": 7,
    "august": 8,
    "september": 9,
    "oktober": 10, "október": 10,
    "november": 11,
    "december": 12,
}

# Slovak display (genitive)
MONTH_GENITIVE_SK = {
    1: "Januára",
    2: "Februára",
    3: "Marca",
    4: "Apríla",
    5: "Mája",
    6: "Júna",
    7: "Júla",
    8: "Augusta",
    9: "Septembra",
    10: "Októbra",
    11: "Novembra",
    12: "Decembra",
}

MONTH_ABBR_SK = {
    1: "jan",
    2: "feb",
    3: "mar",
    4: "apr",
    5: "máj",
    6: "jún",
    7: "júl",
    8: "aug",
    9: "sep",
    10: "okt",
    11: "nov",
    12: "dec",
}


def make_calendar_key(day: int, month: int) -> str:
    """Key format used in names.json: 'DD-MonthKeyName'."""
    return f"{day:02d}-{MONTH_NUM_TO_KEYNAME[month]}"


def parse_calendar_key(key: str):
    """
    Parse keys from names.json safely.
    Expected: 'DD-Januar' etc, but we also accept variants so it never crashes.
    Returns (day:int, month:int) or None.
    """
    if not isinstance(key, str) or "-" not in key:
        return None
    parts = key.split("-", 1)
    if len(parts) != 2:
        return None
    day_s, month_s = parts[0].strip(), parts[1].strip()
    try:
        day = int(day_s)
    except Exception:
        return None
    month = MONTH_KEYNAME_TO_NUM.get(month_s.lower())
    if not month:
        return None
    # validate actual date existence (ignore invalid combos)
    try:
        _ = date(2024, month, day)  # leap-safe-ish year, just for validation
    except ValueError:
        return None
    return day, month


# =====================
# Name normalization / matching
# =====================

def split_names(names: str):
    if not isinstance(names, str):
        return []
    cleaned = (
        names.replace(" a ", ", ")
        .replace(" - ", ", ")
        .replace(".", "")
    )
    return [n.strip().lower() for n in cleaned.split(",") if n.strip()]


def normalize_name(text: str):
    # strip diacritics, lowercase
    return "".join(
        c for c in unicodedata.normalize("NFD", (text or "").lower())
        if unicodedata.category(c) != "Mn"
    )


def find_similar_name(name_norm: str, candidates_norm):
    matches = difflib.get_close_matches(name_norm, candidates_norm, n=1, cutoff=0.75)
    return matches[0] if matches else None


# Build index: name -> list of (month, day)
name_to_dates = defaultdict(list)

for key, names_str in NAMEDAYS_BY_KEY.items():
    parsed = parse_calendar_key(key)
    if not parsed:
        continue
    day, month = parsed
    for nm in split_names(names_str):
        name_to_dates[nm].append((month, day))

# normalized -> canonical key (for diacritics + small typos)
normalized_to_canonical = {normalize_name(n): n for n in name_to_dates.keys()}


def resolve_name(user_text: str):
    """
    Return canonical lowercase name key from name_to_dates, or None.
    Accepts diacritics and small typos.
    """
    q = (user_text or "").strip()
    if not q:
        return None

    q_low = q.lower()
    if q_low in name_to_dates:
        return q_low

    q_norm = normalize_name(q_low)
    canon = normalized_to_canonical.get(q_norm)
    if canon:
        return canon

    close = find_similar_name(q_norm, normalized_to_canonical.keys())
    return normalized_to_canonical.get(close) if close else None


# =====================
# Meaning helpers
# =====================

def get_single_name_meaning(names_str: str):
    """
    If exactly one name is listed on that date, try to append meaning for it.
    """
    mena = split_names(names_str)
    if len(mena) != 1:
        return ""
    meno = mena[0]
    data = NAME_MEANINGS.get(meno)
    if data:
        return f"\n\nPôvod: {data.get('origin')}\nVýznam: {data.get('meaning')}"
    return f"\n\n{FALLBACK_TEXT}"


def format_meaning_block(name_key: str):
    data = NAME_MEANINGS.get(name_key)
    if not data:
        return f"\n\n{FALLBACK_TEXT}"
    return f"\n\nPôvod: {data.get('origin')}\nVýznam: {data.get('meaning')}"


# =====================
# Next nameday calc
# =====================

def next_nameday_info(name_key: str):
    """
    Returns (next_date: date, countdown_text: str) or (None, None)
    """
    today = date.today()
    dates = name_to_dates.get(name_key) or []
    if not dates:
        return None, None

    upcoming = []
    for month, day in dates:
        try:
            nd = date(today.year, month, day)
        except ValueError:
            continue
        if nd < today:
            nd = date(today.year + 1, month, day)
        upcoming.append(nd)

    if not upcoming:
        return None, None

    next_day = min(upcoming)
    delta = (next_day - today).days

    if delta == 0:
        countdown = "dnes"
    elif delta == 1:
        countdown = "zajtra"
    else:
        countdown = f"o {delta} dní"

    return next_day, countdown


# =====================
# Commands text
# =====================

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
        "/blahozelanie Pavel – prianie pre meno: Pavel\n\n"
        "ℹ️ Info\n"
        "/meninar – o botovi\n"
        "/help | /pomoc | /info – tento zoznam"
    )


# =====================
# Random / gift
# =====================

def random_pick():
    if not RANDOM_MSGS:
        return "Nič tu nemám."

    # list of strings
    if isinstance(RANDOM_MSGS, list):
        return random.choice(RANDOM_MSGS) if RANDOM_MSGS else "Nič tu nemám."

    # dict (name -> something)
    if isinstance(RANDOM_MSGS, dict) and RANDOM_MSGS:
        raw_name = random.choice(list(RANDOM_MSGS.keys()))
        display = raw_name.strip().capitalize()
        canon = resolve_name(raw_name)

        extra = ""
        if canon:
            nd, countdown = next_nameday_info(canon)
            if nd:
                extra += f"\nMeniny: {nd.day:02d}. {MONTH_GENITIVE_SK[nd.month]} ({countdown})"
            extra += format_meaning_block(canon)

        return f"🎲 Náhodné meno: {display}{extra}"

    return "Nič tu nemám."


def random_gift_template():
    if not GIFT_MSGS:
        return None
    if isinstance(GIFT_MSGS, list) and GIFT_MSGS:
        return random.choice(GIFT_MSGS)
    return None


# =====================
# Handlers
# =====================

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
    bot.send_message(message.chat.id, random_pick())


@bot.message_handler(commands=["blahozelanie", "gift"])
def blahozelanie_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.send_message(message.chat.id, "Použitie: /blahozelanie Igor")
        return

    raw_name = parts[1].strip()
    display_name = raw_name[:1].upper() + raw_name[1:]

    template = random_gift_template()
    if not template:
        bot.send_message(message.chat.id, "Nemám uložené priania 😕")
        return

    # Support {meno} placeholder
    wish = template.replace("{meno}", display_name)

    # REQUIRED FORMAT from you:
    bot.send_message(
        message.chat.id,
        f"🎁 Blahoželanie pre meno: {display_name}\n\n{wish}"
    )


@bot.message_handler(commands=["meniny"])
def meniny_cmd(message):
    now = datetime.now()
    parts = message.text.split(maxsplit=1)
    query_raw = parts[1].strip() if len(parts) > 1 else ""
    query = query_raw.lower().strip()

    # ---- tyzden ----
    if query in ["tyzden", "týždeň", "7", "7dni"]:
        dnes = date.today()
        vystup = []
        for i in range(7):
            d = dnes + timedelta(days=i)
            key = make_calendar_key(d.day, d.month)
            mena = NAMEDAYS_BY_KEY.get(key, "—")
            vystup.append(f"{WEEKDAYS[d.weekday()]} {d.day:02d}.{d.month:02d}. – {mena}")
        bot.send_message(message.chat.id, "\n".join(vystup))
        return

    # ---- specific date "13-07" / "13/07" / "13.07" ----
    m = re.match(r"^\s*(\d{1,2})\s*[.\-/]\s*(\d{1,2})\s*$", query_raw)
    if m:
        dd = int(m.group(1))
        mm = int(m.group(2))
        if 1 <= mm <= 12 and 1 <= dd <= 31:
            try:
                _ = date(2024, mm, dd)
            except ValueError:
                bot.send_message(message.chat.id, "Neplatný dátum.")
                return

            key = make_calendar_key(dd, mm)
            mena = NAMEDAYS_BY_KEY.get(key)
            if not mena:
                bot.send_message(message.chat.id, "Tento dátum nemá meniny.")
                return

            vyznam = get_single_name_meaning(mena)
            bot.send_message(
                message.chat.id,
                f"{dd:02d}. {MONTH_GENITIVE_SK[mm]} ({key}): {mena}{vyznam}"
            )
            return

    # ---- today / tomorrow / yesterday ----
    if not query or query == "dnes":
        d = now.date()
        label = "Dnes"
    elif query == "zajtra":
        d = (now + timedelta(days=1)).date()
        label = "Zajtra"
    elif query == "vcera":
        d = (now - timedelta(days=1)).date()
        label = "Včera"
    else:
        # ---- treat as name ----
        keyname = resolve_name(query_raw)
        if not keyname:
            bot.send_message(message.chat.id, "Neznámy príkaz alebo meno.")
            return

        nd, countdown = next_nameday_info(keyname)
        if not nd:
            bot.send_message(message.chat.id, "Neznámy príkaz alebo meno.")
            return

        key = make_calendar_key(nd.day, nd.month)
        mena = NAMEDAYS_BY_KEY.get(key, "-")

        bot.send_message(
            message.chat.id,
            f"{keyname.capitalize()}\n\n"
            f"Meniny: {nd.day:02d}. {MONTH_GENITIVE_SK[nd.month]} ({countdown})\n"
            f"Dátum: {key}\n"
            f"V ten deň má meniny: {mena}"
            f"{format_meaning_block(keyname)}"
        )
        return

    key = make_calendar_key(d.day, d.month)
    mena = NAMEDAYS_BY_KEY.get(key)
    if not mena:
        bot.send_message(message.chat.id, "Tento dátum nemá meniny.")
        return

    vyznam = get_single_name_meaning(mena)
    bot.send_message(message.chat.id, f"{label} ({key}): {mena}{vyznam}")


@bot.message_handler(commands=["vyznam", "meaning"])
def vyznam_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.send_message(message.chat.id, "Použitie: /vyznam Daniel")
        return

    raw = parts[1].strip()
    keyname = resolve_name(raw)
    if not keyname:
        bot.send_message(message.chat.id, f"{raw.capitalize()}\n\n{FALLBACK_TEXT}")
        return

    data = NAME_MEANINGS.get(keyname)
    if not data:
        bot.send_message(message.chat.id, f"{keyname.capitalize()}\n\n{FALLBACK_TEXT}")
        return

    nd, countdown = next_nameday_info(keyname)
    line = ""
    if nd:
        line = f"\n\nMeniny: {nd.day:02d} {MONTH_ABBR_SK[nd.month]} ({countdown})"

    bot.send_message(
        message.chat.id,
        f"{keyname.capitalize()}{line}\n\n"
        f"Pôvod: {data.get('origin')}\n"
        f"Význam: {data.get('meaning')}"
    )


# =====================
# Auto-reply: one-word name
# =====================

@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def name_autoreply(message):
    text = message.text.strip()

    # Only one word (so we don't answer "ahoj ako sa mas")
    if not text or len(text.split()) != 1:
        return

    if len(text) < 2 or len(text) > 30:
        return

    keyname = resolve_name(text)
    if not keyname:
        return  # silent ignore for random words

    nd, countdown = next_nameday_info(keyname)
    if not nd:
        return

    date_str = f"{nd.day:02d}. {MONTH_GENITIVE_SK[nd.month]}"

    bot.send_message(
        message.chat.id,
        f"📅 {keyname.capitalize()}\n\n"
        f"Meniny: {date_str} ({countdown})"
        f"{format_meaning_block(keyname)}"
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
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get("WEBHOOK_URL") + TOKEN)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
