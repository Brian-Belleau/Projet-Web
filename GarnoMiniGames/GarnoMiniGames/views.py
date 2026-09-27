from django.shortcuts import render

from games.models import Jeu


def home(request):
    """Affiche la page d'accueil avec le catalogue des jeux."""
    jeux = Jeu.objects.all().order_by('nom')
    return render(request, 'home.html', {'jeux': jeux})
    