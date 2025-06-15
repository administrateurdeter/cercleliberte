# cogs/xp_cog.py

import discord
import random
import logging
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time

from db import fetch_user, save_user
from utils import total_xp_to_level
from config import (XP_PER_MSG, MIN_LEN, COOLDOWN, DAILY_LIMIT, COIN_PER_MSG,
                    ROLE_CITIZEN, ROLE_THRESHOLDS, LEVEL_UP_MESSAGES)


class XPCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.reset_daily_counts.start()

    @tasks.loop(hours=24)
    async def reset_daily_counts(self):
        """
        Réinitialise daily & muted_today chaque minuit (UTC+2).
        CETTE FONCTION EST MAINTENANT PROTÉGÉE CONTRE LES CRASHS.
        """
        logging.info("--- [TACHE QUOTIDIENNE] Démarrage de la réinitialisation journalière ---")
        from replit import db as _db

        user_keys = [key for key in _db.keys() if key.startswith("user:")]
        logging.info(f"[TACHE QUOTIDIENNE] {len(user_keys)} utilisateurs à traiter.")

        success_count = 0
        error_count = 0

        for key in user_keys:
            try:
                uid = int(key.replace("user:", ""))
                u = fetch_user(uid)
                u["daily"] = 0
                u["muted_today"] = None
                save_user(uid, u)
                success_count += 1
            except Exception as e:
                # Au lieu de crasher, on enregistre l'erreur et on continue.
                logging.error(f"[TACHE QUOTIDIENNE] Impossible de réinitialiser la clé '{key}': {e}")
                error_count += 1
                continue # Essentiel: on passe à l'utilisateur suivant.

        logging.info(f"--- [TACHE QUOTIDIENNE] Réinitialisation terminée. {success_count} succès, {error_count} erreurs. ---")


    @reset_daily_counts.before_loop
    async def before_reset(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow() + timedelta(hours=2)
        next_mid = datetime.combine(now.date() + timedelta(days=1),
                                    time()) - timedelta(hours=2)
        await discord.utils.sleep_until(next_mid)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Donne le rôle Citoyen à l'arrivée.
        CETTE FONCTION EST MAINTENANT PROTÉGÉE CONTRE LES CRASHS.
        """
        if member.bot:
            return

        try:
            role = discord.utils.get(member.guild.roles, name=ROLE_CITIZEN)
            if role:
                await member.add_roles(role)
                logging.info(
                    f"Rôle '{ROLE_CITIZEN}' ajouté à {member.display_name}.")
            else:
                logging.warning(
                    f"Le rôle '{ROLE_CITIZEN}' n'a pas été trouvé sur le serveur.")
        except discord.Forbidden:
            logging.error(
                f"Permissions manquantes pour ajouter le rôle '{ROLE_CITIZEN}' à {member.display_name}. VÉRIFIER LA HIÉRARCHIE DES RÔLES."
            )
        except Exception as e:
            logging.exception(
                f"Erreur imprévue en ajoutant le rôle à {member.display_name}: {e}")

    @commands.Cog.listener()
    async def on_message(self, msg):
        """
        Gère le gain d'XP et les level-ups.
        CETTE FONCTION EST MAINTENANT INTÉGRALEMENT PROTÉGÉE CONTRE LES CRASHS.
        """
        if msg.author.bot or not msg.guild:
            return

        try:
            u = fetch_user(msg.author.id)
            now = datetime.utcnow()

            # Sauvegarde proactive du pseudo et de l'avatar si non présents
            if u["nick"] is None or u["avatar"] is None:
                u["nick"] = msg.author.display_name
                u["avatar"] = str(msg.author.display_avatar.url)

            # Purge des bonus expirés
            u["active_bonus"] = [dt for dt in u["active_bonus"] if dt > now]

            # Conditions de validité (longueur + cooldown)
            if len(msg.content) < MIN_LEN or (
                    u["last"] and (now - u["last"]).total_seconds() < COOLDOWN):
                if u["last"] is None:
                    u["last"] = now
                    save_user(msg.author.id, u)
                return

            # 1) Crédits MC (sans limite journalière)
            u["money"] = u.get("money", 0) + COIN_PER_MSG

            # 2) Crédits XP (avec blocage, bonus, daily limit)
            blocked = u.get("xp_blocked_until") and now < u["xp_blocked_until"]
            has_bonus = len(u["active_bonus"]) > 0
            old_lvl = u["level"]

            if not blocked and (has_bonus or u["daily"] < DAILY_LIMIT):
                xp_gain = 40 if has_bonus else XP_PER_MSG
                u["xp"] += xp_gain
                if not has_bonus:
                    u["daily"] += 1

                # Passage de niveau ?
                new_lvl = total_xp_to_level(u["xp"])
                if new_lvl > old_lvl:
                    u["level"] = new_lvl
                    phrase = random.choice(LEVEL_UP_MESSAGES)
                    logging.info(
                        f"Level-up pour {msg.author.display_name} : {old_lvl} -> {new_lvl}"
                    )

                    await msg.channel.send(
                        f"{msg.author.mention}, tu as atteint le niveau **{new_lvl}** ! {phrase}"
                    )

                    # 🚦 Gestion des rôles : on ne retire QUE le rôle précédent au seuil franchi
                    thresholds = sorted(ROLE_THRESHOLDS.items())
                    for idx, (lvl_req, role_name) in enumerate(thresholds):
                        if old_lvl < lvl_req <= new_lvl:
                            #  ➡️ Retirer l’ancien rôle
                            prev_role_name = ROLE_CITIZEN if idx == 0 else thresholds[
                                idx - 1][1]
                            role_prev_obj = discord.utils.get(msg.guild.roles,
                                                              name=prev_role_name)
                            if role_prev_obj and role_prev_obj in msg.author.roles:
                                await msg.author.remove_roles(role_prev_obj)
                            #  ➡️ Ajouter le nouveau rôle
                            role_new_obj = discord.utils.get(msg.guild.roles,
                                                             name=role_name)
                            if role_new_obj:
                                await msg.author.add_roles(role_new_obj)

            # 3) Mise à jour du timestamp et sauvegarde
            u["last"] = now
            save_user(msg.author.id, u)

        except Exception as e:
            # Ce bloc attrape TOUTES les erreurs possibles (Forbidden, HTTPException, etc.)
            # qui pourraient survenir dans la fonction, empêchant le bot de planter.
            logging.error(f"ERREUR GÉRÉE DANS ON_MESSAGE (bot n'a pas crashé) pour l'utilisateur {msg.author} ({msg.author.id})")
            logging.exception(e) # Affiche l'erreur complète dans les logs pour le diagnostic.


async def setup(bot):
    await bot.add_cog(XPCog(bot))