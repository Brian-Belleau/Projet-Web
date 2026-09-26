from django.contrib import messages
from django.shortcuts import redirect, render

from django.contrib.auth.views import LoginView
from .forms import LoginForm

from .forms import CustomUserCreationForm

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginForm

def signup_view(request):
    """Affiche et traite le formulaire d'inscription."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Inscription réussie ! Vous pouvez maintenant vous connecter."
            )
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(
        request,
        'registration/signup.html',
        {'form': form},
    )