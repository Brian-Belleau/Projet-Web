from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Greatest, Least


class FriendshipManager(models.Manager):
    def status_between(self, user, other):
        """Retourne (statut, lien) entre deux utilisateurs."""
        friendship = self.filter(
            Q(from_user=user, to_user=other) | Q(from_user=other, to_user=user)
        ).first()
        if friendship is None:
            return Friendship.NONE, None
        return friendship.status_for(user), friendship


class Friendship(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    STATUS_CHOICES = [
        (PENDING, "En attente"),
        (ACCEPTED, "Acceptée"),
    ]
    NONE = "none"
    SENT = "sent"
    RECEIVED = "received"
    FRIENDS = "friends"

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FriendshipManager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                Least("from_user", "to_user"),
                Greatest("from_user", "to_user"),
                name="unique_friendship_pair",
            ),
            models.CheckConstraint(
                condition=~Q(from_user=F("to_user")),
                name="friendship_not_with_self",
            ),
        ]

    def status_for(self, user):
        """Retourne le statut du lien du point de vue de l'utilisateur."""
        if self.status == self.ACCEPTED:
            return self.FRIENDS
        return self.SENT if self.from_user_id == user.pk else self.RECEIVED
