import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer

class RoomConsumerBase(AsyncWebsocketConsumer):
    ROOMS = None  # à définir dans les sous-classes pour ne pas avoir de room principale
    MAX_PLAYERS = 2
    GAME_PREFIX = "room"  # à écraser dans chaque sous-classe


    def _get_room(self):
        """Regarde information sur la room"""
        return self.ROOMS.setdefault(self.room_name, {
            "players": {},
            "scores": {},
            "button_visible": False,
            "round_active": False,
            "task": None,
        })

    def _remove_player(self):
        """Nettoyage"""
        room = self.ROOMS.get(self.room_name)
        if not room or self.channel_name not in room["players"]:
            return None
        room["players"].pop(self.channel_name, None)
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

    async def connect(self):
        """Connexion des joueurs au jeu"""
        if self.ROOMS is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} doit définir son propre ROOMS = {{}}"
            )
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"{self.GAME_PREFIX}_{self.room_name}"
        self.username = (
            self.scope["user"].username
            if self.scope["user"].is_authenticated
            else f"Joueur-{self.channel_name[-4:]}"
        )

        room = self._get_room()
        print("CONNECT", self.channel_name[-6:], "déjà présents:", [c[-6:] for c in room["players"]])

        if len(room["players"]) >= self.MAX_PLAYERS:
            # Laisse le temps à une ancienne connexion (retour, rechargement) de se fermer
            await asyncio.sleep(1)
            room = self._get_room()
            if len(room["players"]) >= self.MAX_PLAYERS:
                await self.close()
                return

        room["players"][self.channel_name] = self.username
        room["scores"].setdefault(self.channel_name, 0)

        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.channel_layer.group_send(self.group_name, {
                "type": "player_joined",
                "players": list(room["players"].values()),
                "count": len(room["players"]),
            })
            if len(room["players"]) == 2:
                room["task"] = asyncio.create_task(self.start_round())
        except Exception:
            self._remove_player()
            raise

    async def disconnect(self, close_code):
        """Déconnexion des joueurs"""
        print("DISCONNECT", self.channel_name[-6:])
        room = self._remove_player()          # d'abord, sans await
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if room and room["players"]:          # il reste quelqu'un à prévenir
            await self.channel_layer.group_send(self.group_name, {
                "type": "opponent_left",
            })