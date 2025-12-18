import telebot
import flask
import os
from datetime import datetime

TOKEN = os.environ["TOKEN"]

bot = telebot.TeleBot(TOKEN, threaded=False)
app = flask.Flask(__name__)


# Full namedays dict (from your Vojvodina calendar)
namedays = {
    "01-01": "Novy rok, Jezis",
    "01-02": "Abel, Set",
    "01-03": "Daniel",
    "01-04": "Eugen",
    "01-05": "Simeon, Andrea",
    "01-06": "Zj. Kr. Pana, Gaspar, Melichar, Baltazar",
    "01-07": "Bohuslava",
    "01-08": "Pravdomil",
    "01-09": "Pravolub, Alexej",
    "01-10": "Dalimir",
    "01-11": "Malvina, Majda",
    "01-12": "Rastislav",
    "01-13": "Cistko",
    "01-14": "Stastko",
    "01-15": "Dobroslav",
    "01-16": "Vladimir",
    "01-17": "Anton, Natasa",
    "01-18": "Bohdana, Teodora",
    "01-19": "Sara, Drahomira",
    "01-20": "Dalibor",
    "01-21": "Vincent",
    "01-22": "Zora, Alexandra",
    "01-23": "Milos",
    "01-24": "Ctiboh, Timotej",
    "01-25": "Pavel",
    "01-26": "Svatoboj, Tamara",
    "01-27": "Ján Zlatousty",
    "01-28": "Karol",
    "01-29": "Pribina",
    "01-30": "Ema, Amadea",
    "01-31": "Emil",

    "02-01": "Tatiana, Tea",
    "02-02": "Maria - Hromnice",
    "02-03": "Blazej",
    "02-04": "Veronika, Veronka",
    "02-05": "Svetlusa, Alosa",
    "02-06": "Dorota",
    "02-07": "Daria, Dajana",
    "02-08": "Prokop",
    "02-09": "Zdenko",
    "02-10": "Gorazd",
    "02-11": "Libusa",
    "02-12": "Zoroslav",
    "02-13": "Horislav",
    "02-14": "Velimir, Valentin",
    "02-15": "Den statnosti",
    "02-16": "Juliana",
    "02-17": "Miloslava",
    "02-18": "Jaromir",
    "02-19": "Zuzana",
    "02-20": "Vsemil, Livia",
    "02-21": "Eleonora, Lena, Lenka",
    "02-22": "Veleslava",
    "02-23": "Lazar, Leonora",
    "02-24": "Matej",
    "02-25": "Viktor",
    "02-26": "Alexander, Sasa",
    "02-27": "Drahotina, Drahusa",
    "02-28": "Zlatica, Zlatka",
    "02-29": "Roman",

    "03-01": "Albin, Belo",
    "03-02": "Amalia, Mia",
    "03-03": "Bohumil",
    "03-04": "Jadran, Adrian",
    "03-05": "Fridrich",
    "03-06": "Radoslav",
    "03-07": "Tomas",
    "03-08": "Medzinarodny den zien",
    "03-09": "Raduz",
    "03-10": "Branislav",
    "03-11": "Jurina, Dina",
    "03-12": "Gregor",
    "03-13": "Vlastimil",
    "03-14": "Matilda, Maja",
    "03-15": "Belomir, Svetlana",
    "03-16": "Boleslav",
    "03-17": "Lubica",
    "03-18": "Ctislav, Hviezdoslav",
    "03-19": "Jozef",
    "03-20": "Vitazoslav",
    "03-21": "Blahoslav",
    "03-22": "Vesna, Kazimir",
    "03-23": "Darko, Darius",
    "03-24": "Gabriel",
    "03-25": "Zvest narodenia Krista Pana",
    "03-26": "Emanuel, Emanuela",
    "03-27": "Alena, Aneta",
    "03-28": "Sona, Rastislava",
    "03-29": "Miroslav, Sabina",
    "03-30": "Vieroslava",
    "03-31": "Gabriela",

    "04-01": "Hugo",
    "04-02": "Stastka",
    "04-03": "Bohurad, Richard",
    "04-04": "Bohumila, Izidora",
    "04-05": "Bohuslav",
    "04-06": "Irena",
    "04-07": "Radhost",
    "04-08": "Dagmar, Albert",
    "04-09": "Milena, Mileva",
    "04-10": "Igor",
    "04-11": "Julius, Leona",
    "04-12": "Estera",
    "04-13": "Silorad",
    "04-14": "Hrdos",
    "04-15": "Fedor",
    "04-16": "Danica, Dana",
    "04-17": "Rudolf",
    "04-18": "Valer",
    "04-19": "Ratimir",
    "04-20": "Hvezdon, Marcel",
    "04-21": "Zelislav",
    "04-22": "Vojtech, Svatomir",
    "04-23": "Jelena, Jela",
    "04-24": "Juraj, Duro",
    "04-25": "Marek, Marko",
    "04-26": "Jaroslava",
    "04-27": "Jaroslav",
    "04-28": "Jarmila",
    "04-29": "Dobrotka, Lea, Leo",
    "04-30": "Miroslava",

    "05-01": "Sviatok prace, Filip",
    "05-02": "Zigmund",
    "05-03": "Desana, Denis",
    "05-04": "Florian, Alex",
    "05-05": "Kvetoslav",
    "05-06": "Hermina, Mina",
    "05-07": "Stanislav, Monika",
    "05-08": "Milutin, Ingrid, Ines",
    "05-09": "Den vitazstva",
    "05-10": "Viktoria",
    "05-11": "Blazena",
    "05-12": "Pankrac",
    "05-13": "Servac",
    "05-14": "Bonifac",
    "05-15": "Zofia, Sofia",
    "05-16": "Svetozar",
    "05-17": "Zobor",
    "05-18": "Viola, Vida",
    "05-19": "Dezider, Hana",
    "05-20": "Borivoj",
    "05-21": "Dobromir",
    "05-22": "Julia, Petra",
    "05-23": "Zelmira",
    "05-24": "Danusa, Daniela",
    "05-25": "Urban",
    "05-26": "Dusan",
    "05-27": "Miliduch, Iveta",
    "05-28": "Viliam",
    "05-29": "Vilma, Amanda",
    "05-30": "Ferdinand",
    "05-31": "Blahoslava, Ivona",

    "06-01": "Ales, Zaneta",
    "06-02": "Vlastimila, Xenia",
    "06-03": "Bronislav",
    "06-04": "Divis, Pravoslava",
    "06-05": "Meclislav, Laura",
    "06-06": "Radoboj",
    "06-07": "Borislav, Robert",
    "06-08": "Medard",
    "06-09": "Vojislav, Stanislava",
    "06-10": "Cestimir, Margareta",
    "06-11": "Barnabas",
    "06-12": "Svatoslav",
    "06-13": "Milada, Kasandra",
    "06-14": "Vasil",
    "06-15": "Vit, Sandra",
    "06-16": "Bozetech",
    "06-17": "Vladivoj",
    "06-18": "Vratislav",
    "06-19": "Volnomil",
    "06-20": "Valeria, Klaudia",
    "06-21": "Alojz, Blanka",
    "06-22": "Paulina, Marusa",
    "06-23": "Zeno, Zena",
    "06-24": "Jan Krstitel",
    "06-25": "Olivera, Oliver",
    "06-26": "Jeremias, Adriana",
    "06-27": "Ladislav, Natalia",
    "06-28": "Slavoj, Beata",
    "06-29": "Peter",
    "06-30": "Vlastimir, Melania, Melita",

    "07-01": "Lubor, Liliana",
    "07-02": "Berta, Debora",
    "07-03": "Miloslav",
    "07-04": "Ervin, Mateja",
    "07-05": "Cyril a Metod",
    "07-06": "Majster Jan Hus",
    "07-07": "Veleslav",
    "07-08": "Ivan, Johana",
    "07-09": "Lujza, Iva",
    "07-10": "Liba, Lada",
    "07-11": "Milota, Milusa",
    "07-12": "Borisa, Nina",
    "07-13": "Margita, Nike",
    "07-14": "Kamil, Leon",
    "07-15": "Karolina, Henrich",
    "07-16": "Rut, Hviezdoslava",
    "07-17": "Svorad",
    "07-18": "Kamila, Kalina",
    "07-19": "Dusana",
    "07-20": "Elias",
    "07-21": "Antonia, Tina",
    "07-22": "Magdalena",
    "07-23": "Olga, Olina",
    "07-24": "Kristina",
    "07-25": "Jakub",
    "07-26": "Anna",
    "07-27": "Marta",
    "07-28": "Svatos, Kristof",
    "07-29": "Bozena",
    "07-30": "Julian, Nino",
    "07-31": "Ernestina, Erik, Erika",

    "08-01": "Lubomil, Luboslav",
    "08-02": "Adolf, Gustav",
    "08-03": "August, Augustin",
    "08-04": "Krasoslav, Dominik",
    "08-05": "Jadviga, Hedviga",
    "08-06": "Jozefina, Jozefa",
    "08-07": "Stefania, Stefana",
    "08-08": "Oskar",
    "08-09": "Ratibor",
    "08-10": "Vavrinec",
    "08-11": "Jasna, Lubomira",
    "08-12": "Darina, Dasa",
    "08-13": "Lubomir",
    "08-14": "Mojmir, Marcela",
    "08-15": "Velka Maria",
    "08-16": "Titus, Timea",
    "08-17": "Michaela, Milica",
    "08-18": "Helena, Elena",
    "08-19": "Vratislava",
    "08-20": "Lydia, Anabela",
    "08-21": "Jana, Ivana",
    "08-22": "Frantiska",
    "08-23": "Vlastislav",
    "08-24": "Bartolomej",
    "08-25": "Ludovit",
    "08-26": "Samuel",
    "08-27": "Ruzena, Silvia",
    "08-28": "Augusta, Augustina",
    "08-29": "Statie Jana",
    "08-30": "Benjamin",
    "08-31": "Tichomir, Nora",

    "09-01": "Drahoslava",
    "09-02": "Bronislava",
    "09-03": "Otokar",
    "09-04": "Rozalia, Rachel",
    "09-05": "Budislava",
    "09-06": "Boemil, Alica",
    "09-07": "Mariena, Mariana",
    "09-08": "Annamaria, Masa",
    "09-09": "Martina, Dobrusha",
    "09-10": "Oleg, Patrik",
    "09-11": "Zdislav",
    "09-12": "Dobroslava",
    "09-13": "Ctibor",
    "09-14": "Drahotin",
    "09-15": "Duchoslav, Jolana",
    "09-16": "Ludmila",
    "09-17": "Drahoslav",
    "09-18": "Radomir",
    "09-19": "Konstantin",
    "09-20": "Luboslava",
    "09-21": "Matus",
    "09-22": "Moric",
    "09-23": "Zdenka",
    "09-24": "Lubos",
    "09-25": "Vladislav",
    "09-26": "Edita, Vladislava",
    "09-27": "Damian, Kozmas",
    "09-28": "Vaclav",
    "09-29": "Michal",
    "09-30": "Jarolim",

    "10-01": "Arnold, Belina",
    "10-02": "Levoslav",
    "10-03": "Koloman",
    "10-04": "Frantisek, Fero",
    "10-05": "Blahomir",
    "10-06": "Viera, Patricia",
    "10-07": "Eliska, Ela",
    "10-08": "Eugenia, Una",
    "10-09": "Silas, Anastazia",
    "10-10": "Gedeon, Slavomira",
    "10-11": "Zvonimir, Zvonimira",
    "10-12": "Maximilian, Maxim",
    "10-13": "Eduard, Edvin",
    "10-14": "Boris",
    "10-15": "Terezia",
    "10-16": "Gal, Vladimira",
    "10-17": "Bozej, Ignac",
    "10-18": "Lukas",
    "10-19": "Kristian",
    "10-20": "Vendelin",
    "10-21": "Ursula",
    "10-22": "Dobromil, Sergej",
    "10-23": "Zitomir",
    "10-24": "Kvetoslava",
    "10-25": "Zlatko, Zlatusa",
    "10-26": "Mitar, Demeter",
    "10-27": "Horislava, Stela",
    "10-28": "Simon, Juda",
    "10-29": "Klara, Valentina",
    "10-30": "Petronela, Simona",
    "10-31": "Aurelia",

    "11-01": "Vsechsvatych, Diana",
    "11-02": "Vekoslav, Denisa",
    "11-03": "Ida, Elizabeta",
    "11-04": "Hostimil",
    "11-05": "Imrich",
    "11-06": "Renata",
    "11-07": "Boholub",
    "11-08": "Bohumir",
    "11-09": "Fedora",
    "11-10": "Marian, Tibor",
    "11-11": "Den primeria, Martin",
    "11-12": "Svatopluk",
    "11-13": "Lutobor",
    "11-14": "Mladen",
    "11-15": "Irma, Klementina",
    "11-16": "Anezka, Agneza",
    "11-17": "Dionyz, Sebastian",
    "11-18": "Oto",
    "11-19": "Alzbeta, Erza",
    "11-20": "Bohumira",
    "11-21": "Ctirad",
    "11-22": "Ernest, Nada",
    "11-23": "Dagmara",
    "11-24": "Emilia, Milina",
    "11-25": "Katarina",
    "11-26": "Kornel",
    "11-27": "Nestor, Noe",
    "11-28": "Milan, Henrieta",
    "11-29": "Vratko",
    "11-30": "Ondrej, Andrej",

    "12-01": "Slavia",
    "12-02": "Budislav",
    "12-03": "Slavomir",
    "12-04": "Barbara, Barbora",
    "12-05": "Sava",
    "12-06": "Mikulas",
    "12-07": "Ambroz",
    "12-08": "Mario, Marina",
    "12-09": "Izabela",
    "12-10": "Judita",
    "12-11": "Hostivit",
    "12-12": "Otilia",
    "12-13": "Lucia",
    "12-14": "Branislava",
    "12-15": "Ivor, Ivica",
    "12-16": "Albina, Bela",
    "12-17": "Kornelia, Korina",
    "12-18": "Osvetin, Slavia",
    "12-19": "Abraham",
    "12-20": "Izak",
    "12-21": "Tomas, Bohdan",
    "12-22": "Adela, Etela",
    "12-23": "Nadezda, Vlasta",
    "12-24": "Stedry den, Adam a Eva",
    "12-25": "Narodenie Krista Pana",
    "12-26": "Stefan mucenik",
    "12-27": "Jan",
    "12-28": "Mladatka, Silvia",
    "12-29": "Jonatan",
    "12-30": "David",
    "12-31": "Silvester",
}



name_to_date = {}
for date, names in namedays.items():
    cleaned = names.replace(" a ", ", ").replace(" - ", ", ")
    for name in [n.strip() for n in cleaned.split(",") if n.strip()]:
        name_to_date[name.lower()] = date

@bot.message_handler(commands=["start", "help"])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "Zvláštny meninový bot 😊\n\n"
        "/meniny → dnešné meniny\n"
        "/meniny 17.12 → meniny v daný dátum\n"
        "/meniny Daniel → dátum menín pre dané meno\n\n"
        "!meniny → dnešné meniny (v skupinách)"
    )

@bot.message_handler(commands=["meniny"])
def handle_meniny(message):
    args = message.text.split(maxsplit=1)
    query = args[1].strip() if len(args) > 1 else ""

    if not query or query.lower() in ["dnes", "dnes", "dneska"]:
        key = datetime.now().strftime("%m-%d")
        names = namedays.get(key, "Dnes nemá meniny nikto.")
        date = datetime.now().strftime("%d.%m.%Y")
        bot.send_message(message.chat.id, f"Dnes ({date}): {names}")

    elif any(sep in query for sep in [".", "-", "/"]):
        try:
            cleaned = query.replace("/", ".").replace("-", ".")
            day, month = cleaned.split(".")[:2]
            key = f"{month.zfill(2)}-{day.zfill(2)}"
            bot.send_message(message.chat.id, f"{query}: {namedays.get(key, 'V tento dátum nemá meniny nikto.')}")
        except:
            bot.send_message(message.chat.id, "Nesprávny formát dátumu – použite dd.mm 😅")

    else:
        date = name_to_date.get(query.lower())
        if date:
            d, m = date.split("-")
            bot.send_message(message.chat.id, f"{query.capitalize()} má meniny dňa {d}.{m}.")
        else:
            bot.send_message(message.chat.id, "Meno nebolo nájdené. 😔")

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("!meniny"))
def handle_group(message):
    key = datetime.now().strftime("%m-%d")
    names = namedays.get(key, "Dnes nemá meniny nikto.")
    date = datetime.now().strftime("%d.%m.%Y")
    bot.send_message(message.chat.id, f"Dnes ({date}): {names}")

@app.route("/" + TOKEN, methods=["POST"])
def telegram_webhook():
    update = telebot.types.Update.de_json(
        flask.request.get_data().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def index():
    return "Bot is alive and looking at % of alcohol in Padinec's blood"

if os.environ.get("RENDER"):
    bot.remove_webhook()
    bot.set_webhook(
        url=f"https://meniny-bot.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
