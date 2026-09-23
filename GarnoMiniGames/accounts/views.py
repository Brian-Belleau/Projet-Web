from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ProfileForm
from .models import Profile


def get_user_profile(user, request=None):
    profile_data, created = Profile.objects.get_or_create(
        user=user,
        defaults={"pseudonym": f"{user.username[:20]}_{user.pk}"[:30]},
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
    if not profile_data.photo:
        messages.info(
            request,
            "Ajoutez une photo de profil pour personnaliser votre compte.",
        )
    if not profile_data.bio:
        messages.info(
            request,
            "Pensez à ajouter une biographie pour vous présenter aux autres joueurs.",
        )
    context = {
        "profile": profile_data,
        "win_rate": profile_data.win_rate,
        "total_games": profile_data.total_games,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def search_profiles(request):
    """Recherche des profils par pseudonyme."""
    get_user_profile(request.user, request)
    query = request.GET.get("q", "").strip()
    profiles = Profile.objects.all()
    if query:
        profiles = profiles.filter(pseudonym__icontains=query)
    profiles = profiles.order_by("pseudonym")
    if query and not profiles.exists():
        messages.warning(
            request, f"Aucun joueur trouvé pour « {query} ».")
    elif query:
        count = profiles.count()
        messages.success(
            request,
            f"{count} joueur trouvé." if count == 1
            else f"{count} joueurs trouvés.",
        )
    context = {
        "profiles": profiles,
        "query": query,
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
                return redirect("accounts:profile")
            form.save()
            if "photo" in form.changed_data:
                if form.cleaned_data.get("photo"):
                    messages.success(
                        request, "Votre photo de profil a été mise à jour.")
                else:
                    messages.warning(
                        request, "Votre photo de profil a été supprimée.")
            if "pseudonym" in form.changed_data:
                messages.success(
                    request, "Votre pseudonyme a été modifié.")
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
        profile_data = Profile.objects.get(pseudonym=pseudonym)
    except Profile.DoesNotExist:
        messages.error(
            request, f"Le joueur « {pseudonym} » n'existe pas.")
        return redirect("accounts:search_profiles")
    if profile_data.user == request.user:
        messages.info(request, "Voici votre propre profil.")
        return redirect("accounts:profile")
    context = {
        "profile": profile_data,
        "win_rate": profile_data.win_rate,
        "total_games": profile_data.total_games,
    }
    return render(request, "accounts/player_profile.html", context)
