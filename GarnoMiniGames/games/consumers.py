import asyncio
import random
import json

from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F

from .base_consumers import RoomConsumerBase


@sync_to_async
def update_game_stats(winner_id, loser_id):
    """Met à jour les statistiques des deux joueurs après une victoire."""

    from accounts.models import Profile

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


@sync_to_async
def update_draw_stats(user_ids):
    """Compte une partie jouée pour chaque joueur connecté (égalité)."""

    from accounts.models import Profile

    ids = [uid for uid in user_ids if uid is not None]
    if ids:
        Profile.objects.filter(user_id__in=ids).update(
            games_played=F("games_played") + 1,
        )


class PremierClicConsumer(RoomConsumerBase):
    ROOMS = {}
    GAME_PREFIX = "premier_clic"
    WINNING_SCORE = 5

    async def receive(self, text_data):
        if not self.registered:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if data.get("action") == "click":
            await self.handle_click()

    async def handle_click(self):
        room = self.ROOMS.get(self.room_name)

        if not room or not room["round_active"] or not room["button_visible"]:
            return

        room["round_active"] = False
        room["button_visible"] = False
        room["scores"][self.channel_name] += 1

        winner_score = room["scores"][self.channel_name]
        game_over = winner_score >= self.WINNING_SCORE

        await self.channel_layer.group_send(self.group_name, {
            "type": "round_result",
            "winner": room["players"][self.channel_name],
            "scores": {
                room["players"][ch]: s
                for ch, s in room["scores"].items()
            },
            "game_over": game_over,
        })

        if game_over:
            winner_id = room["user_ids"].get(self.channel_name)

            loser_id = None

            for channel_name in room["players"]:
                if channel_name != self.channel_name:
                    loser_id = room["user_ids"].get(channel_name)

            await update_game_stats(winner_id, loser_id)

            self.ROOMS.pop(self.room_name, None)
        else:
            room["task"] = asyncio.create_task(self.start_round())

    async def start_round(self):
        room = self.ROOMS.get(self.room_name)
        if not room or len(room["players"]) < 2:
            return

        await self.channel_layer.group_send(self.group_name, {"type": "round_waiting"})
        await asyncio.sleep(random.uniform(2, 5))

        room = self.ROOMS.get(self.room_name)
        if not room:
            return

        room["round_active"] = True
        room["button_visible"] = True
        await self.channel_layer.group_send(self.group_name, {"type": "show_button"})

    # peut etre a mettre dans le base_consumer.py
    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            "event": "player_joined",
            "players": event["players"],
            "count": event["count"],
        }))

    async def round_waiting(self, event):
        await self.send(text_data=json.dumps({"event": "waiting"}))

    async def show_button(self, event):
        await self.send(text_data=json.dumps({"event": "show_button"}))

    async def round_result(self, event):
        await self.send(text_data=json.dumps({
            "event": "round_result",
            "winner": event["winner"],
            "scores": event["scores"],
            "game_over": event["game_over"],
        }))

    # peut etre a mettre dans le base_consumer.py
    async def opponent_left(self, event):
        await self.send(text_data=json.dumps({"event": "opponent_left"}))
