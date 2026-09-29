from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, ExpressionWrapper, F, FloatField, Value, When
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import CustomUserCreationForm, ProfileForm, LoginForm
from .models import CustomUser, Profile, generate_pseudonym
from django.contrib.auth.views import LoginView


def is_ajax(request):
    """Détecte une requête envoyée via fetch/XMLHttpRequest."""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginForm


def signup(request):
    """Affiche et traite le formulaire d'inscription."""
    if request.user.is_authenticated:
        return redirect('home')

    ajax_request = is_ajax(request)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Inscription réussie ! Vous pouvez maintenant vous connecter."
            )
            if ajax_request:
                return JsonResponse({
                    "success": True,
                    "redirect_url": reverse("home"),
                })
            return redirect('home')

        if ajax_request:
            return JsonResponse(
                {"success": False, "errors": form.errors},
                status=400,
            )
    else:
        form = CustomUserCreationForm()

    return render(
        request,
        'registration/signup.html',
        {'form': form},
    )


def get_user_profile(user, request=None):
    """Retourne le profil de l'utilisateur (le crée s'il n'existe pas encore)."""
    profile_data, created = Profile.objects.get_or_create(
        user=user,
        defaults={"pseudonym": generate_pseudonym(user)},
    )
    if created and request is not None:
        messages.info(
            request,
            "Bienvenue ! Votre profil a été créé automatiquement. "
            "Vous pouvez le personnaliser dès maintenant.",
        )
    return profile_data


@login_required
def profile(request):
    """Affiche le profil de l'utilisateur connecté."""
    profile_data = get_user_profile(request.user, request)
    return render(request, "accounts/profile.html", {"profile": profile_data})


SORT_OPTIONS = {
    "pseudonym": ("pseudonym",),
    "pseudonym_desc": ("-pseudonym",),
    "games_played_desc": ("-games_played", "pseudonym"),
    "games_played_asc": ("games_played", "pseudonym"),
    "win_rate_desc": ("-win_rate_calc", "-games_played", "pseudonym"),
    "win_rate_asc": ("win_rate_calc", "-games_played", "pseudonym"),
    "wins_desc": ("-wins", "pseudonym"),
}
SORT_LABELS = {
    "pseudonym": "Pseudonyme (A → Z)",
    "pseudonym_desc": "Pseudonyme (Z → A)",
    "games_played_desc": "Parties jouées (plus → moins)",
    "games_played_asc": "Parties jouées (moins → plus)",
    "win_rate_desc": "Taux de victoire (plus → moins)",
    "win_rate_asc": "Taux de victoire (moins → plus)",
    "wins_desc": "Victoires (plus → moins)",
}
DEFAULT_SORT = "pseudonym"


@login_required
def search_profiles(request):
    """Recherche des profils par pseudonyme, avec filtre et tri."""
    query = request.GET.get("q", "").strip()
    min_games = request.GET.get("min_games", "").strip()
    sort = request.GET.get("sort", DEFAULT_SORT)
    if sort not in SORT_OPTIONS:
        sort = DEFAULT_SORT

    profiles = Profile.objects.annotate(
        win_rate_calc=Case(
            When(games_played=0, then=Value(0.0)),
            default=ExpressionWrapper(
                F("wins") * 100.0 / F("games_played"),
                output_field=FloatField(),
            ),
            output_field=FloatField(),
        )
    )

    if query:
        profiles = profiles.filter(pseudonym__icontains=query)

    if min_games.isdigit():
        profiles = profiles.filter(games_played__gte=int(min_games))

    profiles = profiles.order_by(*SORT_OPTIONS[sort])
    sort_choices = [
        {"value": value, "label": label, "selected": value == sort}
        for value, label in SORT_LABELS.items()
    ]

    context = {
        "profiles": profiles,
        "query": query,
        "min_games": min_games,
        "sort": sort,
        "sort_choices": sort_choices,
    }
    return render(request, "accounts/profile_search.html", context)


@login_required
def profile_edit(request):
    """Permet de modifier le profil de l'utilisateur connecté."""
    user_profile = get_user_profile(request.user, request)
    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=user_profile,
        )
        if form.is_valid():
            if not form.has_changed():
                messages.info(
                    request, "Aucune modification n'a été effectuée.")
            else:
                form.save()
                messages.success(
                    request, "Votre profil a été mis à jour avec succès.")
            return redirect("accounts:profile")
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProfileForm(instance=user_profile)
    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
def player_profile(request, pseudonym):
    """Affiche le profil public d'un autre joueur."""
    try:
        profile_data = Profile.objects.select_related(
            "user").get(pseudonym=pseudonym)
    except Profile.DoesNotExist:
        messages.error(
            request, f"Le joueur « {pseudonym} » n'existe pas.")
        return redirect("accounts:search_profiles")
    if profile_data.user_id == request.user.pk:
        return redirect("accounts:profile")
    return render(
        request, "accounts/player_profile.html", {"profile": profile_data})


def check_username(request):
    """Vérifie en AJAX si un nom d'utilisateur est disponible.

    Accessible aux visiteurs non connectés (formulaire d'inscription) et
    aux utilisateurs connectés (modification de profil, en excluant leur
    propre compte).
    """
    username = request.GET.get("username", "").strip()
    available = True
    if username:
        candidates = CustomUser.objects.filter(username__iexact=username)
        if request.user.is_authenticated:
            candidates = candidates.exclude(pk=request.user.pk)
        available = not candidates.exists()
    return JsonResponse({"available": available})


def check_email(request):
    """Vérifie en AJAX si une adresse courriel est disponible.

    Accessible aux visiteurs non connectés (formulaire d'inscription) et
    aux utilisateurs connectés (modification de profil, en excluant leur
    propre compte).
    """
    email = request.GET.get("email", "").strip()
    available = True
    if email:
        candidates = CustomUser.objects.filter(email__iexact=email)
        if request.user.is_authenticated:
            candidates = candidates.exclude(pk=request.user.pk)
        available = not candidates.exists()
    return JsonResponse({"available": available})


@login_required
def check_pseudonym(request):
    """Vérifie en AJAX si un pseudonyme est disponible."""
    pseudonym = request.GET.get("pseudonym", "").strip()
    available = True
    if pseudonym:
        user_profile = get_user_profile(request.user)
        available = not Profile.objects.filter(
            pseudonym__iexact=pseudonym).exclude(pk=user_profile.pk).exists()
    return JsonResponse({"available": available})
