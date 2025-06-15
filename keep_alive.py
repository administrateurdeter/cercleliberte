# keep_alive.py

import os
import json
import math
import requests
import time
from flask import Flask, render_template_string, request
from threading import Thread

# On lit le leaderboard depuis le cache (db.py)
from db import get_leaderboard_from_cache
from utils import xp_cum, total_xp_to_level

app = Flask(__name__)
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")


def xp_bounds(level: int):
    # Correction pour le niveau 1 et au-delà
    if level < 1:
        return 0, xp_cum[0]
    if level >= len(xp_cum):
        return xp_cum[-2], xp_cum[-1]
    return xp_cum[level - 1], xp_cum[level]


@app.route("/")
def home():
    return "Bot is alive!"


@app.route("/logs")
def logs():
    try:
        with open("bot.log", "r", encoding="utf-8") as f:
            return f"<pre>{f.read()[-5000:]}</pre>"
    except Exception as e:
        return f"Erreur logs : {e}"


@app.route("/leaderboard")
def leaderboard():
    # Récupère page et per_page depuis l'URL
    page     = max(int(request.args.get("page", 1)), 1)
    per_page = int(request.args.get("per_page", 50))
    if per_page not in (50, 100, 200):
        per_page = 50

    # Lit le cache, déjà trié par XP décroissant
    cached_members = get_leaderboard_from_cache()

    # Prépare la liste pour le template
    members = []
    for d in cached_members:
        uid    = d.get("uid")
        xp     = d.get("xp", 0)
        lvl    = total_xp_to_level(xp)
        name   = d.get("nick") or f"Utilisateur {uid}"
        avatar = d.get("avatar") or "https://cdn.discordapp.com/embed/avatars/0.png"
        mn, mx = xp_bounds(lvl)
        pct    = int((xp - mn) / (mx - mn) * 100) if mx > mn else 100

        members.append({
            "uid":     uid,
            "name":    name,
            "avatar":  avatar,
            "level":   lvl,
            "xp":      xp,
            "percent": pct
        })

    total   = len(members)
    pages   = math.ceil(total / per_page) if total > 0 else 1
    if page > pages:
        page = pages
    start         = (page - 1) * per_page
    page_entries  = members[start:start + per_page]

    # Le même template HTML que celui que tu avais, inchangé
    html = """
    <!DOCTYPE html><html><head><meta charset="utf-8"><title>Leaderboard XP</title>
    <style>body{background:#1e1e2f;color:#eee;font-family:sans-serif;padding:20px;}
    h1{text-align:center;}.entry{display:flex;align-items:center;background:#2c2f48;margin:10px 0;
    padding:10px;border-radius:8px;}.entry img{width:48px;height:48px;border-radius:50%;
    margin-right:10px;}.info{flex:1;}.bar{background:#444;width:300px;height:10px;border-radius:5px;
    overflow:hidden;margin-top:5px;}.fill{background:#00cc88;height:100%;}.controls{text-align:center;
    margin:20px 0;}.controls a{color:#00ccff;text-decoration:none;margin:0 5px;}
    .controls strong{margin:0 5px;}
    </style></head><body>
    <h1>🏆 Leaderboard XP</h1>
    <div class="controls">
      <form method="get">
        Résultats par page:
        <select name="per_page" onchange="this.form.submit()">
          <option value="50" {% if per_page==50 %}selected{% endif %}>50</option>
          <option value="100" {% if per_page==100 %}selected{% endif %}>100</option>
          <option value="200" {% if per_page==200 %}selected{% endif %}>200</option>
        </select>
        <input type="hidden" name="page" value="{{page}}">
      </form>
    </div>
    {% for u in page_entries %}
    <div class="entry">
      <img src="{{u.avatar}}" alt="avatar">
      <div class="info">
        <strong>#{{start+loop.index}} – {{u.name}}</strong><br>
        Niveau {{u.level}} – {{u.xp}} XP
        <div class="bar"><div class="fill" style="width:{{u.percent}}%"></div></div>
      </div>
    </div>
    {% endfor %}
    <div class="controls">
      {% for p in range(1,pages+1) %}
        {% if p==page %}<strong>{{p}}</strong>{% else %}
          <a href="?page={{p}}&per_page={{per_page}}">{{p}}</a>
        {% endif %}
      {% endfor %}
    </div>
    </body></html>
    """

    return render_template_string(
        html,
        page_entries=page_entries,
        page=page,
        per_page=per_page,
        start=start,
        pages=pages
    )


def run_app():
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    # 1) Lancement du serveur Flask en arrière-plan
    Thread(target=run_app, daemon=True).start()

    # 2) Auto-ping pour rester "awake"
    def _auto_ping():
        url = os.getenv("KEEP_ALIVE_URL", "http://127.0.0.1:3000/")
        while True:
            try:
                requests.get(url)
            except:
                pass
            time.sleep(300)

    Thread(target=_auto_ping, daemon=True).start()
