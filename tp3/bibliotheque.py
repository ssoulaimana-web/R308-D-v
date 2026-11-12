"""TP3 - Parties B, C et E : Bibliotheque, persistance CSV, extensions.

Les méthodes d'action (ajouter, emprunter, rendre...) renvoient True ou
False sans jamais lever d'exception ; `dernier_message` explique le
résultat de la dernière action (utile pour le menu).
"""

import csv
import json
from pathlib import Path

from livre import Livre
from utilisateur import Utilisateur

ENTETE_CSV = ["titre", "auteur", "annee", "disponible", "emprunteur"]


class Bibliotheque:
    def __init__(self, max_emprunts=None):
        self.livres = {}          # titre -> Livre
        self.utilisateurs = {}    # nom -> Utilisateur
        self.max_emprunts = max_emprunts  # extension : limite par utilisateur
        self.dernier_message = ""

    # -- messages ---------------------------------------------------------
    def _ok(self, message):
        self.dernier_message = message
        return True

    def _echec(self, message):
        self.dernier_message = message
        return False

    # -- partie B ---------------------------------------------------------
    def ajouter_livre(self, livre):
        if livre.titre in self.livres:
            return self._echec(f"« {livre.titre} » existe déjà.")
        self.livres[livre.titre] = livre
        return self._ok(f"Livre « {livre.titre} » ajouté.")

    def ajouter_utilisateur(self, utilisateur):
        if not utilisateur.nom:
            return self._echec("Le nom ne peut pas être vide.")
        if utilisateur.nom in self.utilisateurs:
            return self._echec(f"L'utilisateur {utilisateur.nom} existe déjà.")
        self.utilisateurs[utilisateur.nom] = utilisateur
        return self._ok(f"Utilisateur {utilisateur.nom} ajouté.")

    def _trouver(self, nom, titre):
        """Renvoie (utilisateur, livre) ou (None, None) avec un message d'échec."""
        utilisateur = self.utilisateurs.get(nom)
        livre = self.livres.get(titre)
        if utilisateur is None:
            self._echec(f"Utilisateur inconnu : {nom}.")
        elif livre is None:
            self._echec(f"Livre inconnu : « {titre} ».")
        else:
            return utilisateur, livre
        return None, None

    def emprunter(self, nom, titre):
        utilisateur, livre = self._trouver(nom, titre)
        if livre is None:
            return False
        if not livre.disponible:
            return self._echec(f"« {titre} » est déjà emprunté par {livre.emprunteur}.")
        if (self.max_emprunts is not None
                and len(utilisateur.emprunts) >= self.max_emprunts):
            return self._echec(f"{nom} a atteint la limite de {self.max_emprunts} emprunt(s).")
        utilisateur.emprunter_livre(livre)
        return self._ok(f"{nom} a emprunté « {titre} ».")

    def rendre(self, nom, titre):
        utilisateur, livre = self._trouver(nom, titre)
        if livre is None:
            return False
        if livre.disponible:
            return self._echec(f"« {titre} » n'est pas emprunté.")
        if livre.emprunteur != nom:
            return self._echec(f"« {titre} » a été emprunté par {livre.emprunteur}, "
                               f"pas par {nom} : retour refusé.")
        utilisateur.rendre_livre(livre)
        return self._ok(f"{nom} a rendu « {titre} ».")

    def afficher_livres(self):
        disponibles = [l for l in self.livres.values() if l.disponible]
        empruntes = [l for l in self.livres.values() if not l.disponible]
        print("Livres disponibles :")
        for livre in disponibles:
            print(f"  - {livre.titre} ({livre.auteur}, {livre.annee})")
        if not disponibles:
            print("  (aucun)")
        print("Livres empruntés :")
        for livre in empruntes:
            print(f"  - {livre.titre} ({livre.auteur}, {livre.annee}) "
                  f"- emprunté par {livre.emprunteur}")
        if not empruntes:
            print("  (aucun)")

    # -- partie C : persistance -------------------------------------------
    def sauvegarder_livres(self, chemin):
        """Écrit les livres en CSV : titre, auteur, annee, disponible, emprunteur."""
        try:
            with open(chemin, "w", encoding="utf-8", newline="") as f:
                ecrivain = csv.writer(f)
                ecrivain.writerow(ENTETE_CSV)
                for l in self.livres.values():
                    ecrivain.writerow([l.titre, l.auteur, l.annee, l.disponible,
                                       l.emprunteur or ""])
        except OSError as erreur:
            return self._echec(f"Sauvegarde impossible ({chemin}) : {erreur}")
        return self._ok(f"{len(self.livres)} livre(s) sauvegardé(s).")

    def charger_livres(self, chemin):
        """Recharge les livres depuis un CSV.

        La colonne « emprunteur » fait foi : un livre avec un emprunteur est
        indisponible. Les utilisateurs cités sont créés s'ils n'existent pas,
        et le livre est ajouté à leurs emprunts (ils peuvent donc le rendre).
        Fichier absent -> False (la bibliothèque n'est pas modifiée).
        Lignes invalides -> ignorées.
        """
        try:
            with open(chemin, encoding="utf-8", newline="") as f:
                lignes = list(csv.DictReader(f))
        except FileNotFoundError:
            return self._echec(f"Aucune sauvegarde trouvée ({chemin}).")
        except (OSError, UnicodeDecodeError, csv.Error) as erreur:
            return self._echec(f"Lecture impossible ({chemin}) : {erreur}")

        self.livres = {}
        for utilisateur in self.utilisateurs.values():
            utilisateur.emprunts = []

        ignorees = 0
        for ligne in lignes:
            try:
                emprunteur = (ligne.get("emprunteur") or "").strip()
                livre = Livre(ligne["titre"], ligne["auteur"], ligne["annee"],
                              disponible=not emprunteur,
                              emprunteur=emprunteur or None)
                if not livre.titre or livre.titre in self.livres:
                    raise ValueError("titre vide ou en double")
            except (KeyError, TypeError, ValueError, AttributeError):
                ignorees += 1
                continue
            self.livres[livre.titre] = livre
            if emprunteur:
                utilisateur = self.utilisateurs.setdefault(emprunteur,
                                                           Utilisateur(emprunteur))
                utilisateur.emprunts.append(livre)

        message = f"{len(self.livres)} livre(s) chargé(s)."
        if ignorees:
            message += f" {ignorees} ligne(s) invalide(s) ignorée(s)."
        return self._ok(message)

    def sauvegarder_utilisateurs(self, chemin):
        """Un nom par ligne (conserve aussi les utilisateurs sans emprunt)."""
        try:
            Path(chemin).write_text("".join(f"{nom}\n" for nom in self.utilisateurs),
                                    encoding="utf-8")
        except OSError as erreur:
            return self._echec(f"Sauvegarde impossible ({chemin}) : {erreur}")
        return True

    def charger_utilisateurs(self, chemin):
        try:
            texte = Path(chemin).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return False
        for nom in texte.splitlines():
            nom = nom.strip()
            if nom:
                self.utilisateurs.setdefault(nom, Utilisateur(nom))
        return True

    def sauvegarder(self, dossier):
        """Sauvegarde livres.csv et utilisateurs.txt dans `dossier`."""
        dossier = Path(dossier)
        try:
            dossier.mkdir(parents=True, exist_ok=True)
        except OSError as erreur:
            return self._echec(f"Dossier inutilisable ({dossier}) : {erreur}")
        ok_utilisateurs = self.sauvegarder_utilisateurs(dossier / "utilisateurs.txt")
        ok_livres = self.sauvegarder_livres(dossier / "livres.csv")
        return ok_utilisateurs and ok_livres

    def charger(self, dossier):
        """Recharge l'état sauvegardé. False si aucune sauvegarde."""
        dossier = Path(dossier)
        self.charger_utilisateurs(dossier / "utilisateurs.txt")
        return self.charger_livres(dossier / "livres.csv")

    # -- partie E : extensions --------------------------------------------
    def recherche_par_auteur(self, texte):
        """Livres dont l'auteur contient `texte` (sans tenir compte de la casse)."""
        texte = texte.strip().lower()
        return [l for l in self.livres.values() if texte and texte in l.auteur.lower()]

    def export_json(self, chemin):
        donnees = {
            "livres": [{"titre": l.titre, "auteur": l.auteur, "annee": l.annee,
                        "disponible": l.disponible, "emprunteur": l.emprunteur}
                       for l in self.livres.values()],
            "utilisateurs": list(self.utilisateurs),
        }
        try:
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(donnees, f, ensure_ascii=False, indent=2)
        except OSError as erreur:
            return self._echec(f"Export impossible ({chemin}) : {erreur}")
        return self._ok(f"Export JSON écrit dans {chemin}.")

    # -- défi 1 -----------------------------------------------------------
    def stats(self):
        """Nombre de livres, d'emprunts et emprunts par utilisateur."""
        par_utilisateur = {}
        for livre in self.livres.values():
            if not livre.disponible:
                par_utilisateur[livre.emprunteur] = par_utilisateur.get(livre.emprunteur, 0) + 1
        return {"total": len(self.livres),
                "empruntes": sum(par_utilisateur.values()),
                "par_utilisateur": par_utilisateur}
