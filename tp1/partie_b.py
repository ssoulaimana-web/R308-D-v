"""TP1 - Partie B : mini-jeu « Devine le nombre »."""

import random

ESSAIS_MAX = 10


def comparer(secret, proposition):
    """Renvoie « Trop petit », « Trop grand » ou « Gagné »."""
    if proposition < secret:
        return "Trop petit"
    if proposition > secret:
        return "Trop grand"
    return "Gagné"


def lire_entier(invite, defaut=None):
    """Demande un entier ; une saisie vide renvoie `defaut` s'il est fourni."""
    while True:
        texte = input(invite).strip()
        if texte == "" and defaut is not None:
            return defaut
        try:
            return int(texte)
        except ValueError:
            print("Veuillez entrer un nombre entier.")


def jouer(borne_min=1, borne_max=100, essais_max=ESSAIS_MAX, secret=None):
    """Joue une partie. Renvoie True si le joueur a gagné."""
    if secret is None:
        secret = random.randint(borne_min, borne_max)
    print(f"J'ai choisi un nombre entre {borne_min} et {borne_max}. "
          f"Vous avez {essais_max} essais.")

    essais = 0
    while essais < essais_max:
        proposition = lire_entier(f"Essai {essais + 1}/{essais_max} : ")
        if not borne_min <= proposition <= borne_max:
            # Proposition hors bornes : message, sans consommer d'essai.
            print(f"Entrez un nombre entre {borne_min} et {borne_max}.")
            continue
        essais += 1
        resultat = comparer(secret, proposition)
        print(resultat)
        if resultat == "Gagné":
            print(f"Bravo, trouvé en {essais} essai(s) !")
            return True

    print(f"Perdu ! Le nombre était {secret}.")
    return False


def demander_bornes():
    """Bonus : bornes personnalisées (Entrée = valeurs par défaut)."""
    while True:
        borne_min = lire_entier("Borne minimale [1] : ", 1)
        borne_max = lire_entier("Borne maximale [100] : ", 100)
        if borne_min < borne_max:
            return borne_min, borne_max
        print("La borne maximale doit être supérieure à la borne minimale.")


def main():
    print("=== Devine le nombre ===")
    borne_min, borne_max = 1, 100
    if input("Bornes personnalisées ? (o/n) ").strip().lower() == "o":
        borne_min, borne_max = demander_bornes()

    try:
        while True:
            jouer(borne_min, borne_max)
            if input("Rejouer ? (o/n) ").strip().lower() != "o":
                break
    except (EOFError, KeyboardInterrupt):
        print()
    print("À bientôt !")


if __name__ == "__main__":
    main()
