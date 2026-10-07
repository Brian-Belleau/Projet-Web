import uuid

# Registre global des joueurs actuellement connectés à une partie :
ACTIVE_PLAYERS = {}

MESSAGES = {
    "self_play": "Tu ne peux pas jouer contre toi-même.",
    "already_in_game": (
        "Tu es déjà dans une partie (autre onglet ou autre appareil). "
        "Ferme-la avant d'en rejoindre une autre."
    ),
    "room_full": "Cette partie est déjà pleine.",
    "room_guests_only": (
        "Cette partie est réservée aux invités. "
        "Déconnecte-toi pour la rejoindre."
    ),
    "room_users_only": (
        "Cette partie est réservée aux joueurs connectés. "
        "Connecte-toi pour la rejoindre."
    ),
}


def get_identity(user, session, create=False):
    """Identifie un joueur de façon stable.
    Retourne None si un invité n'a pas encore d'identifiant.
    """
    if user.is_authenticated:
        return f"user:{user.pk}"

    if session is None:
        return None

    guest_id = session.get("guest_id")
    if guest_id is None:
        if not create:
            return None
        guest_id = uuid.uuid4().hex
        session["guest_id"] = guest_id
    return f"guest:{guest_id}"


def check_join(identity, is_auth, game, room_name, room, max_players):
    """Vérifie qu'un joueur a le droit de rejoindre une salle. """
    active = ACTIVE_PLAYERS.get(identity)
    if active is not None:
        active_game, active_room, _ = active
        if active_game == game and active_room == room_name:
            return "self_play"
        return "already_in_game"

    if room and room["players"]:
        if len(room["players"]) >= max_players:
            return "room_full"
        # Une salle est soit 100 % invités, soit 100 % utilisateurs connectés
        if room["is_auth"] != is_auth:
            return "room_users_only" if room["is_auth"] else "room_guests_only"

    return None
