from django.contrib import admin

from .models import Jeu


@admin.register(Jeu)
class JeuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'actif', 'date_creation')
    list_filter = ('actif',)
    search_fields = ('nom',)