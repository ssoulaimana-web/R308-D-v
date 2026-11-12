"""Tests du TP3 : python test_tp3.py (ou python -m unittest)."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from bibliotheque import Bibliotheque
from livre import Livre
from main import main
from utilisateur import Utilisateur


class SansAffichage(unittest.TestCase):
    def setUp(self):
        patcher = patch("sys.stdout", new_callable=io.StringIO)
        patcher.start()
        self.addCleanup(patcher.stop)


def biblio_exemple():
    b = Bibliotheque()
    b.ajouter_livre(Livre("1984", "Orwell", 1949))
    b.ajouter_livre(Livre("La Ferme des animaux", "Orwell", 1945))
    b.ajouter_livre(Livre("Dune", "Herbert", 1965))
    b.ajouter_utilisateur(Utilisateur("Ana"))
    b.ajouter_utilisateur(Utilisateur("Léo"))
    return b


class TestPartieA(SansAffichage):
    def test_livre_jeu_d_essai(self):
        l = Livre("1984", "Orwell", 1949)
        self.assertTrue(l.emprunter("Ana"))
        self.assertFalse(l.emprunter("Léo"))
        self.assertTrue(l.rendre())
        self.assertFalse(l.rendre())

    def test_rendre_par_un_autre(self):
        l = Livre("1984", "Orwell", 1949)
        l.emprunter("Ana")
        self.assertFalse(l.rendre("Léo"))
        self.assertFalse(l.disponible)
        self.assertTrue(l.rendre("Ana"))

    def test_annee_non_numerique(self):
        with self.assertRaises(ValueError):
            Livre("X", "Y", "abc")
        self.assertEqual(Livre("X", "Y", "1949").annee, 1949)

    def test_utilisateur(self):
        u, l = Utilisateur("Ana"), Livre("1984", "Orwell", 1949)
        self.assertTrue(u.emprunter_livre(l))
        self.assertFalse(Utilisateur("Léo").emprunter_livre(l))
        self.assertEqual(u.emprunts, [l])
        self.assertFalse(Utilisateur("Léo").rendre_livre(l))
        self.assertTrue(u.rendre_livre(l))
        self.assertEqual(u.emprunts, [])
        u.afficher_emprunts()


class TestPartieB(SansAffichage):
    def test_emprunt_et_retour(self):
        b = biblio_exemple()
        self.assertTrue(b.emprunter("Ana", "1984"))
        self.assertEqual(b.livres["1984"].emprunteur, "Ana")
        self.assertEqual(len(b.utilisateurs["Ana"].emprunts), 1)
        self.assertTrue(b.rendre("Ana", "1984"))
        self.assertTrue(b.livres["1984"].disponible)
        self.assertEqual(b.utilisateurs["Ana"].emprunts, [])

    def test_cas_pieges(self):
        b = biblio_exemple()
        self.assertFalse(b.emprunter("Ana", "Inconnu"))
        self.assertIn("inconnu", b.dernier_message)
        self.assertFalse(b.emprunter("Zoé", "1984"))
        self.assertIn("Utilisateur inconnu", b.dernier_message)
        self.assertTrue(b.emprunter("Ana", "1984"))
        self.assertFalse(b.emprunter("Léo", "1984"))          # déjà emprunté
        self.assertIn("déjà emprunté", b.dernier_message)
        self.assertFalse(b.rendre("Léo", "1984"))             # autre que l'emprunteur
        self.assertTrue(b.livres["1984"].emprunteur == "Ana")
        self.assertFalse(b.rendre("Ana", "Dune"))             # pas emprunté
        self.assertFalse(b.rendre("Zoé", "1984"))
        self.assertFalse(b.rendre("Ana", "Inconnu"))

    def test_doublons(self):
        b = biblio_exemple()
        self.assertFalse(b.ajouter_livre(Livre("1984", "Autre", 2000)))
        self.assertFalse(b.ajouter_utilisateur(Utilisateur("Ana")))
        self.assertFalse(b.ajouter_utilisateur(Utilisateur("  ")))

    def test_afficher_livres(self):
        b = biblio_exemple()
        b.emprunter("Ana", "1984")
        sortie = io.StringIO()
        with redirect_stdout(sortie):
            b.afficher_livres()
        texte = sortie.getvalue()
        self.assertIn("Livres disponibles", texte)
        self.assertIn("emprunté par Ana", texte)
        Bibliotheque().afficher_livres()  # bibliothèque vide : pas de plantage


class TestPartieC(SansAffichage):
    def test_sauvegarde_et_rechargement(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "livres.csv")
            b = biblio_exemple()
            b.emprunter("Ana", "1984")
            self.assertTrue(b.sauvegarder_livres(chemin))

            neuve = Bibliotheque()
            self.assertTrue(neuve.charger_livres(chemin))
            self.assertEqual(len(neuve.livres), 3)
            self.assertFalse(neuve.livres["1984"].disponible)
            self.assertEqual(neuve.livres["1984"].emprunteur, "Ana")
            self.assertTrue(neuve.livres["Dune"].disponible)
            self.assertTrue(neuve.rendre("Ana", "1984"))      # Ana peut le rendre

    def test_titre_avec_virgule_et_guillemets(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "livres.csv")
            b = Bibliotheque()
            b.ajouter_livre(Livre('Cent ans, "seul"', "García Márquez", 1967))
            b.sauvegarder_livres(chemin)
            neuve = Bibliotheque()
            neuve.charger_livres(chemin)
            self.assertIn('Cent ans, "seul"', neuve.livres)

    def test_fichier_absent(self):
        b = biblio_exemple()
        self.assertFalse(b.charger_livres("/chemin/absent/livres.csv"))
        self.assertEqual(len(b.livres), 3)  # rien n'est perdu

    def test_lignes_invalides_ignorees(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "livres.csv")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write("titre,auteur,annee,disponible,emprunteur\n"
                        "1984,Orwell,1949,False,Ana\n"
                        "Mauvais,Auteur,abc,True,\n"
                        ",Sans titre,2000,True,\n"
                        "Dune,Herbert,1965,True,\n"
                        "Dune,Doublon,1999,True,\n"
                        "Court\n")
            b = Bibliotheque()
            self.assertTrue(b.charger_livres(chemin))
            self.assertEqual(sorted(b.livres), ["1984", "Dune"])
            self.assertIn("ignorée", b.dernier_message)

    def test_erreur_d_ecriture(self):
        self.assertFalse(biblio_exemple().sauvegarder_livres("/chemin/absent/x.csv"))

    def test_sauvegarde_complete_avec_utilisateurs(self):
        with tempfile.TemporaryDirectory() as dossier:
            b = biblio_exemple()
            b.emprunter("Ana", "1984")
            self.assertTrue(b.sauvegarder(os.path.join(dossier, "sous", "donnees")))
            neuve = Bibliotheque()
            self.assertTrue(neuve.charger(os.path.join(dossier, "sous", "donnees")))
            self.assertEqual(sorted(neuve.utilisateurs), ["Ana", "Léo"])
            self.assertEqual(len(neuve.utilisateurs["Ana"].emprunts), 1)


class TestExtensionsEtDefis(SansAffichage):
    def test_stats(self):
        b = biblio_exemple()
        b.emprunter("Ana", "1984")
        b.emprunter("Ana", "Dune")
        self.assertEqual(b.stats(), {"total": 3, "empruntes": 2,
                                     "par_utilisateur": {"Ana": 2}})
        self.assertEqual(Bibliotheque().stats(),
                         {"total": 0, "empruntes": 0, "par_utilisateur": {}})

    def test_recherche_par_auteur(self):
        b = biblio_exemple()
        self.assertEqual(len(b.recherche_par_auteur("orwell")), 2)
        self.assertEqual(b.recherche_par_auteur("inconnu"), [])
        self.assertEqual(b.recherche_par_auteur(""), [])

    def test_limite_d_emprunts(self):
        b = biblio_exemple()
        b.max_emprunts = 1
        self.assertTrue(b.emprunter("Ana", "1984"))
        self.assertFalse(b.emprunter("Ana", "Dune"))
        self.assertIn("limite", b.dernier_message)

    def test_export_json(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "export.json")
            b = biblio_exemple()
            b.emprunter("Ana", "1984")
            self.assertTrue(b.export_json(chemin))
            with open(chemin, encoding="utf-8") as f:
                donnees = json.load(f)
            self.assertEqual(len(donnees["livres"]), 3)
            self.assertEqual(donnees["livres"][0]["emprunteur"], "Ana")
            self.assertFalse(b.export_json("/chemin/absent/x.json"))


class TestMenu(unittest.TestCase):
    def lancer(self, dossier, saisies):
        sortie = io.StringIO()
        with patch("builtins.input", side_effect=saisies), redirect_stdout(sortie):
            main(dossier)
        return sortie.getvalue()

    def test_session_complete_et_relance(self):
        with tempfile.TemporaryDirectory() as dossier:
            donnees = os.path.join(dossier, "donnees")
            sortie = self.lancer(donnees, [
                "1", "1984", "Orwell", "abc",        # année non numérique
                "1", "1984", "Orwell", "1949",
                "2", "Ana",
                "3", "Ana", "1984",
                "3", "Ana", "Inconnu",               # livre inconnu
                "9",                                  # choix invalide
                "5", "7", "8", "orw",
                "6"])
            self.assertIn("Aucune sauvegarde", sortie)      # fichier absent au lancement
            self.assertIn("L'année doit être un nombre entier", sortie)
            self.assertIn("Choix invalide", sortie)
            self.assertIn("Livre inconnu", sortie)
            self.assertIn("emprunté par Ana", sortie)
            self.assertIn("sauvegardées", sortie)

            # Relance : l'état est retrouvé et Ana peut rendre le livre.
            sortie = self.lancer(donnees, ["5", "4", "Ana", "1984", "6"])
            self.assertIn("État restauré", sortie)
            self.assertIn("emprunté par Ana", sortie)
            self.assertIn("Ana a rendu « 1984 »", sortie)

    def test_fin_de_saisie_sauvegarde(self):
        with tempfile.TemporaryDirectory() as dossier:
            self.lancer(dossier, ["2", "Ana", EOFError()])  # fin de saisie (Ctrl-D)
            self.assertTrue(os.path.exists(os.path.join(dossier, "livres.csv")))


if __name__ == "__main__":
    unittest.main()
