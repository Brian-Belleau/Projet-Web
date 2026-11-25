from django.db import migrations


def definir_image_battleship(apps, schema_editor):
    Jeu = apps.get_model("games", "Jeu")
    Jeu.objects.filter(slug="battleship").update(image="games/default.png")


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0009_ajouter_r_p_c_l_s"),
    ]

    operations = [
        migrations.RunPython(definir_image_battleship,
                             migrations.RunPython.noop),
    ]
