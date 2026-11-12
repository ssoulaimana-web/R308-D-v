"""TP3 - Partie D : programme principal (menu texte interactif)."""

from pathlib import Path

from bibliotheque import Bibliotheque
from livre import Livre
from utilisateur import Utilisateur

DOSSIER_DONNEES = Path(__file__).resolve().parent / "donnees"

MENU = """
=== Bibliothèque ===
1. Ajouter un livre
2. Ajouter un utilisateur
3. Emprunter un livre
4. Rendre un livre
5. Afficher les livres
6. Quitter et sauvegarder
7. Statistiques
8. Rechercher par auteur"""


def ajouter_livre(biblio):
    titre = input("Titre : ").strip()
    auteur = input("Auteur : ").strip()
    annee = input("Année : ").strip()
    if not titre or not auteur:
        print("Le titre et l'auteur sont obligatoires.")
        return
    try:
        livre = Livre(titre, auteur, annee)
    except ValueError:
        print("L'année doit être un nombre entier (ex. 1949).")
        return
    biblio.ajouter_livre(livre)
    print(biblio.dernier_message)


def ajouter_utilisateur(biblio):
    biblio.ajouter_utilisateur(Utilisateur(input("Nom : ")))
    print(biblio.dernier_message)


def emprunter(biblio):
    nom = input("Nom de l'utilisateur : ").strip()
    titre = input("Titre du livre : ").strip()
    biblio.emprunter(nom, titre)
    print(biblio.dernier_message)


def rendre(biblio):
    nom = input("Nom de l'utilisateur : ").strip()
    titre = input("Titre du livre : ").strip()
    biblio.rendre(nom, titre)
    print(biblio.dernier_message)


def afficher(biblio):
    biblio.afficher_livres()


def statistiques(biblio):
    stats = biblio.stats()
    print(f"Livres : {stats['total']} | emprunts : {stats['empruntes']}")
    for nom, nombre in stats["par_utilisateur"].items():
        print(f"  - {nom} : {nombre}")


def rechercher(biblio):
    resultats = biblio.recherche_par_auteur(input("Auteur (ou partie du nom) : "))
    if not resultats:
        print("Aucun livre trouvé.")
    for livre in resultats:
        livre.afficher()


ACTIONS = {"1": ajouter_livre, "2": ajouter_utilisateur, "3": emprunter,
           "4": rendre, "5": afficher, "7": statistiques, "8": rechercher}


def main(dossier=DOSSIER_DONNEES):
    biblio = Bibliotheque()
    if not biblio.charger(dossier):
        print(f"{biblio.dernier_message} Départ avec une bibliothèque vide.")
    else:
        print(f"État restauré : {biblio.dernier_message}")

    try:
        while True:
            print(MENU)
            choix = input("Votre choix : ").strip()
            if choix == "6":
                break
            action = ACTIONS.get(choix)
            if action is None:
                print("Choix invalide.")
            else:
                action(biblio)
    except (EOFError, KeyboardInterrupt):
        print()

    if biblio.sauvegarder(dossier):
        print("Données sauvegardées. Au revoir !")
    else:
        print(f"Attention : {biblio.dernier_message}")


if __name__ == "__main__":
    main()
