"""TP2 - Partie A : classe Grille (morpion 3x3).

Convention : jouer(x, y, joueur) -> x = numéro de ligne, y = numéro de
colonne, de 0 à 2 (jouer(0, 1, "O") place un O en haut au milieu).
"""


class Grille:
    TAILLE = 3
    VIDE = " "

    def __init__(self):
        self.cases = [[self.VIDE] * self.TAILLE for _ in range(self.TAILLE)]

    def dans_grille(self, x, y):
        return (isinstance(x, int) and isinstance(y, int)
                and 0 <= x < self.TAILLE and 0 <= y < self.TAILLE)

    def est_libre(self, x, y):
        return self.dans_grille(x, y) and self.cases[x][y] == self.VIDE

    def jouer(self, x, y, joueur):
        """Place « X » ou « O » si la case est libre.

        Renvoie True si le coup est accepté, False s'il est refusé
        (case occupée, hors grille ou symbole invalide).
        """
        if joueur not in ("X", "O") or not self.est_libre(x, y):
            return False
        self.cases[x][y] = joueur
        return True

    def cases_libres(self):
        return [(x, y) for x in range(self.TAILLE) for y in range(self.TAILLE)
                if self.cases[x][y] == self.VIDE]

    def est_gagnant(self, j):
        """True si `j` a aligné trois symboles (ligne, colonne, diagonale)."""
        n = self.TAILLE
        lignes = [list(ligne) for ligne in self.cases]
        colonnes = [list(colonne) for colonne in zip(*self.cases)]
        diagonales = [[self.cases[i][i] for i in range(n)],
                      [self.cases[i][n - 1 - i] for i in range(n)]]
        return any(all(case == j for case in alignement)
                   for alignement in lignes + colonnes + diagonales)

    def est_plein(self):
        return not self.cases_libres()

    def copie(self):
        autre = Grille()
        autre.cases = [list(ligne) for ligne in self.cases]
        return autre

    def __str__(self):
        lignes = [" " + " | ".join(ligne) + " " for ligne in self.cases]
        return ("\n" + "-" * 11 + "\n").join(lignes)

    def afficher(self):
        print(self)
