from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProfileForm
from .models import Profile


@login_required
def profile(request):
    """Affiche le profil de l'utilisateur connecté."""
    profile_data = request.user.profile
    context = {
        "profile": profile_data,
        "win_rate": profile_data.win_rate,
        "total_games": profile_data.total_games,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def profile_edit(request):
    """Permet de modifier le profil de l'utilisateur connecté."""
    user_profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
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
    profile_data = get_object_or_404(Profile, pseudonym=pseudonym)
    if profile_data.user == request.user:
        return redirect("accounts:profile")
    context = {
        "profile": profile_data,
        "win_rate": profile_data.win_rate,
        "total_games": profile_data.total_games,
    }
    return render(request, "accounts/player_profile.html", context)
