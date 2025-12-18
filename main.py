import telebot
import flask
import os
from datetime import datetime

# ================= CONFIG =================
TOKEN = os.environ["TOKEN"]

bot = telebot.TeleBot(TOKEN, threaded=False)
app = flask.Flask(__name__)


# Full namedays dict (from your Vojvodina calendar)
namedays = {
    "01-01": "Nový rok, Ježiš",
    "01-02": "Ábel, Set",
    "01-03": "Daniel",
    "01-04": "Eugen",
    "01-05": "Simeón, Andrea",
    "01-06": "Zj. Kr. Pána, Gašpar, Melichár, Baltazár",
    "01-07": "Bohuslava",
    "01-08": "Pravdomil",
    "01-09": "Pravoľub, Alexej",
    "01-10": "Dalimír",
    "01-11": "Malvína, Majda",
    "01-12": "Rastislav",
    "01-13": "Čistko",
    "01-14": "Šťastko",
    "01-15": "Dobroslav",
    "01-16": "Vladimír",
    "01-17": "Anton, Nataša",
    "01-18": "Bohdana, Teodora",
    "01-19": "Sára, Drahomíra",
    "01-20": "Dalibor",
    "01-21": "Vincent",
    "01-22": "Zora, Alexandra",
    "01-23": "Miloš",
    "01-24": "Ctiboh, Timotej",
    "01-25": "Pavel",
    "01-26": "Svätoboj, Tamara",
    "01-27": "Ján Zlatoústy",
    "01-28": "Karol",
    "01-29": "Pribina",
    "01-30": "Ema, Amadea",
    "01-31": "Emil",
    "02-01": "Tatiana, Tea",
    "02-02": "Mária - Hromnice",
    "02-03": "Blažej",
    "02-04": "Veronika, Veronka",
    "02-05": "Svetluša, Aľoša",
    "02-06": "Dorota",
    "02-07": "Dária, Dajana",
    "02-08": "Prokop",
    "02-09": "Zdenko",
    "02-10": "Gorazd",
    "02-11": "Libuša",
    "02-12": "Zoroslav",
    "02-13": "Horislav",
    "02-14": "Velimír, Valentín",
    "02-15": "Deň štátnosti",
    "02-16": "Juliana",
    "02-17": "Miloslava",
    "02-18": "Jaromír",
    "02-19": "Zuzana",
    "02-20": "Všemil, Lívia",
    "02-21": "Eleonóra, Lena, Lenka",
    "02-22": "Veleslava",
    "02-23": "Lazár, Leonóra",
    "02-24": "Matej",
    "02-25": "Viktor",
    "02-26": "Alexander, Saša",
    "02-27": "Drahotína, Drahuša",
    "02-28": "Zlatica, Zlatka",
    "02-29": "Roman",
    "03-01": "Albín, Belo",
    "03-02": "Amália, Mia",
    "03-03": "Bohumil",
    "03-04": "Jadran, Adrian",
    "03-05": "Fridrich",
    "03-06": "Radoslav",
    "03-07": "Tomáš",
    "03-08": "Medzinárodný deň žien",
    "03-09": "Radúz",
    "03-10": "Branislav",
    "03-11": "Jurina, Dina",
    "03-12": "Gregor",
    "03-13": "Vlastimil",
    "03-14": "Matilda, Maja",
    "03-15": "Belomír, Svetlana",
    "03-16": "Boleslav",
    "03-17": "Ľubica",
    "03-18": "Ctislav, Hviezdoslav",
    "03-19": "Jozef",
    "03-20": "Víťazoslav",
    "03-21": "Blahoslav",
    "03-22": "Vesna, Kazimír",
    "03-23": "Darko, Dárius",
    "03-24": "Gabriel",
    "03-25": "Zvesť narodenia Krista Pána",
    "03-26": "Emanuel, Emanuela",
    "03-27": "Alena, Aneta",
    "03-28": "Soňa, Rastislava",
    "03-29": "Miroslav, Sabína",
    "03-30": "Vieroslava",
    "03-31": "Gabriela",
    "04-01": "Hugo",
    "04-02": "Šťastka",
    "04-03": "Bohurád, Richard",
    "04-04": "Bohumila, Izidora",
    "04-05": "Bohuslav",
    "04-06": "Irena",
    "04-07": "Radhošť",
    "04-08": "Dagmar, Albert",
    "04-09": "Milena, Miléva",
    "04-10": "Igor",
    "04-11": "Július, Leona",
    "04-12": "Estera",
    "04-13": "Silorád",
    "04-14": "Hrdoš",
    "04-15": "Fedor",
    "04-16": "Danica, Dana",
    "04-17": "Rudolf",
    "04-18": "Valér",
    "04-19": "Ratimír",
    "04-20": "Hvezdoň, Marcel",
    "04-21": "Želislav",
    "04-22": "Vojtech, Svätomír",
    "04-23": "Jelena, Jela",
    "04-24": "Juraj, Ďuro",
    "04-25": "Marek, Marko",
    "04-26": "Jaroslava",
    "04-27": "Jaroslav",
    "04-28": "Jarmila",
    "04-29": "Dobrôtka, Lea, Leo",
    "04-30": "Miroslava",
    "05-01": "Sviatok práce, Filip",
    "05-02": "Žigmund",
    "05-03": "Desana, Denis",
    "05-04": "Florián, Alex",
    "05-05": "Kvetoslav",
    "05-06": "Hermína, Mina",
    "05-07": "Stanislav, Monika",
    "05-08": "Milutín, Ingrid, Ines",
    "05-09": "Deň víťazstva",
    "05-10": "Viktória",
    "05-11": "Blažena",
    "05-12": "Pankrác",
    "05-13": "Servác",
    "05-14": "Bonifác",
    "05-15": "Žofia, Sofia",
    "05-16": "Svetozár",
    "05-17": "Zobor",
    "05-18": "Viola, Vida",
    "05-19": "Dezider, Hana",
    "05-20": "Borivoj",
    "05-21": "Dobromír",
    "05-22": "Júlia, Petra",
    "05-23": "Želmíra",
    "05-24": "Danuša, Daniela",
    "05-25": "Urban",
    "05-26": "Dušan",
    "05-27": "Miliduch, Iveta",
    "05-28": "Viliam",
    "05-29": "Vilma, Amanda",
    "05-30": "Ferdinand",
    "05-31": "Blahoslava, Ivona",
    "06-01": "Aleš, Žaneta",
    "06-02": "Vlastimila, Xénia",
    "06-03": "Bronislav",
    "06-04": "Diviš, Pravoslava",
    "06-05": "Mečislav, Laura",
    "06-06": "Radoboj",
    "06-07": "Borislav, Róbert",
    "06-08": "Medard",
    "06-09": "Vojislav, Stanislava",
    "06-10": "Čestimir, Margaréta",
    "06-11": "Barnabáš",
    "06-12": "Svätoslav",
    "06-13": "Milada, Kasandra",
    "06-14": "Vasil",
    "06-15": "Vít, Sandra",
    "06-16": "Božetech",
    "06-17": "Vladivoj",
    "06-18": "Vratislav",
    "06-19": "Voľnomil",
    "06-20": "Valéria, Klaudia",
    "06-21": "Alojz, Blanka",
    "06-22": "Paulína, Maruša",
    "06-23": "Zeno, Zena",
    "06-24": "Ján Krstiteľ",
    "06-25": "Olivera, Oliver",
    "06-26": "Jeremiáš, Adriána",
    "06-27": "Ladislav, Natália",
    "06-28": "Slavoj, Beáta",
    "06-29": "Peter a Pavel",
    "06-30": "Vlastimír, Melánia, Melita",
    "07-01": "Ľubor, Liliana",
    "07-02": "Berta, Debora",
    "07-03": "Miloslav",
    "07-04": "Ervin, Mateja",
    "07-05": "Cyril a Metod",
    "07-06": "Majster Ján Hus",
    "07-07": "Veleslav",
    "07-08": "Ivan, Johana",
    "07-09": "Lujza, Iva",
    "07-10": "Liba, Lada",
    "07-11": "Milota, Miluša",
    "07-12": "Boriša, Nina",
    "07-13": "Margita, Niké",
    "07-14": "Kamil, León",
    "07-15": "Karolína, Henrich",
    "07-16": "Rút, Hviezdoslava",
    "07-17": "Svorád",
    "07-18": "Kamila, Kalina",
    "07-19": "Dušana",
    "07-20": "Eliáš",
    "07-21": "Antónia, Tina",
    "07-22": "Magdaléna",
    "07-23": "Oľga, Olina",
    "07-24": "Kristína",
    "07-25": "Jakub",
    "07-26": "Anna",
    "07-27": "Marta",
    "07-28": "Svätoš, Krištof",
    "07-29": "Božena",
    "07-30": "Julián, Nino",
    "07-31": "Ernestína, Erik, Erika",
    "08-01": "Ľubomil, Ľuboslav",
    "08-02": "Adolf, Gustáv",
    "08-03": "August, Augustín",
    "08-04": "Krasoslav, Dominik",
    "08-05": "Jadviga, Hedviga",
    "08-06": "Jozefína, Jozefa",
    "08-07": "Štefánia, Štefana",
    "08-08": "Oskár",
    "08-09": "Ratibor",
    "08-10": "Vavrinec",
    "08-11": "Jasna, Ľubomíra",
    "08-12": "Darina, Daša",
    "08-13": "Ľubomír",
    "08-14": "Mojmír, Marcela",
    "08-15": "Veľká Mária",
    "08-16": "Títus, Timea",
    "08-17": "Michaela, Milica",
    "08-18": "Helena, Elena",
    "08-19": "Vratislava",
    "08-20": "Lýdia, Anabela",
    "08-21": "Jana, Ivana",
    "08-22": "Františka",
    "08-23": "Vlastislav",
    "08-24": "Bartolomej",
    "08-25": "Ľudovít",
    "08-26": "Samuel",
    "08-27": "Ružena, Silvia",
    "08-28": "Augusta, Augustína",
    "08-29": "Sťatie Jána",
    "08-30": "Benjamín",
    "08-31": "Tichomír, Nora",
    "09-01": "Drahoslava",
    "09-02": "Bronislava",
    "09-03": "Otokar",
    "09-04": "Rozália, Ráchel",
    "09-05": "Budislava",
    "09-06": "Boemil, Alica",
    "09-07": "Mariena, Mariana",
    "09-08": "Annamária, Máša",
    "09-09": "Martina, Dobruša",
    "09-10": "Oleg, Patrik",
    "09-11": "Zdislav",
    "09-12": "Dobroslava",
    "09-13": "Ctibor",
    "09-14": "Drahotín",
    "09-15": "Duchoslav, Jolana",
    "09-16": "Ľudmila",
    "09-17": "Drahoslav",
    "09-18": "Radomír",
    "09-19": "Konštantín",
    "09-20": "Ľuboslava",
    "09-21": "Matúš",
    "09-22": "Móric",
    "09-23": "Zdenka",
    "09-24": "Ľuboš",
    "09-25": "Vladislav",
    "09-26": "Edita, Vladislava",
    "09-27": "Damian, Kozmas",
    "09-28": "Václav",
    "09-29": "Michal",
    "09-30": "Jarolím",
    "10-01": "Arnold, Belína",
    "10-02": "Levoslav",
    "10-03": "Koloman",
    "10-04": "František, Fero",
    "10-05": "Blahomír",
    "10-06": "Viera, Patrícia",
    "10-07": "Eliška, Ela",
    "10-08": "Eugénia, Una",
    "10-09": "Silas, Anastázia",
    "10-10": "Gedeón, Slavomíra",
    "10-11": "Zvonimír, Zvonimíra",
    "10-12": "Maximilián, Maxim",
    "10-13": "Eduard, Edvín",
    "10-14": "Boris",
    "10-15": "Terézia",
    "10-16": "Gál, Vladimíra",
    "10-17": "Božej, Ignác",
    "10-18": "Lukáš",
    "10-19": "Kristián",
    "10-20": "Vendelín",
    "10-21": "Uršuľa",
    "10-22": "Dobromil, Sergej",
    "10-23": "Žitomír",
    "10-24": "Kvetoslava",
    "10-25": "Zlatko, Zlatuša",
    "10-26": "Mitar, Demeter",
    "10-27": "Horislava, Stela",
    "10-28": "Šimon, Júda",
    "10-29": "Klára, Valentína",
    "10-30": "Petronela, Simona",
    "10-31": "Aurelia",
    "11-01": "Všechsvätých, Diana",
    "11-02": "Vekoslav, Denisa",
    "11-03": "Ida, Elizabeta",
    "11-04": "Hostimil",
    "11-05": "Imrich",
    "11-06": "Renáta",
    "11-07": "Bohoľub",
    "11-08": "Bohumír",
    "11-09": "Fedora",
    "11-10": "Marián, Tibor",
    "11-11": "Deň prímeria, Martin",
    "11-12": "Svätopluk",
    "11-13": "Ľutobor",
    "11-14": "Mladen",
    "11-15": "Irma, Klementína",
    "11-16": "Anežka, Agneza",
    "11-17": "Dionýz, Sebastián",
    "11-18": "Oto",
    "11-19": "Alžbeta, Erža",
    "11-20": "Bohumíra",
    "11-21": "Ctirad",
    "11-22": "Ernest, Naďa",
    "11-23": "Dagmara",
    "11-24": "Emília, Milina",
    "11-25": "Katarína",
    "11-26": "Kornel",
    "11-27": "Nestor, Noe",
    "11-28": "Milan, Henrieta",
    "11-29": "Vratko",
    "11-30": "Ondrej, Andrej",
    "12-01": "Slávia",
    "12-02": "Budislav",
    "12-03": "Slavomír",
    "12-04": "Barbara, Barbora",
    "12-05": "Sáva",
    "12-06": "Mikuláš",
    "12-07": "Ambróz",
    "12-08": "Mário, Marína",
    "12-09": "Izabela",
    "12-10": "Judita",
    "12-11": "Hostivít",
    "12-12": "Otília",
    "12-13": "Lucia",
    "12-14": "Branislava",
    "12-15": "Ivor, Ivica",
    "12-16": "Albína, Bela",
    "12-17": "Kornélia, Korina",
    "12-18": "Osvetín, Slávia",
    "12-19": "Abrahám",
    "12-20": "Izák",
    "12-21": "Tomáš, Bohdan",
    "12-22": "Adela, Etela",
    "12-23": "Nadežda, Vlasta",
    "12-24": "Štedrý deň, Adam a Eva",
    "12-25": "Narodenie Krista Pána",
    "12-26": "Štefan mučeník",
    "12-27": "Ján evanjelista",
    "12-28": "Mláďatká, Silvia",
    "12-29": "Jonatán",
    "12-30": "Dávid",
    "12-31": "Silvester",
}



# ================= REVERSE INDEX =================
name_to_date = {}
for date, names in namedays.items():
    cleaned = names.replace(" a ", ", ").replace(" - ", ", ")
    for name in [n.strip() for n in cleaned.split(",") if n.strip()]:
        name_to_date[name.lower()] = date

# ================= COMMANDS =================
@bot.message_handler(commands=["start", "help"])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "Simple meniny bot 😊\n\n"
        "/meniny → today's meniny\n"
        "/meniny dnes → same\n"
        "/meniny 17.12 → meniny on that date\n"
        "/meniny Daniel → date for that name\n\n"
        "!meniny → today's meniny (groups)"
    )

@bot.message_handler(commands=["meniny"])
def handle_meniny(message):
    args = message.text.split(maxsplit=1)
    query = args[1].strip() if len(args) > 1 else ""

    if not query or query.lower() in ["dnes", "today", "dneska"]:
        key = datetime.now().strftime("%m-%d")
        names = namedays.get(key, "No entry today.")
        date = datetime.now().strftime("%d.%m.%Y")
        bot.send_message(message.chat.id, f"Today ({date}): {names}")

    elif any(sep in query for sep in [".", "-", "/"]):
        try:
            cleaned = query.replace("/", ".").replace("-", ".")
            day, month = cleaned.split(".")[:2]
            key = f"{month.zfill(2)}-{day.zfill(2)}"
            bot.send_message(message.chat.id, f"{query}: {namedays.get(key, 'No entry on this date.')}")
        except:
            bot.send_message(message.chat.id, "Wrong date format – use dd.mm 😅")

    else:
        date = name_to_date.get(query.lower())
        if date:
            d, m = date.split("-")
            bot.send_message(message.chat.id, f"{query.capitalize()} has meniny on {d}.{m}.")
        else:
            bot.send_message(message.chat.id, "Name not found 😔")

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("!meniny"))
def handle_group(message):
    key = datetime.now().strftime("%m-%d")
    names = namedays.get(key, "No entry today.")
    date = datetime.now().strftime("%d.%m.%Y")
    bot.send_message(message.chat.id, f"Today ({date}): {names}")

# ================= WEBHOOK =================
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

# ================= RUN =================

if os.environ.get("RENDER"):
    bot.remove_webhook()
    bot.set_webhook(
        url=f"https://meniny-bot.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
