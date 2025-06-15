# Fichier main.py (Modifié pour être une fonction de démarrage)

import asyncio
import logging
import discord
from discord.ext import commands

from config import BOT_TOKEN, GUILD_ID

# Le logging reste le même
logging.basicConfig(filename="bot.log",
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Cette fonction contient toute la logique de votre bot
async def run_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    initial_extensions = ["cogs.xp_cog", "cogs.commands_cog", "cogs.economy_cog"]

    @bot.event
    async def on_ready():
        logging.info(f"✅ Connecté comme {bot.user}")
        try:
            await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
            logging.info("Slash commands synchronisées.")
        except Exception as e:
            logging.error(f"Erreur de synchronisation des slash commands: {e}")
        # On garde keep_alive ici pour qu'il se lance à chaque démarrage du bot


    # Le démarrage du bot est maintenant encapsulé
    async with bot:
        for ext in initial_extensions:
            await bot.load_extension(ext)
            logging.info(f"✅ Cog chargé : {ext}")
        await bot.start(BOT_TOKEN)

# La partie qui lançait le bot (__main__) est supprimée d'ici.
# Elle sera dans notre nouveau fichier de surveillance.
