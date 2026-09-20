from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ProfileForm


@login_required
def profile(request):
    """Affiche le profil de l'utilisateur connecté."""
    return render(request, "accounts/profile.html", {"profile": request.user.profile})


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
        else:
            messages.error(
                request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProfileForm(instance=user_profile)
    return render(request, "accounts/profile_edit.html", {"form": form})
