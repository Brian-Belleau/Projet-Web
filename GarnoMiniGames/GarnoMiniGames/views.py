from django.shortcuts import render

from games.models import Jeu


def home(request):
    """Affiche la page d'accueil avec le catalogue des jeux."""
    jeux = Jeu.objects.all().order_by('date_creation')
    return render(request, 'home.html', {'jeux': jeux})
