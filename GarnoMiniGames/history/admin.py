from django.contrib import admin

from .models import GameResult


@admin.register(GameResult)
class GameResultAdmin(admin.ModelAdmin):
    list_display = ("player", "jeu_nom", "result", "opponent_name",
                    "player_score", "opponent_score", "forfeit", "played_at")
    list_filter = ("result", "jeu_nom", "forfeit")
    search_fields = ("player__username", "opponent_name")