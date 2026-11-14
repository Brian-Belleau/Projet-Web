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
