from django.core.cache import cache
from django.db.models import Q

from .models import Friendship

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


def get_friends(user):
    """Retourne la liste des amis acceptés, avec leur statut, triée par pseudonyme."""
    friendships = Friendship.objects.filter(
        Q(from_user=user) | Q(to_user=user),
        status=Friendship.ACCEPTED,
    ).select_related("from_user__profile", "to_user__profile")

    friends = []
    for friendship in friendships:
        other = friendship.to_user if friendship.from_user_id == user.pk else friendship.from_user
        status = get_status(other)
        friends.append({
            "friendship": friendship,
            "profile": other.profile,
            "status": status,
            "status_label": STATUS_LABELS[status],
        })
    friends.sort(key=lambda item: item["profile"].pseudonym.lower())
    return friends
