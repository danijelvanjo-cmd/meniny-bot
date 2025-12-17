import telebot
from datetime import datetime
import os

TOKEN = os.environ['TOKEN']
bot = telebot.TeleBot(TOKEN)

# (full namedays dict and name_to_date from before – unchanged)

@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    help_text = (
        "Simple meniny bot 😊\n\n"
        "/meniny → today's meniny\n"
        "/meniny dnes → same\n"
        "/meniny 17.12 → meniny on that date\n"
        "/meniny Daniel → date for that name\n\n"
        "In groups: !meniny → today's meniny"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['meniny'])
def handle_meniny(message):
    args = message.text.split(maxsplit=1)
    query = args[1].strip() if len(args) > 1 else ""

    if not query or query.lower() in ["dnes", "today", "dneska"]:
        today_key = datetime.now().strftime("%m-%d")
        names = namedays.get(today_key, "No entry today.")
        date_str = datetime.now().strftime("%d.%m.%Y")
        bot.reply_to(message, f"Today ({date_str}): {names}")

    elif any(sep in query for sep in ['.', '-', '/']):
        try:
            cleaned = query.replace('/', '.').replace('-', '.')
            parts = cleaned.split('.')
            day = parts[0].zfill(2)
            month = parts[1].zfill(2)
            key = f"{month}-{day}"
            names = namedays.get(key, "No entry on this date.")
            bot.reply_to(message, f"{query}: {names}")
        except:
            bot.reply_to(message, "Wrong date format – use dd.mm 😅")

    else:
        date = name_to_date.get(query.lower())
        if date:
            d, m = date.split('-')
            full = namedays[date]
            bot.reply_to(message, f"{query.capitalize()} has meniny on {d}.{m}. ({full})")
        else:
            bot.reply_to(message, "Name not found 😔")

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith('!meniny'))
def handle_bang(message):
    query = message.text[7:].strip()  # after !meniny
    if query:
        bot.reply_to(message, "Just type !meniny for today 😊")
        return
    today_key = datetime.now().strftime("%m-%d")
    names = namedays.get(today_key, "No entry today.")
    date_str = datetime.now().strftime("%d.%m.%Y")
    bot.reply_to(message, f"Today ({date_str}): {names}")

bot.polling()