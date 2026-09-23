from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("pseudonym", "user", "games_played", "wins", "losses")
    search_fields = ("pseudonym", "user__username")
    readonly_fields = ("games_played", "wins", "losses")
