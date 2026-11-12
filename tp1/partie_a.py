"""TP1 - Partie A : dictionnaire d'étudiants (nom -> note)."""

import math

NOTE_MIN, NOTE_MAX = 0.0, 20.0


def convertir_note(valeur):
    """Convertit `valeur` en float compris entre 0 et 20.

    Accepte la virgule décimale ("12,5"). Lève ValueError si la valeur
    n'est pas convertible ou sort de l'intervalle.
    """
    if isinstance(valeur, str):
        valeur = valeur.strip().replace(",", ".")
    try:
        note = float(valeur)
    except (TypeError, ValueError):
        raise ValueError(f"note invalide : {valeur!r}") from None
    if not math.isfinite(note) or not NOTE_MIN <= note <= NOTE_MAX:
        raise ValueError(f"note hors de [0, 20] : {valeur!r}")
    return note


def ajouter_etudiant(d, nom, note):
    """Ajoute ou met à jour un étudiant dans `d`.

    Renvoie True si l'opération a réussi, False si le nom ou la note est
    invalide (le dictionnaire reste alors inchangé).
    """
    nom = str(nom).strip()
    if not nom:
        return False
    try:
        d[nom] = convertir_note(note)
    except ValueError:
        return False
    return True


def moyenne_classe(d):
    """Moyenne arrondie à 2 décimales (0.0 si le dictionnaire est vide)."""
    if not d:
        return 0.0
    return round(sum(d.values()) / len(d), 2)


def meilleur_etudiant(d):
    """Renvoie (nom, note) du meilleur étudiant, ou None si `d` est vide."""
    if not d:
        return None
    nom = max(d, key=d.get)
    return nom, d[nom]


def sauvegarder(d, chemin):
    """Écrit `d` dans `chemin` (une ligne "nom:note" par étudiant).

    Renvoie True en cas de succès, False en cas d'erreur d'écriture.
    """
    try:
        with open(chemin, "w", encoding="utf-8") as f:
            for nom, note in d.items():
                f.write(f"{nom}:{note}\n")
    except OSError as erreur:
        print(f"Erreur d'écriture de {chemin} : {erreur}")
        return False
    return True


def charger(chemin):
    """Lit un fichier "nom:note" et renvoie le dictionnaire correspondant.

    Fichier absent ou illisible -> dictionnaire vide. Les lignes mal
    formées sont ignorées (avec un avertissement).
    """
    d = {}
    try:
        with open(chemin, encoding="utf-8") as f:
            lignes = f.readlines()
    except FileNotFoundError:
        print(f"Fichier {chemin} introuvable : départ avec une classe vide.")
        return d
    except (OSError, UnicodeDecodeError) as erreur:
        print(f"Lecture de {chemin} impossible : {erreur}")
        return d

    for numero, ligne in enumerate(lignes, start=1):
        ligne = ligne.strip()
        if not ligne:
            continue
        nom, separateur, note = ligne.rpartition(":")
        if not separateur or not ajouter_etudiant(d, nom, note):
            print(f"Ligne {numero} ignorée (mal formée) : {ligne!r}")
    return d


def main():
    classe = {}
    for nom, note in (("Alice", 12), ("Bob", 15), ("Claire", 9.5)):
        ajouter_etudiant(classe, nom, note)

    print("Classe :", classe)
    print("Moyenne :", moyenne_classe(classe))
    print("Meilleur étudiant :", meilleur_etudiant(classe))

    fichier = "etudiants.txt"
    if sauvegarder(classe, fichier):
        print(f"Sauvegardé dans {fichier}, rechargé :", charger(fichier))


if __name__ == "__main__":
    main()
