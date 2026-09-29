from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.jeu_detail, name='jeu_detail'),
    path("premier-clic/<str:room_name>/", views.premier_clic, name="premier_clic"),
]