from .models import Friendship


def pending_friend_requests(request):
    """Ajoute le nombre de demandes d'amis reçues en attente (menu du haut)."""
    count = 0
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        count = Friendship.objects.filter(
            to_user=user,
            status=Friendship.PENDING
        ).count()
    return {"pending_friend_requests_count": count}
