"""TP1 - Partie C : manipulation des mots."""

import random
from pathlib import Path

# Liste de secours si le fichier mots.txt est absent ou vide.
MOTS_PAR_DEFAUT = ["python", "reseau", "routeur", "commutateur", "protocole",
                   "serveur", "passerelle", "fibre", "ethernet"]


def charger_mots(chemin=None):
    """Charge une liste de mots (un par ligne) depuis un fichier .txt.

    Sans chemin, ou si le fichier est absent, illisible ou vide, la liste
    par défaut est utilisée.
    """
    if chemin is None:
        return list(MOTS_PAR_DEFAUT)
    try:
        texte = Path(chemin).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        print(f"{chemin} illisible : liste de mots par défaut utilisée.")
        return list(MOTS_PAR_DEFAUT)
    mots = [ligne.strip() for ligne in texte.splitlines() if ligne.strip()]
    return mots or list(MOTS_PAR_DEFAUT)


def choisir_mot(liste):
    """Renvoie un mot de `liste` tiré au hasard, en MAJUSCULES."""
    if not liste:
        raise ValueError("la liste de mots est vide")
    return random.choice(liste).strip().upper()


def masque(mot):
    """Renvoie une liste de « _ » de même longueur que `mot`."""
    return ["_"] * len(mot)


def main():
    mot = choisir_mot(charger_mots(Path(__file__).with_name("mots.txt")))
    print("Mot choisi :", mot)
    print("Masque     :", masque(mot))


if __name__ == "__main__":
    main()
