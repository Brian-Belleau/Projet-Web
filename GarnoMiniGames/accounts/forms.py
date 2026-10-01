from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import transaction
from .models import CustomUser, Profile
from .validators import valider_nom_propre

MAX_PHOTO_SIZE = 5 * 1024 * 1024


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
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Cette adresse courriel est déjà utilisée.")
        return email


class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        validators=CustomUser._meta.get_field("username").validators,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Veuillez inscrire un nom d'utilisateur",
        }),
    )
    first_name = forms.CharField(
        label="Prénom",
        required=False,
        max_length=150,
        validators=[valider_nom_propre],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Veuillez inscrire votre prénom",
        }),
    )
    last_name = forms.CharField(
        label="Nom",
        required=False,
        max_length=150,
        validators=[valider_nom_propre],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Veuillez inscrire votre nom",
        }),
    )
    email = forms.EmailField(
        label="Adresse e-mail",
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Veuillez inscrire votre adresse e-mail",
        }),
    )

    class Meta:
        model = Profile
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "pseudonym",
            "bio",
            "photo",
        ]
        labels = {
            "pseudonym": "Pseudonyme",
            "bio": "Biographie",
        }
        widgets = {
            "pseudonym": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Veuillez inscrire un pseudonyme",
            }),
            "bio": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Veuillez inscrire une courte biographie",
            }),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pseudonym"].validators.extend([
            MinLengthValidator(
                3, "Le pseudonyme doit contenir au moins 3 caractères."),
            RegexValidator(
                r"^[\w.@+-]+$",
                "Le pseudonyme ne peut contenir que des lettres, chiffres "
                "et les caractères . @ + - _ (sans espace).",
            ),
        ])
        self.user = self.instance.user
        self.fields["username"].initial = self.user.username
        self.fields["first_name"].initial = self.user.first_name
        self.fields["last_name"].initial = self.user.last_name
        self.fields["email"].initial = self.user.email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if CustomUser.objects.filter(username__iexact=username).exclude(
                pk=self.user.pk).exists():
            raise forms.ValidationError(
                "Ce nom d'utilisateur est déjà utilisé.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exclude(
                pk=self.user.pk).exists():
            raise forms.ValidationError(
                "Cette adresse courriel est déjà utilisée.")
        return email

    def clean_pseudonym(self):
        pseudonym = self.cleaned_data["pseudonym"]
        if Profile.objects.filter(pseudonym__iexact=pseudonym).exclude(
                pk=self.instance.pk).exists():
            raise forms.ValidationError("Ce pseudonyme est déjà utilisé.")
        return pseudonym

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if isinstance(photo, UploadedFile) and photo.size > MAX_PHOTO_SIZE:
            raise forms.ValidationError(
                "La photo est trop volumineuse (5 Mo maximum).")
        return photo

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.username = self.cleaned_data["username"]
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            with transaction.atomic():
                self.user.save()
                profile.save()
        return profile


class ProfileDeleteForm(BootstrapMixin, forms.Form):
    """Demande le mot de passe de l'utilisateur pour confirmer la suppression de son compte."""
    password = forms.CharField(
        label="Mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError("Mot de passe incorrect.")
        return password
