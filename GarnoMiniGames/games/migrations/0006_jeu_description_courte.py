from django.db import migrations, models


DESCRIPTIONS_COURTES = {
    "premier-clic": "Soyez le plus rapide à cliquer ! Premier à 5 manches gagnantes.",
    "tic-tac-toe": "Alignez trois X ou trois O avant votre adversaire.",
    "connect-4": "Alignez quatre jetons avant votre adversaire.",
    "battleship": "Coulez la flotte ennemie avant qu'elle ne coule la vôtre.",
    "pierre-papier-ciseaux-duel": "Le classique duel simultané, en plusieurs manches gagnantes.",
    "pong-versus": "Le tennis de table classique à deux. Ne ratez pas la balle !",
    "dames-royale": "Sautez les pions adverses pour décrocher la couronne.",
    "course-obstacles-en-duo": "Sautez au bon moment et devancez votre adversaire.",
    "air-hockey-multijoueur": "Repoussez le palet dans le camp adverse.",
    "puissance-mots": "Trouvez un mot qui commence par la dernière lettre du précédent.",
    "echecs-rapides": "Un duel tactique pour mater le roi adverse.",
    "combat-de-tanks": "Détruisez les murs et touchez l'adversaire en premier.",
    "duel-de-penaltys": "Tirez, plongez, inversez les rôles : qui sera le meilleur ?",
    "bagarre-boules-de-neige": "Esquivez et lancez des boules de neige dans une arène glacée.",
    "course-de-relais-a-deux": "Franchissez la ligne d'arrivée en premier.",
    "mastermind-duel": "Devinez la combinaison secrète plus vite que l'autre.",
    "duel-de-slap": "Tapez au signal, sans faux départ !",
    "combat-de-sumo-pixel": "Bousculez votre adversaire hors du cercle.",
    "dots-and-boxes-duel": "Reliez les points, fermez des carrés, marquez le plus de points.",
    "flappy-versus": "Survivez plus longtemps que votre ami entre les obstacles.",
    "bataille-de-cartes-express": "Retournez vos cartes : la plus forte remporte la mise.",
    "snake-en-arene": "Coupez la route de l'adversaire pour le forcer à la collision.",
    "quiz-clash-informatique": "Répondez plus vite que votre adversaire à des questions de culture et de programmation.",
    "labyrinthe-de-course-a-deux": "Sortez le premier d'un labyrinthe généré en temps réel.",
    "choc-des-billes": "Éjectez les billes de l'adversaire hors du plateau.",
    "combinaison-gagnante": "Reproduisez la séquence lumineuse sans erreur et plus vite que l'autre.",
    "chasse-aux-bugs-en-duo": "Nettoyez l'écran des bugs plus vite que votre adversaire.",
    "combat-de-toupies": "Foncez sur la toupie ennemie pour l'immobiliser.",
    "bataille-de-chiffres-chrono": "Résolvez des mini-calculs : chaque bonne réponse pénalise l'autre.",
    "drapeaux-face-a-face": "Un quiz de rapidité sur les drapeaux du monde.",
    "tir-a-la-corde-numerique": "Martelez votre touche pour ramener la corde de votre côté.",
    "demineur-duel": "Nettoyez votre zone sans déclencher de mine avant l'autre.",
}


def remplir_descriptions_courtes(apps, schema_editor):
    Jeu = apps.get_model("games", "Jeu")
    for slug, texte in DESCRIPTIONS_COURTES.items():
        Jeu.objects.filter(slug=slug).update(description_courte=texte)


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0005_activer_connect_4"),
    ]

    operations = [
        migrations.AddField(
            model_name="jeu",
            name="description_courte",
            field=models.CharField(
                blank=True,
                help_text="Une phrase affichée sur la carte de l'accueil.",
                max_length=140,
            ),
        ),
        migrations.RunPython(remplir_descriptions_courtes,
                             migrations.RunPython.noop),
    ]
