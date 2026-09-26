from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

class BootstrapMixin:
    """Ajoute les classes Bootstrap aux widgets de tous les champs."""

    def __init__(self, *args, **kwargs):
        """Initialise les champs du formulaire avec les classes Bootstrap appropriées."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                css = 'form-check-input'
            elif isinstance(widget, forms.Select):
                css = 'form-select'
            else:
                css = 'form-control'
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing} {css}'.strip()

class LoginForm(BootstrapMixin, AuthenticationForm):
    """Formulaire de connexion avec les classes Bootstrap."""

class CustomUserCreationForm(BootstrapMixin, UserCreationForm):
    """Formulaire d'inscription avec les classes Bootstrap, incluant l'email."""

    email = forms.EmailField(required=True, label="Adresse courriel")

    class Meta(UserCreationForm.Meta):
        model = UserCreationForm.Meta.model
        fields = UserCreationForm.Meta.fields + ('email',)
