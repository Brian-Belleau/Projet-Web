from django.shortcuts import render, get_object_or_404
from .models import Jeu


def jeu_detail(request, pk):
    """Affiche le détail d'un jeu, ou refuse l'accès s'il est inactif."""
    jeu = get_object_or_404(Jeu, pk=pk)

    if not jeu.actif:
        messages.error(request, "Ce jeu n'est pas disponible actuellement.")
        return redirect('home')

    return render(request, 'games/jeu_detail.html', {'jeu': jeu})