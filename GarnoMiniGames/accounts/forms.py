from django import forms
from .models import CustomUser
from .models import Profile


class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
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
        self.user = self.instance.user
        self.fields["username"].initial = self.user.username
        self.fields["first_name"].initial = self.user.first_name
        self.fields["last_name"].initial = self.user.last_name
        self.fields["email"].initial = self.user.email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if CustomUser.objects.filter(username=username).exclude(
                pk=self.user.pk).exists():
            raise forms.ValidationError(
                "Ce nom d'utilisateur est déjà utilisé.")
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.username = self.cleaned_data["username"]
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save()
            profile.save()
        return profile

    def clean(self):
        cleaned_data = super().clean()
        pseudonym = cleaned_data.get("pseudonym", "").strip()
        if pseudonym:
            if len(pseudonym) < 3:
                self.add_error(
                    "pseudonym",
                    "Le pseudonyme doit contenir au moins 3 caractères.",
                )
            existing_profiles = Profile.objects.filter(
                pseudonym__iexact=pseudonym)
            if self.instance and self.instance.pk:
                existing_profiles = existing_profiles.exclude(
                    pk=self.instance.pk)
            if existing_profiles.exists():
                self.add_error("pseudonym", "Ce pseudonyme est déjà utilisé.")
            cleaned_data["pseudonym"] = pseudonym
        return cleaned_data
