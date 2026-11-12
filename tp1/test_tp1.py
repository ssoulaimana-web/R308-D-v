"""Tests du TP1 : python test_tp1.py (ou python -m unittest)."""

import io
import os
import tempfile
import unittest
from unittest.mock import patch

import mots
import partie_a
import partie_b
import pendu
import scores


class SansAffichage(unittest.TestCase):
    """Masque les print() pendant les tests."""

    def setUp(self):
        patcher = patch("sys.stdout", new_callable=io.StringIO)
        patcher.start()
        self.addCleanup(patcher.stop)


class TestPartieA(SansAffichage):
    def classe(self):
        d = {}
        for nom, note in (("Alice", 12), ("Bob", 15), ("Claire", 9.5)):
            partie_a.ajouter_etudiant(d, nom, note)
        return d

    def test_jeu_d_essai(self):
        d = self.classe()
        self.assertEqual(partie_a.moyenne_classe(d), 12.17)
        self.assertEqual(partie_a.meilleur_etudiant(d), ("Bob", 15.0))

    def test_mise_a_jour(self):
        d = self.classe()
        partie_a.ajouter_etudiant(d, "Alice", 18)
        self.assertEqual(d["Alice"], 18.0)
        self.assertEqual(len(d), 3)

    def test_conversion_robuste(self):
        d = {}
        self.assertTrue(partie_a.ajouter_etudiant(d, "Ana", "12,5"))
        self.assertEqual(d["Ana"], 12.5)
        for mauvaise in ("abc", "", None, "nan", "inf", 25, -1):
            self.assertFalse(partie_a.ajouter_etudiant(d, "Zoe", mauvaise))
        self.assertFalse(partie_a.ajouter_etudiant(d, "  ", 10))
        self.assertEqual(list(d), ["Ana"])

    def test_dictionnaire_vide(self):
        self.assertEqual(partie_a.moyenne_classe({}), 0.0)
        self.assertIsNone(partie_a.meilleur_etudiant({}))

    def test_sauvegarde_et_rechargement(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "etudiants.txt")
            d = self.classe()
            self.assertTrue(partie_a.sauvegarder(d, chemin))
            self.assertEqual(partie_a.charger(chemin), d)

    def test_fichier_absent(self):
        self.assertEqual(partie_a.charger("/chemin/qui/nexiste/pas.txt"), {})

    def test_ligne_mal_formee(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "e.txt")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write("Alice:12\nn'importe quoi\nBob:abc\n\nClaire:9,5\n:7\n")
            self.assertEqual(partie_a.charger(chemin),
                             {"Alice": 12.0, "Claire": 9.5})

    def test_erreur_d_ecriture(self):
        self.assertFalse(partie_a.sauvegarder({"A": 1.0}, "/chemin/inexistant/x.txt"))


class TestPartieB(SansAffichage):
    def test_comparer(self):
        self.assertEqual(partie_b.comparer(50, 10), "Trop petit")
        self.assertEqual(partie_b.comparer(50, 90), "Trop grand")
        self.assertEqual(partie_b.comparer(50, 50), "Gagné")

    def test_victoire(self):
        with patch("builtins.input", side_effect=["50", "30", "abc", "500", "42"]):
            self.assertTrue(partie_b.jouer(secret=42))

    def test_defaite_apres_10_essais(self):
        with patch("builtins.input", side_effect=["1"] * 10):
            self.assertFalse(partie_b.jouer(secret=42))

    def test_bornes_personnalisees(self):
        with patch("builtins.input", side_effect=["7"]):
            self.assertTrue(partie_b.jouer(5, 9, secret=7))

    def test_demander_bornes(self):
        with patch("builtins.input", side_effect=["", ""]):
            self.assertEqual(partie_b.demander_bornes(), (1, 100))
        # bornes incohérentes (50 >= 10) puis valides, avec une saisie non numérique
        with patch("builtins.input", side_effect=["50", "10", "abc", "5", "20"]):
            self.assertEqual(partie_b.demander_bornes(), (5, 20))

    def test_secret_dans_les_bornes(self):
        with patch("random.randint", return_value=7) as tirage, \
                patch("builtins.input", side_effect=["7"]):
            self.assertTrue(partie_b.jouer(5, 9))
        tirage.assert_called_once_with(5, 9)


class TestPartieC(SansAffichage):
    def test_masque(self):
        self.assertEqual(mots.masque("PYTHON"), ["_"] * 6)

    def test_choisir_mot_majuscules(self):
        self.assertEqual(mots.choisir_mot(["python"]), "PYTHON")
        self.assertEqual(mots.choisir_mot(["Éléphant"]), "ÉLÉPHANT")

    def test_liste_vide(self):
        with self.assertRaises(ValueError):
            mots.choisir_mot([])

    def test_charger_mots(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "m.txt")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write("chat\n\n  chien  \n")
            self.assertEqual(mots.charger_mots(chemin), ["chat", "chien"])
        self.assertEqual(mots.charger_mots("/absent.txt"), mots.MOTS_PAR_DEFAUT)
        self.assertEqual(mots.charger_mots(), mots.MOTS_PAR_DEFAUT)


class TestPartieD(SansAffichage):
    def partie(self, mot, saisies):
        with patch("builtins.input", side_effect=saisies):
            return pendu.jouer(mot)

    def test_victoire(self):
        self.assertTrue(self.partie("PYTHON", list("python")))

    def test_defaite_sept_erreurs(self):
        self.assertFalse(self.partie("PYTHON", list("abcdefg")))

    def test_six_erreurs_ne_perdent_pas(self):
        self.assertTrue(self.partie("PYTHON", list("abcdef") + list("python")))

    def test_lettre_deja_proposee_sans_erreur(self):
        saisies = ["a", "a", "a", "b", "c", "d", "e", "f"] + list("python")
        self.assertTrue(self.partie("PYTHON", saisies))

    def test_traiter_lettre(self):
        m, deja = mots.masque("PYTHON"), []
        self.assertEqual(pendu.traiter_lettre("PYTHON", m, deja, "p"), "present")
        self.assertEqual(m[0], "P")
        self.assertEqual(pendu.traiter_lettre("PYTHON", m, deja, "P"), "deja")
        self.assertEqual(pendu.traiter_lettre("PYTHON", m, deja, "z"), "absent")
        for invalide in ("", "ab", "1", "!", " "):
            self.assertEqual(pendu.traiter_lettre("PYTHON", m, deja, invalide), "invalide")

    def test_lettre_repetee_dans_le_mot(self):
        m, deja = mots.masque("ELEPHANT"), []
        pendu.traiter_lettre("ELEPHANT", m, deja, "e")
        self.assertEqual(m.count("E"), 2)

    def test_mot_accentue(self):
        self.assertTrue(self.partie("ÉLÉPHANT", list("elphant")))
        self.assertTrue(self.partie("ÉLÉPHANT", list("éLphant")))

    def test_mot_en_casse_mixte_et_tiret(self):
        self.assertTrue(self.partie("Python", list("python")))
        self.assertTrue(self.partie("pare-feu", list("parefu")))

    def test_dessin(self):
        self.assertEqual(pendu.dessin(0), "\n" * 5)
        self.assertIn("O", pendu.dessin(4))
        self.assertIn("/ \\", pendu.dessin(7))
        self.assertEqual(pendu.dessin(7), pendu.dessin(99))


class TestHallOfFame(SansAffichage):
    def test_deux_victoires(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "scores.txt")
            table = scores.charger(chemin)  # absent : départ à zéro
            self.assertEqual(table, {})
            scores.ajouter_victoire(table, "Ana")
            scores.ajouter_victoire(table, "Ana")
            scores.sauvegarder(table, chemin)
            with open(chemin, encoding="utf-8") as f:
                self.assertEqual(f.read(), "Ana:2.0\n")
            self.assertEqual(scores.charger(chemin), {"Ana": 2.0})

    def test_ligne_invalide_ignoree(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "scores.txt")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write("Ana:2.0\nabc\nLéo:x\n")
            self.assertEqual(scores.charger(chemin), {"Ana": 2.0})

    def test_main_rejouer_et_scores(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "scores.txt")
            saisies = (["Ana", "1"] + list("python") + ["o", "1"]
                       + list("python") + ["n"])
            with patch.object(pendu, "FICHIER_SCORES", chemin), \
                    patch.object(pendu, "choisir_mot", return_value="PYTHON"), \
                    patch("builtins.input", side_effect=saisies):
                pendu.main()
            self.assertEqual(scores.charger(chemin), {"Ana": 2.0})
            # relance : Ana repart de 2.0
            saisies = ["Ana", "1"] + list("python") + ["n"]
            with patch.object(pendu, "FICHIER_SCORES", chemin), \
                    patch.object(pendu, "choisir_mot", return_value="PYTHON"), \
                    patch("builtins.input", side_effect=saisies):
                pendu.main()
            self.assertEqual(scores.charger(chemin), {"Ana": 3.0})


if __name__ == "__main__":
    unittest.main()
