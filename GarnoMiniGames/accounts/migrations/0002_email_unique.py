from django.db import migrations, models


def normaliser_et_verifier_courriels(apps, schema_editor):
    """Met les courriels en minuscules et refuse la migration s'il reste des
    doublons ou des courriels vides (la contrainte d'unicité échouerait)."""
    CustomUser = apps.get_model("accounts", "CustomUser")

    vus = {}
    problemes = []
    for user in CustomUser.objects.order_by("pk"):
        courriel = (user.email or "").strip().lower()
        if not courriel:
            problemes.append(f"  - {user.username} : courriel vide")
        elif courriel in vus:
            problemes.append(
                f"  - {user.username} et {vus[courriel]} : même courriel ({courriel})")
        else:
            vus[courriel] = user.username

    if problemes:
        raise RuntimeError(
            "Impossible de rendre le courriel unique. Corrigez d'abord ces "
            "comptes (admin Django ou shell), puis relancez la migration :\n"
            + "\n".join(problemes)
        )

    for user in CustomUser.objects.all():
        courriel = user.email.strip().lower()
        if courriel != user.email:
            CustomUser.objects.filter(pk=user.pk).update(email=courriel)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            normaliser_et_verifier_courriels, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                error_messages={
                    "unique": "Cette adresse courriel est déjà utilisée."},
                max_length=254,
                unique=True,
                verbose_name="adresse courriel",
            ),
        ),
    ]
