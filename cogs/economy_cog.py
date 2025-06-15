import discord
from discord.ext import commands
from discord import app_commands, ui
from datetime import datetime, timedelta

from db import fetch_user, save_user
from utils import total_xp_to_level
from config import ECONOMY_ITEMS, GUILD_ID


class BuyButton(ui.Button):

    def __init__(self, key: str, user_id: int):
        it = ECONOMY_ITEMS[key]
        super().__init__(label=f"{it['name']} – {it['price']} MC",
                         style=discord.ButtonStyle.primary,
                         custom_id=f"buy_{key}")
        self.key = key
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        # Sécurité : seul l’utilisateur qui a ouvert la boutique peut acheter
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                "Ce n'est pas ta boutique !", ephemeral=True)
        u = fetch_user(self.user_id)
        price = ECONOMY_ITEMS[self.key]["price"]
        if u["money"] < price:
            return await interaction.response.send_message(
                "Solde insuffisant.", ephemeral=True)
        # Débite et stocke dans l’inventaire
        u["money"] -= price
        inv = u.get("inventory", {})
        inv[self.key] = inv.get(self.key, 0) + 1
        u["inventory"] = inv
        save_user(self.user_id, u)
        await interaction.response.send_message(
            f"✅ **{ECONOMY_ITEMS[self.key]['name']}** a été stocké dans ton sac à dos.",
            ephemeral=True)


class ShopView(ui.View):

    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        for key in ECONOMY_ITEMS:
            self.add_item(BuyButton(key, user_id))


class EconomyCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="boutique",
                          description="Ouvre la boutique (niveau ≥ 10 requis)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def boutique(self, interaction: discord.Interaction):
        u = fetch_user(interaction.user.id)
        lvl = total_xp_to_level(u["xp"])
        if lvl < 10:
            return await interaction.response.send_message(
                "Tu dois être au moins niveau 10 pour accéder à la boutique.",
                ephemeral=True)

        mc = u.get("money", 0)
        embed = discord.Embed(title="🏪 Boutique Métaverse",
                              description=f"💰 Solde : **{mc} MC**",
                              color=0x00CC88)
        for it in ECONOMY_ITEMS.values():
            embed.add_field(name=f"{it['name']} – {it['price']} MC",
                            value=it["description"],
                            inline=False)
        view = ShopView(interaction.user.id)
        await interaction.response.send_message(embed=embed,
                                                view=view,
                                                ephemeral=True)

    @app_commands.command(name="sac",
                          description="Affiche ton solde et ton inventaire")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def sac(self, interaction: discord.Interaction):
        u = fetch_user(interaction.user.id)
        mc = u.get("money", 0)
        inv = u.get("inventory", {})
        inv_txt = "\n".join(f"- {ECONOMY_ITEMS[k]['name']} x{v}"
                            for k, v in inv.items() if v > 0) or "Aucun objet"
        txt = f"💰 **{mc} MC**\n🎒 Inventaire :\n{inv_txt}"
        await interaction.response.send_message(txt, ephemeral=True)

    @app_commands.command(name="info",
                          description="Obtenir la description d'un objet")
    @app_commands.describe(
        objet="Clé de l'objet (paypal, xp_bonus, xp_block, spy, timemute)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def info(self, interaction: discord.Interaction, objet: str):
        it = ECONOMY_ITEMS.get(objet)
        if not it:
            return await interaction.response.send_message("Objet inconnu.",
                                                           ephemeral=True)
        txt = f"**{it['name']}**\nPrix : {it['price']} MC\n{it['description']}"
        await interaction.response.send_message(txt, ephemeral=True)


async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
