import asyncio
import random
import json

from .base_consumers import RoomConsumerBase
from .results import update_draw_stats, update_game_stats

class PremierClicConsumer(RoomConsumerBase):
    ROOMS = {}
    GAME_PREFIX = "premier_clic"
    GAME_SLUG = "premier-clic"
    RECORD_SCORES = True
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

        if game_over:
            room["finished"] = True

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
            loser_score = None

            for channel_name in room["players"]:
                if channel_name != self.channel_name:
                    loser_id = room["user_ids"].get(channel_name)
                    loser_score = room["scores"].get(channel_name)

            await update_game_stats(
                winner_id, loser_id,
                game_slug=self.GAME_SLUG,
                winner_score=winner_score,
                loser_score=loser_score,
            )

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


class TicTacToeConsumer(RoomConsumerBase):
    """Tic-Tac-Toe multijoueur (2 joueurs). Réutilise RoomConsumerBase."""

    ROOMS = {}
    GAME_PREFIX = "tic_tac_toe"
    GAME_SLUG = "tic-tac-toe"

    WINNING_LINES = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # lignes
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # colonnes
        (0, 4, 8), (2, 4, 6),             # diagonales
    )

    async def receive(self, text_data):
        if not self.registered:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if data.get("action") == "move":
            await self.handle_move(data.get("index"))

    @classmethod
    def check_winner(cls, board):
        """Retourne (symbole gagnant, ligne gagnante) ou (None, None)."""
        for a, b, c in cls.WINNING_LINES:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a], [a, b, c]
        return None, None

    async def start_round(self):
        """Appelée par la base quand 2 joueurs sont présents : démarre la partie."""
        room = self.ROOMS.get(self.room_name)
        if not room or len(room["players"]) < 2:
            return

        channels = list(room["players"])
        random.shuffle(channels)
        room["symbols"] = {channels[0]: "X", channels[1]: "O"}
        room["board"] = [""] * 9
        room["turn"] = "X"
        room["round_active"] = True
        room["finished"] = False

        await self.channel_layer.group_send(self.group_name, {
            "type": "game_start",
        })

    async def handle_move(self, index):
        room = self.ROOMS.get(self.room_name)

        if (
            not room
            or not room.get("round_active")
            or room.get("finished")
            or not isinstance(index, int)
            or isinstance(index, bool)
            or not 0 <= index <= 8
        ):
            return

        symbol = room["symbols"].get(self.channel_name)
        if symbol is None or symbol != room["turn"] or room["board"][index]:
            return

        room["board"][index] = symbol
        winner_symbol, line = self.check_winner(room["board"])
        is_draw = winner_symbol is None and all(room["board"])

        if winner_symbol is None and not is_draw:
            room["turn"] = "O" if symbol == "X" else "X"
            await self.channel_layer.group_send(self.group_name, {
                "type": "move_made",
                "board": list(room["board"]),
                "turn": room["turn"],
            })
            return

        # Fin de partie
        room["finished"] = True
        room["round_active"] = False
        winner_name = room["players"][self.channel_name] if winner_symbol else None

        await self.channel_layer.group_send(self.group_name, {
            "type": "game_over",
            "board": list(room["board"]),
            "winner": winner_name,
            "line": line,
            "draw": is_draw,
        })

        if is_draw:
            await update_draw_stats(
                list(room["user_ids"].values()), game_slug=self.GAME_SLUG
            )
        else:
            winner_id = room["user_ids"].get(self.channel_name)
            loser_id = None
            for channel_name in room["players"]:
                if channel_name != self.channel_name:
                    loser_id = room["user_ids"].get(channel_name)
            await update_game_stats(
                winner_id, loser_id, game_slug=self.GAME_SLUG
            )

        self.ROOMS.pop(self.room_name, None)

    def _players_by_symbol(self, room):
        return {sym: room["players"][ch] for ch, sym in room["symbols"].items()
                if ch in room["players"]}

    # ----- Événements envoyés au client -----
    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            "event": "player_joined",
            "players": event["players"],
            "count": event["count"],
        }))

    async def game_start(self, event):
        room = self.ROOMS.get(self.room_name)
        if not room or self.channel_name not in room.get("symbols", {}):
            return
        await self.send(text_data=json.dumps({
            "event": "game_start",
            "you": room["symbols"][self.channel_name],
            "players": self._players_by_symbol(room),
            "board": room["board"],
            "turn": room["turn"],
        }))

    async def move_made(self, event):
        await self.send(text_data=json.dumps({
            "event": "move_made",
            "board": event["board"],
            "turn": event["turn"],
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            "event": "game_over",
            "board": event["board"],
            "winner": event["winner"],
            "line": event["line"],
            "draw": event["draw"],
        }))

    async def opponent_left(self, event):
        await self.send(text_data=json.dumps({"event": "opponent_left"}))

class Connect4Consumer(RoomConsumerBase):
    """Gère une partie multijoueur de Puissance 4."""

    ROOMS = {}
    GAME_PREFIX = "connect_4"

    ROWS = 6
    COLS = 7
    WINNING_LENGTH = 4

    async def receive(self, text_data):
        if not self.registered:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if data.get("action") == "move":
            await self.handle_move(data.get("column"))

    async def start_round(self):
        room = self.ROOMS.get(self.room_name)

        if not room or len(room["players"]) < 2:
            return

        channels = list(room["players"])
        random.shuffle(channels)

        room["symbols"] = {
            channels[0]: "R",
            channels[1]: "Y",
        }
        room["board"] = [
            [""] * self.COLS for _ in range(self.ROWS)
        ]
        room["turn"] = "R"
        room["round_active"] = True
        room["finished"] = False

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "game_start"},
        )

    @classmethod
    def check_winner(cls, board, row, col):
        symbol = board[row][col]
        directions = ((0, 1), (1, 0), (1, 1), (1, -1))

        for row_step, col_step in directions:
            line = [(row, col)]

            for sign in (1, -1):
                current_row = row + row_step * sign
                current_col = col + col_step * sign

                while (
                    0 <= current_row < cls.ROWS
                    and 0 <= current_col < cls.COLS
                    and board[current_row][current_col] == symbol
                ):
                    line.append((current_row, current_col))
                    current_row += row_step * sign
                    current_col += col_step * sign

            if len(line) >= cls.WINNING_LENGTH:
                return line

        return None

    async def handle_move(self, column):
        room = self.ROOMS.get(self.room_name)

        if (
            not room
            or not room.get("round_active")
            or room.get("finished")
            or not isinstance(column, int)
            or isinstance(column, bool)
            or not 0 <= column < self.COLS
        ):
            return

        symbol = room["symbols"].get(self.channel_name)

        if symbol is None or symbol != room["turn"]:
            return

        board = room["board"]
        row = None

        for row_index in range(self.ROWS - 1, -1, -1):
            if board[row_index][column] == "":
                row = row_index
                break

        if row is None:
            return

        board[row][column] = symbol
        winning_line = self.check_winner(board, row, column)

        is_draw = (
            winning_line is None
            and all(board_row.count("") == 0 for board_row in board)
        )

        if winning_line is None and not is_draw:
            room["turn"] = "Y" if symbol == "R" else "R"

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "move_made",
                    "board": board,
                    "turn": room["turn"],
                    "column": column,
                    "row": row,
                },
            )
            return

        room["finished"] = True
        room["round_active"] = False

        winner_name = (
            room["players"][self.channel_name]
            if winning_line is not None
            else None
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "game_over",
                "board": board,
                "winner": winner_name,
                "line": winning_line,
                "draw": is_draw,
            },
        )

        if is_draw:
            await update_draw_stats(list(room["user_ids"].values()))
        else:
            winner_id = room["user_ids"].get(self.channel_name)
            loser_id = None

            for channel_name in room["players"]:
                if channel_name != self.channel_name:
                    loser_id = room["user_ids"].get(channel_name)

            await update_game_stats(winner_id, loser_id)

        self.ROOMS.pop(self.room_name, None)

    def _players_by_symbol(self, room):
        return {
            symbol: room["players"][channel_name]
            for channel_name, symbol in room["symbols"].items()
            if channel_name in room["players"]
        }

    async def player_joined(self, event):
        await self.send(
            text_data=json.dumps({
                "event": "player_joined",
                "players": event["players"],
                "count": event["count"],
            })
        )

    async def game_start(self, event):
        room = self.ROOMS.get(self.room_name)

        if not room or self.channel_name not in room.get("symbols", {}):
            return

        await self.send(
            text_data=json.dumps({
                "event": "game_start",
                "you": room["symbols"][self.channel_name],
                "players": self._players_by_symbol(room),
                "board": room["board"],
                "turn": room["turn"],
            })
        )

    async def move_made(self, event):
        await self.send(
            text_data=json.dumps({
                "event": "move_made",
                "board": event["board"],
                "turn": event["turn"],
                "column": event["column"],
                "row": event["row"],
            })
        )

    async def game_over(self, event):
        await self.send(
            text_data=json.dumps({
                "event": "game_over",
                "board": event["board"],
                "winner": event["winner"],
                "line": event["line"],
                "draw": event["draw"],
            })
        )

    async def opponent_left(self, event):
        await self.send(
            text_data=json.dumps({
                "event": "opponent_left",
            })
        )
