from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Utilisateur personnalisé pour l'application GarnoMiniGames."""
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"


class Profile(models.Model):
    """Profil de jeu lié à un utilisateur de la plateforme GarnoMiniGames."""
    user = models.OneToOneField(
        "CustomUser",
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Utilisateur",
    )
    pseudonym = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Pseudonyme",
        help_text="Votre nom d'affichage unique dans les jeux.",
    )
    bio = models.TextField(
        max_length=160,
        blank=True,
        verbose_name="Biographie",
        help_text="Décrivez-vous en quelques mots.",
    )
    photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True,
        verbose_name="Photo de profil",
    )
    games_played = models.PositiveIntegerField(
        default=0,
        verbose_name="Parties jouées",
    )
    wins = models.PositiveIntegerField(
        default=0,
        verbose_name="Victoires",
    )
    losses = models.PositiveIntegerField(
        default=0,
        verbose_name="Défaites",
    )

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"
        ordering = ["pseudonym"]

    @property
    def win_rate(self):
        if self.games_played == 0:
            return 0
        return round((self.wins / self.games_played) * 100)

    @property
    def total_games(self):
        return self.games_played

    def __str__(self):
        return self.pseudonym
