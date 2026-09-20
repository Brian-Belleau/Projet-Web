from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Profil de jeu lié à un utilisateur de la plateforme GarnoMiniGames."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
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

    def __str__(self):
        return self.pseudonym
