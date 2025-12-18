import os
import flask
import telebot
from datetime import datetime, timedelta, date
from collections import defaultdict

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = flask.Flask(__name__)

namedays = {
    "01-Januar": "Novy rok, Jezis",
    "02-Januar": "Abel, Set",
    "03-Januar": "Daniel",
    "04-Januar": "Eugen",
    "05-Januar": "Simeon, Andrea",
    "06-Januar": "Zj. Kr. Pana, Gaspar, Melichar, Baltazar",
    "07-Januar": "Bohuslava",
    "08-Januar": "Pravdomil",
    "09-Januar": "Pravolub, Alexej",
    "10-Januar": "Dalimir",
    "11-Januar": "Malvina, Majda",
    "12-Januar": "Rastislav",
    "13-Januar": "Cistko",
    "14-Januar": "Stastko",
    "15-Januar": "Dobroslav",
    "16-Januar": "Vladimir",
    "17-Januar": "Anton, Natasa",
    "18-Januar": "Bohdana, Teodora",
    "19-Januar": "Sara, Drahomira",
    "20-Januar": "Dalibor",
    "21-Januar": "Vincent",
    "22-Januar": "Zora, Alexandra",
    "23-Januar": "Milos",
    "24-Januar": "Ctiboh, Timotej",
    "25-Januar": "Pavel",
    "26-Januar": "Svatoboj, Tamara",
    "27-Januar": "Jan Zlatousty",
    "28-Januar": "Karol",
    "29-Januar": "Pribina",
    "30-Januar": "Ema, Amadea",
    "31-Januar": "Emil",

    "01-Februar": "Tatiana, Tea",
    "02-Februar": "Maria - Hromnice",
    "03-Februar": "Blazej",
    "04-Februar": "Veronika, Veronka",
    "05-Februar": "Svetlusa, Alosa",
    "06-Februar": "Dorota",
    "07-Februar": "Daria, Dajana",
    "08-Februar": "Prokop",
    "09-Februar": "Zdenko",
    "10-Februar": "Gorazd",
    "11-Februar": "Libusa",
    "12-Februar": "Zoroslav",
    "13-Februar": "Horislav",
    "14-Februar": "Velimir, Valentin",
    "15-Februar": "Den statnosti",
    "16-Februar": "Juliana",
    "17-Februar": "Miloslava",
    "18-Februar": "Jaromir",
    "19-Februar": "Zuzana",
    "20-Februar": "Vsemil, Livia",
    "21-Februar": "Eleonora, Lena, Lenka",
    "22-Februar": "Veleslava",
    "23-Februar": "Lazar, Leonora",
    "24-Februar": "Matej",
    "25-Februar": "Viktor",
    "26-Februar": "Alexander, Sasa",
    "27-Februar": "Drahotina, Drahusa",
    "28-Februar": "Zlatica, Zlatka",
    "29-Februar": "Roman",

    "01-Marec": "Albin, Belo",
    "02-Marec": "Amalia, Mia",
    "03-Marec": "Bohumil",
    "04-Marec": "Jadran, Adrian",
    "05-Marec": "Fridrich",
    "06-Marec": "Radoslav",
    "07-Marec": "Tomas",
    "08-Marec": "Medzinarodny den zien",
    "09-Marec": "Raduz",
    "10-Marec": "Branislav",
    "11-Marec": "Jurina, Dina",
    "12-Marec": "Gregor",
    "13-Marec": "Vlastimil",
    "14-Marec": "Matilda, Maja",
    "15-Marec": "Belomir, Svetlana",
    "16-Marec": "Boleslav",
    "17-Marec": "Lubica",
    "18-Marec": "Ctislav, Hviezdoslav",
    "19-Marec": "Jozef",
    "20-Marec": "Vitazoslav",
    "21-Marec": "Blahoslav",
    "22-Marec": "Vesna, Kazimir",
    "23-Marec": "Darko, Darius",
    "24-Marec": "Gabriel",
    "25-Marec": "Zvest narodenia Krista Pana",
    "26-Marec": "Emanuel, Emanuela",
    "27-Marec": "Alena, Aneta",
    "28-Marec": "Sona, Rastislava",
    "29-Marec": "Miroslav, Sabina",
    "30-Marec": "Vieroslava",
    "31-Marec": "Gabriela",

    "01-April": "Hugo",
    "02-April": "Stastka",
    "03-April": "Bohurad, Richard",
    "04-April": "Bohumila, Izidora",
    "05-April": "Bohuslav",
    "06-April": "Irena",
    "07-April": "Radhost",
    "08-April": "Dagmar, Albert",
    "09-April": "Milena, Mileva",
    "10-April": "Igor",
    "11-April": "Julius, Leona",
    "12-April": "Estera",
    "13-April": "Silorad",
    "14-April": "Hrdos",
    "15-April": "Fedor",
    "16-April": "Danica, Dana",
    "17-April": "Rudolf",
    "18-April": "Valer",
    "19-April": "Ratimir",
    "20-April": "Hvezdon, Marcel",
    "21-April": "Zelislav",
    "22-April": "Vojtech, Svatomir",
    "23-April": "Jelena, Jela",
    "24-April": "Juraj, Duro",
    "25-April": "Marek, Marko",
    "26-April": "Jaroslava",
    "27-April": "Jaroslav",
    "28-April": "Jarmila",
    "29-April": "Dobrotka, Lea, Leo",
    "30-April": "Miroslava",

    "01-Maj": "Sviatok prace, Filip",
    "02-Maj": "Zigmund",
    "03-Maj": "Desana, Denis",
    "04-Maj": "Florian, Alex",
    "05-Maj": "Kvetoslav",
    "06-Maj": "Hermina, Mina",
    "07-Maj": "Stanislav, Monika",
    "08-Maj": "Milutin, Ingrid, Ines",
    "09-Maj": "Den vitazstva",
    "10-Maj": "Viktoria",
    "11-Maj": "Blazena",
    "12-Maj": "Pankrac",
    "13-Maj": "Servac",
    "14-Maj": "Bonifac",
    "15-Maj": "Zofia, Sofia",
    "16-Maj": "Svetozar",
    "17-Maj": "Zobor",
    "18-Maj": "Viola, Vida",
    "19-Maj": "Dezider, Hana",
    "20-Maj": "Borivoj",
    "21-Maj": "Dobromir",
    "22-Maj": "Julia, Petra",
    "23-Maj": "Zelmira",
    "24-Maj": "Danusa, Daniela",
    "25-Maj": "Urban",
    "26-Maj": "Dusan",
    "27-Maj": "Miliduch, Iveta",
    "28-Maj": "Viliam",
    "29-Maj": "Vilma, Amanda",
    "30-Maj": "Ferdinand",
    "31-Maj": "Blahoslava, Ivona",

    "01-Jun": "Ales, Zaneta",
    "02-Jun": "Vlastimila, Xenia",
    "03-Jun": "Bronislav",
    "04-Jun": "Divis, Pravoslava",
    "05-Jun": "Meclislav, Laura",
    "06-Jun": "Radoboj",
    "07-Jun": "Borislav, Robert",
    "08-Jun": "Medard",
    "09-Jun": "Vojislav, Stanislava",
    "10-Jun": "Cestimir, Margareta",
    "11-Jun": "Barnabas",
    "12-Jun": "Svatoslav",
    "13-Jun": "Milada, Kasandra",
    "14-Jun": "Vasil",
    "15-Jun": "Vit, Sandra",
    "16-Jun": "Bozetech",
    "17-Jun": "Vladivoj",
    "18-Jun": "Vratislav",
    "19-Jun": "Volnomil",
    "20-Jun": "Valeria, Klaudia",
    "21-Jun": "Alojz, Blanka",
    "22-Jun": "Paulina, Marusa",
    "23-Jun": "Zeno, Zena",
    "24-Jun": "Jan Krstitel",
    "25-Jun": "Olivera, Oliver",
    "26-Jun": "Jeremias, Adriana",
    "27-Jun": "Ladislav, Natalia",
    "28-Jun": "Slavoj, Beata",
    "29-Jun": "Peter",
    "30-Jun": "Vlastimir, Melania, Melita",

    "01-Jul": "Lubor, Liliana",
    "02-Jul": "Berta, Debora",
    "03-Jul": "Miloslav",
    "04-Jul": "Ervin, Mateja",
    "05-Jul": "Cyril a Metod",
    "06-Jul": "Majster Jan Hus",
    "07-Jul": "Veleslav",
    "08-Jul": "Ivan, Johana",
    "09-Jul": "Lujza, Iva",
    "10-Jul": "Liba, Lada",
    "11-Jul": "Milota, Milusa",
    "12-Jul": "Borisa, Nina",
    "13-Jul": "Margita, Nike",
    "14-Jul": "Kamil, Leon",
    "15-Jul": "Karolina, Henrich",
    "16-Jul": "Rut, Hviezdoslava",
    "17-Jul": "Svorad",
    "18-Jul": "Kamila, Kalina",
    "19-Jul": "Dusana",
    "20-Jul": "Elias",
    "21-Jul": "Antonia, Tina",
    "22-Jul": "Magdalena",
    "23-Jul": "Olga, Olina",
    "24-Jul": "Kristina",
    "25-Jul": "Jakub",
    "26-Jul": "Anna",
    "27-Jul": "Marta",
    "28-Jul": "Svatos, Kristof",
    "29-Jul": "Bozena",
    "30-Jul": "Julian, Nino",
    "31-Jul": "Ernestina, Erik, Erika",

    "01-August": "Lubomil, Luboslav",
    "02-August": "Adolf, Gustav",
    "03-August": "August, Augustin",
    "04-August": "Krasoslav, Dominik",
    "05-August": "Jadviga, Hedviga",
    "06-August": "Jozefina, Jozefa",
    "07-August": "Stefania, Stefana",
    "08-August": "Oskar",
    "09-August": "Ratibor",
    "10-August": "Vavrinec",
    "11-August": "Jasna, Lubomira",
    "12-August": "Darina, Dasa",
    "13-August": "Lubomir",
    "14-August": "Mojmir, Marcela",
    "15-August": "Velka Maria",
    "16-August": "Titus, Timea",
    "17-August": "Michaela, Milica",
    "18-August": "Helena, Elena",
    "19-August": "Vratislava",
    "20-August": "Lydia, Anabela",
    "21-August": "Jana, Ivana",
    "22-August": "Frantiska",
    "23-August": "Vlastislav",
    "24-August": "Bartolomej",
    "25-August": "Ludovit",
    "26-August": "Samuel",
    "27-August": "Ruzena, Silvia",
    "28-August": "Augusta, Augustina",
    "29-August": "Statie Jana",
    "30-August": "Benjamin",
    "31-August": "Tichomir, Nora",

    "01-September": "Drahoslava",
    "02-September": "Bronislava",
    "03-September": "Otokar",
    "04-September": "Rozalia, Rachel",
    "05-September": "Budislava",
    "06-September": "Boemil, Alica",
    "07-September": "Mariena, Mariana",
    "08-September": "Annamaria, Masa",
    "09-September": "Martina, Dobrusha",
    "10-September": "Oleg, Patrik",
    "11-September": "Zdislav",
    "12-September": "Dobroslava",
    "13-September": "Ctibor",
    "14-September": "Drahotin",
    "15-September": "Duchoslav, Jolana",
    "16-September": "Ludmila",
    "17-September": "Drahoslav",
    "18-September": "Radomir",
    "19-September": "Konstantin",
    "20-September": "Luboslava",
    "21-September": "Matus",
    "22-September": "Moric",
    "23-September": "Zdenka",
    "24-September": "Lubos",
    "25-September": "Vladislav",
    "26-September": "Edita, Vladislava",
    "27-September": "Damian, Kozmas",
    "28-September": "Vaclav",
    "29-September": "Michal",
    "30-September": "Jarolim",

    "01-Oktober": "Arnold, Belina",
    "02-Oktober": "Levoslav",
    "03-Oktober": "Koloman",
    "04-Oktober": "Frantisek, Fero",
    "05-Oktober": "Blahomir",
    "06-Oktober": "Viera, Patricia",
    "07-Oktober": "Eliska, Ela",
    "08-Oktober": "Eugenia, Una",
    "09-Oktober": "Silas, Anastazia",
    "10-Oktober": "Gedeon, Slavomira",
    "11-Oktober": "Zvonimir, Zvonimira",
    "12-Oktober": "Maximilian, Maxim",
    "13-Oktober": "Eduard, Edvin",
    "14-Oktober": "Boris",
    "15-Oktober": "Terezia",
    "16-Oktober": "Gal, Vladimira",
    "17-Oktober": "Bozej, Ignac",
    "18-Oktober": "Lukas",
    "19-Oktober": "Kristian",
    "20-Oktober": "Vendelin",
    "21-Oktober": "Ursula",
    "22-Oktober": "Dobromil, Sergej",
    "23-Oktober": "Zitomir",
    "24-Oktober": "Kvetoslava",
    "25-Oktober": "Zlatko, Zlatusa",
    "26-Oktober": "Mitar, Demeter",
    "27-Oktober": "Horislava, Stela",
    "28-Oktober": "Simon, Juda",
    "29-Oktober": "Klara, Valentina",
    "30-Oktober": "Petronela, Simona",
    "31-Oktober": "Aurelia",

    "01-November": "Vsechsvatych, Diana",
    "02-November": "Vekoslav, Denisa",
    "03-November": "Ida, Elizabeta",
    "04-November": "Hostimil",
    "05-November": "Imrich",
    "06-November": "Renata",
    "07-November": "Boholub",
    "08-November": "Bohumir",
    "09-November": "Fedora",
    "10-November": "Marian, Tibor",
    "11-November": "Den primeria, Martin",
    "12-November": "Svatopluk",
    "13-November": "Lutobor",
    "14-November": "Mladen",
    "15-November": "Irma, Klementina",
    "16-November": "Anezka, Agneza",
    "17-November": "Dionyz, Sebastian",
    "18-November": "Oto",
    "19-November": "Alzbeta, Erza",
    "20-November": "Bohumira",
    "21-November": "Ctirad",
    "22-November": "Ernest, Nada",
    "23-November": "Dagmara",
    "24-November": "Emilia, Milina",
    "25-November": "Katarina",
    "26-November": "Kornel",
    "27-November": "Nestor, Noe",
    "28-November": "Milan, Henrieta",
    "29-November": "Vratko",
    "30-November": "Ondrej, Andrej",

    "01-December": "Slavia",
    "02-December": "Budislava",
    "03-December": "Slavomir",
    "04-December": "Barbora, Barbara",
    "05-December": "Sava",
    "06-December": "Mikulas",
    "07-December": "",
    "08-December": "Mario, Marina",
    "09-December": "Izabela",
    "10-December": "Judita",
    "11-December": "Hostivit",
    "12-December": "Otilia",
    "13-December": "Lucia",
    "14-December": "",
    "15-December": "Ivor, Ivica",
    "16-December": "Albina, Bela",
    "17-December": "Kornelia, Kornina, Nela",
    "18-December": "Osveclin, Slava",
    "19-December": "Abraham",
    "20-December": "Izak",
    "21-December": "",
    "22-December": "Adela, Etela, Adelina",
    "23-December": "Nadezda, Vlasta",
    "24-December": "Adam, Eva",
    "25-December": "",
    "26-December": "Stefan",
    "27-December": "Jan",
    "28-December": "",
    "29-December": "David",
    "30-December": "Silvester"
}

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

def split_names(names: str):
    cleaned = names.replace(" a ", ", ").replace(" - ", ", ")
    return [n.strip().lower() for n in cleaned.split(",") if n.strip()]

def key_to_date(key: str, year: int):
    day, month_name = key.split("-")
    month_num = list(MONTH_KEY_NAMES.values()).index(month_name) + 1
    return date(year, month_num, int(day))

name_to_date = defaultdict(list)

for date_key, names in namedays.items():
    for name in split_names(names):
        name_to_date[name].append(date_key)

subscriptions = defaultdict(set) 

@bot.message_handler(commands=["start", "help"])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "Zvláštny meninový bot 😊\n\n"
        "/meniny → dnešné meniny\n"
        "/meniny 17-12 → meniny v daný dátum\n"
        "/meniny Daniel → dátum menín pre meno\n\n"
        "/meniny zajtra | včera\n"
        "/kedy má meniny Daniel\n\n"
        "/odoberat Meno → zvýrazní meno pri meninách\n"
        "/odhlasit Meno → zruší sledovanie\n"
        "/sledovane → zobrazí sledované mená\n\n"
        "/ziveli Meno → prianie k meninám\n\n"
        "!meniny → dnešné meniny (v skupinách)"
    )

@bot.message_handler(commands=["meniny"])
def handle_meniny(message):
    args = message.text.split(maxsplit=1)
    query = args[1].strip().lower() if len(args) > 1 else ""

    now = datetime.now()
    label = "Dnes"

    if not query or query in ["dnes", "dneska"]:
        d = now

    elif query == "zajtra":
        d = now + timedelta(days=1)
        label = "Zajtra"

    elif query == "vcera":
        d = now - timedelta(days=1)
        label = "Vcera"

    elif query == "najblizsie":
        d = now
        label = "Najblizsie"
        for _ in range(366):
            key = f"{d.day:02d}-{MONTH_KEY_NAMES[d.strftime('%m')]}"
            if namedays.get(key, "").strip():
                break
            d += timedelta(days=1)

    elif any(sep in query for sep in [".", "-", "/"]):
        try:
            cleaned = query.replace("/", ".").replace("-", ".")
            day, month = cleaned.split(".")[:2]
            key = f"{day.zfill(2)}-{MONTH_KEY_NAMES[month.zfill(2)]}"
            bot.send_message(
                message.chat.id,
                f"{key}: {namedays.get(key, 'V tento datum nema meniny nikto.')}"
            )
            return
        except:
            bot.send_message(message.chat.id, "Nespravny format datumu – pouzi dd.mm 😅")
            return

    else:
        dates = name_to_date.get(query)
        if dates:
            out = []
            for dkey in sorted(dates):
                day, month = dkey.split("-")
                out.append(f"{day}-{MONTH_GENITIVE.get(month, month)}")
            bot.send_message(message.chat.id, f"{query.capitalize()} ma meniny: {', '.join(out)}")
        else:
            bot.send_message(message.chat.id, "Meno nebolo najdene. 😔")
        return

    key = f"{d.day:02d}-{MONTH_KEY_NAMES[d.strftime('%m')]}"
    names = namedays.get(key, "Dnes nema meniny nikto.")

    emoji = ""
    tracked = subscriptions.get(message.chat.id, set())
    if any(n in tracked for n in split_names(names)):
        emoji = " 🎉"

    bot.send_message(message.chat.id, f"{label} ({key}): {names}{emoji}")

@bot.message_handler(commands=["kedy"])
def handle_kedy(message):
    text = message.text.lower()
    if "meniny" not in text:
        return

    name = text.split("meniny", 1)[1].strip()
    if not name:
        bot.send_message(message.chat.id, "Pouzi: /kedy ma meniny Meno")
        return

    today = date.today()
    dates = name_to_date.get(name)

    if not dates:
        bot.send_message(message.chat.id, "Meno nebolo najdene. 😔")
        return

    future = []
    for key in dates:
        d = key_to_date(key, today.year)
        if d < today:
            d = key_to_date(key, today.year + 1)
        future.append(d)

    next_date = min(future)
    diff = (next_date - today).days

    if diff == 0:
        bot.send_message(message.chat.id, f"{name.capitalize()} ma dnes meniny! 🎉")
    else:
        key = f"{next_date.day:02d}-{MONTH_KEY_NAMES[str(next_date.month).zfill(2)]}"
        bot.send_message(
            message.chat.id,
            f"{name.capitalize()} ma meniny o {diff} dni ({key})."
        )

@bot.message_handler(commands=["odoberat"])
def subscribe(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Pouzi: /odoberat Meno")
        return
    name = parts[1].strip().lower()
    subscriptions[message.chat.id].add(name)
    bot.send_message(message.chat.id, f"Meno {name.capitalize()} je sledovane ✅")

@bot.message_handler(commands=["odhlasit"])
def unsubscribe(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Pouzi: /odhlasit Meno")
        return
    name = parts[1].strip().lower()
    subscriptions[message.chat.id].discard(name)
    bot.send_message(message.chat.id, f"Meno {name.capitalize()} uz nie je sledovane ❌")

@bot.message_handler(commands=["sledovane"])
def show_subscriptions(message):
    names = sorted(subscriptions.get(message.chat.id, []))
    if not names:
        bot.send_message(message.chat.id, "Zatial nesledujes ziadne mena.")
    else:
        bot.send_message(message.chat.id, "Sledovane mena:\n" + ", ".join(n.capitalize() for n in names))

@bot.message_handler(commands=["ziveli"])
def ziveli(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Pouzi: /ziveli Meno")
        return
    name = parts[1].strip().capitalize()
    bot.send_message(
        message.chat.id,
        f"Vsetko najlepsie k meninam, {name}! 🎉 Prajeme vela zdravia a pohody."
    )

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("!meniny"))
def handle_group(message):
    now = datetime.now()
    key = f"{now.day:02d}-{MONTH_KEY_NAMES[now.strftime('%m')]}"
    bot.send_message(message.chat.id, f"Dnes ({key}): {namedays.get(key, 'Dnes nema meniny nikto.')}")

@app.route("/" + TOKEN, methods=["POST"])
def telegram_webhook():
    update = telebot.types.Update.de_json(flask.request.get_data().decode("utf-8"))
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
