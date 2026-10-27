from django.shortcuts import render

from collections import Counter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import GameResult

HISTORY_SIZE = 15


@login_required
def game_history(request):
    """Affiche les 15 dernières parties du joueur connecté."""
    results = list(
        GameResult.objects
        .filter(player=request.user)
        .select_related("opponent__profile")[:HISTORY_SIZE]
    )
    counts = Counter(r.result for r in results)
    context = {
        "results": results,
        "history_size": HISTORY_SIZE,
        "wins": counts[GameResult.Result.WIN],
        "losses": counts[GameResult.Result.LOSS],
        "draws": counts[GameResult.Result.DRAW],
    }
    return render(request, "history/history.html", context)