from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
import uuid
import re

from .models import Jeu
from .consumers import PremierClicConsumer
from .forms import RejoindreJeuForm


def premier_clic(request, room_name):
    return render(request, "games/premier_clic.html", {"room_name": room_name})


def jeu_detail(request, slug):
    """Affiche le détail d'un jeu, ou refuse l'accès s'il est inactif."""
    jeu = get_object_or_404(Jeu, slug=slug)

    if not jeu.actif:
        messages.error(request, "Ce jeu n'est pas disponible actuellement.")
        return redirect('home')

    form = RejoindreJeuForm()

    return render(
        request,
        'games/jeu_detail.html',
        {
            'jeu': jeu,
            'form': form,
        }
    )


def lancer_jeu(request, slug):
    """Lance le jeu sélectionné."""

    jeu = get_object_or_404(Jeu, slug=slug)

    if not jeu.actif:
        messages.error(request, "Ce jeu n'est pas disponible actuellement.")
        return redirect('home')

    room_name = uuid.uuid4().hex[:6].upper()

    if jeu.slug == "premier-clic":
        return redirect('premier_clic', room_name=room_name)

    messages.error(request, "Ce jeu n'est pas encore disponible.")
    return redirect('jeu_detail', slug=jeu.slug)


def rejoindre_jeu(request, slug):
    """Permet de rejoindre une partie existante."""

    jeu = get_object_or_404(Jeu, slug=slug)

    if not jeu.actif:
        messages.error(request, "Ce jeu n'est pas disponible actuellement.")
        return redirect('home')

    form = RejoindreJeuForm(request.POST)

    if form.is_valid():
        room_name = form.cleaned_data["room_name"]

        if jeu.slug == "premier-clic":
            room = PremierClicConsumer.ROOMS.get(room_name)

            if room is None:
                form.add_error(
                    "room_name",
                    "Cette partie n'existe pas."
                )
            elif len(room["players"]) >= PremierClicConsumer.MAX_PLAYERS:
                form.add_error(
                    "room_name",
                    "Cette partie est déjà pleine."
                )
            else:
                return redirect(
                    'premier_clic',
                    room_name=room_name
                )

        else:
            messages.error(
                request,
                "Ce jeu n'est pas encore disponible."
            )
            return redirect(
                'jeu_detail',
                slug=jeu.slug
            )

    if form.errors:
        form.fields["room_name"].widget.attrs["class"] += " is-invalid"

    return render(
        request,
        'games/jeu_detail.html',
        {
            'jeu': jeu,
            'form': form,
        }
    )