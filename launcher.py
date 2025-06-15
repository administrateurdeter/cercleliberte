# launcher.py

import asyncio
import logging
import time
from main import run_bot  # On importe la fonction de démarrage depuis main.py

def main_launcher():
    # 1) Créer un nouveau loop et l'enregistrer
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 2) Configurer logging à la fois sur console et fichier
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s – %(levelname)s – %(message)s",
        handlers=[
            logging.FileHandler("bot.log", encoding="utf-8"),
            logging.StreamHandler()           # ← envoie aussi vers la console
        ],
    )

    while True:
        try:
            logging.info("🚀 [LANCEUR] Démarrage du bot...")
            # Lance la coroutine run_bot(), et reste bloqué ici tant que le bot tourne
            loop.run_until_complete(run_bot())

        except KeyboardInterrupt:
            # Ctrl+C détecté, on sort proprement
            logging.info("⛔ [LANCEUR] Arrêt manuel détecté. Au revoir.")
            break

        except Exception as e:
            # N'importe quelle autre erreur ne fait pas planter le script
            logging.error("🔥 [LANCEUR] ERREUR FATALE, LE BOT A CRASHÉ !")
            logging.exception(e)
            time.sleep(5)  # on attend 5 secondes avant de relancer

if __name__ == "__main__":
    main_launcher()
