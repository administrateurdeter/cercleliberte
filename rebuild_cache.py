# rebuild_cache.py
import os
import json
from replit import db
from config import USER_PREFIX, LEADERBOARD_CACHE_KEY

print("🔧 Démarrage de la reconstruction du cache du leaderboard...")

leaderboard_data = []
user_keys = [key for key in db.keys() if key.startswith(USER_PREFIX)]

print(f"🔍 {len(user_keys)} utilisateurs trouvés dans la base de données.")

for key in user_keys:
    try:
        uid = int(key.replace(USER_PREFIX, ""))
        user_json = db[key]
        user_data = json.loads(user_json)

        # On ne prend que les informations nécessaires pour le cache
        cache_entry = {
            "uid": uid,
            "xp": user_data.get("xp", 0),
            "nick": user_data.get("nick"),
            "avatar": user_data.get("avatar")
        }
        leaderboard_data.append(cache_entry)

    except (ValueError, json.JSONDecodeError, KeyError) as e:
        print(f"⚠️ Erreur en traitant la clé '{key}': {e}. On ignore.")
        continue

# Trier la liste complète par XP
leaderboard_data.sort(key=lambda x: x.get("xp", 0), reverse=True)

# Sauvegarder la liste triée dans la clé de cache
db[LEADERBOARD_CACHE_KEY] = json.dumps(leaderboard_data)

print(
    f"✅ Cache du leaderboard reconstruit avec succès avec {len(leaderboard_data)} membres."
)
print("🚀 Le leaderboard devrait maintenant s'afficher correctement.")
