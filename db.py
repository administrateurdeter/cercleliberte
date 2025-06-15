import json
from datetime import datetime
from replit import db
from config import USER_PREFIX, LEADERBOARD_CACHE_KEY


def fetch_user(uid: int) -> dict:
    key = USER_PREFIX + str(uid)
    if key in db:
        r = json.loads(db[key])
        return {
            "xp":
            r.get("xp", 0),
            "daily":
            r.get("daily", 0),
            "last":
            datetime.fromisoformat(r["last"]) if r.get("last") else None,
            "level":
            r.get("level", 0),
            "nick":
            r.get("nick"),
            "avatar":
            r.get("avatar"),
            "money":
            r.get("money", 0),
            "inventory":
            r.get("inventory", {}),
            "active_bonus":
            [datetime.fromisoformat(ts) for ts in r.get("active_bonus", [])],
            "xp_blocked_until":
            datetime.fromisoformat(r["xp_blocked_until"])
            if r.get("xp_blocked_until") else None,
            "mute_history": {
                int(k): datetime.fromisoformat(v)
                for k, v in r.get("mute_history", {}).items()
            },
            "muted_today":
            r.get("muted_today")
        }
    # Valeurs par défaut
    return {
        "xp": 0,
        "daily": 0,
        "last": None,
        "level": 0,
        "nick": None,
        "avatar": None,
        "money": 0,
        "inventory": {},
        "active_bonus": [],
        "xp_blocked_until": None,
        "mute_history": {},
        "muted_today": None
    }


def save_user(uid: int, data: dict):
    key = USER_PREFIX + str(uid)
    d = {
        "xp":
        data["xp"],
        "daily":
        data["daily"],
        "last":
        data["last"].isoformat() if data.get("last") else None,
        "level":
        data.get("level", 0),
        "nick":
        data.get("nick"),
        "avatar":
        data.get("avatar"),
        "money":
        data.get("money", 0),
        "inventory":
        data.get("inventory", {}),
        "active_bonus":
        [ts.isoformat() for ts in data.get("active_bonus", [])],
        "xp_blocked_until":
        data["xp_blocked_until"].isoformat()
        if data.get("xp_blocked_until") else None,
        "mute_history": {
            str(k): v.isoformat()
            for k, v in data.get("mute_history", {}).items()
        },
        "muted_today":
        data.get("muted_today")
    }
    db[key] = json.dumps(d)

    ### MODIFICATION ###
    # Mise à jour du cache après la sauvegarde de l'utilisateur
    update_leaderboard_cache(uid, data)


def update_leaderboard_cache(uid: int, data: dict):
    """Met à jour le cache du leaderboard avec les infos d'un utilisateur."""
    try:
        cache_raw = db.get(LEADERBOARD_CACHE_KEY)
        cache = json.loads(cache_raw) if cache_raw else []
    except (json.JSONDecodeError, TypeError):
        cache = []

    user_info = {
        "uid": uid,
        "xp": data.get("xp", 0),
        "nick": data.get("nick"),
        "avatar": data.get("avatar")
    }

    # Trouve l'utilisateur dans le cache et le met à jour, ou l'ajoute s'il est nouveau
    found = False
    for i, user in enumerate(cache):
        if user.get("uid") == uid:
            cache[i] = user_info
            found = True
            break

    if not found:
        cache.append(user_info)

    # Trie le cache par XP décroissant
    cache.sort(key=lambda x: x.get("xp", 0), reverse=True)

    db[LEADERBOARD_CACHE_KEY] = json.dumps(cache)


def get_leaderboard_from_cache() -> list:
    """Récupère le leaderboard trié depuis le cache."""
    try:
        cache_raw = db.get(LEADERBOARD_CACHE_KEY)
        return json.loads(cache_raw) if cache_raw else []
    except (json.JSONDecodeError, TypeError):
        return []
