from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("pseudonym", "user", "games_played", "wins", "losses")
    search_fields = ("pseudonym", "user__username")
    readonly_fields = ("games_played", "wins", "losses")
