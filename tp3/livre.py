"""TP3 - Partie A : classe Livre."""


class Livre:
    def __init__(self, titre, auteur, annee, disponible=True, emprunteur=None):
        self.titre = str(titre).strip()
        self.auteur = str(auteur).strip()
        self.annee = int(annee)  # ValueError si l'année n'est pas un entier
        # Cohérence : un livre emprunté a toujours un emprunteur.
        self.disponible = bool(disponible) and not emprunteur
        self.emprunteur = None if self.disponible else emprunteur

    def afficher(self):
        print(self)

    def emprunter(self, nom):
        """Marque le livre emprunté par `nom`. False s'il ne l'est pas déjà."""
        if not self.disponible:
            return False
        self.disponible = False
        self.emprunteur = nom
        return True

    def rendre(self, nom=None):
        """Rend le livre. False s'il n'était pas emprunté.

        Si `nom` est donné, seul l'emprunteur peut rendre le livre.
        """
        if self.disponible:
            return False
        if nom is not None and nom != self.emprunteur:
            return False
        self.disponible = True
        self.emprunteur = None
        return True

    def __str__(self):
        etat = ("disponible" if self.disponible
                else f"emprunté par {self.emprunteur}")
        return f"« {self.titre} » de {self.auteur} ({self.annee}) - {etat}"
