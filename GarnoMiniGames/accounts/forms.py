from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import transaction
from .models import CustomUser, Profile

MAX_PHOTO_SIZE = 5 * 1024 * 1024


class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        validators=CustomUser._meta.get_field("username").validators,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    first_name = forms.CharField(
        label="Prénom",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        label="Nom",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Adresse e-mail",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
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
            "pseudonym": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
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
