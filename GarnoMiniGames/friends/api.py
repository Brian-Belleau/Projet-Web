from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from games.models import Jeu
from .models import Friendship, GameInvitation
from .views import login_required
from .services import get_friends, mark_online


def _room_is_joinable(invitation):
    """Vrai tant que la partie de l'invitation existe"""
    from games.presence import PENDING_ROOMS, _purge_pending
    from games.views import JEUX_MULTIJOUEUR

    if invitation.game_slug not in JEUX_MULTIJOUEUR:
        return False
    _, consumer = JEUX_MULTIJOUEUR[invitation.game_slug]
    room = consumer.ROOMS.get(invitation.room_name)
    if room is not None:
        return (
            bool(room["players"])
            and not room.get("finished")
            and len(room["players"]) < consumer.MAX_PLAYERS
        )
    _purge_pending()
    return (consumer.GAME_PREFIX, invitation.room_name) in PENDING_ROOMS


@login_required
@never_cache
def poll(request):
    """Demandes reçues, invitations de jeu et empreinte des relations."""
    mark_online(request.user)
    links = Friendship.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user)
    ).order_by("pk")
    pending = sum(
        1 for l in links
        if l.to_user_id == request.user.pk and l.status == Friendship.PENDING
    )
    signature = ",".join(f"{l.pk}:{l.status}" for l in links)

    cutoff = timezone.now() - timedelta(seconds=GameInvitation.TTL_SECONDS)
    GameInvitation.objects.filter(
        to_user=request.user,
        created_at__lt=cutoff - timedelta(hours=1),
    ).delete()
    invitations = list(
        GameInvitation.objects.filter(
            to_user=request.user,
            status=GameInvitation.PENDING,
            created_at__gte=cutoff,
        ).select_related("from_user__profile")
    )
    stale = [i for i in invitations if not _room_is_joinable(i)]
    if stale:
        GameInvitation.objects.filter(
            pk__in=[i.pk for i in stale]).delete()
        stale_ids = {i.pk for i in stale}
        invitations = [i for i in invitations if i.pk not in stale_ids]
    game_names = dict(
        Jeu.objects.filter(
            slug__in={i.game_slug for i in invitations}
        ).values_list("slug", "nom")
    )

    friends = get_friends(request.user)
    statuses = {f["profile"].pseudonym: f["status"] for f in friends}

    return JsonResponse({
        "pending": pending,
        "signature": signature,
        "statuses": statuses,
        "online_count": sum(1 for v in statuses.values() if v != "offline"),
        "invitations": [
            {
                "id": i.pk,
                "sent_at": int(i.created_at.timestamp()),
                "from": i.from_user.profile.pseudonym,
                "game": game_names.get(i.game_slug, i.game_slug),
                "join_url": reverse("friends:join_invitation", args=[i.pk]),
            }
            for i in invitations
        ],
    })
