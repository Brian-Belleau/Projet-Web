from accounts.models import Profile
from games.models import Jeu

from .models import GameResult

_OPPOSITE = {
    GameResult.Result.WIN: GameResult.Result.LOSS,
    GameResult.Result.LOSS: GameResult.Result.WIN,
    GameResult.Result.DRAW: GameResult.Result.DRAW,
}


def record_game(game_slug, user_a_id, user_b_id, result_a,
                score_a=None, score_b=None, forfeit=False):
    """Enregistre une partie dans l'historique des deux joueurs."""

    if user_a_id is None or user_b_id is None:
        return []

    pseudonyms = dict(
        Profile.objects.filter(user_id__in=[user_a_id, user_b_id])
        .values_list("user_id", "pseudonym")
    )
    jeu = Jeu.objects.filter(slug=game_slug).first() if game_slug else None
    jeu_nom = jeu.nom if jeu else (game_slug or "Jeu inconnu")

    sides = (
        (user_a_id, user_b_id, result_a, score_a, score_b),
        (user_b_id, user_a_id, _OPPOSITE[result_a], score_b, score_a),
    )
    rows = [
        GameResult(
            player_id=me,
            opponent_id=other,
            opponent_name=pseudonyms.get(other, "Joueur inconnu"),
            jeu=jeu,
            jeu_nom=jeu_nom,
            result=result,
            player_score=my_score,
            opponent_score=other_score,
            forfeit=forfeit,
        )
        for me, other, result, my_score, other_score in sides
    ]
    GameResult.objects.bulk_create(rows)
    return rows