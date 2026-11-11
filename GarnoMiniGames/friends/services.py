from django.core.cache import cache

PRESENCE_TTL = 45

STATUS_LABELS = {
    "online": "En ligne",
    "ingame": "En partie",
    "offline": "Hors ligne",
}


def mark_online(user):
    """Marque l'utilisateur comme en ligne pour les PRESENCE_TTL prochaines secondes."""
    cache.set(f"presence:{user.pk}", True, PRESENCE_TTL)


def mark_offline(user):
    """Retire immédiatement la présence (déconnexion explicite)."""
    cache.delete(f"presence:{user.pk}")


def get_status(user):
    """Retourne « ingame », « online » ou « offline »."""
    from games.presence import ACTIVE_PLAYERS

    if f"user:{user.pk}" in ACTIVE_PLAYERS:
        return "ingame"
    return "online" if cache.get(f"presence:{user.pk}") else "offline"
