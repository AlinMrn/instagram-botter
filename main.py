import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import os
import json
import asyncio

# ==========================================
# CONFIGURARE COTAIALA
# ==========================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

FISIER_SCORURI = "scoruri_trivia.json"
FISIER_PEDEPSE = "pedepse_cotaiala.json"
FISIER_STATISTICI = "statistici_cotaiala.json"
CANAL_TRIVIA_ID = 1565074384916451700

STATISTICI_IMPLICITE = {
    "batausi": {},
    "cupluri": {},
    "roast": {},
}


def incarca_statistici():
    try:
        with open(FISIER_STATISTICI, "r", encoding="utf-8") as f:
            date = json.load(f)

        if not isinstance(date, dict):
            return json.loads(json.dumps(STATISTICI_IMPLICITE))

        for categorie, valoare in STATISTICI_IMPLICITE.items():
            if not isinstance(date.get(categorie), dict):
                date[categorie] = valoare.copy()

        return date

    except (FileNotFoundError, json.JSONDecodeError):
        return json.loads(json.dumps(STATISTICI_IMPLICITE))


STATISTICI = incarca_statistici()


def salveaza_statistici():
    temporar = FISIER_STATISTICI + ".tmp"
    with open(temporar, "w", encoding="utf-8") as f:
        json.dump(STATISTICI, f, ensure_ascii=False, indent=2)
    os.replace(temporar, FISIER_STATISTICI)


def inregistreaza_victorie(membru):
    uid = str(membru.id)
    date = STATISTICI["batausi"].get(uid, {})
    STATISTICI["batausi"][uid] = {
        "nume": membru.display_name,
        "victorii": date.get("victorii", 0) + 1
    }
    salveaza_statistici()


def inregistreaza_cuplu(membru1, membru2, procent):
    id1, id2 = sorted([str(membru1.id), str(membru2.id)])
    cheia = f"{id1}_{id2}"
    date = STATISTICI["cupluri"].get(cheia, {})
    procente = date.get("procente", [])
    procente.append(procent)

    STATISTICI["cupluri"][cheia] = {
        "id1": id1,
        "id2": id2,
        "nume1": membru1.display_name if str(membru1.id) == id1 else membru2.display_name,
        "nume2": membru2.display_name if str(membru2.id) == id2 else membru1.display_name,
        "procente": procente,
        "maxim": max(procente)
    }
    salveaza_statistici()


def inregistreaza_roast(membru):
    uid = str(membru.id)
    date = STATISTICI["roast"].get(uid, {})
    STATISTICI["roast"][uid] = {
        "nume": membru.display_name,
        "numar": date.get("numar", 0) + 1
    }
    salveaza_statistici()


# ==========================================
# INJURATURI COTAIALA
# ==========================================

INJURATURI = [
    "Slobozi-m-as pe prima albina care se aseaza pe floarea mormantului ma-tii",
    "sa te futa borrasca in cur pe unde bei apa",
    "te bag in pizza ma-tii cu picioarele inainte ca sa-ti dau si muie dupa aia.",
    "Zii lu ma-ta sa nu isi mai schimbe rujurile ca imi face pula curcubeu",
    "eu nu am pula...destula pentru ma-ta",
    "sa ma cac in pizda ma-tii cu bucati de pula",
    "baga-mi-as pula in ma-ta pana ii fac pizda tunel de metrou",
    "sugeti pula la negrii pana se face alba",
    "parerea mea e sa va duceti toti in pula mea ca e destula pentru toata lumea",
    "sa-mi usuc chilotii pe crucea ma-tii",
    "sa-mi luati cacatul la polizot pana va sare pana in ochi",
    "bagami-as pula in capul vostru de imbecil avortat",
    "nu valorezi nici cat microbii de anthrax dintre celulele de sperma coclita infestata,cu sifilis din pizda curvelor de mame ce aveti",
    "bagami-ati limba.n gaura curului sa-mi gadilati hemoroiziii",
    "spune-i ma-tii sa-mi de-a banii inapoi",
    "esti mereu la fel de idiot sau azi este o ocazie speciala",
    "de ziua muncii,ma-ta defileaza pe autostrada",
    "daca asa avea un dinte in cur te-as musca de nas",
    "daca as avea un ochi in pula,m-as uita la tine toata ziua in gura",
    "daca te lasa parintii sa intri pe mirc in cursul saptamanii,sa aduci maine buletinul ca sa trec numele pula pe el",
    "daca slobozul ar eroda,ma-ta ar fi la a 10-a proteza",
    "pizda -matii e prea mica,a intrat la apa de cata sperma fierbinte a inghitit.",
    "Lu m-ata i s-o virusat pizda cand te-a facut si a trebuit sa de-a reset de acea tu functionezi numai cu pastille",
    "spune-i lui ma-ta sa se mai spele pe dinti ca-i fermenteaza spera pe care i-am lasat-o in gura",
    "auzi ma pula bleaga,o mai dor pe ma-ta genunchii ?",
    "trage aer in cur ca nu o sa mai poti respire de atata pula cat o sa primeste,sugea-mi-ai nectarul din pula",
    "sugea-m-ai de pula pana intra un coi in coma",
    "imi pare rau pentru ma-ta care te-a basit asa prost,acum trebuie sa suga pula sa iti de-a de mancare pentru papagali.",
    "esti o putulica de sconcs pansat",
    "nu ai vrea sa te facem toti o retea?",
    "transfer sifilis si ciuma din contul meu in pizda ma-tii",
    "baga ti as organelle genitaled in pamanat sa putrezeasca ca lemnul ca zi si noapte sunteti cu ele in gura",
    "va e pofta bulangiilor? stati cu dintii la gard ca,cacat veti primi",
    "te-ai futut cu cei 7 piciti,nu?",
    "am un deposit de muie pentru tine",
    "erecta-mi-as pula in esofagul ma-tii"
]


# ==========================================
# ROAST-URI
# ==========================================

ROASTURI = [
    "are nevoie de GPS ca să-și găsească ideile 😂",
    "dacă inteligența ar fi Wi-Fi, ar avea o singură liniuță 📶",
    "e genul de om care pierde la tutorial 🤣",
    "are procesor de calculator din 2005 și răcire pasivă 🥶",
    "când deschide frigiderul, uită ce căuta acolo 💀",
    "dacă lenea era sport olimpic, ar lipsi de la premiere 🥇",
    "are mai mult lag decât un server pe cartofi 🥔",
    "nici Google nu mai încearcă să-i înțeleagă căutările 😭",
    "ar pierde și la piatră, hârtie, foarfecă împotriva unui perete 🧱",
    "e motivul pentru care există butonul «Skip tutorial» 😂",
    "are noroc că prostia nu consumă gigabytes 🤣",
    "dacă ar fi un cartonaș FIFA, ar avea rating 12 💀",
    "Ascult. Dă-mi doar un moment să procesez atâta informație stupidă deodată.",
    "E așa drăguț când încerci să vorbești despre lucruri pe care nu le înțelegi.",
    "Nu te ignor. Îți dau doar timp să reflectezi la cât de idiot ești acum.",
    "Tot cred că nu poți deveni mai prost, dar apoi îți place să-mi dovedești contrariul.",
    "De ce e OK să fii idiot, dar nu e OK să-ți atrag atenția?",
    "Continuă să-ți dai ochii peste cap. Poate îți vei găsi creierul acolo, în spate.",
    "Tu ești motivul pentru care există instrucțiuni pe sticlele de șampon.",
    "Ți-aș explica, dar am lăsat dicționarul meu Engleză-Idiot acasă.",
    "Prostia nu e o crimă, așa că ești liber să pleci.",
    "Dacă ignoranța e fericire, tu trebuie să fii cea mai fericită persoană de pe planetă.",
    "Ai dreptul la părerea ta incorectă.",
    "Sunt alergic la prostie, așa că mă manifest prin sarcasm.",
    "Poate ar trebui să încerci să mănânci niște machiaj ca să fii frumoasă și pe dinăuntru.",
    "Când karma se întoarce să te lovească în față, vreau să fiu acolo dacă are nevoie de ajutor.",
    "Cine ți-a spus să fii tu însuți ți-a dat un sfat teribil.",
    "Nu te rușina de cine ești – asta e treaba părinților tăi.",
    "Secretele tale sunt mereu în siguranță cu mine. Nici măcar nu ascult când mi le spui.",
    "M-am gândit la tine azi. Mi-a amintit să duc gunoiul.",
    "Ești o bilă gri pe o brioșă curcubeu.",
    "Ești ca un nor. Când dispari, e o zi frumoasă.",
    "Arăți ca ceva ce a ieșit dintr-un slow cooker.",
    "Arăți ca poza «înainte». Cât timp trebuie să așteptăm să vedem «după» al tău?",
    "Ești atât de plin de rahat, încât și toaleta e geloasă.",
    "Ești ca soarele… te rog, depărtează-te 150 de milioane de kilometri de mine.",
    "Nu trebuie să-ți faci griji pentru mine. Fă-ți griji pentru sprâncenele tale.",
    "Nebunia ta se vede. Poate vrei să o ascunzi la loc.",
    "Să ai o zi frumoasă în altă parte.",
    "Dacă aș arunca un băț, ai pleca, nu-i așa?",
    "Credeam că am gripă, dar apoi mi-am dat seama că fața ta mă îmbolnăvise.",
    "Nu voi uita niciodată prima dată când ne-am întâlnit, dar voi continua să încerc.",
    "Mai ai mult până să ajungi mediocru.",
    "Probabil auzi des: «Hai să fim prieteni».",
    "E imposibil să te subestimezi.",
    "Dacă te simți jignit de părerea mea, ar trebui să le auzi pe cele pe care le păstrez pentru mine.",
    "Toată lumea aduce fericire într-o cameră. Eu aduc fericire când intru, iar tu aduci fericire când pleci.",
    "Dacă aș fi vrut să aud de la un fund, aș fi pârțâit.",
    "Am uitat că lumea se învârte în jurul tău. Scuzele mele! Cât de prost sunt.",
    "Fața ta e OK, dar ar trebui să-ți pui o pungă peste personalitatea aia.",
    "Dacă vrei să fii un deștept, trebuie să fii deștept. Altfel, ești doar un măgar.",
    "Fă-ți un favor și ignoră pe oricine îți spune să fii tu însuți. E o idee proastă în cazul tău.",
    "Îți sugerez să faci o mică introspecție. Poate vei găsi una.",
    "Nu sunt astronom, dar sunt destul de sigur că Pământul se învârte în jurul Soarelui și nu în jurul tău.",
    "Ești mai dezamăgitor decât un covrig fără sare.",
    "Oh, vorbești cu mine? Credeam că vorbești doar pe la spatele meu."
]


# ==========================================
# PROVOCARI PENTRU RULETA
# ==========================================

PROVOCARI_RULETA = [
    "Trebuie să scrii pe chat: «Sunt legenda eșecului!» 😂",
    "Trebuie să folosești 😂 în următoarele 5 mesaje.",
    "Trebuie să faci un compliment sincer unui membru ales de server.",
    "Trebuie să te autoproclami campion mondial la pierdut vremea. 🏆",
    "Trebuie să scrii o poezie de două versuri despre cartofi. 🥔",
    "Trebuie să recunoști cea mai amuzantă greșeală făcută într-un joc. 🎮",
    "Trebuie să spui cine de pe server ar supraviețui cel mai puțin într-o apocalipsă zombie. 🧟",
    "Trebuie să scrii o replică de agățat atât de proastă încât să provoace râsete. 😏",
    "Trebuie să te prezinți drept «Excelența Sa, Maestrul Eșecului» pentru următoarele 5 minute. 👑",
    "Trebuie să inventezi un slogan pentru Cotaiala. 🤖",
    "Trebuie să scrii «Tribunalul Cotaială are mereu dreptate». ⚖️",
    "Trebuie să alegi un membru și să-i dai un titlu regal amuzant. 👑",
    "Trebuie să descrii serverul în exact trei cuvinte.",
    "Trebuie să scrii o scuză absurdă pentru ultima ta înfrângere. 😂",
    "Trebuie să spui ce animal ar reprezenta cel mai bine personalitatea ta. 🦆",
    "Trebuie să scrii un discurs de victorie pentru o victorie pe care încă n-ai obținut-o. 🏆",
    "Trebuie să trimiți un emoji care îți descrie ziua și să explici de ce.",
    "Trebuie să recunoști cine e cel mai mare troll de pe server. 😈",
    "Trebuie să scrii un mesaj ca și cum ai fi un robot defect. 🤖",
    "Trebuie să declari oficial că un cartof are mai mult noroc decât tine. 🥔"
]


# ==========================================
# TRIBUNALUL COTAIALA
# ==========================================

ACUZATII = [
    "a furat ultima felie de pizza și a dat vina pe pisică 🍕",
    "a intrat pe server doar ca să creeze haos 😂",
    "a spus «vin imediat» și a dispărut trei ore ⏰",
    "a consumat tot norocul serverului și n-a lăsat nimic pentru ceilalți 🍀",
    "a dat rage quit după ce a pierdut o rundă 🎮",
    "a folosit Google înainte să răspundă la trivia 🧠",
    "a promis că se culcă devreme și a stat până dimineață 🌙",
    "a mâncat ultima prăjitură fără să întrebe pe nimeni 🍰",
    "a trimis un mesaj și apoi a zis că i-a fost spart contul 📱",
    "a provocat lagul serverului doar prin prezența sa 🥔",
    "a spus «știam eu» după ce toată lumea avea dreptate 🙄",
    "a râs la propria glumă înainte să o termine 🤡",
    "a furat locul altuia la coadă și a pretins că era acolo de la început 🧍",
    "a făcut pe expertul fără să citească instrucțiunile 📖",
    "a promis că nu mai face spam și a continuat după două minute 📢",
    "a avut o șansă să tacă și a ales să vorbească 🗣️",
    "a dat vina pe internet pentru o greșeală personală 📶",
    "a intrat într-un joc doar ca să le spună tuturor cum se joacă 🕹️",
    "a confundat încrederea în sine cu priceperea 😎",
    "a furat gloria altcuiva după o victorie 🏆",
    "a întârziat și apoi s-a plâns că ceilalți nu l-au așteptat ⌛",
    "a făcut o promisiune pe care nici el nu o credea 🤥",
    "a deschis frigiderul de cinci ori, sperând să apară mâncare nouă 🧊",
    "a dat sfaturi nesolicitate cu o încredere suspectă 🎓",
    "a pretins că citește regulile, dar a apăsat direct pe acceptă 📜"
]

CATEGORII_PEDEPSE = {
    "obraznice": {
        "nume": "😏 Obraznice",
        "pedepse": [
            "Trebuie să spună pe chat «Sunt o legendă… a eșecului!» 😂",
            "Trebuie să-și schimbe statusul într-o declarație de modestie pentru 10 minute.",
            "Trebuie să-i ofere câștigătorului un compliment sincer.",
            "Trebuie să scrie trei motive pentru care ceilalți sunt mai șmecheri.",
            "Trebuie să recunoască public cea mai amuzantă greșeală făcută recent.",
            "Trebuie să folosească un emoji ales de câștigător în următoarele 5 mesaje."
        ]
    },
    "rusinoase": {
        "nume": "🍑 Rușinoase",
        "pedepse": [
            "Trebuie să scrie «Am fost învins de propria mea genialitate».",
            "Trebuie să se autoproclame campion la pierdut vremea.",
            "Trebuie să compună o poezie de două versuri despre propria înfrângere.",
            "Trebuie să-și descrie stilul de joc în trei cuvinte, dintre care unul să fie «dezastru».",
            "Trebuie să declare că astăzi cartofii au IQ mai mare decât el.",
            "Trebuie să scrie un discurs de victorie pentru cel care l-a învins, deși a pierdut procesul."
        ]
    },
    "perversul": {
        "nume": "🔥 Perversul zilei",
        "pedepse": [
            "Trebuie să trimită un 😏 și să spună «Nu pun întrebări, nu dau explicații».",
            "Trebuie să-și recunoască cea mai nevinovată obsesie amuzantă.",
            "Trebuie să spună «Am o minte nevinovată… aproape!» 😂",
            "Trebuie să aleagă între 😏, 🔥 și 👀 și să explice alegerea în glumă.",
            "Trebuie să scrie o replică de agățat atât de proastă încât să provoace râsete."
        ]
    },
    "suprema": {
        "nume": "👑 Condamnare supremă",
        "pedepse": [
            "Este declarat oficial «Clovnul regal al serverului» până la următorul proces. 🤡",
            "Trebuie să compună un imn de două versuri dedicat Tribunalului Cotaială.",
            "Trebuie să accepte titlul de «Campion mondial la decizii proaste».",
            "Trebuie să scrie un mesaj de 3 propoziții în care își cere scuze cartofilor pentru comparațiile nedrepte.",
            "Trebuie să se prezinte drept «Excelența Sa, Maestrul Eșecului» pentru următoarele 10 minute.",
            "Trebuie să facă o declarație oficială: «Tribunalul a avut dreptate, eu am avut prea multă încredere»."
        ]
    }
}


def incarca_pedepse():
    try:
        with open(FISIER_PEDEPSE, "r", encoding="utf-8") as f:
            date = json.load(f)

        if not isinstance(date, dict):
            return {}

        rezultat = {}
        for categorie, lista in date.items():
            if categorie in CATEGORII_PEDEPSE and isinstance(lista, list):
                rezultat[categorie] = [
                    str(pedeapsa).strip()
                    for pedeapsa in lista
                    if isinstance(pedeapsa, str) and str(pedeapsa).strip()
                ]

        return rezultat

    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def salveaza_pedepse():
    temporar = FISIER_PEDEPSE + ".tmp"
    with open(temporar, "w", encoding="utf-8") as f:
        json.dump(PEDEPSE_PERSONALIZATE, f, ensure_ascii=False, indent=2)
    os.replace(temporar, FISIER_PEDEPSE)


PEDEPSE_PERSONALIZATE = incarca_pedepse()


def alege_pedeapsa(categorie):
    lista = (
        CATEGORII_PEDEPSE[categorie]["pedepse"]
        + PEDEPSE_PERSONALIZATE.get(categorie, [])
    )
    return random.choice(lista)


class TribunalCotaiala(discord.ui.View):
    def __init__(self, initiator_id, acuzat_id, acuzatie):
        super().__init__(timeout=60)
        self.initiator_id = initiator_id
        self.acuzat_id = acuzat_id
        self.acuzatie = acuzatie
        self.voturi = {}
        self.mesaj = None
        self.incheiat = False

    def numara_voturile(self):
        vinovati = sum(1 for vot in self.voturi.values() if vot is True)
        nevinovati = sum(1 for vot in self.voturi.values() if vot is False)
        return vinovati, nevinovati

    def creeaza_embed(self):
        vinovati, nevinovati = self.numara_voturile()
        embed = discord.Embed(
            title="⚖️ TRIBUNALUL COTAIALĂ",
            description=(
                f"**Acuzat:** <@{self.acuzat_id}>\n"
                f"**Acuzația:** {self.acuzatie}\n\n"
                "🗳️ Membrii serverului trebuie să decidă dacă persoana este vinovată sau nevinovată.\n\n"
                f"🔨 **Vinovat:** {vinovati} voturi\n"
                f"🛡️ **Nevinovat:** {nevinovati} voturi\n\n"
                "Ai 60 de secunde pentru a vota!"
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Acuzatul nu poate vota. Fiecare membru are un singur vot.")
        return embed

    async def actualizeaza_mesajul(self):
        if self.mesaj is not None:
            try:
                await self.mesaj.edit(embed=self.creeaza_embed(), view=self)
            except discord.HTTPException:
                pass

    async def voteaza(self, interaction, este_vinovat):
        if self.incheiat:
            await interaction.response.send_message(
                "Procesul s-a încheiat deja! ⚖️", ephemeral=True
            )
            return

        if interaction.user.id == self.acuzat_id:
            await interaction.response.send_message(
                "Acuzatul nu are voie să voteze în propriul proces! 😂",
                ephemeral=True
            )
            return

        if interaction.user.id in self.voturi:
            await interaction.response.send_message(
                "Ai votat deja! Nu poți vota de două ori. 🗳️",
                ephemeral=True
            )
            return

        self.voturi[interaction.user.id] = este_vinovat
        await interaction.response.send_message(
            "Ai votat **VINOVAT** 🔨!" if este_vinovat
            else "Ai votat **NEVINOVAT** 🛡️!",
            ephemeral=True
        )
        await self.actualizeaza_mesajul()

    @discord.ui.button(label="Vinovat 🔨", style=discord.ButtonStyle.danger)
    async def buton_vinovat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.voteaza(interaction, True)

    @discord.ui.button(label="Nevinovat 🛡️", style=discord.ButtonStyle.success)
    async def buton_nevinovat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.voteaza(interaction, False)

    async def on_timeout(self):
        if self.incheiat:
            return

        self.incheiat = True
        for item in self.children:
            item.disabled = True

        vinovati, nevinovati = self.numara_voturile()

        if vinovati > nevinovati:
            categorie = random.choice(list(CATEGORII_PEDEPSE.keys()))
            pedeapsa = alege_pedeapsa(categorie)
            verdict = discord.Embed(
                title="🔨 VERDICT: VINOVAT!",
                description=(
                    f"<@{self.acuzat_id}> a fost găsit **VINOVAT**!\n\n"
                    f"**Acuzația:** {self.acuzatie}\n\n"
                    f"🔨 Vinovat: **{vinovati}**\n"
                    f"🛡️ Nevinovat: **{nevinovati}**\n\n"
                    f"**Categoria pedepsei:** {CATEGORII_PEDEPSE[categorie]['nume']}\n"
                    f"**Sentința:** {pedeapsa}"
                ),
                color=discord.Color.red()
            )
        elif nevinovati > vinovati:
            verdict = discord.Embed(
                title="🛡️ VERDICT: NEVINOVAT!",
                description=(
                    f"<@{self.acuzat_id}> a fost declarat **NEVINOVAT**!\n\n"
                    f"**Acuzația:** {self.acuzatie}\n\n"
                    f"🔨 Vinovat: **{vinovati}**\n"
                    f"🛡️ Nevinovat: **{nevinovati}**\n\n"
                    "Acuzatul scapă de pedeapsă de data aceasta! 😎"
                ),
                color=discord.Color.green()
            )
        else:
            verdict = discord.Embed(
                title="⚖️ VERDICT: EGALITATE!",
                description=(
                    f"<@{self.acuzat_id}> scapă deocamdată!\n\n"
                    f"**Acuzația:** {self.acuzatie}\n\n"
                    f"🔨 Vinovat: **{vinovati}**\n"
                    f"🛡️ Nevinovat: **{nevinovati}**\n\n"
                    "La egalitate, Tribunalul nu poate condamna pe nimeni. 😂"
                ),
                color=discord.Color.gold()
            )

        if self.mesaj is not None:
            try:
                await self.mesaj.edit(embed=verdict, view=self)
            except discord.HTTPException:
                pass


# ==========================================
# SINCRONIZARE COMENZI
# ==========================================

@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    sincronizate = await bot.tree.sync()
    await ctx.send(f"✅ Am sincronizat {len(sincronizate)} comenzi slash!")


# ==========================================
# COMENZI EXISTENTE
# ==========================================

@bot.tree.command(name="ce_faci", description="Cotaiala iti raspunde!")
async def ce_faci(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice([
        "Respir si eu.", "Fac un part", "Ma scarpin la coaie", "Dau apa la draci, nu iti e sete?",
    "Fac posta toate rudele tale feminine", "Baie la mata.Tu cui ii faci baie?",
    "Te fac sa pierzi 10 sec. din viata citind asta", "Le raspund prostilor...dc? mai ai vreo intrebare stupida?",
    "Ce vrei ba?", "Mars!", "Nu vorbesc cu toti handicapatii!", "Alinee sugi pulaa!",
    "Dorinee sugi pulaa!", "Myshu suge pula!", "DuVale iesi acas'", "Dau in voi",
    "Dau in Myshu", "Dau in Duvale", "Dau in adi", "ii dau la muie lui adi",
            "ii bag un pumn Cristinei", "Eh,fac laba", "Va cotaiesc pe toti", "Ce sa fac,ma duc pe la ma-ta"
    ]))



@bot.tree.command(name="injura", description="Cotaiala alege o injuratura pentru un membru!")
@app_commands.describe(membru="Persoana pe care vrei sa o injuri")
async def injura(interaction: discord.Interaction, membru: discord.Member):
    await interaction.response.send_message(
        f"🤬 {interaction.user.mention} i-a spus lui/ei {membru.mention}:\n\n"
        f"**{random.choice(INJURATURI)}**"
    )


@bot.tree.command(name="palma", description="Da-i o palma virtuala cuiva!")
@app_commands.describe(membru="Persoana careia vrei sa-i dai o palma")
async def palma(interaction: discord.Interaction, membru: discord.Member):
    if membru.id == interaction.user.id:
        await interaction.response.send_message("Nu poti sa-ti dai singur o palma! 😂")
        return
    await interaction.response.send_message(
        f"👋 {interaction.user.mention} i-a dat o palma virtuala lui {membru.mention}!"
    )


@bot.tree.command(name="cat_de_prost", description="Procent de prostie, in gluma!")
@app_commands.describe(membru="Persoana pe care o verificam")
async def cat_de_prost(interaction: discord.Interaction, membru: discord.Member):
    await interaction.response.send_message(
        f"🧠 {membru.mention} este **{random.randint(0, 100)}%** de prost! 😂"
    )


@bot.tree.command(name="sunt_smecher", description="Verifica nivelul tau de smecherie!")
async def sunt_smecher(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"😎 {interaction.user.mention}, nivelul tau de smecherie este "
        f"**{random.randint(0, 100)}%**!"
    )


@bot.tree.command(name="baba_vanga", description="Cotaiala iti prezice viitorul!")
async def baba_vanga(interaction: discord.Interaction):
    predictii = [
        "Vei avea noroc in urmatoarele 24 de ore! 🍀",
        "Cineva iti va trimite un mesaj neasteptat! 📱",
        "Azi e o zi buna sa castigi la trivia! 🧠",
        "Vei gasi ceva ce credeai pierdut! 🔎",
        "Viitorul tau spune: mai dormi putin! 😂",
        "O surpriza te asteapta curand! 🎁"
    ]
    await interaction.response.send_message(f"🔮 **Baba Vanga spune:** {random.choice(predictii)}")


@bot.tree.command(name="roast", description="Cotaiala ia pe cineva la misto!")
@app_commands.describe(membru="Membrul pe care vrei sa-l prajesti")
async def roast(interaction: discord.Interaction, membru: discord.Member):
    if membru.id == interaction.user.id:
        await interaction.response.send_message(
            "🔥 Vrei sa te prajesti singur? Ai curaj, nu gluma! 😂"
        )
        return

    gluma = random.choice(ROASTURI)

    try:
        inregistreaza_roast(membru)
    except OSError:
        print("Nu am putut salva statistica roast.")

    embed = discord.Embed(
        title="🔥 COTAIALA ROAST 🔥",
        description=f"🎯 {membru.mention}, {gluma}",
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"Roast cerut de {interaction.user.display_name} 😂")
    await interaction.response.send_message(embed=embed)


# ==========================================
# /BATAIE
# ==========================================

@bot.tree.command(name="bataie", description="Simuleaza o bataie intre doi membri!")
@app_commands.describe(membru1="Primul luptator", membru2="Al doilea luptator")
async def bataie(
    interaction: discord.Interaction,
    membru1: discord.Member,
    membru2: discord.Member
):
    if membru1.id == membru2.id:
        await interaction.response.send_message(
            "😂 Ai nevoie de doi luptatori diferiti!", ephemeral=True
        )
        return

    if membru1.bot or membru2.bot:
        await interaction.response.send_message(
            "Roboții nu intră în ringul Cotaielii! 🤖",
            ephemeral=True
        )
        return

    castigator, invins = random.sample([membru1, membru2], 2)

    try:
        inregistreaza_victorie(castigator)
    except OSError:
        print("Nu am putut salva statistica bataie.")

    actiuni = [
        f"🥊 {membru1.mention} încearcă un croșeu, dar lovește aerul!",
        f"🦵 {membru2.mention} încearcă o lovitură spectaculoasă și aproape cade!",
        f"💨 {membru1.mention} face o eschivă de campion!",
        f"😂 {membru2.mention} se oprește să-și lege șireturile în mijlocul luptei!",
        f"💥 {membru1.mention} lansează atacul special: perna zburătoare!",
        f"🛡️ {membru2.mention} se apără cu o tigaie imaginară!",
        "🍌 O coajă de banană apare misterios în ring!",
        "📣 Arbitrul cere VAR, dar monitorul este stricat!"
    ]
    random.shuffle(actiuni)

    embed = discord.Embed(
        title="🥊 COTAIALA FIGHT NIGHT 🥊",
        description=(
            f"**Luptători:**\n🔴 {membru1.mention}\n🔵 {membru2.mention}\n\n"
            + "\n".join(actiuni[:4])
            + f"\n\n🏆 **CÂȘTIGĂTOR: {castigator.mention}!**\n"
            f"💀 {invins.mention} cere revanșă și un pachet de gheață."
        ),
        color=discord.Color.red()
    )
    embed.set_footer(
        text=f"Luptă organizată de {interaction.user.display_name} • Rezultat aleatoriu"
    )
    await interaction.response.send_message(embed=embed)


# ==========================================
# /CUPLU
# ==========================================

@bot.tree.command(name="cuplu", description="Afla compatibilitatea dintre doi membri!")
@app_commands.describe(membru1="Prima persoana", membru2="A doua persoana")
async def cuplu(
    interaction: discord.Interaction,
    membru1: discord.Member,
    membru2: discord.Member
):
    if membru1.bot or membru2.bot:
        await interaction.response.send_message(
            "🤖 Roboții nu pot avea o poveste de dragoste în testul Cotaielii!",
            ephemeral=True
        )
        return

    procent = random.randint(0, 100)

    if membru1.id == membru2.id:
        replica = "Te iubești pe tine însuți. Narcisism de nivel legendar! 😂"
    elif procent <= 10:
        replica = "💔 Mai bine rămâneți doar prieteni... dacă și asta merge!"
    elif procent <= 30:
        replica = "🥶 Scânteia romantică pare că s-a deconectat de la Wi-Fi."
    elif procent <= 50:
        replica = "🤔 Există potențial, dar trebuie să mai treceți câteva teste!"
    elif procent <= 75:
        replica = "💕 Nu-i rău deloc! Serverul începe să bârfească!"
    elif procent <= 90:
        replica = "🔥 Se pare că între voi chiar zboară scântei!"
    else:
        replica = "💍 Nunta e aproape! Cotaiala cere să fie naș!"

    try:
        inregistreaza_cuplu(membru1, membru2, procent)
    except OSError:
        print("Nu am putut salva statistica cuplu.")

    embed = discord.Embed(
        title="❤️ CUPLU COTAIALA ❤️",
        description=(
            f"💘 **{membru1.display_name} + {membru2.display_name}**\n\n"
            f"**Compatibilitate: {procent}%**\n\n{replica}"
        ),
        color=discord.Color.magenta()
    )
    embed.set_footer(
        text=f"Test cerut de {interaction.user.display_name} • Doar de distracție 😂"
    )
    await interaction.response.send_message(embed=embed)


# ==========================================
# /RULETA
# ==========================================

@bot.tree.command(name="ruleta", description="Alege un membru și îi dă o provocare!")
async def ruleta(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ruleta poate fi folosită doar pe un server! 🎰",
            ephemeral=True
        )
        return

    membri = [m for m in interaction.guild.members if not m.bot]
    if not membri:
        await interaction.response.send_message(
            "Nu am găsit membri eligibili pentru ruletă! 😢",
            ephemeral=True
        )
        return

    ales = random.choice(membri)
    provocare = random.choice(PROVOCARI_RULETA)

    embed = discord.Embed(
        title="🎰 RULETA COTAIALĂ 🎰",
        description=(
            f"Roata s-a oprit și ghinionistul este...\n\n"
            f"🎯 **{ales.mention}**\n\n"
            f"🎲 **Provocarea ta:**\n{provocare}"
        ),
        color=discord.Color.gold()
    )
    embed.set_footer(
        text=f"Ruletă pornită de {interaction.user.display_name} • Mult noroc 😂"
    )
    await interaction.response.send_message(embed=embed)


# ==========================================
# /TOP_BATAUSI
# ==========================================

@bot.tree.command(name="top_batausi", description="Clasamentul luptatorilor cu cele mai multe victorii!")
async def top_batausi(interaction: discord.Interaction):
    top = sorted(
        STATISTICI["batausi"].items(),
        key=lambda item: item[1].get("victorii", 0),
        reverse=True
    )[:10]

    if not top:
        await interaction.response.send_message(
            "🥊 Clasamentul este gol! Folosiți /bataie ca să înregistrați victorii."
        )
        return

    linii = []
    for pozitie, (_, date) in enumerate(top, start=1):
        nume = discord.utils.escape_markdown(date.get("nume", "Luptător"))
        linii.append(f"**{pozitie}.** {nume} — 🏆 **{date.get('victorii', 0)}** victorii")

    embed = discord.Embed(
        title="💀 TOP BĂTĂUȘI",
        description="\n".join(linii),
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)


# ==========================================
# /TOP_CUPLURI
# ==========================================

@bot.tree.command(name="top_cupluri", description="Cele mai compatibile cupluri de pe server!")
async def top_cupluri(interaction: discord.Interaction):
    top = sorted(
        STATISTICI["cupluri"].items(),
        key=lambda item: item[1].get("maxim", 0),
        reverse=True
    )[:10]

    if not top:
        await interaction.response.send_message(
            "❤️ Încă nu există cupluri în clasament! Folosiți /cuplu."
        )
        return

    linii = []
    for pozitie, (_, date) in enumerate(top, start=1):
        nume1 = discord.utils.escape_markdown(date.get("nume1", "Membru 1"))
        nume2 = discord.utils.escape_markdown(date.get("nume2", "Membru 2"))
        linii.append(
            f"**{pozitie}.** {nume1} + {nume2} — "
            f"💘 **{date.get('maxim', 0)}%**"
        )

    embed = discord.Embed(
        title="❤️ TOP CUPLURI COTAIALA",
        description="\n".join(linii),
        color=discord.Color.magenta()
    )
    embed.set_footer(text="Clasament după cel mai mare procent obținut.")
    await interaction.response.send_message(embed=embed)


# ==========================================
# /RULETA_TOTI
# ==========================================

@bot.tree.command(name="ruleta_toti", description="Ruleta alege un membru online!")
async def ruleta_toti(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Folosește ruleta pe un server!", ephemeral=True
        )
        return

    membri = [
        m for m in interaction.guild.members
        if not m.bot and m.status != discord.Status.offline
    ]

    if not membri:
        await interaction.response.send_message(
            "Nu am găsit membri online! Verifică dacă botul are acces la prezențe.",
            ephemeral=True
        )
        return

    ales = random.choice(membri)
    provocare = random.choice(PROVOCARI_RULETA)

    embed = discord.Embed(
        title="🎰 RULETA ONLINE",
        description=(
            f"Roata a decis! Ghinionistul este {ales.mention}!\n\n"
            f"🎲 **Provocarea:** {provocare}"
        ),
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Ruletă pornită de {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)


# ==========================================
# /REGELE
# ==========================================

@bot.tree.command(name="regele", description="Alege regele sau regina serverului pentru o oră!")
async def regele(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Comanda poate fi folosită doar pe un server!", ephemeral=True
        )
        return

    membri = [m for m in interaction.guild.members if not m.bot]
    if not membri:
        await interaction.response.send_message(
            "Nu am găsit membri pentru încoronare!", ephemeral=True
        )
        return

    ales = random.choice(membri)

    embed = discord.Embed(
        title="👑 ÎNCORONAREA COTAIALĂ 👑",
        description=(
            f"Toată lumea în genunchi!\n\n"
            f"👑 Astăzi, coroana îi revine lui **{ales.display_name}**!\n\n"
            f"{ales.mention} este declarat **REGELE/REGINA SERVERULUI** "
            "pentru următoarea oră! 🎉\n\n"
            "Profită de putere cât poți. După o oră, revii la statutul de muritor. 😂"
        ),
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Încoronare organizată de {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    mesaj = await interaction.original_response()

    async def expira_coroana():
        await asyncio.sleep(3600)
        try:
            await mesaj.reply(
                f"🔔 S-a terminat mandatul regal al lui {ales.mention}! "
                "Coroana se întoarce la Cotaiala. 😂"
            )
        except (discord.HTTPException, discord.NotFound):
            pass

    asyncio.create_task(expira_coroana())


# ==========================================
# /TOP_ROAST
# ==========================================

@bot.tree.command(name="top_roast", description="Clasamentul membrilor prajiti cel mai des!")
async def top_roast(interaction: discord.Interaction):
    top = sorted(
        STATISTICI["roast"].items(),
        key=lambda item: item[1].get("numar", 0),
        reverse=True
    )[:10]

    if not top:
        await interaction.response.send_message(
            "🔥 Încă n-a fost prăjit nimeni! Folosiți /roast ca să înceapă dezastrul."
        )
        return

    linii = []
    for pozitie, (_, date) in enumerate(top, start=1):
        nume = discord.utils.escape_markdown(date.get("nume", "Membru"))
        linii.append(f"**{pozitie}.** {nume} — 🔥 **{date.get('numar', 0)}** roast-uri")

    embed = discord.Embed(
        title="🏆 TOP ROAST COTAIALA",
        description="\n".join(linii),
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)


# ==========================================
# /COMENZI

# ==========================================
# COMENZI MUIE COTAIALA
# ==========================================

FISIER_STATISTICI_MUI = "statistici_muie.json"


def incarca_statistici_muie():
    try:
        with open(FISIER_STATISTICI_MUI, "r", encoding="utf-8") as f:
            date = json.load(f)
        if isinstance(date, dict) and isinstance(date.get("membri"), dict):
            return date
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {"membri": {}}


STATISTICI_MUI = incarca_statistici_muie()


def salveaza_statistici_muie():
    temporar = FISIER_STATISTICI_MUI + ".tmp"
    with open(temporar, "w", encoding="utf-8") as f:
        json.dump(STATISTICI_MUI, f, ensure_ascii=False, indent=2)
    os.replace(temporar, FISIER_STATISTICI_MUI)


def obtine_statistici_muie(membru):
    uid = str(membru.id)
    date = STATISTICI_MUI["membri"].setdefault(uid, {
        "nume": membru.display_name,
        "date": 0,
        "primite": 0
    })
    date["nume"] = membru.display_name
    date.setdefault("date", 0)
    date.setdefault("primite", 0)
    return date


def inregistreaza_muie(expeditor, destinatar):
    date_expeditor = obtine_statistici_muie(expeditor)
    date_destinatar = obtine_statistici_muie(destinatar)
    date_expeditor["date"] += 1
    date_destinatar["primite"] += 1
    salveaza_statistici_muie()


def inregistreaza_muie_primita(membru):
    obtine_statistici_muie(membru)["primite"] += 1
    salveaza_statistici_muie()


def verifica_tinta(interaction, membru):
    if interaction.guild is None:
        return "Comanda poate fi folosită doar pe un server!"
    if membru.bot:
        return "Boții nu participă la statisticile Cotaielii! 🤖"
    if membru.id == interaction.user.id:
        return "Nu poți folosi comanda asupra ta! 😂"
    return None


@bot.tree.command(name="dick", description="Vezi dimensiunea ta virtuală!")
async def dick(interaction: discord.Interaction):
    date = obtine_statistici_muie(interaction.user)
    centimetri = min(30, 5 + date["date"])

    await interaction.response.send_message(
        f"🍆 {interaction.user.mention}, ai **{centimetri} cm** virtuali!\n"
        f"😈 Muie date cu succes: **{date['date']}**"
    )


@bot.tree.command(name="muie", description="Oferă-i cuiva o muie virtuală!")
@app_commands.describe(membru="Persoana aleasă")
async def muie(interaction: discord.Interaction, membru: discord.Member):
    eroare = verifica_tinta(interaction, membru)
    if eroare:
        await interaction.response.send_message(eroare, ephemeral=True)
        return

    try:
        inregistreaza_muie(interaction.user, membru)
    except OSError:
        await interaction.response.send_message(
            "Nu am putut salva statisticile. Încearcă din nou!",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"😈 {interaction.user.mention} i-a oferit o muie virtuală lui "
        f"{membru.mention}!\n📊 Muia a fost înregistrată în statistici!"
    )


@bot.tree.command(
    name="megamuie",
    description="Încearcă o megamuie cu 20% șanse de reușită!"
)
@app_commands.describe(membru="Persoana aleasă")
async def megamuie(interaction: discord.Interaction, membru: discord.Member):
    eroare = verifica_tinta(interaction, membru)
    if eroare:
        await interaction.response.send_message(eroare, ephemeral=True)
        return

    reusita = random.randint(1, 100) <= 20

    try:
        if reusita:
            inregistreaza_muie(interaction.user, membru)
        else:
            inregistreaza_muie_primita(interaction.user)
    except OSError:
        await interaction.response.send_message(
            "Nu am putut salva statisticile. Încearcă din nou!",
            ephemeral=True
        )
        return

    if reusita:
        await interaction.response.send_message(
            f"💥 MEGAMUIE REUȘITĂ!\n{interaction.user.mention} l-a prins "
            f"pe {membru.mention} într-o megamuie legendară! 😂"
        )
    else:
        await interaction.response.send_message(
            f"💀 MEGAMUIE EȘUATĂ!\n{interaction.user.mention} a ratat "
            f"și a primit propria muie! Aleluia! 😂"
        )


@bot.tree.command(name="topmuie", description="Vezi top 5 muie date și primite!")
async def topmuie(interaction: discord.Interaction):
    membri = STATISTICI_MUI["membri"]

    top_date = sorted(
        membri.items(),
        key=lambda item: item[1].get("date", 0),
        reverse=True
    )[:5]

    top_primite = sorted(
        membri.items(),
        key=lambda item: item[1].get("primite", 0),
        reverse=True
    )[:5]

    linii_date = [
        f"**{i}.** {discord.utils.escape_markdown(d.get('nume', 'Membru'))}"
        f" — **{d.get('date', 0)}**"
        for i, (_, d) in enumerate(top_date, 1)
    ]

    linii_primite = [
        f"**{i}.** {discord.utils.escape_markdown(d.get('nume', 'Membru'))}"
        f" — **{d.get('primite', 0)}**"
        for i, (_, d) in enumerate(top_primite, 1)
    ]

    embed = discord.Embed(
        title="🏆 TOP MUIE COTAIALA",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="😈 Cele mai multe date",
        value="\n".join(linii_date) if linii_date else "Încă nu există statistici.",
        inline=False
    )
    embed.add_field(
        name="💀 Cele mai multe primite",
        value="\n".join(linii_primite) if linii_primite else "Încă nu există statistici.",
        inline=False
    )
    await interaction.response.send_message(embed=embed)

# ==========================================

@bot.tree.command(name="comenzi", description="Vezi toate comenzile Cotaielii!")
async def comenzi(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 COMENZILE COTAIELII",
        description="Alege-ți arma și începe distracția! 😂",
        color=discord.Color.blurple()
    )

    comenzi_lista = [
        ("/ce_faci", "Vorbește cu Cotaiala."),
        ("/injura", "Alege un membru și Cotaiala îi spune o replică din lista ta."),
        ("/palma", "Dă o palmă virtuală unui membru."),
        ("/cat_de_prost", "Află procentul de prostie, în glumă."),
        ("/sunt_smecher", "Află nivelul tău de șmecherie."),
        ("/baba_vanga", "Primește o predicție."),
        ("/roast", "Prăjește un membru cu o replică aleatorie."),
        ("/bataie", "Simulează o bătaie între doi membri."),
        ("/cuplu", "Calculează compatibilitatea dintre doi membri."),
        ("/ruleta", "Alege un membru și îi atribuie o provocare."),
        ("/top_batausi", "Vezi primii 10 luptători după victorii."),
        ("/top_cupluri", "Vezi cele mai compatibile perechi."),
        ("/ruleta_toti", "Alege un membru online și îi dă o provocare."),
        ("/regele", "Alege regele sau regina serverului pentru o oră."),
        ("/top_roast", "Vezi membrii prăjiți cel mai des."),
        ("/trivia", "Primește o întrebare trivia la alegere."),
        ("/clasament", "Vezi primii 10 jucători trivia."),
        ("/proces", "Deschide un proces la Tribunalul Cotaială."),
        ("/adauga_pedeapsa", "Administratorii pot adăuga pedepse personalizate."),
        ("Trivia automată", "O întrebare nouă la fiecare 2 minute.")
    ]

    for nume, descriere in comenzi_lista:
        embed.add_field(name=nume, value=descriere, inline=False)

    await interaction.response.send_message(embed=embed)


# ==========================================
# /PROCES
# ==========================================

@bot.tree.command(name="proces", description="Trimite un membru în fața Tribunalului Cotaială!")
@app_commands.describe(membru="Membrul acuzat în proces")
async def proces(interaction: discord.Interaction, membru: discord.Member):
    if membru.bot:
        await interaction.response.send_message(
            "Roboții nu pot fi judecați la Tribunalul Cotaială! 🤖",
            ephemeral=True
        )
        return

    if membru.id == interaction.user.id:
        await interaction.response.send_message(
            "Nu te poți da singur în judecată! 😂", ephemeral=True
        )
        return

    acuzatie = random.choice(ACUZATII)
    view = TribunalCotaiala(interaction.user.id, membru.id, acuzatie)

    await interaction.response.send_message(
        content=f"📢 Atenție, server! {membru.mention} este judecat!",
        embed=view.creeaza_embed(),
        view=view
    )
    view.mesaj = await interaction.original_response()


# ==========================================
# /ADAUGA_PEDEAPSA
# ==========================================

@bot.tree.command(
    name="adauga_pedeapsa",
    description="Adaugă o pedeapsă personalizată pentru Tribunalul Cotaială."
)
@app_commands.describe(
    categorie="Categoria în care va fi adăugată pedeapsa",
    pedeapsa="Textul pedepsei care va putea fi aleasă de tribunal"
)
@app_commands.choices(categorie=[
    app_commands.Choice(name="😏 Obraznice", value="obraznice"),
    app_commands.Choice(name="🍑 Rușinoase", value="rusinoase"),
    app_commands.Choice(name="🔥 Perversul zilei", value="perversul"),
    app_commands.Choice(name="👑 Condamnare supremă", value="suprema")
])
@app_commands.default_permissions(administrator=True)
async def adauga_pedeapsa(
    interaction: discord.Interaction,
    categorie: app_commands.Choice[str],
    pedeapsa: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Doar administratorii serverului pot adăuga pedepse! 🔒",
            ephemeral=True
        )
        return

    pedeapsa = pedeapsa.strip()

    if len(pedeapsa) < 5:
        await interaction.response.send_message(
            "Pedeapsa este prea scurtă. Scrie cel puțin 5 caractere.",
            ephemeral=True
        )
        return

    if len(pedeapsa) > 500:
        await interaction.response.send_message(
            "Pedeapsa este prea lungă. Limita este de 500 de caractere.",
            ephemeral=True
        )
        return

    cheia = categorie.value
    PEDEPSE_PERSONALIZATE.setdefault(cheia, []).append(pedeapsa)

    try:
        salveaza_pedepse()
    except OSError:
        PEDEPSE_PERSONALIZATE[cheia].pop()
        await interaction.response.send_message(
            "Nu am putut salva pedeapsa. Verifică permisiunile fișierelor.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"✅ Pedeapsa a fost adăugată în categoria "
        f"**{CATEGORII_PEDEPSE[cheia]['nume']}**!\n"
        f"**Pedeapsă:** {pedeapsa}",
        ephemeral=True
    )


# ==========================================
# INTREBARI TRIVIA
# ==========================================

TRIVIA_INTREBARI = {
    "Cultură generală": [
        {"q": "Care este capitala României?", "o": ["Cluj-Napoca", "București", "Iași", "Craiova"], "a": 1},
        {"q": "Câte laturi are un hexagon?", "o": ["5", "6", "7", "8"], "a": 1},
        {"q": "Care este cea mai mare planetă?", "o": ["Marte", "Saturn", "Jupiter", "Venus"], "a": 2},
        {"q": "Ce gaz respiră oamenii?", "o": ["Oxigen", "Heliu", "Hidrogen", "Neon"], "a": 0},
        {"q": "Câte minute are o oră?", "o": ["30", "45", "60", "100"], "a": 2},
    ],
    "Fotbal": [
        {"q": "Câți jucători are o echipă pe teren?", "o": ["9", "10", "11", "12"], "a": 2},
        {"q": "La câți ani are loc în mod normal Campionatul Mondial?", "o": ["2", "3", "4", "5"], "a": 2},
        {"q": "Cine a câștigat Campionatul Mondial din 2022?", "o": ["Franța", "Argentina", "Brazilia", "Croația"], "a": 1},
        {"q": "Ce cartonaș înseamnă eliminarea?", "o": ["Verde", "Albastru", "Galben", "Roșu"], "a": 3},
        {"q": "Cât durează timpul regulamentar al unui meci?", "o": ["60 min", "80 min", "90 min", "100 min"], "a": 2},
    ],
    "Jocuri video": [
        {"q": "Cine dezvoltă seria Grand Theft Auto?", "o": ["Rockstar Games", "Nintendo", "Mojang", "Valve"], "a": 0},
        {"q": "Din ce se face masa de lucru în Minecraft?", "o": ["Scânduri de lemn", "Diamante", "Sticlă", "Lână"], "a": 0},
        {"q": "Cum se numește eroul principal din The Legend of Zelda?", "o": ["Zelda", "Link", "Mario", "Kirby"], "a": 1},
        {"q": "Ce tip de joc este Counter-Strike?", "o": ["Fotbal", "Shooter", "Curse auto", "Simulare"], "a": 1},
        {"q": "Ce companie a creat PlayStation?", "o": ["Microsoft", "Sony", "Sega", "Apple"], "a": 1},
    ],
    "Filme și seriale": [
        {"q": "Cum se numește școala de magie din Harry Potter?", "o": ["Narnia", "Hogwarts", "Camelot", "Nevermore"], "a": 1},
        {"q": "În ce serial apare Walter White?", "o": ["Lost", "Breaking Bad", "The Boys", "Friends"], "a": 1},
        {"q": "Ce animal este Simba?", "o": ["Tigru", "Leu", "Leopard", "Lup"], "a": 1},
        {"q": "Ce familie este asociată cu Jon Snow în Game of Thrones?", "o": ["Lannister", "Stark", "Targaryen", "Baratheon"], "a": 1},
        {"q": "În ce serie apare Darth Vader?", "o": ["Star Wars", "Star Trek", "Matrix", "Avatar"], "a": 0},
    ],
    "Muzică": [
        {"q": "Câte clape are un pian standard?", "o": ["66", "76", "88", "100"], "a": 2},
        {"q": "Ce instrument are de obicei șase corzi?", "o": ["Flaut", "Chitară", "Trompetă", "Tobă"], "a": 1},
        {"q": "Din ce țară provine formația ABBA?", "o": ["Norvegia", "Suedia", "Germania", "Italia"], "a": 1},
        {"q": "Care este un instrument de percuție?", "o": ["Tobă", "Vioară", "Flaut", "Harpă"], "a": 0},
        {"q": "Cine cântă la pian?", "o": ["Pianistul", "Violonistul", "Toboșarul", "Dirijorul"], "a": 0},
    ],
    "Întrebări amuzante": [
        {"q": "Dacă un cocoș face un ou pe gard, unde cade?", "o": ["La stânga", "La dreapta", "În față", "Cocoșul nu face ouă"], "a": 3},
        {"q": "Ce se udă în timp ce usucă?", "o": ["Prosopul", "Focul", "Umbrela", "Radiatorul"], "a": 0},
        {"q": "Ce are dinți, dar nu poate mușca?", "o": ["Crocodilul", "Pieptenele", "Câinele", "Rechinul"], "a": 1},
        {"q": "Ce poți prinde, dar nu poți arunca?", "o": ["O minge", "O răceală", "O piatră", "Un băț"], "a": 1},
        {"q": "Ce urcă și coboară, dar rămâne în același loc?", "o": ["Un lift", "O scară", "Un leagăn", "Un balon"], "a": 1},
    ],
    "Istorie și geografie": [
        {"q": "În ce an a avut loc Marea Unire?", "o": ["1848", "1877", "1918", "1945"], "a": 2},
        {"q": "Care este cel mai mare ocean?", "o": ["Atlantic", "Indian", "Arctic", "Pacific"], "a": 3},
        {"q": "Cine a construit piramidele de la Giza?", "o": ["Romanii", "Egiptenii antici", "Vikingii", "Grecii"], "a": 1},
        {"q": "Care este capitala Franței?", "o": ["Lyon", "Marsilia", "Paris", "Nisa"], "a": 2},
        {"q": "Pe ce continent se află România?", "o": ["Asia", "Europa", "Africa", "America de Sud"], "a": 1},
    ],
}


# ==========================================
# SALVARE SI INCARCARE PUNCTUAJE TRIVIA
# ==========================================

def incarca_scoruri():
    try:
        with open(FISIER_SCORURI, "r", encoding="utf-8") as f:
            date = json.load(f)
            return date if isinstance(date, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def salveaza_scoruri():
    temporar = FISIER_SCORURI + ".tmp"
    with open(temporar, "w", encoding="utf-8") as f:
        json.dump(SCORURI_TRIVIA, f, ensure_ascii=False, indent=2)
    os.replace(temporar, FISIER_SCORURI)


SCORURI_TRIVIA = incarca_scoruri()


# ==========================================
# BUTOANE TRIVIA
# ==========================================

class ButonTrivia(discord.ui.View):
    def __init__(self, intrebare):
        super().__init__(timeout=45)
        self.intrebare = intrebare
        self.au_raspuns = set()
        self.mesaj = None

        for index, varianta in enumerate(intrebare["o"]):
            buton = discord.ui.Button(
                label=f"{chr(65 + index)}. {varianta}",
                style=discord.ButtonStyle.primary
            )
            buton.callback = self.creeaza_callback(index)
            self.add_item(buton)

    def creeaza_callback(self, index):
        async def callback(interaction: discord.Interaction):
            uid = str(interaction.user.id)

            if uid in self.au_raspuns:
                await interaction.response.send_message(
                    "Ai răspuns deja la întrebarea aceasta! 😁",
                    ephemeral=True
                )
                return

            self.au_raspuns.add(uid)

            if index == self.intrebare["a"]:
                intrare = SCORURI_TRIVIA.get(uid, {})
                SCORURI_TRIVIA[uid] = {
                    "nume": interaction.user.display_name,
                    "puncte": intrare.get("puncte", 0) + 1
                }

                try:
                    salveaza_scoruri()
                except OSError:
                    SCORURI_TRIVIA[uid]["puncte"] -= 1
                    await interaction.response.send_message(
                        "Nu am putut salva punctajul. Verifică permisiunile fișierului.",
                        ephemeral=True
                    )
                    return

                await interaction.response.send_message(
                    "✅ Corect! Ai câștigat un punct!", ephemeral=True
                )
            else:
                corect = self.intrebare["o"][self.intrebare["a"]]
                await interaction.response.send_message(
                    f"❌ Greșit! Răspunsul corect era **{corect}**.",
                    ephemeral=True
                )

        return callback

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.mesaj:
            try:
                await self.mesaj.edit(view=self)
            except discord.HTTPException:
                pass


# ==========================================
# /TRIVIA
# ==========================================

@bot.tree.command(name="trivia", description="Răspunde la o întrebare și câștigă puncte!")
@app_commands.choices(categorie=[
    app_commands.Choice(name="Cultură generală", value="Cultură generală"),
    app_commands.Choice(name="Fotbal", value="Fotbal"),
    app_commands.Choice(name="Jocuri video", value="Jocuri video"),
    app_commands.Choice(name="Filme și seriale", value="Filme și seriale"),
    app_commands.Choice(name="Muzică", value="Muzică"),
    app_commands.Choice(name="Întrebări amuzante", value="Întrebări amuzante"),
    app_commands.Choice(name="Istorie și geografie", value="Istorie și geografie"),
])
async def trivia(interaction: discord.Interaction, categorie: app_commands.Choice[str]):
    intrebare = random.choice(TRIVIA_INTREBARI[categorie.value])
    embed = discord.Embed(
        title=f"🧠 TRIVIA — {categorie.value}",
        description=f"**{intrebare['q']}**",
        color=discord.Color.gold()
    )
    embed.set_footer(text="Ai 45 de secunde să răspunzi!")

    view = ButonTrivia(intrebare)
    await interaction.response.send_message(embed=embed, view=view)
    view.mesaj = await interaction.original_response()


# ==========================================
# TRIVIA AUTOMATA - DIN 2 IN 2 MINUTE
# ==========================================

@tasks.loop(minutes=2)
async def trivia_automat():
    try:
        canal = bot.get_channel(CANAL_TRIVIA_ID)
        if canal is None:
            canal = await bot.fetch_channel(CANAL_TRIVIA_ID)

        categorie = random.choice(list(TRIVIA_INTREBARI.keys()))
        intrebare = random.choice(TRIVIA_INTREBARI[categorie])

        embed = discord.Embed(
            title=f"🧠 TRIVIA AUTOMATĂ — {categorie}",
            description=f"**{intrebare['q']}**",
            color=discord.Color.gold()
        )
        embed.set_footer(
            text="Ai 45 de secunde să răspunzi! Răspunsul corect îți aduce un punct."
        )

        view = ButonTrivia(intrebare)
        view.mesaj = await canal.send(embed=embed, view=view)

    except discord.NotFound:
        print("EROARE: ID-ul canalului nu există. Verifică CANAL_TRIVIA_ID.")
    except discord.Forbidden:
        print("EROARE: Cotaiala nu are permisiunea să vadă sau să scrie în canal.")
    except discord.HTTPException as eroare:
        print(f"Eroare Discord la trimiterea trivia: {eroare}")


@trivia_automat.before_loop
async def inainte_de_trivia_automata():
    await bot.wait_until_ready()


# ==========================================
# /CLASAMENT TRIVIA
# ==========================================

@bot.tree.command(name="clasament", description="Vezi primii 10 jucători la trivia!")
async def clasament(interaction: discord.Interaction):
    if not SCORURI_TRIVIA:
        await interaction.response.send_message(
            "🏆 Clasamentul este gol! Răspunde corect la trivia ca să câștigi primul punct."
        )
        return

    top = sorted(
        SCORURI_TRIVIA.items(),
        key=lambda item: item[1].get("puncte", 0),
        reverse=True
    )[:10]

    linii = []
    for pozitie, (uid, date) in enumerate(top, start=1):
        nume = discord.utils.escape_markdown(date.get("nume", "Jucător"))
        puncte = date.get("puncte", 0)
        linii.append(f"**{pozitie}.** {nume} — **{puncte}** puncte")

    embed = discord.Embed(
        title="🏆 CLASAMENT COTAIALA",
        description="\n".join(linii),
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)


# ==========================================

# ==========================================
# /UMILINTA - TRIBUNALUL COTAIALA
# ==========================================

UMILINTE = [
    "Ai atâta minte încât și un cartof îți poate da lecții.",
    "Ești motivul pentru care instrucțiunile au și poze.",
    "Dacă prostia ar produce curent, ai alimenta tot satul.",
    "Ai două neuroni și ambii sunt în concediu.",
    "Când te-ai născut, barza a cerut retur.",
    "Ai IQ-ul unei uși, dar măcar ușa se deschide.",
    "Ești dovada că se poate trăi și fără actualizări.",
    "Dacă tăceai, păreai misterios. Acum știm.",
    "Ai mintea atât de odihnită încât doarme și când ești treaz.",
    "Când gândești, se aude ventilatorul, dar nu pornește nimic.",
    "Ai personalitatea unui bon fiscal ud.",
    "Ești ca Wi-Fi-ul gratuit: promiți mult și nu funcționezi.",
    "Ai fața unui om care a pierdut o ceartă cu oglinda.",
    "Dacă erai mai lent, mergeai înapoi în timp.",
    "Ai atâta logică precum un scaun cu trei picioare.",
    "Când intri într-o cameră, și conversația cere să iasă.",
    "Ești versiunea demo a unui om funcțional.",
    "Ai mai multe probleme decât soluții într-un manual de matematică.",
    "Dacă erai o aplicație, te dezinstala și telefonul.",
    "Ai carisma unei facturi la întreținere.",
    "Creierul tău e în modul avion și parola s-a pierdut.",
    "Ai atâta noroc încât și ghinionul te evită de rușine.",
    "Ești ca o actualizare Windows: apari când nu te cheamă nimeni.",
    "Ai o minte sclipitoare. Păcat că e stinsă.",
    "Dacă prostia era sport olimpic, veneai pe locul doi. Nici primul nu-l nimereai.",
    "Ai energia unui telefon la 1% fără încărcător.",
    "Ești dovada că natura mai face și experimente nereușite.",
    "Ai o prezență atât de puternică încât nimeni n-a observat-o.",
    "Ai argumente atât de bune încât nici tu nu le crezi.",
    "Ești genul de persoană care pierde la piatră-hârtie-foarfecă singură.",
    "Ai nevoie de GPS ca să-ți găsești ideile.",
    "Ai atâta stil încât manechinele se îmbracă singure când te văd.",
    "Ești ca o alarmă stricată: deranjezi fără niciun rezultat.",
    "Dacă răbdarea era bani, tot ai fi dator.",
    "Ai talentul rar de a strica și lucrurile deja stricate.",
    "Ești o surpriză, dar genul pe care nimeni nu-l vrea.",
    "Ai atâta autoritate cât are o telecomandă fără baterii.",
    "Când dai sfaturi, până și Google își închide rezultatele.",
    "Ești un mister. Mai ales pentru oamenii care încearcă să te înțeleagă.",
    "Ai mintea ca un browser cu 100 de taburi și toate blocate.",
    "Ești mai util decât o umbrelă făcută din hârtie. Adică deloc.",
    "Ai o reputație atât de bună încât nici zvonurile nu te mai pomenesc.",
    "Dacă erai condiment, erai făină.",
    "Ai farmecul unui formular de completat în trei exemplare.",
    "Ești genul care citește termenii și tot apasă greșit.",
    "Ai atâtea idei bune încât încă așteptăm prima.",
    "Ești ca o imprimantă: mult zgomot și niciun rezultat.",
    "Ai încrederea unui rege și realizările unui cartof.",
    "Ești atât de previzibil încât și surprizele se plictisesc.",
    "Ai o gândire profundă. Din păcate, doar în pauza de masă.",
    "Dacă bunul-simț era abonament, al tău a expirat.",
    "Ai o minte deschisă. Curentul trece prin ea fără probleme.",
    "Ești ca o parolă uitată: toată lumea vrea să scape de tine.",
    "Ai mai multe scuze decât realizări.",
    "Ești singurul care poate pierde o discuție cu propriul ecou.",
    "Ai reacții rapide, mai ales când trebuie să fugi de responsabilitate.",
    "Ești ca un spoiler: strici totul când apari.",
    "Ai atâta precizie încât nimerești greșit și când ai dreptate.",
    "Ești genul care pune întrebări la care nici întrebarea nu vrea răspuns.",
    "Ai o gândire originală. Nimeni n-a mai gândit atât de greșit.",
    "Dacă seriozitatea era obligatorie, tu primeai scutire medicală.",
    "Ai atâta energie pozitivă încât până și bateria se descarcă lângă tine.",
    "Ești o lecție de viață pe care nimeni nu vrea s-o învețe.",
    "Ai memoria unui peștișor și pretențiile unui elefant.",
    "Ești ca un meniu fără prețuri: nimeni nu știe ce oferi.",
    "Ai o strategie impecabilă: greșești, apoi repeți.",
    "Ești campion la complicat lucruri simple.",
    "Ai o minte atât de liniștită încât nici gândurile nu te vizitează.",
    "Ești genul care se rătăcește urmând indicatoarele.",
    "Ai atâta inspirație încât până și aerul se simte irosit.",
    "Ești ca o șosetă desperecheată: nimeni nu știe ce cauți acolo.",
    "Ai un talent special: faci tăcerea să pară o idee excelentă.",
    "Dacă ideile ar fi monede, tu ai avea pușculița goală.",
    "Ești mai confuz decât un tutorial tradus automat.",
    "Ai o logică aparte. Aparte de realitate.",
    "Ești ca o notificare de spam: nimeni nu te-a cerut.",
    "Ai atâta eleganță cât are un frigider pe scări.",
    "Ești dovada că nu orice conexiune duce undeva.",
    "Ai un plan de rezervă pentru fiecare plan care n-a funcționat.",
    "Ești atât de discret încât nici greșelile tale nu te mai recunosc.",
    "Ai reflexe excelente când trebuie să schimbi subiectul.",
    "Ești genul care caută ochelarii în timp ce îi poartă.",
    "Ai mai mult tupeu decât conținut.",
    "Ești ca o pizza fără blat: ideea era bună, execuția nu.",
    "Ai atâta prestanță încât și scaunul pe care stai pare mai important.",
    "Ești un proiect început și abandonat de univers.",
    "Ai talentul de a transforma cinci minute în două ore pierdute.",
    "Ești ca un bec ars: ocupi loc, dar nu luminezi.",
    "Ai o reputație atât de solidă încât nimeni nu se bazează pe tine.",
    "Ești genul care apasă pe «Anulează» și întreabă de ce nu merge.",
    "Ai mai multă încredere decât experiență.",
    "Ești ca o hartă fără legendă: greu de descifrat și rar de folos.",
    "Ai o minte de colecție. Nimeni nu știe ce colecționează.",
    "Ești campion mondial la a fi pe lângă subiect.",
    "Ai un simț al orientării care te duce exact unde nu trebuie.",
    "Ești ca o ușă automată care nu se deschide când te apropii.",
    "Ai atâta profunzime încât o baltă pare ocean lângă tine.",
    "Ești genul care face un grup să aprecieze butonul de mute.",
    "Ai mai multe versiuni ale poveștii decât fapte.",
    "Ești un argument viu pentru a citi instrucțiunile.",
    "Ai o minte atât de rapidă încât ideile ajung mâine.",
    "Ești ca un update care repară o problemă și creează alte zece.",
    "Ai o abilitate impresionantă de a rata esențialul.",
    "Ești o legendă. Mai ales în poveștile despre ce să nu faci.",
    "Ai atâta organizare încât haosul îți cere sfaturi.",
    "Ești dovada că uneori tăcerea chiar e de aur.",
    "Ai ajuns la tribunal. Nu pentru ce ai făcut, ci pentru ce urmează să spui."
]


@bot.tree.command(name="umilinta", description="Primește un verdict de la Tribunalul Cotaiala!")
@app_commands.describe(membru="Membrul pe care vrei să-l umilești")
async def umilinta(
    interaction: discord.Interaction,
    membru: discord.Member = None
):
    tinta = membru if membru is not None else interaction.user

    if tinta.bot:
        await interaction.response.send_message(
            "🤖 Boții nu pot fi judecați de Tribunalul Cotaiala!",
            ephemeral=True
        )
        return

    verdict = random.choice(UMILINTE)

    embed = discord.Embed(
        title="💀 TRIBUNALUL UMILINȚEI COTAIALA 💀",
        description=f"⚖️ **Persoana judecată:** {tinta.mention}\n\n{verdict}",
        color=discord.Color.dark_red()
    )
    embed.set_footer(
        text=f"Umilință solicitată de {interaction.user.display_name} • Fără drept de apel 😂"
    )

    await interaction.response.send_message(embed=embed)

    embed = discord.Embed(
        title="💀 TRIBUNALUL UMILINȚEI COTAIALA 💀",
        description=f"⚖️ **Persoana judecată:** {tinta.mention}\n\n{verdict}",
        color=discord.Color.dark_red()
    )
    embed.set_footer(
        text=f"Umilință solicitată de {interaction.user.display_name} • Fără drept de apel 😂"
    )

    await interaction.response.send_message(embed=embed)

# ==========================================
# CITIRE SI POSTARE STIRI DIGISPORT (AUTOMAT LA 15 MINUTE)
# ==========================================

from bs4 import BeautifulSoup
import aiohttp

URL_STIRI_DIGISPORT = "https://digisport.ro"
CANAL_SPORT_ID = None  # Se va seta automat prin comanda /sport
ULTIMELE_STIRI_TRIMISE = set()  # Memorează titlurile ca să nu pună dubluri


async def citeste_stiri_digisport():
    stiri = []
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        async with aiohttp.ClientSession(timeout=timeout) as sesiune:
            async with sesiune.get(URL_STIRI_DIGISPORT, headers=headers) as raspuns:
                if raspuns.status != 200:
                    print(f"Eroare DigiSport: HTTP {raspuns.status}")
                    return stiri

                html = await raspuns.text()

        soup = BeautifulSoup(html, "html.parser")

        # Selectăm elementele de tip articol sau linkurile care fac parte din știri
        for articol in soup.select("article, .story, .news-item, .title"):
            link = articol if articol.name == "a" else articol.find("a")
            if not link:
                continue

            url = link.get("href", "").strip()
            titlu_tag = articol.find(["h2", "h3"]) if articol.name != "a" else None
            titlu = titlu_tag.get_text(" ", strip=True) if titlu_tag else link.get_text(" ", strip=True)

            if not titlu or len(titlu) < 25:
                continue

            termeni_de_evitat = ["descarcă aplicația", "program tv", "live tv", "termeni și condiții", "politica de", "contact"]
            if any(termen in titlu.lower() for termen in termeni_de_evitat):
                continue

            if url.startswith("/"):
                url = "https://digisport.ro" + url

            if not url.startswith("https://digisport.ro"):
                continue

            if any(stire["url"] == url for stire in stiri):
                continue

            stiri.append({
                "titlu": titlu,
                "url": url
            })

    except Exception as e:
        print(f"Eroare la citirea DigiSport: {e}")

    return stiri


@tasks.loop(minutes=15)
async def bucla_stiri_sport():
    global CANAL_SPORT_ID
    if not CANAL_SPORT_ID:
        return

    canal = bot.get_channel(CANAL_SPORT_ID)
    if not canal:
        try:
            canal = await bot.fetch_channel(CANAL_SPORT_ID)
        except Exception:
            return

    toate_stiri = await citeste_stiri_digisport()
    
    # Selectăm doar știrile care nu au mai fost trimise în această sesiune
    stiri_noi = [s for s in toate_stiri if s["titlu"] not in ULTIMELE_STIRI_TRIMISE]

    # Luăm primele 3 știri noi
    stiri_de_trimis = stiri_noi[:3]

    if not stiri_de_trimis:
        return  # Dacă nu e nimic nou, așteptăm următoarea rulare

    embed = discord.Embed(
        title="📰 ULTIMELE ȘTIRI DIN SPORT",
        description="Iată cele mai noi actualizări de pe Digi Sport:",
        color=discord.Color.blue()
    )

    for index, stire in enumerate(stiri_de_trimis, start=1):
        embed.add_field(
            name=f"{index}. {stire['titlu']}",
            value=f"[Citește tot articolul]({stire['url']})",
            inline=False
        )
        ULTIMELE_STIRI_TRIMISE.add(stire["titlu"])

    embed.set_footer(text="Actualizare automată la fiecare 15 minute • Digi Sport")

    try:
        await canal.send(embed=embed)
    except Exception as e:
        print(f"Eroare la trimiterea știrilor: {e}")


@bucla_stiri_sport.before_loop
async def inainte_de_stiri_sportive():
    await bot.wait_until_ready()


@bot.tree.command(name="sport", description="Setează canalul curent pentru știri sportive automate la 15 minute!")
@app_commands.default_permissions(administrator=True)
async def sport(interaction: discord.Interaction):
    global CANAL_SPORT_ID
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Doar administratorii pot seta canalul de știri! 🔒",
            ephemeral=True
        )
        return

    CANAL_SPORT_ID = interaction.channel_id
    
    if not bucla_stiri_sport.is_running():
        bucla_stiri_sport.start()
        
    await interaction.response.send_message(
        f"✅ Canalul {interaction.channel.mention} a fost activat pentru știri sportive la fiecare 15 minute!"
    )


# ==========================================
# PORNIRE BOT
# ==========================================

@bot.event
async def on_ready():
    print(f"Cotaiala este online ca {bot.user}!")

    if not trivia_automat.is_running():
        trivia_automat.start()


if __name__ == "__main__":
    if os.path.exists("token.txt"):
        with open("token.txt", "r", encoding="utf-8") as f:
            TOKEN = f.read().strip()

        if TOKEN:
            bot.run(TOKEN)
        else:
            print("EROARE: Fișierul token.txt este gol!")
    else:
        print("EROARE: Nu găsesc token.txt! Pune-l lângă bot.py.")
