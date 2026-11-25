import re
from django.core.exceptions import ValidationError

# Longueurs maximales
MAX_USERNAME_LENGTH = 15
MAX_NAME_LENGTH = 30
MAX_EMAIL_LENGTH = 50


def message_max_length(limite):
    return f"Ce champ ne peut pas dépasser {limite} caractères."


MAX_USERNAME_MESSAGE = message_max_length(MAX_USERNAME_LENGTH)
MAX_NAME_MESSAGE = message_max_length(MAX_NAME_LENGTH)
MAX_EMAIL_MESSAGE = message_max_length(MAX_EMAIL_LENGTH)

NOM_PROPRE_REGEX = re.compile(
    r"^[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[ '’\-][A-Za-zÀ-ÖØ-öø-ÿ]+)*$"
)


def valider_nom_propre(valeur):
    """Valide un nom ou un prénom (lettres, espaces, traits d'union, apostrophes)."""
    if not NOM_PROPRE_REGEX.match(valeur):
        raise ValidationError(
            "Ce champ ne doit contenir que des lettres, espaces, "
            "traits d'union ou apostrophes (pas de chiffres ni de "
            "caractères spéciaux)."
        )
