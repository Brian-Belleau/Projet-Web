from django.core.paginator import Paginator
from django.db.models import ExpressionWrapper, F, FloatField, Q
from django.db.models.functions import Cast
from django.shortcuts import render

from accounts.models import Profile

PLAYERS_PER_PAGE = 10

# Un joueur doit avoir joué au moins ce nombre de parties pour être classé.
MIN_GAMES_PLAYED = 1

# (champ annoté, sens)
RANKING_KEYS = (
    ("win_rate_calc", "desc"),
    ("games_played", "desc"),
    ("pseudonym", "asc"),
)


def ranked_profiles():
    """Retourne les profils classés, du meilleur au moins bon."""
    order = [
        F(field).desc() if direction == "desc" else F(field).asc()
        for field, direction in RANKING_KEYS
    ]
    return (
        Profile.objects
        .filter(games_played__gte=MIN_GAMES_PLAYED)
        .annotate(
            win_rate_calc=ExpressionWrapper(
                (Cast("wins", FloatField())
                 + Cast("draws", FloatField()) * 0.5)
                * 100 / F("games_played"),
                output_field=FloatField(),
            )
        )
        .order_by(*order)
    )


def _ranked_before(profile):
    """Q() des profils classés strictement avant `profile`.

    Comparaison lexicographique sur RANKING_KEYS : meilleur sur le critère 1,
    ou égal sur le 1 et meilleur sur le 2, etc.
    """
    before = Q()
    equal_so_far = Q()
    for field, direction in RANKING_KEYS:
        value = getattr(profile, field)
        lookup = "gt" if direction == "desc" else "lt"
        before |= equal_so_far & Q(**{f"{field}__{lookup}": value})
        equal_so_far &= Q(**{field: value})
    return before


def get_player_position(user):
    """Retourne (profil, position) du joueur ou (None, None)
    s'il n'est pas encore classé."""
    me = ranked_profiles().filter(user=user).first()
    if me is None:
        return None, None
    position = ranked_profiles().filter(_ranked_before(me)).count() + 1
    return me, position


def ranking(request):
    """Page de classement (10 joueurs par page.)"""
    paginator = Paginator(ranked_profiles(), PLAYERS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )

    my_profile, my_position = (None, None)
    if request.user.is_authenticated:
        my_profile, my_position = get_player_position(request.user)

    context = {
        "page_obj": page_obj,
        "page_range": page_range,
        "ellipsis": Paginator.ELLIPSIS,
        "total_players": paginator.count,
        "my_profile": my_profile,
        "my_position": my_position,
    }
    return render(request, "ranking/ranking.html", context)
