"""TP2 - Partie C : jeu complet du Morpion (+ scores, modes de jeu)."""

from grille import Grille
from joueurs import JoueurHumain, JoueurIA, JoueurIAMalin


def raison_du_refus(grille, x, y):
    if not grille.dans_grille(x, y):
        return "hors de la grille (valeurs de 0 à 2)"
    return "case déjà occupée"


def jouer_partie(joueur1, joueur2, afficher=True):
    """Joue une partie : `joueur1` joue X et commence, `joueur2` joue O.

    Renvoie "X", "O" ou None (match nul). Un coup invalide affiche un
    message et le même joueur rejoue.
    """
    grille = Grille()
    participants = [(joueur1, "X"), (joueur2, "O")]
    tour = 0
    while True:
        joueur, symbole = participants[tour % 2]
        if afficher:
            print()
            grille.afficher()
        try:
            x, y = joueur.prochain_coup(grille, symbole)
        except (TypeError, ValueError):
            x = y = None
        if not grille.jouer(x, y, symbole):
            if afficher:
                print(f"Coup refusé : {raison_du_refus(grille, x, y)}. Rejouez.")
            continue
        if grille.est_gagnant(symbole):
            if afficher:
                print()
                grille.afficher()
                print(f"{joueur.nom} ({symbole}) gagne !")
            return symbole
        if grille.est_plein():
            if afficher:
                print()
                grille.afficher()
                print("Match nul.")
            return None
        tour += 1


def championnat(joueur1, joueur2, parties, afficher=False):
    """Enchaîne `parties` parties et renvoie {'X': .., 'O': .., 'nuls': ..}."""
    bilan = {"X": 0, "O": 0, "nuls": 0}
    for _ in range(parties):
        gagnant = jouer_partie(joueur1, joueur2, afficher)
        bilan["nuls" if gagnant is None else gagnant] += 1
    return bilan


MODES = {
    "1": ("Humain contre IA (hasard)",
          lambda: (JoueurHumain("Joueur 1"), JoueurIA("IA"))),
    "2": ("Humain contre IA maligne",
          lambda: (JoueurHumain("Joueur 1"), JoueurIAMalin("IA maligne"))),
    "3": ("Deux humains",
          lambda: (JoueurHumain("Joueur 1"), JoueurHumain("Joueur 2"))),
    "4": ("IA contre IA maligne (20 parties)",
          lambda: (JoueurIA("IA"), JoueurIAMalin("IA maligne"))),
}


def choisir_mode():
    print("Modes de jeu :")
    for cle, (libelle, _) in MODES.items():
        print(f"  {cle}) {libelle}")
    while True:
        choix = input("Votre choix : ").strip()
        if choix in MODES:
            return choix
        print("Choix invalide.")


def main():
    print("=== Morpion ===")
    try:
        choix = choisir_mode()
        _, fabrique = MODES[choix]
        joueur1, joueur2 = fabrique()

        if choix == "4":
            bilan = championnat(joueur1, joueur2, 20)
            print(f"{joueur1.nom} (X) : {bilan['X']}  |  "
                  f"{joueur2.nom} (O) : {bilan['O']}  |  nuls : {bilan['nuls']}")
            return

        scores = {joueur1.nom: 0, joueur2.nom: 0, "nuls": 0}
        premier, second = joueur1, joueur2
        while True:
            gagnant = jouer_partie(premier, second)
            if gagnant is None:
                scores["nuls"] += 1
            else:
                scores[(premier if gagnant == "X" else second).nom] += 1
            print("Score :", ", ".join(f"{nom} {points}"
                                       for nom, points in scores.items()))
            if input("Rejouer ? (o/n) ").strip().lower() != "o":
                break
            premier, second = second, premier  # on alterne le premier joueur
    except (EOFError, KeyboardInterrupt):
        print()
    print("À bientôt !")


if __name__ == "__main__":
    main()
