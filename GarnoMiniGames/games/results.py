from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F


@sync_to_async
def update_game_stats(winner_id, loser_id, game_slug=None,
                      winner_score=None, loser_score=None, forfeit=False):
    """Met à jour les statistiques ET l'historique après une victoire.

    Les deux opérations sont dans la même transaction : l'historique ne peut
    jamais être en désaccord avec les compteurs du profil.
    """

    from accounts.models import Profile
    from history.models import GameResult
    from history.services import record_game

    with transaction.atomic():
        if winner_id is not None:
            Profile.objects.filter(user_id=winner_id).update(
                games_played=F("games_played") + 1,
                wins=F("wins") + 1,
            )

        if loser_id is not None:
            Profile.objects.filter(user_id=loser_id).update(
                games_played=F("games_played") + 1,
                losses=F("losses") + 1,
            )

        record_game(
            game_slug, winner_id, loser_id, GameResult.Result.WIN,
            winner_score, loser_score, forfeit,
        )


@sync_to_async
def update_draw_stats(user_ids, game_slug=None):
    """Compte une égalité (stats + historique) pour chaque joueur connecté."""

    from accounts.models import Profile
    from history.models import GameResult
    from history.services import record_game

    ids = [uid for uid in user_ids if uid is not None]
    user_a, user_b = (list(user_ids) + [None, None])[:2]

    with transaction.atomic():
        if ids:
            Profile.objects.filter(user_id__in=ids).update(
                games_played=F("games_played") + 1,
                draws=F("draws") + 1,
            )
        record_game(game_slug, user_a, user_b, GameResult.Result.DRAW)