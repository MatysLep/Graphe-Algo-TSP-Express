# Informations pour l'enseignant

## Objectif du projet
Ce projet illustre différentes approches pour résoudre un TSP avec clients prioritaires "express". Les principaux algorithmes disponibles sont :
- heuristique hybride basée sur Christofides + insertion gloutonne (`algo/algorithme.py`) ;
- colonie de fourmis (`algo/aco.py`) ;
- recherche exhaustive pour validation sur petits jeux de données (`algo/bruteforce.py`).

## Comment lancer une démonstration rapide ?
1. Créer un environnement virtuel (optionnel mais recommandé) :
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancer au choix :
   - `python -m algo.bruteforce` pour le brute force ;
   - le bloc de démonstration indiqué dans le README pour `algo/algorithme.py` ;
   - ou `python -m pip install jupyter` puis ouvrir `main.ipynb` pour une exploration guidée.

## Résultats attendus
Les scripts affichent la tournée calculée ainsi que les temps d'arrivée. `utils.plot_tour` déclenche une figure matplotlib.

## Remarque du professeur
Remarque : vous pouvez utiliser d’autres langages que Python si vous le souhaitez mais vous devez vous assurer que nous puissions l’exécuter (avec des instructions).
