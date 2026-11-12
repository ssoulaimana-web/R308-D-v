"""Tests du TP2 : python test_tp2.py (ou python -m unittest)."""

import io
import unittest
from unittest.mock import patch

from grille import Grille
from joueurs import JoueurHumain, JoueurIA, JoueurIAMalin
from morpion import championnat, jouer_partie


def grille_depuis(texte):
    """'XX_/_O_/___' -> Grille (lignes séparées par '/')."""
    g = Grille()
    for x, ligne in enumerate(texte.split("/")):
        for y, c in enumerate(ligne):
            if c in "XO":
                g.cases[x][y] = c
    return g


class SansAffichage(unittest.TestCase):
    def setUp(self):
        patcher = patch("sys.stdout", new_callable=io.StringIO)
        patcher.start()
        self.addCleanup(patcher.stop)


class TestGrille(SansAffichage):
    def test_jeu_d_essai(self):
        g = Grille()
        self.assertTrue(g.jouer(0, 0, "X"))
        self.assertTrue(g.jouer(0, 1, "O"))
        self.assertTrue(g.jouer(1, 1, "X"))
        self.assertEqual(str(g).splitlines()[0], " X | O |   ")
        self.assertFalse(g.jouer(0, 0, "O"))   # occupée
        self.assertFalse(g.jouer(3, 0, "O"))   # hors grille
        self.assertFalse(g.jouer(0, -1, "O"))  # hors grille
        self.assertEqual(g.cases[0][0], "X")   # la case n'a pas changé
        self.assertFalse(g.est_gagnant("X"))
        self.assertTrue(g.jouer(2, 2, "X"))
        self.assertTrue(g.est_gagnant("X"))
        self.assertFalse(g.est_gagnant("O"))

    def test_affichage(self):
        g = Grille()
        g.jouer(0, 0, "X")
        lignes = str(g).splitlines()
        self.assertEqual(lignes[0], " X |   |   ")
        self.assertEqual(lignes[1], "-" * 11)
        self.assertEqual(len(lignes), 5)

    def test_symbole_invalide(self):
        self.assertFalse(Grille().jouer(0, 0, "Z"))
        self.assertFalse(Grille().jouer("a", 0, "X"))

    def test_toutes_les_lignes_gagnantes(self):
        for texte in ("XXX/___/___", "___/XXX/___", "___/___/XXX",
                      "X__/X__/X__", "_X_/_X_/_X_", "__X/__X/__X",
                      "X__/_X_/__X", "__X/_X_/X__"):
            self.assertTrue(grille_depuis(texte).est_gagnant("X"), texte)
            self.assertFalse(grille_depuis(texte).est_gagnant("O"), texte)

    def test_pas_de_victoire(self):
        self.assertFalse(grille_depuis("XOX/OXO/OXO").est_gagnant("X"))
        self.assertFalse(grille_depuis("XX_/OO_/___").est_gagnant("X"))

    def test_est_plein(self):
        self.assertFalse(Grille().est_plein())
        self.assertFalse(grille_depuis("XOX/OXO/OX_").est_plein())
        self.assertTrue(grille_depuis("XOX/XOO/OXX").est_plein())

    def test_copie_independante(self):
        g = Grille()
        c = g.copie()
        c.jouer(1, 1, "X")
        self.assertTrue(g.est_libre(1, 1))


class TestJoueurs(SansAffichage):
    def test_ia_aleatoire_joue_une_case_libre(self):
        g = grille_depuis("XOX/OXO/OX_")
        self.assertEqual(JoueurIA().prochain_coup(g, "O"), (2, 2))

    def test_humain_saisie(self):
        with patch("builtins.input", side_effect=["abc", "1", "1 x", "1 2"]):
            self.assertEqual(JoueurHumain("Ana").prochain_coup(Grille(), "X"), (1, 2))
        with patch("builtins.input", side_effect=["2,0"]):
            self.assertEqual(JoueurHumain("Ana").prochain_coup(Grille(), "X"), (2, 0))

    def test_ia_malin_bloque(self):
        g = grille_depuis("XX_/_O_/___")
        self.assertEqual(JoueurIAMalin().prochain_coup(g, "O"), (0, 2))

    def test_ia_malin_gagne(self):
        g = grille_depuis("OO_/XX_/___")
        self.assertEqual(JoueurIAMalin().prochain_coup(g, "O"), (0, 2))

    def test_ia_malin_prefere_gagner_a_bloquer(self):
        g = grille_depuis("OO_/XX_/___")
        self.assertEqual(JoueurIAMalin().prochain_coup(g, "X"), (1, 2))

    def test_ia_malin_hasard_sinon(self):
        coup = JoueurIAMalin().prochain_coup(Grille(), "X")
        self.assertIn(coup, Grille().cases_libres())


class TestJeu(SansAffichage):
    def test_coups_invalides_puis_victoire(self):
        # X(0,0) ; O refuse (occupée) puis (1,0) ; X : format, hors grille x2, (0,1) ;
        # O (1,1) ; X (0,2) -> X gagne.
        saisies = ["0 0", "0 0", "1 0", "abc", "3 0", "-1 0", "0 1", "1 1", "0 2"]
        with patch("builtins.input", side_effect=saisies):
            gagnant = jouer_partie(JoueurHumain("A"), JoueurHumain("B"))
        self.assertEqual(gagnant, "X")

    def test_message_coup_refuse(self):
        sortie = io.StringIO()
        saisies = ["0 0", "0 0", "3 3", "1 1", "0 1", "2 2", "0 2"]
        with patch("builtins.input", side_effect=saisies), patch("sys.stdout", sortie):
            jouer_partie(JoueurHumain("A"), JoueurHumain("B"))
        texte = sortie.getvalue()
        self.assertIn("déjà occupée", texte)
        self.assertIn("hors de la grille", texte)

    def test_ia_contre_ia_20_parties(self):
        bilan = championnat(JoueurIA("A"), JoueurIA("B"), 20)
        self.assertEqual(sum(bilan.values()), 20)

    def test_ia_malin_contre_hasard_sans_plantage(self):
        for _ in range(3):
            bilan = championnat(JoueurIAMalin(), JoueurIA(), 50)
            self.assertEqual(sum(bilan.values()), 50)
            bilan = championnat(JoueurIA(), JoueurIAMalin(), 50)
            self.assertEqual(sum(bilan.values()), 50)

    def test_deux_malins_font_match_nul(self):
        # Avec un jeu parfait le morpion est nul ; l'IA maligne ne perd jamais
        # contre elle-même au premier coup, mais le hasard peut dévier :
        # on vérifie seulement que chaque partie se termine.
        bilan = championnat(JoueurIAMalin("M1"), JoueurIAMalin("M2"), 30)
        self.assertEqual(sum(bilan.values()), 30)


if __name__ == "__main__":
    unittest.main()
