from django.db import models


class Jeu(models.Model):
    """Représente un jeu disponible sur GarnoMiniGames."""

    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    description_courte = models.CharField(
        max_length=140,
        blank=True,
        help_text="Une phrase affichée sur la carte de l'accueil.",
    )
    image = models.ImageField(upload_to='games/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    points_victoire = models.PositiveSmallIntegerField(
        default=10, verbose_name="Points gagnés en cas de victoire")
    points_defaite = models.PositiveSmallIntegerField(
        default=5, verbose_name="Points perdus en cas de défaite")

    class Meta:
        verbose_name = "jeu"
        verbose_name_plural = "jeux"

    def __str__(self):
        return self.nom
