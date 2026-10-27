from django.db import models

# Create your models here.

from django.conf import settings
from django.db import models
from django.utils import timezone


class GameResult(models.Model):
    """Model d'une partie terminée."""

    class Result(models.TextChoices):
        WIN = "win", "Victoire"
        LOSS = "loss", "Défaite"
        DRAW = "draw", "Égalité"

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="game_results",
        verbose_name="Joueur",
    )

    opponent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Adversaire",
    )

    opponent_name = models.CharField(max_length=30, verbose_name="Nom de l'adversaire")
    jeu = models.ForeignKey(
        "games.Jeu",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Jeu",
    )

    jeu_nom = models.CharField(max_length=100, verbose_name="Nom du jeu")
    result = models.CharField(max_length=4, choices=Result.choices, verbose_name="Résultat")
    player_score = models.PositiveSmallIntegerField(null=True, blank=True)
    opponent_score = models.PositiveSmallIntegerField(null=True, blank=True)
    forfeit = models.BooleanField(default=False, verbose_name="Par abandon")
    played_at = models.DateTimeField(default=timezone.now, verbose_name="Date")

    class Meta:
        verbose_name = "résultat de partie"
        verbose_name_plural = "résultats de parties"
        ordering = ["-played_at", "-id"]
        indexes = [models.Index(fields=["player", "-played_at"])]

    def __str__(self):
        return f"{self.player} - {self.jeu_nom} - {self.get_result_display()}"