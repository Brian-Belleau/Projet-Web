import re
from django.core.exceptions import ValidationError

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
