from django.apps import AppConfig


class FriendsConfig(AppConfig):
    name = 'friends'

    def ready(self):
        from . import signals
