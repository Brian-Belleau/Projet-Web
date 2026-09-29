from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("connexion/", views.CustomLoginView.as_view(), name="login"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout",),
    path("inscription/", views.signup, name="signup"),
    path("profil/", views.profile, name="profile"),
    path("profil/recherche/", views.search_profiles, name="search_profiles"),
    path("profil/modifier/", views.profile_edit, name="profile_edit"),
    path("joueur/<str:pseudonym>/", views.player_profile, name="player_profile"),
    path("api/verifier-nom-utilisateur/",
         views.check_username, name="check_username"),
    path("api/verifier-courriel/", views.check_email, name="check_email"),
    path("api/verifier-pseudonyme/", views.check_pseudonym, name="check_pseudonym"),
]
