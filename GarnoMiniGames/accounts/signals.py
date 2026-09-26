from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from .models import CustomUser, Profile, generate_pseudonym


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, raw=False, **kwargs):
    """Crée automatiquement le profil dès la création de l'utilisateur."""
    if created and not raw:
        Profile.objects.get_or_create(
            user=instance,
            defaults={"pseudonym": generate_pseudonym(instance)},
        )


@receiver(pre_save, sender=Profile)
def delete_replaced_photo(sender, instance, **kwargs):
    """Supprime l'ancien fichier quand la photo est remplacée ou effacée."""
    if not instance.pk:
        return
    old = (
        Profile.objects.filter(pk=instance.pk)
        .values_list("photo", flat=True)
        .first()
    )
    if old and old != (instance.photo.name or ""):
        instance.photo.storage.delete(old)


@receiver(post_delete, sender=Profile)
def delete_photo_with_profile(sender, instance, **kwargs):
    """Supprime le fichier photo quand le profil est supprimé."""
    if instance.photo:
        instance.photo.delete(save=False)
