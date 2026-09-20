from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("profil/", views.profile, name="profile"),
    path("profil/modifier/", views.profile_edit, name="profile_edit"),
]
