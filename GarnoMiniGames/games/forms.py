import re

from django import forms


class CreerPartieForm(forms.Form):
    """Choix de la visibilité d'une partie à sa création."""

    VISIBILITE_CHOICES = [
        ("privee", "Privée"),
        ("publique", "Publique"),
    ]

    visibilite = forms.ChoiceField(
        choices=VISIBILITE_CHOICES,
        initial="privee",
        required=True,
        error_messages={
            "required": "Choisis si la partie est publique ou privée.",
            "invalid_choice": "Choix de visibilité invalide.",
        },
    )

    def est_publique(self):
        return self.cleaned_data["visibilite"] == "publique"


class RejoindreJeuForm(forms.Form):
    """Formulaire permettant de rejoindre une partie."""

    room_name = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        label="Code de la partie",
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg bg-dark text-light border-secondary text-center text-uppercase fw-bold join-code-input",
                "placeholder": "ABC123",
                "maxlength": "6",
                "autocomplete": "off",
                "autocapitalize": "characters",
                "spellcheck": "false",
            }
        ),
        error_messages={
            "required": "Le code de la partie est obligatoire.",
            "min_length": "Le code doit contenir exactement 6 caractères.",
            "max_length": "Le code doit contenir exactement 6 caractères.",
        },
    )

    def clean_room_name(self):
        room_name = self.cleaned_data["room_name"].strip().upper()

        if not re.fullmatch(r"[A-Z0-9]{6}", room_name):
            raise forms.ValidationError(
                "Le code doit contenir 6 lettres ou chiffres."
            )

        return room_name
