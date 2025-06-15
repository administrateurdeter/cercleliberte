# Fichier launcher.py (Le nouveau point de démarrage de votre application)

import asyncio
import logging
import time
from main import run_bot # On importe la fonction de démarrage depuis main.py

# On configure le logging ici aussi pour attraper les erreurs du lanceur
logging.basicConfig(filename="bot.log",
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def main_launcher():
    loop = asyncio.get_event_loop()
    while True:
        try:
            logging.info("🚀 [LANCEUR] Démarrage du bot...")
            # On lance le bot. Le script va rester bloqué sur cette ligne tant que le bot tourne.
            loop.run_until_complete(run_bot())

        except KeyboardInterrupt:
            # Si on arrête manuellement le bot (Ctrl+C), on sort de la boucle.
            logging.info("🛑 [LANCEUR] Arrêt manuel détecté. Au revoir.")
            break

        except Exception as e:
            # Si N'IMPORTE QUELLE erreur fait crasher le bot, on l'attrape ici.
            logging.error("🔥 [LANCEUR] ERREUR FATALE, LE BOT A CRASHÉ !")
            logging.exception(e)

        # Si on arrive ici, c'est que le bot s'est arrêté (crash ou déconnexion).
        logging.warning("⚠️ [LANCEUR] Le bot s'est arrêté. Redémarrage dans 15 secondes...")
        time.sleep(15) # On attend 15 secondes avant de relancer pour éviter de spammer l'API de Discord.

if __name__ == "__main__":
    main_launcher()