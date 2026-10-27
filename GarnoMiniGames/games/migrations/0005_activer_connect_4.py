from django.db import migrations


def activer_connect_4(apps, schema_editor):
    Jeu = apps.get_model("games", "Jeu")
    Jeu.objects.filter(slug="connect-4").update(actif=True)


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0004_seed_jeux"),
    ]

    operations = [
        migrations.RunPython(activer_connect_4),
    ]
