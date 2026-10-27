from django.db import migrations


JEUX = [
    {
        "nom": "Premier Clic",
        "slug": "premier-clic",
        "description": (
            "Voici notre premier jeu qui consiste à être le plus rapide à "
            "appuyer sur un bouton. Se déroulant en 5 manches gagnantes, "
            "qui sera le plus rapide."
        ),
        "image": "games/premier-clic.png",
        "actif": True,
    },
    {
        "nom": "TicTacToe",
        "slug": "tic-tac-toe",
        "description": (
            "Facile à comprendre, difficile à maîtriser !\n\n"
            "Placez vos X et vos O stratégiquement pour bloquer votre "
            "adversaire et aligner trois symboles victorieux. "
            "Réflexion et tactique seront vos meilleures armes."
        ),
        "image": "games/tic-tac-toe.png",
        "actif": True,
    },
    {
        "nom": "Connect 4",
        "slug": "connect-4",
        "description": (
            "Connect 4 est le jeu de stratégie classique à deux joueurs où "
            "tactique et anticipation sont les clés de la victoire. "
            "Alignez quatre jetons de votre couleur horizontalement, "
            "verticalement ou en diagonale tout en bloquant les coups de "
            "votre adversaire. Simple à apprendre, mais plein de défis !"
        ),
        "image": "games/connect-4.png",
        "actif": False,
    },
    {
        "nom": "Battleship",
        "slug": "battleship",
        "description": (
                "Plongez au cœur d'une bataille navale tactique au tour par tour ! "
                "Placez stratégiquement vos navires sur votre grille pour dissimuler "
                "leur position à votre adversaire. À chaque tour, désignez les coordonnées "
                "cibles pour tenter de toucher et couler la flotte ennemie. Réflexion, "
                "déduction et un brin de chance seront vos meilleurs alliés pour remporter "
                "la victoire."
        ),
        "image": "games/battleship.png",
        "actif": False,
    },
    {
        "nom": "Pierre Papier Ciseaux Duel",
        "slug": "pierre-papier-ciseaux-duel",
        "description": "Affrontez un ami en simultané dans ce duel intense de Pierre-Papier-Ciseaux en plusieurs manches gagnantes.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Pong Versus",
        "slug": "pong-versus",
        "description": "Le duel de tennis de table classique à deux joueurs sur le même écran ou en réseau. Ne ratez pas la balle !",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Dames Royale",
        "slug": "dames-royale",
        "description": "Le jeu de dames traditionnel revisité en multijoueur. Sautez par-dessus les pions adverses pour décrocher la couronne.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Course d'Obstacles en Duo",
        "slug": "course-obstacles-en-duo",
        "description": "Sautez au bon moment pour éviter les obstacles et devancez votre adversaire dans cette course effrénée.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Air Hockey Multijoueur",
        "slug": "air-hockey-multijoueur",
        "description": "Repoussez le palet dans le camp adverse avec votre curseur dans ce jeu d'adresse ultra dynamique à deux.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Puissance Mots",
        "slug": "puissance-mots",
        "description": "À tour de rôle, trouvez un mot débutant par la dernière lettre du mot précédent sous un compte à rebours féroce.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Échecs Rapides",
        "slug": "echecs-rapides",
        "description": "Un duel tactique intemporel où chaque joueur déplace ses pièces pour mater le roi adverse.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Combat de Tanks",
        "slug": "combat-de-tanks",
        "description": "Pilotez votre tank, détruisez les murs destructibles et touchez l'adversaire avant qu'il ne vous réduise en pièces.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Duel de Penaltys",
        "slug": "duel-de-penaltys",
        "description": "Un joueur tire, l'autre gardien plonge. Inverser les rôles pour déterminer le meilleur tireur d'élite.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Bagarre de Boules de Neige",
        "slug": "bagarre-boules-de-neige",
        "description": "Esquivez et lancez des boules de neige sur votre adversaire dans une arène enneigée pleine de rebondissements.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Course de Relais à Deux",
        "slug": "course-de-relais-a-deux",
        "description": "Synchronisez vos efforts ou mesurez votre vitesse de frappe en simultané pour franchir la ligne d'arrivée en premier.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Mastermind Duel",
        "slug": "mastermind-duel",
        "description": "Créez une combinaison secrète pour l'autre ou devinez-la plus rapidement que votre adversaire.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Duel de Slap",
        "slug": "duel-de-slap",
        "description": "Testez vos réflexes à deux : tapez au moment exact où le signal retentit sans commettre de faux départ.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Combat de Sumo Pixel",
        "slug": "combat-de-sumo-pixel",
        "description": "Bousculez votre adversaire hors du cercle central dans ce jeu de lutte multijoueur survolté.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Dots and Boxes Duel",
        "slug": "dots-and-boxes-duel",
        "description": "Reliez les points un par un pour fermer des carrés et marquer le maximum de points face à votre rival.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Flappy Versus",
        "slug": "flappy-versus",
        "description": "Survivrez-vous plus longtemps que votre ami à travers les obstacles en mode compétitif partagé ?",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Bataille de Cartes Express",
        "slug": "bataille-de-cartes-express",
        "description": "Le jeu de cartes de la bataille classique : retournez vos cartes simultanément, le plus fort remporte la mise.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Snake en Arène",
        "slug": "snake-en-arene",
        "description": "Deux serpents dans une même arène fermée : coupez la route à votre adversaire pour le forcer à la collision.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Quiz Clash Informatique",
        "slug": "quiz-clash-informatique",
        "description": "Répondez le plus vite possible à des questions de culture générale et de programmation pour battre votre adversaire au score.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Labyrinthe de Course à Deux",
        "slug": "labyrinthe-de-course-a-deux",
        "description": "Qui sortira vivant et le premier d'un labyrinthe généré en temps réel face à un autre joueur ?",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Choc des Billes",
        "slug": "choc-des-billes",
        "description": "Propulsez vos billes pour éjecter celles de votre adversaire hors du plateau circulaire.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Combinaison Gagnante",
        "slug": "combinaison-gagnante",
        "description": "Reproduisez une séquence lumineuse complexe plus rapidement et sans erreur face à votre opposant.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Chasse aux Bugs en Duo",
        "slug": "chasse-aux-bugs-en-duo",
        "description": "Nettoyez l'écran des erreurs logicielles plus vite que votre coéquipier ou adversaire dans un match chronométré.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Combat de Toupies",
        "slug": "combat-de-toupies",
        "description": "Faites tournez votre arène virtuelle et foncez sur la toupie ennemie pour l'immobiliser.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Bataille de Chiffres Chrono",
        "slug": "bataille-de-chiffres-chrono",
        "description": "Résolvez des mini-calculs mathématiques en même temps ; chaque bonne réponse inflige des points de pénalité à l'autre.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Drapeaux Face-à-Face",
        "slug": "drapeaux-face-a-face",
        "description": "Un quiz de rapidité pure sur les drapeaux du monde entier en mode compétitif à deux joueurs.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Tir à la Corde Numérique",
        "slug": "tir-a-la-corde-numerique",
        "description": "Appuyez le plus frénétiquement possible sur votre touche pour ramener la corde de votre côté.",
        "image": "games/default.png",
        "actif": False,
    },
    {
        "nom": "Démineur Duel",
        "slug": "demineur-duel",
        "description": "Nettoyez votre zone de mines en premier sans déclencher d'explosion fatale sous les yeux de votre adversaire.",
        "image": "games/default.png",
        "actif": False,
    }
]


def creer_jeux(apps, schema_editor):
    Jeu = apps.get_model("games", "Jeu")
    for jeu in JEUX:
        Jeu.objects.update_or_create(
            slug=jeu["slug"],
            defaults={
                "nom": jeu["nom"],
                "description": jeu["description"],
                "image": jeu["image"],
                "actif": jeu["actif"],
            },
        )


def supprimer_jeux(apps, schema_editor):
    Jeu = apps.get_model("games", "Jeu")
    Jeu.objects.filter(slug__in=[j["slug"] for j in JEUX]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0003_jeu_slug"),
    ]

    operations = [
        migrations.RunPython(creer_jeux, supprimer_jeux),
    ]
