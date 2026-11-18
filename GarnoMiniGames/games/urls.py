from django.urls import path
from . import views

urlpatterns = [
    path("<slug:slug>/jouer/", views.lancer_jeu, name="lancer_jeu"),
    path("<slug:slug>/rejoindre/", views.rejoindre_jeu, name="rejoindre_jeu"),
    path("premier-clic/<str:room_name>/", views.premier_clic, name="premier_clic"),
    path("tic-tac-toe/<str:room_name>/", views.tic_tac_toe, name="tic_tac_toe"),
    path("connect-4/<str:room_name>/", views.connect_4, name="connect_4"),
    path("r-p-c-l-s/<str:room_name>/", views.r_p_c_l_s, name="r_p_c_l_s"),
    path("jouer/", views.jouer, name="jouer"),
    path("<slug:slug>/", views.jeu_detail, name="jeu_detail"),
]
