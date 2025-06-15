from config import LEVEL_MAX, XP_MIN, XP_MAX, XP_EXPONENT

# → XP cumulés pour chaque niveau (1→200)
xp_cum = [
    int(XP_MIN + (XP_MAX - XP_MIN) * ((i / (LEVEL_MAX - 1))**XP_EXPONENT))
    for i in range(LEVEL_MAX)
]


def total_xp_to_level(xp: int) -> int:
    """
    Retourne le niveau (0≤L≤LEVEL_MAX) pour un total d'XP donné.
    """
    for idx, thr in enumerate(xp_cum):
        if xp < thr:
            return idx
    return LEVEL_MAX


def make_progress_bar(cur: int, need: int, length: int = 12) -> str:
    """
    Génère une barre de progression de `length` cases.
    """
    if need <= 0:
        return "🟦" * length
    filled = int((cur / need) * length)
    return "🟦" * filled + "⬛" * (length - filled)
