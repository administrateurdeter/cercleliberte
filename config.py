# config.py

import os
from dotenv import load_dotenv

# Charge automatiquement le fichier .env en local
load_dotenv()

# → Discord
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID  = int(os.getenv("DISCORD_GUILD_ID"))

# → Préfixe base de données & clés dynamiques
DB_ENV_PREFIX         = os.getenv("DB_PREFIX", "prod")
USER_PREFIX           = f"{DB_ENV_PREFIX}_user:"
LEADERBOARD_CACHE_KEY = f"{DB_ENV_PREFIX}_leaderboard_cache"

# → XP par message & limites
XP_PER_MSG  = 100  # XP gagné par message valide
MIN_LEN     = 5    # longueur minimale pour valider un message
COOLDOWN    = 30   # secondes entre deux gains d’XP
DAILY_LIMIT = 10   # max de messages comptabilisés par jour

# → Monnaie
COIN_PER_MSG = 1  # MetaCoin gagné par message valide

# → Niveaux
LEVEL_MAX = 200

# → Courbe d’XP
XP_MIN      = 300        # XP cumulés requis au niveau 1
XP_MAX      = 730_000    # XP cumulés requis au niveau 200
XP_EXPONENT = 1.5151515151515151  # exposant calibré sur tes paliers

# → Rôles et paliers automatiques
ROLE_CITIZEN     = "Citoyen"
ROLE_LIBERTARIAN = "Voie Libertaire"
ROLE_FREE_THINKER= "Libre Penseur"
ROLE_THRESHOLDS  = {
    10: ROLE_LIBERTARIAN,
    50: ROLE_FREE_THINKER,
}

# → Messages aléatoires à chaque level-up
LEVEL_UP_MESSAGES = [
    "J’ai ajouté un bouton Like à ta vie. Dommage, personne ne l’a cliqué.",
    "Tu es une vraie star montante !",
    "Ta daronne m’a ajouté sur Facebook. C’est gênant.",
    "Je vois tout ce que tu fais. Même ce que t’as effacé. Surtout ce que t’as effacé.",
    "Tu galères à finir ton mois ? J’ai payé une pizza en actions Meta. Maintenant le pizzaiolo est millionnaire.",
    "Je me connecte dans le Metaverse pour fuir la réalité... comme toi, mais avec une meilleure résolution.",
    "Tu crois avoir des amis ? Ce sont mes algorithmes qui ont décidé.",
    "J’ai copié ton idée avant que tu la penses. Ça s’appelle de l’optimisation prédictive.",
    "Ta confidentialité, je l’ai lue pendant mon café.",
    "Pourquoi bosser 35h alors que tu peux danser en JPEG dans mon Metaverse pour 0,003 ETH la minute ?",
    "Tu me prends pour une IA. Mais je possède un hoodie et un compte en banque offshore.",
    "J’ai mis des pubs dans ton sommeil. Tu t’es réveillé avec l’envie d’acheter un grille-pain.",
    "J’ai racheté ta dignité avec 12 centimes et un GIF de chat.",
    "J'ai mis un NFT de mes émotions sur la blockchain. Il s’est vendu avant que je ressente quoi que ce soit.",
    "Ta grand-mère a rejoint le Metaverse. Elle m’a poké.",
    "Je gagne plus d’argent quand tu clignes des yeux que toi en une année entière.",
    "J’ai mis un captcha sur ma porte d’entrée. Ma femme n’a jamais réussi à rentrer.",
    "Mon wifi est tellement rapide qu’il a liké ton crush avant toi.",
    "J’ai scanné ton âme. Trop de bugs. Tu devrais être ban.",
    "Ta daronne pleure devant Netflix ? Normal, c’est moi qui ai produit le chagrin.",
    "Chaque fois que tu touches un clavier, je gagne une action. Et une érection boursière.",
    "J’ai ajouté un filtre sang sur la réalité. C’est plus immersif pour les pauvres.",
    "J’ai modifié les conditions d’utilisation de l’air. T’étouffes si t’acceptes pas.",
    "T’existes encore parce que t’es rentable. Le jour où tu côutes plus que tu rapportes, c’est alt+F4 IRL.",
    "Ton père est dans le Metaverse. Il ramasse des tokens pour pouvoir pisser.",
    "Tu es une vraie star montante !"
]

# → Emoji pour l’annonce de level-up
EMOJI_KERMIT = "<:kermit:1380164139649073322>"

# → Boutique : définition des items
ECONOMY_ITEMS = {
    "paypal": {
        "name": "Action Meta",
        "price": 59997,
        "description": "Vous recevrez 5 € sur PayPal. (Usage unique)"
    },
    "xp_bonus": {
        "name": "Puce GPU",
        "price": 1440,
        "description": "Supprime la limite d'XP pendant 1 h. Cumulable ×5."
    },
    "xp_block": {
        "name": "Malware",
        "price": 348,
        "description": "Bloque l'XP d'un utilisateur ≥ lvl 10 du prochain minuit au suivant. (Non cumulable)"
    },
    "spy": {
        "name": "Lunettes Meta",
        "price": 20,
        "description": "Vous permet de voir le sac (objets + argent) d'un autre utilisateur."
    },
    "timemute": {
        "name": "Attaque DDOS",
        "price": 999,
        "description": "Mute un utilisateur ≥ lvl 10 pendant 10 minutes. 1-usage/jour par cible."
    }
}

# → URL publique du leaderboard
WEB_URL = os.getenv(
    "WEB_URL",
    "https://066aa20b-6b88-4b02-bae9-25b2f4d65e77-00-2fft007ciljp2.spock.replit.dev/leaderboard"
)
