from django.shortcuts import render, get_object_or_404, redirect
from .models import Jeu
from django.contrib import messages

def premier_clic(request, room_name):
    return render(request, "games/premier_clic.html", {"room_name": room_name})

def jeu_detail(request, pk):
    """Affiche le détail d'un jeu, ou refuse l'accès s'il est inactif."""
    jeu = get_object_or_404(Jeu, pk=pk)

    if not jeu.actif:
        messages.error(request, "Ce jeu n'est pas disponible actuellement.")
        return redirect('home')

    return render(request, 'games/jeu_detail.html', {'jeu': jeu})