from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from .models import Friendship
from .views import login_required
from .services import get_friends, mark_online


@login_required
@never_cache
def poll(request):
    """Nombre de demandes reçues + empreinte des relations (pour détecter un changement)."""
    mark_online(request.user)
    links = Friendship.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user)
    ).order_by("pk")
    pending = sum(
        1 for l in links
        if l.to_user_id == request.user.pk and l.status == Friendship.PENDING
    )
    signature = ",".join(f"{l.pk}:{l.status}" for l in links)
    friends = get_friends(request.user)
    statuses = {f["profile"].pseudonym: f["status"] for f in friends}

    return JsonResponse({
        "pending": pending,
        "signature": signature,
        "statuses": statuses,
        "online_count": sum(1 for v in statuses.values() if v != "offline"),
    })
