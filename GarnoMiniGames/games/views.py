from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
import uuid

from .models import Jeu
from .consumers import PremierClicConsumer, TicTacToeConsumer, Connect4Consumer
from .forms import RejoindreJeuForm
from .presence import ACTIVE_PLAYERS, MESSAGES, check_join, get_identity, has_reservation, reserve_room


# slug du jeu -> (nom de l'URL de la partie, consumer qui gère les salles)
JEUX_MULTIJOUEUR = {
    "premier-clic": ("premier_clic", PremierClicConsumer),
    "tic-tac-toe": ("tic_tac_toe", TicTacToeConsumer),
    "connect-4": ("connect_4", Connect4Consumer),
}


def _acces_partie(request, slug, room_name):
    """Autorise l'accès à la page d'une partie seulement si la salle existe
    (quelqu'un l'a créée) ou si le joueur vient de la créer lui-même.
    Empêche de créer une salle en modifiant l'URL à la main."""
    _, consumer = JEUX_MULTIJOUEUR[slug]
    identity = get_identity(request.user, request.session, create=True)

    if (
        consumer.ROOMS.get(room_name) is not None
        or has_reservation(identity, consumer.GAME_PREFIX, room_name)
    ):
        return True

    messages.error(request, MESSAGES["room_not_found"])
    return False


def premier_clic(request, room_name):
    if not _acces_partie(request, "premier-clic", room_name):
        return redirect("jeu_detail", slug="premier-clic")
    return render(request, "games/premier_clic.html", {"room_name": room_name})


def tic_tac_toe(request, room_name):
    if not _acces_partie(request, "tic-tac-toe", room_name):
        return redirect("jeu_detail", slug="tic-tac-toe")
    return render(request, "games/tic_tac_toe.html", {"room_name": room_name})

def connect_4(request, room_name):
    """Affiche le plateau de Puissance 4."""
    get_identity(request.user, request.session, create=True)
    return render(
        request,
        "games/connect_4.html",
        {"room_name": room_name},
    )

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

    identity = get_identity(request.user, request.session, create=True)
    if identity in ACTIVE_PLAYERS:
        messages.error(request, MESSAGES["already_in_game"])
        return redirect('jeu_detail', slug=jeu.slug)

    room_name = uuid.uuid4().hex[:6].upper()

    if jeu.slug in JEUX_MULTIJOUEUR:
        url_name, consumer = JEUX_MULTIJOUEUR[jeu.slug]
        reserve_room(identity, consumer.GAME_PREFIX, room_name)
        return redirect(url_name, room_name=room_name)

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

        if jeu.slug in JEUX_MULTIJOUEUR:
            url_name, consumer = JEUX_MULTIJOUEUR[jeu.slug]
            room = consumer.ROOMS.get(room_name)
            identity = get_identity(
                request.user, request.session, create=True
            )
            refus = check_join(
                identity,
                request.user.is_authenticated,
                consumer.GAME_PREFIX,
                room_name,
                room,
                consumer.MAX_PLAYERS,
            )

            if room is None:
                form.add_error(
                    "room_name",
                    "Cette partie n'existe pas."
                )
            elif refus:
                form.add_error("room_name", MESSAGES[refus])
            else:
                return redirect(url_name, room_name=room_name)

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
