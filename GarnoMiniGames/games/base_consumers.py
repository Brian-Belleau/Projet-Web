import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer

class RoomConsumerBase(AsyncWebsocketConsumer):
    ROOMS = None  # à définir dans les sous-classes pour ne pas avoir de room principale
    MAX_PLAYERS = 2
    GAME_PREFIX = "room"  # à écraser dans chaque sous-classe


    async def connect(self):
        if self.ROOMS is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} doit définir son propre ROOMS = {{}}"
            )
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"{self.GAME_PREFIX}_{self.room_name}"
        self.username = self.scope["user"].username if self.scope["user"].is_authenticated else f"Joueur-{self.channel_name[-4:]}"

        room = self.ROOMS.setdefault(self.room_name, {
            "players": {},
            "scores": {},
            "button_visible": False,
            "round_active": False,
            "task": None,
        })

        if len(room["players"]) >= self.MAX_PLAYERS:
            await self.close()
            return

        room["players"][self.channel_name] = self.username
        room["scores"].setdefault(self.channel_name, 0)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(self.group_name, {
            "type": "player_joined",
            "players": list(room["players"].values()),
            "count": len(room["players"]),
        })

        if len(room["players"]) == 2:
            room["task"] = asyncio.create_task(self.start_round())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        room = self.ROOMS.get(self.room_name)
        if not room or self.channel_name not in room["players"]:
            return

        room["players"].pop(self.channel_name, None)
        room["scores"].pop(self.channel_name, None)
        room["round_active"] = False
        room["button_visible"] = False
        if room["task"]:
            room["task"].cancel()

        if room["players"]:
            await self.channel_layer.group_send(self.group_name, {
                "type": "opponent_left",
            })
        else:
            self.ROOMS.pop(self.room_name, None)
