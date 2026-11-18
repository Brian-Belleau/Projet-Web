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

    async def game_start(self, event):
        room = self.ROOMS.get(self.room_name)

        if not room or self.channel_name not in room["players"]:
            return

        await self.send(
            text_data=json.dumps(
                {
                    "event": "game_start",
                    "players": list(room["players"].values()),
                    "scores": {
                        room["players"][ch]: score
                        for ch, score in room["scores"].items()
                    },
                }
            )
        )

    async def receive(self, text_data):
        if not self.registered:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if data.get("action") == "click":
            await self.handle_click()
        elif data.get("action") == "rematch":
            await self.request_rematch()

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

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "round_result",
                "winner": room["players"][self.channel_name],
                "winner_channel": self.channel_name,
                "scores": {room["players"][ch]: s for ch, s in room["scores"].items()},
                "game_over": game_over,
            },
        )

        if game_over:
            winner_id = room["user_ids"].get(self.channel_name)

            loser_id = None
            loser_score = None

            for channel_name in room["players"]:
                if channel_name != self.channel_name:
                    loser_id = room["user_ids"].get(channel_name)
                    loser_score = room["scores"].get(channel_name)

            await update_game_stats(
                winner_id,
                loser_id,
                game_slug=self.GAME_SLUG,
                winner_score=winner_score,
                loser_score=loser_score,
            )

        else:
            room["task"] = asyncio.create_task(self.start_round())

    async def start_round(self):
        room = self.ROOMS.get(self.room_name)

        if not room or len(room["players"]) < 2:
            return

        room["finished"] = False
        room["round_active"] = False
        room["button_visible"] = False

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "round_waiting"},
        )

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "game_start"},
        )

        await asyncio.sleep(random.uniform(2, 5))

        room = self.ROOMS.get(self.room_name)

        if not room or len(room["players"]) < 2:
            return

        room["round_active"] = True
        room["button_visible"] = True

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "show_button"},
        )

    # peut etre a mettre dans le base_consumer.py
    async def player_joined(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "player_joined",
                    "players": event["players"],
                    "count": event["count"],
                }
            )
        )

    async def round_waiting(self, event):
        await self.send(text_data=json.dumps({"event": "waiting"}))

    async def show_button(self, event):
        await self.send(text_data=json.dumps({"event": "show_button"}))

    async def round_result(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "round_result",
                    "winner": event["winner"],
                    "scores": event["scores"],
                    "game_over": event["game_over"],
                    "you_won": self.channel_name == event["winner_channel"],
                }
            )
        )

    # peut etre a mettre dans le base_consumer.py
    async def opponent_left(self, event):
        await self.send(text_data=json.dumps({"event": "opponent_left"}))


class TicTacToeConsumer(RoomConsumerBase):
    """Tic-Tac-Toe multijoueur (2 joueurs). Réutilise RoomConsumerBase."""

    ROOMS = {}
    GAME_PREFIX = "tic_tac_toe"
    GAME_SLUG = "tic-tac-toe"

    WINNING_LINES = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),  # lignes
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),  # colonnes
        (0, 4, 8),
        (2, 4, 6),  # diagonales
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

        elif data.get("action") == "rematch":
            await self.request_rematch()

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

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "game_start",
            },
        )

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
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "move_made",
                    "board": list(room["board"]),
                    "turn": room["turn"],
                },
            )
            return

        # Fin de partie
        room["finished"] = True
        room["round_active"] = False
        winner_name = room["players"][self.channel_name] if winner_symbol else None

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "game_over",
                "board": list(room["board"]),
                "winner": winner_name,
                "line": line,
                "draw": is_draw,
            },
        )

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
            await update_game_stats(winner_id, loser_id, game_slug=self.GAME_SLUG)

    def _players_by_symbol(self, room):
        return {
            sym: room["players"][ch]
            for ch, sym in room["symbols"].items()
            if ch in room["players"]
        }

    # ----- Événements envoyés au client -----
    async def player_joined(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "player_joined",
                    "players": event["players"],
                    "count": event["count"],
                }
            )
        )

    async def game_start(self, event):
        room = self.ROOMS.get(self.room_name)
        if not room or self.channel_name not in room.get("symbols", {}):
            return
        await self.send(
            text_data=json.dumps(
                {
                    "event": "game_start",
                    "you": room["symbols"][self.channel_name],
                    "players": self._players_by_symbol(room),
                    "board": room["board"],
                    "turn": room["turn"],
                }
            )
        )

    async def move_made(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "move_made",
                    "board": event["board"],
                    "turn": event["turn"],
                }
            )
        )

    async def game_over(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "game_over",
                    "board": event["board"],
                    "winner": event["winner"],
                    "line": event["line"],
                    "draw": event["draw"],
                }
            )
        )

    async def opponent_left(self, event):
        await self.send(text_data=json.dumps({"event": "opponent_left"}))


class Connect4Consumer(RoomConsumerBase):
    """Gère une partie multijoueur de Connect 4."""

    ROOMS = {}
    GAME_PREFIX = "connect_4"
    GAME_SLUG = "connect-4"

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

        elif data.get("action") == "rematch":
            await self.request_rematch()

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
        room["board"] = [[""] * self.COLS for _ in range(self.ROWS)]
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

        is_draw = winning_line is None and all(
            board_row.count("") == 0 for board_row in board
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
            room["players"][self.channel_name] if winning_line is not None else None
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
            await update_draw_stats(
                list(room["user_ids"].values()), game_slug=self.GAME_SLUG
            )
        else:
            winner_id = room["user_ids"].get(self.channel_name)
            loser_id = None

            for channel_name in room["players"]:
                if channel_name != self.channel_name:
                    loser_id = room["user_ids"].get(channel_name)

            await update_game_stats(winner_id, loser_id, game_slug=self.GAME_SLUG)

    def _players_by_symbol(self, room):
        return {
            symbol: room["players"][channel_name]
            for channel_name, symbol in room["symbols"].items()
            if channel_name in room["players"]
        }

    async def player_joined(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "player_joined",
                    "players": event["players"],
                    "count": event["count"],
                }
            )
        )

    async def game_start(self, event):
        room = self.ROOMS.get(self.room_name)

        if not room or self.channel_name not in room.get("symbols", {}):
            return

        await self.send(
            text_data=json.dumps(
                {
                    "event": "game_start",
                    "you": room["symbols"][self.channel_name],
                    "players": self._players_by_symbol(room),
                    "board": room["board"],
                    "turn": room["turn"],
                }
            )
        )

    async def move_made(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "move_made",
                    "board": event["board"],
                    "turn": event["turn"],
                    "column": event["column"],
                    "row": event["row"],
                }
            )
        )

    async def game_over(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "game_over",
                    "board": event["board"],
                    "winner": event["winner"],
                    "line": event["line"],
                    "draw": event["draw"],
                }
            )
        )

    async def opponent_left(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "opponent_left",
                }
            )
        )

class RPCLSConsumer(RoomConsumerBase):
    """Roche-Papier-Ciseaux-Lézard-Spock : premier à 3 manches gagnées."""

    ROOMS = {}
    GAME_PREFIX = "r_p_c_l_s"
    GAME_SLUG = "r-p-c-l-s"
    RECORD_SCORES = True
    WINNING_SCORE = 3

    CHOICES = ("roche", "papier", "ciseaux", "lezard", "spock")

    # (gagnant, perdant): La Phrase Affichée
    RULES = {
        ("ciseaux", "papier"): "Les ciseaux coupent le papier",
        ("papier", "roche"): "Le papier recouvre la roche",
        ("roche", "lezard"): "La roche écrase le lézard",
        ("lezard", "spock"): "Le lézard empoisonne Spock",
        ("spock", "ciseaux"): "Spock casse les ciseaux",
        ("ciseaux", "lezard"): "Les ciseaux décapitent le lézard",
        ("lezard", "papier"): "Le lézard mange le papier",
        ("papier", "spock"): "Le papier réfute Spock",
        ("spock", "roche"): "Spock vaporise la roche",
        ("roche", "ciseaux"): "La roche écrase les ciseaux",
    }

    async def receive(self, text_data):
        if not self.registered:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if not isinstance(data, dict):
            return

        if data.get("action") == "choose":
            await self.handle_choice(data.get("choice"))
        elif data.get("action") == "rematch":
            await self.request_rematch()

    async def start_round(self):
        """Appelée par la base quand 2 joueurs sont présents (et à la revanche)."""
        room = self.ROOMS.get(self.room_name)
        if not room or len(room["players"]) < 2:
            return

        room["finished"] = False
        room["round"] = 0
        for channel_name in room["scores"]:
            room["scores"][channel_name] = 0

        await self._begin_round(room)

    async def _begin_round(self, room):
        room["round"] += 1
        room["choices"] = {}
        room["round_active"] = True

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "round_start"},
        )

    async def handle_choice(self, choice):
        room = self.ROOMS.get(self.room_name)

        if (
            not room
            or not room.get("round_active")
            or room.get("finished")
            or self.channel_name not in room["players"]
            or choice not in self.CHOICES
            or self.channel_name in room["choices"]
        ):
            return

        room["choices"][self.channel_name] = choice

        if len(room["choices"]) < 2:
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "player_chose", "channel": self.channel_name},
            )
            return

        await self._resolve_round(room)

    async def _resolve_round(self, room):
        room["round_active"] = False

        channel_a, channel_b = list(room["players"])
        choice_a = room["choices"][channel_a]
        choice_b = room["choices"][channel_b]

        winner_channel = None
        reason = None
        if (choice_a, choice_b) in self.RULES:
            winner_channel, loser_channel = channel_a, channel_b
            reason = self.RULES[(choice_a, choice_b)]
        elif (choice_b, choice_a) in self.RULES:
            winner_channel, loser_channel = channel_b, channel_a
            reason = self.RULES[(choice_b, choice_a)]

        game_over = False
        if winner_channel is not None:
            room["scores"][winner_channel] += 1
            game_over = room["scores"][winner_channel] >= self.WINNING_SCORE

        if game_over:
            room["finished"] = True

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "round_result",
                "choices": dict(room["choices"]),
                "scores": dict(room["scores"]),
                "winner_channel": winner_channel,
                "reason": reason,
                "game_over": game_over,
            },
        )

        if game_over:
            await update_game_stats(
                room["user_ids"].get(winner_channel),
                room["user_ids"].get(loser_channel),
                game_slug=self.GAME_SLUG,
                winner_score=room["scores"][winner_channel],
                loser_score=room["scores"][loser_channel],
            )
        else:
            await self._begin_round(room)

    def _opponent_channel(self, room):
        return next(ch for ch in room["players"] if ch != self.channel_name)

    async def player_joined(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "player_joined",
                    "players": event["players"],
                    "count": event["count"],
                }
            )
        )

    async def round_start(self, event):
        room = self.ROOMS.get(self.room_name)
        if not room or len(room["players"]) < 2:
            return
        opponent = self._opponent_channel(room)

        await self.send(
            text_data=json.dumps(
                {
                    "event": "round_start",
                    "round": room["round"],
                    "you": room["players"][self.channel_name],
                    "opponent": room["players"][opponent],
                    "my_score": room["scores"][self.channel_name],
                    "opponent_score": room["scores"][opponent],
                }
            )
        )

    async def player_chose(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "player_chose",
                    "by_you": event["channel"] == self.channel_name,
                }
            )
        )

    async def round_result(self, event):
        room = self.ROOMS.get(self.room_name)
        if not room or len(room["players"]) < 2:
            return
        opponent = self._opponent_channel(room)

        winner = event["winner_channel"]
        if winner is None:
            outcome = "draw"
        else:
            outcome = "win" if winner == self.channel_name else "loss"

        await self.send(
            text_data=json.dumps(
                {
                    "event": "round_result",
                    "outcome": outcome,
                    "my_choice": event["choices"][self.channel_name],
                    "opponent_choice": event["choices"][opponent],
                    "reason": event["reason"],
                    "my_score": event["scores"][self.channel_name],
                    "opponent_score": event["scores"][opponent],
                    "game_over": event["game_over"],
                }
            )
        )

    async def opponent_left(self, event):
        await self.send(text_data=json.dumps({"event": "opponent_left"}))
