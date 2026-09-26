from django.db import models


class Jeu(models.Model):
    """Représente un jeu disponible sur GarnoMiniGames."""

    nom = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='games/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "jeu"
        verbose_name_plural = "jeux"
        
    def __str__(self):
        return self.nom