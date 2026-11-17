from django.db import migrations


def creer_jeu(apps, schema_editor):
    Jeu = apps.get_model("games", "Jeu")
    Jeu.objects.update_or_create(
        slug="r-p-c-l-s",
        defaults={
            "nom": "Roche-Papier-Ciseaux-Lézard-Spock",
            "description": (
                "La version améliorée du classique, popularisée par Sheldon "
                "Cooper ! Cinq choix, dix façons de gagner : \n"
                "-> la roche écrase les ciseaux\n"
                "-> la roche écrase le lézard\n"
                "-> le papier recouvre la roche\n"
                "-> le papier réfute Spock\n"
                "-> les ciseaux coupent le papier\n"
                "-> les ciseaux décapitent le lézard\n"
                "-> le lézard empoisonne Spock\n"
                "-> le lézard mange le papier\n"
                "-> Spock vaporise la roche\n"
                "-> Spock casse les ciseaux\n"
                "Le premier à gagner 3 manches remporte la partie. Devinez votre adversaire !"
            ),
            "description_courte": "Cinq choix, dix façons de gagner. Premier à 3 manches !",
            "image": "games/r-p-c-l-s.png",
            "actif": True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0008_remove_jeu_points_defaite_remove_jeu_points_victoire"),
    ]

    operations = [
        migrations.RunPython(creer_jeu, migrations.RunPython.noop),
    ]