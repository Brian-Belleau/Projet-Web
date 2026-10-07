import re

from django import forms


class RejoindreJeuForm(forms.Form):
    """Formulaire permettant de rejoindre une partie."""

    room_name = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        label="Code de la partie",
        widget=forms.TextInput(
            attrs={
                "class": "form-control bg-dark text-light border-secondary text-center text-uppercase fw-bold",
                "placeholder": "ABC123",
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