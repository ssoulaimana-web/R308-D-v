"""TP3 - Partie A : classe Utilisateur."""


class Utilisateur:
    def __init__(self, nom):
        self.nom = str(nom).strip()
        self.emprunts = []  # liste de Livre

    def emprunter_livre(self, livre):
        """Emprunte `livre` s'il est disponible. Renvoie True/False."""
        if livre.emprunter(self.nom):
            self.emprunts.append(livre)
            return True
        return False

    def rendre_livre(self, livre):
        """Rend `livre` s'il fait partie de ses emprunts. Renvoie True/False."""
        if livre in self.emprunts and livre.rendre(self.nom):
            self.emprunts.remove(livre)
            return True
        return False

    def afficher_emprunts(self):
        if not self.emprunts:
            print(f"{self.nom} n'a aucun emprunt.")
            return
        print(f"Emprunts de {self.nom} :")
        for livre in self.emprunts:
            print(f"  - {livre.titre} ({livre.auteur})")
