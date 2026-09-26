from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ProfileForm
from .models import Profile, generate_pseudonym


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


@login_required
def search_profiles(request):
    """Recherche des profils par pseudonyme."""
    query = request.GET.get("q", "").strip()
    profiles = Profile.objects.all()
    if query:
        profiles = profiles.filter(pseudonym__icontains=query)
    context = {
        "profiles": profiles.order_by("pseudonym"),
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
