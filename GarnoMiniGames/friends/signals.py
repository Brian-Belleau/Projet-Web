from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from .services import mark_offline


@receiver(user_logged_out)
def set_offline_on_logout(sender, user, **kwargs):
    """Le joueur apparaît hors ligne dès sa déconnexion (sans attendre le TTL)."""
    if user is not None and user.pk:
        mark_offline(user)
