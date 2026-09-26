from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/', views.jeu_detail, name='jeu_detail'),
]