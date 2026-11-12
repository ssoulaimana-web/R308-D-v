"""TP2 - Partie B (+ bonus) : les joueurs.

Tous les joueurs exposent la même méthode prochain_coup(tab, symbole)
qui renvoie un tuple (x, y).
"""

import random


class Joueur:
    def __init__(self, nom):
        self.nom = nom

    def prochain_coup(self, tab, symbole):
        raise NotImplementedError


class JoueurHumain(Joueur):
    """Saisie clavier : « x y » (ligne, colonne), de 0 à 2."""

    def prochain_coup(self, tab, symbole):
        while True:
            texte = input(f"{self.nom} ({symbole}) - coup « ligne colonne » : ")
            morceaux = texte.replace(",", " ").split()
            if len(morceaux) == 2:
                try:
                    return int(morceaux[0]), int(morceaux[1])
                except ValueError:
                    pass
            print("Format invalide : entrez deux entiers, par exemple « 1 2 ».")


class JoueurIA(Joueur):
    """Coup aléatoire parmi les cases libres."""

    def __init__(self, nom="IA"):
        super().__init__(nom)

    def prochain_coup(self, tab, symbole):
        return random.choice(tab.cases_libres())


def coup_gagnant(tab, symbole):
    """Renvoie une case qui fait gagner `symbole` au prochain coup, sinon None."""
    for x, y in tab.cases_libres():
        essai = tab.copie()
        essai.jouer(x, y, symbole)
        if essai.est_gagnant(symbole):
            return (x, y)
    return None


class JoueurIAMalin(JoueurIA):
    """Gagne si possible, sinon bloque l'adversaire, sinon joue au hasard."""

    def __init__(self, nom="IA maligne"):
        super().__init__(nom)

    def prochain_coup(self, tab, symbole):
        adversaire = "O" if symbole == "X" else "X"
        for cible in (symbole, adversaire):
            coup = coup_gagnant(tab, cible)
            if coup is not None:
                return coup
        return super().prochain_coup(tab, symbole)
