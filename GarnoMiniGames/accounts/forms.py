from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["pseudonym", "bio"]
        labels = {
            "pseudonym": "Pseudonyme",
            "bio": "Biographie",
        }
        widgets = {
            "pseudonym": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

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
