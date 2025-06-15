# db.py

import json
from datetime import datetime
import shelve
from config import USER_PREFIX, LEADERBOARD_CACHE_KEY

# On n'essaie PAS replit.db du tout, on ouvre directement xp_data.db
db = shelve.open("xp_data.db", writeback=True)


def fetch_user(uid: int) -> dict:
    key = USER_PREFIX + str(uid)
    if key in db:
        raw = json.loads(db[key])
        return {
            "xp": raw.get("xp", 0),
            "daily": raw.get("daily", 0),
            "last": datetime.fromisoformat(raw["last"]) if raw.get("last") else None,
            "level": raw.get("level", 0),
            "nick": raw.get("nick"),
            "avatar": raw.get("avatar"),
            "money": raw.get("money", 0),
            "inventory": raw.get("inventory", {}),
            "active_bonus": [
                datetime.fromisoformat(ts) for ts in raw.get("active_bonus", [])
            ],
            "xp_blocked_until": (
                datetime.fromisoformat(raw["xp_blocked_until"])
                if raw.get("xp_blocked_until") else None
            ),
            "mute_history": {
                int(k): datetime.fromisoformat(v)
                for k, v in raw.get("mute_history", {}).items()
            },
            "muted_today": raw.get("muted_today")
        }
    return {
        "xp": 0, "daily": 0, "last": None, "level": 0,
        "nick": None, "avatar": None, "money": 0,
        "inventory": {}, "active_bonus": [],
        "xp_blocked_until": None, "mute_history": {}, "muted_today": None
    }


def save_user(uid: int, data: dict):
    key = USER_PREFIX + str(uid)
    d = {
        "xp": data.get("xp", 0),
        "daily": data.get("daily", 0),
        "last": data.get("last").isoformat() if data.get("last") else None,
        "level": data.get("level", 0),
        "nick": data.get("nick"),
        "avatar": data.get("avatar"),
        "money": data.get("money", 0),
        "inventory": data.get("inventory", {}),
        "active_bonus": [ts.isoformat() for ts in data.get("active_bonus", [])],
        "xp_blocked_until": data["xp_blocked_until"].isoformat() if data.get("xp_blocked_until") else None,
        "mute_history": {str(k): v.isoformat() for k, v in data.get("mute_history", {}).items()},
        "muted_today": data.get("muted_today")
    }
    db[key] = json.dumps(d)
    update_leaderboard_cache(uid, data)


def update_leaderboard_cache(uid: int, data: dict):
    try:
        raw = db.get(LEADERBOARD_CACHE_KEY)
        cache = json.loads(raw) if raw else []
    except:
        cache = []
    user_info = {
        "uid": uid, "xp": data.get("xp", 0),
        "daily": data.get("daily", 0),
        "level": data.get("level", 0),
        "nick": data.get("nick"),
        "avatar": data.get("avatar")
    }
    for i, u in enumerate(cache):
        if u.get("uid") == uid:
            cache[i] = user_info
            break
    else:
        cache.append(user_info)
    cache.sort(key=lambda x: x.get("xp", 0), reverse=True)
    db[LEADERBOARD_CACHE_KEY] = json.dumps(cache)


def get_leaderboard_from_cache() -> list:
    try:
        raw = db.get(LEADERBOARD_CACHE_KEY)
        return json.loads(raw) if raw else []
    except:
        return []
