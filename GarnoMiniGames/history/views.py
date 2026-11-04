from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render

from .models import GameResult

PAGE_SIZE = 15


@login_required
def game_history(request):
    """Affiche l'historique paginé des parties du joueur connecté."""
    queryset = (
        GameResult.objects
        .filter(player=request.user)
        .select_related("opponent__profile")
    )

    stats = queryset.aggregate(
        wins=Count("pk", filter=Q(result=GameResult.Result.WIN)),
        losses=Count("pk", filter=Q(result=GameResult.Result.LOSS)),
        draws=Count("pk", filter=Q(result=GameResult.Result.DRAW)),
    )

    paginator = Paginator(queryset, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "results": page_obj,
        "total": paginator.count,
        **stats,
    }
    return render(request, "history/history.html", context)