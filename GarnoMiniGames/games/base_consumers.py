import asyncio
import json

from channels.generic.websocket import AsyncWebsocketConsumer

from .presence import ACTIVE_PLAYERS, MESSAGES, check_join, get_identity


class RoomConsumerBase(AsyncWebsocketConsumer):
    ROOMS = None  # à définir dans les sous-classes pour ne pas avoir de room principale
    MAX_PLAYERS = 2
    GAME_PREFIX = "room"  # à écraser dans chaque sous-classe

    registered = False

    def _get_room(self):
        """Regarde information sur la room"""
        return self.ROOMS.setdefault(self.room_name, {
            "players": {},
            "user_ids": {},
            "scores": {},
            "is_auth": None,
            "button_visible": False,
            "round_active": False,
            "task": None,
        })

    def _release_identity(self):
        """Libère l'identité du joueur (il peut alors rejoindre une autre partie)."""
        active = ACTIVE_PLAYERS.get(self.identity)
        if self.registered and active and active[2] == self.channel_name:
            ACTIVE_PLAYERS.pop(self.identity, None)

    def _remove_player(self):
        """Nettoyage"""
        room = self.ROOMS.get(self.room_name)
        if not room or self.channel_name not in room["players"]:
            return None
        room["players"].pop(self.channel_name, None)
        room["user_ids"].pop(self.channel_name, None)
        room["scores"].pop(self.channel_name, None)
        for ch in room["scores"]:
            room["scores"][ch] = 0
        room["round_active"] = False
        room["button_visible"] = False
        if room["task"]:
            room["task"].cancel()
            room["task"] = None
        if not room["players"]:
            self.ROOMS.pop(self.room_name, None)
        return room

    async def _try_join(self):
        """Vérifie les règles puis inscrit le joueur dans la salle.

        Retourne un code de refus (voir presence.MESSAGES) ou None si accepté.
        """
        for _ in range(15):
            room = self.ROOMS.get(self.room_name)
            full = room and len(room["players"]) >= self.MAX_PLAYERS
            if self.identity not in ACTIVE_PLAYERS and not full:
                break
            await asyncio.sleep(0.1)
        room = self.ROOMS.get(self.room_name)
        reason = check_join(
            self.identity, self.is_auth, self.GAME_PREFIX,
            self.room_name, room, self.MAX_PLAYERS,
        )
        if reason:
            return reason

        room = self._get_room()
        if not room["players"]:
            room["is_auth"] = self.is_auth

        room["players"][self.channel_name] = self.username
        room["user_ids"][self.channel_name] = (
            self.scope["user"].pk if self.is_auth else None
        )
        room["scores"].setdefault(self.channel_name, 0)

        ACTIVE_PLAYERS[self.identity] = (
            self.GAME_PREFIX, self.room_name, self.channel_name
        )
        self.registered = True
        return None

    async def connect(self):
        """Connexion des joueurs au jeu"""
        if self.ROOMS is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} doit définir son propre ROOMS = {{}}"
            )
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"{self.GAME_PREFIX}_{self.room_name}"
        user = self.scope["user"]
        self.is_auth = user.is_authenticated
        self.username = (
            user.username
            if self.is_auth
            else f"Joueur-{self.channel_name[-4:]}"
        )
        self.identity = (
            get_identity(user, self.scope.get("session"))
            or f"anon:{self.channel_name}"
        )

        await self.accept()

        reason = await self._try_join()
        if reason:
            await self.send(text_data=json.dumps({
                "event": "rejected",
                "reason": reason,
                "message": MESSAGES[reason],
            }))
            await self.close(code=4003)
            return

        room = self.ROOMS[self.room_name]
        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.channel_layer.group_send(self.group_name, {
                "type": "player_joined",
                "players": list(room["players"].values()),
                "count": len(room["players"]),
            })
            if len(room["players"]) == 2:
                room["task"] = asyncio.create_task(self.start_round())
        except Exception:
            self._remove_player()
            self._release_identity()
            raise

    async def disconnect(self, close_code):
        """Déconnexion des joueurs"""
        if not self.registered:
            return
        room = self._remove_player()
        self._release_identity()
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if room and room["players"]:          # il reste quelqu'un à prévenir
            await self.channel_layer.group_send(self.group_name, {
                "type": "opponent_left",
            })
