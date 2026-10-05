from django.urls import path
from . import views

app_name = "friends"

urlpatterns = [
    path("", views.friends_list, name="list"),
    path("api/rechercher/", views.search_users, name="search"),
    path("demander/<str:pseudonym>/", views.send_request, name="send_request"),
    path("demandes/<int:pk>/accepter/", views.accept_request, name="accept"),
    path("demandes/<int:pk>/refuser/", views.decline_request, name="decline"),
    path("demandes/<int:pk>/annuler/", views.cancel_request, name="cancel"),
    path("<int:pk>/retirer/", views.remove_friend, name="remove"),
]
