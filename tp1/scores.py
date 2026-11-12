"""TP1 - Jeu 1 : hall of fame (dictionnaire nom -> victoires, scores.txt)."""

import math


def charger(chemin):
    """Lit scores.txt ("nom:victoires"). Fichier absent -> départ à zéro."""
    table = {}
    try:
        with open(chemin, encoding="utf-8") as f:
            lignes = f.readlines()
    except FileNotFoundError:
        return table
    except (OSError, UnicodeDecodeError) as erreur:
        print(f"Lecture de {chemin} impossible ({erreur}) : départ à zéro.")
        return table

    for ligne in lignes:
        nom, separateur, valeur = ligne.strip().rpartition(":")
        try:
            victoires = float(valeur)
        except ValueError:
            victoires = None
        if separateur and nom and victoires is not None and math.isfinite(victoires):
            table[nom] = victoires
        elif ligne.strip():
            print(f"Ligne ignorée dans {chemin} : {ligne.strip()!r}")
    return table


def sauvegarder(table, chemin):
    """Réécrit scores.txt. Renvoie False en cas d'erreur d'écriture."""
    try:
        with open(chemin, "w", encoding="utf-8") as f:
            for nom, victoires in table.items():
                f.write(f"{nom}:{float(victoires)}\n")
    except OSError as erreur:
        print(f"Impossible d'écrire {chemin} : {erreur}")
        return False
    return True


def ajouter_victoire(table, nom):
    table[nom] = table.get(nom, 0.0) + 1.0


def classement(table):
    """Liste (nom, victoires) triée par victoires décroissantes."""
    return sorted(table.items(), key=lambda element: (-element[1], element[0]))
