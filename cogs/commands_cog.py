import logging
import discord
from discord.ext import commands
from discord import app_commands

### MODIFICATION ###
# On n'importe plus db en entier, mais les fonctions nécessaires
from db import fetch_user, get_leaderboard_from_cache
from utils import total_xp_to_level, make_progress_bar, xp_cum
from config import GUILD_ID, LEVEL_MAX, WEB_URL


class CommandsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rank",
                          description="Affiche ton niveau et ta progression")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def rank(self, interaction: discord.Interaction):
        try:
            u = fetch_user(interaction.user.id)
            nick = u["nick"] or interaction.user.display_name
            lvl = total_xp_to_level(u["xp"])
            if 0 < lvl < LEVEL_MAX:
                # Correction pour le niveau 1
                mn = xp_cum[lvl - 1] if lvl > 1 else 0
                mx = xp_cum[lvl]
            else:
                mn, mx = 0, u["xp"] if u["xp"] > 0 else 1
            cur, need = u["xp"] - mn, mx - mn
            bar = make_progress_bar(cur, need)
            await interaction.response.send_message(
                f"**{nick}**, niveau **{lvl}** ({u['xp']} XP)\n{bar} ({cur}/{need} XP)",
                ephemeral=True)
        except Exception:
            logging.exception("Erreur dans /rank")
            await interaction.response.send_message(
                "❌ Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="leaderboard",
                          description="Top N des membres par XP")
    @app_commands.describe(nombre="Nombre de membres à afficher (max 25)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def leaderboard(self,
                          interaction: discord.Interaction,
                          nombre: int = 10):
        await interaction.response.defer()

        ### MODIFICATION ###
        # Utilisation du cache pour le leaderboard
        lb_cache = get_leaderboard_from_cache()

        em = discord.Embed(
            title="🏆 Classement XP",
            description=f"[📊 Afficher le classement complet]({WEB_URL})",
            color=0x00CC88)

        for i, user_data in enumerate(lb_cache[:min(nombre, 25)], start=1):
            nick = user_data.get("nick") or f"Utilisateur {user_data['uid']}"
            xp = user_data.get("xp", 0)
            lvl = total_xp_to_level(xp)
            em.add_field(name=f"#{i} — {nick}",
                         value=f"Niveau **{lvl}** ({xp} XP)",
                         inline=False)
        await interaction.followup.send(embed=em)

    @app_commands.command(name="help", description="Liste des commandes")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def help(self, interaction: discord.Interaction):
        txt = ("`/rank` — Ton niveau et barre de progression\n"
               "`/leaderboard` — Top en embed + lien web\n"
               "`/boutique` — Accéder à la boutique d'objets\n"
               "`/sac` — Voir ton argent et tes objets\n"
               "`/info [objet]` — Info sur un objet de la boutique\n"
               "`/help` — Ce message")
        await interaction.response.send_message(txt, ephemeral=True)


async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
