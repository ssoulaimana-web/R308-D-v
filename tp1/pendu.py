"""TP1 - Partie D : jeu du Pendu (+ bonus : ASCII art, mode 2 joueurs,
hall of fame, mots accentués)."""

import getpass
import unicodedata
from pathlib import Path

import scores
from mots import charger_mots, choisir_mot, masque

ERREURS_MAX = 7
DOSSIER = Path(__file__).resolve().parent
FICHIER_SCORES = DOSSIER / "scores.txt"
FICHIER_MOTS = DOSSIER / "mots.txt"

# Bonus ASCII art : chaque erreur ajoute des éléments au dessin
# (numéro de ligne, texte). 7 erreurs = dessin complet.
ETAPES = {
    1: [(5, "==========")],
    2: [(0, "  |"), (1, "  |"), (2, "  |"), (3, "  |"), (4, "  |")],
    3: [(0, "  +----+"), (1, "  |    |")],
    4: [(2, "  |    O")],
    5: [(3, "  |    |")],
    6: [(3, "  |   /|\\")],
    7: [(4, "  |   / \\")],
}


def dessin(erreurs):
    lignes = [""] * 6
    for etape in range(1, min(erreurs, ERREURS_MAX) + 1):
        for numero, texte in ETAPES[etape]:
            lignes[numero] = texte
    return "\n".join(lignes)


def sans_accent(texte):
    """« É » -> « E » : permet de jouer « e » sur ÉLÉPHANT."""
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def traiter_lettre(mot, m, deja, lettre):
    """Applique une proposition.

    Révèle les positions dans le masque `m` et mémorise la lettre dans
    `deja`. Renvoie 'invalide', 'deja', 'present' ou 'absent'.
    """
    lettre = lettre.strip()
    if len(lettre) != 1 or not lettre.isalpha():
        return "invalide"
    cle = sans_accent(lettre.upper())
    if cle in deja:
        return "deja"
    deja.append(cle)

    trouvee = False
    for i, caractere in enumerate(mot):
        if sans_accent(caractere) == cle:
            m[i] = caractere  # on révèle le caractère d'origine (avec accent)
            trouvee = True
    return "present" if trouvee else "absent"


def afficher_etat(m, erreurs, erreurs_max, deja):
    if erreurs:
        print(dessin(erreurs))
    print("\nMot      :", " ".join(m))
    print(f"Erreurs  : {erreurs}/{erreurs_max}")
    print("Lettres  :", " ".join(sorted(deja)) if deja else "(aucune)")


def jouer(mot, erreurs_max=ERREURS_MAX):
    """Joue une partie sur `mot`. Renvoie True en cas de victoire."""
    mot = mot.strip().upper()
    m = masque(mot)
    for i, caractere in enumerate(mot):
        if not caractere.isalpha():  # tiret, espace, apostrophe : déjà visibles
            m[i] = caractere

    deja, erreurs = [], 0
    while "_" in m and erreurs < erreurs_max:
        afficher_etat(m, erreurs, erreurs_max, deja)
        statut = traiter_lettre(mot, m, deja, input("Lettre : "))
        if statut == "invalide":
            print("Entrez une seule lettre.")
        elif statut == "deja":
            print("Lettre déjà proposée, pas de pénalité.")
        elif statut == "absent":
            erreurs += 1
            print("Raté !")
        else:
            print("Bien vu !")

    afficher_etat(m, erreurs, erreurs_max, deja)
    if "_" not in m:
        print(f"Gagné ! Le mot était {mot}.")
        return True
    print(f"Perdu, le mot était {mot}.")
    return False


def saisir_mot_secret():
    """Mode 2 joueurs : un joueur saisit (sans écho) le mot de l'autre."""
    while True:
        mot = getpass.getpass("Mot secret (invisible) : ").strip()
        if any(c.isalpha() for c in mot):
            return mot
        print("Le mot doit contenir au moins une lettre.")


def afficher_classement(table):
    print("\n=== Hall of fame ===")
    for nom, victoires in scores.classement(table):
        print(f"{nom:<15} {victoires:g}")


def main():
    table = scores.charger(FICHIER_SCORES)
    mots = charger_mots(FICHIER_MOTS)
    print("=== Jeu du Pendu ===")

    try:
        nom = input("Votre nom : ").strip() or "Anonyme"
        while True:
            mode = input("Mode : 1) mot aléatoire  2) mot choisi par un autre "
                         "joueur [1] : ").strip()
            mot = saisir_mot_secret() if mode == "2" else choisir_mot(mots)
            if jouer(mot):
                scores.ajouter_victoire(table, nom)
            if input("Rejouer ? (o/n) ").strip().lower() != "o":
                break
    except (EOFError, KeyboardInterrupt):
        print()
    finally:
        scores.sauvegarder(table, FICHIER_SCORES)

    afficher_classement(table)


if __name__ == "__main__":
    main()
