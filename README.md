# Graphe Algo TSP Express

Ce dépôt regroupe plusieurs implémentations d'algorithmes pour résoudre des variantes du **problème du voyageur de commerce (TSP)** avec des clients prioritaires ("express") et des contraintes de temps. Il a été conçu dans le cadre d'un projet pédagogique et fournit à la fois du code réutilisable et des démonstrations prêtes à l'emploi.

## Objectif du projet
Ce projet illustre différentes approches pour résoudre un TSP avec clients prioritaires "express". Les principaux algorithmes disponibles sont :
- heuristique hybride basée sur Christofides + insertion gloutonne (`algo/algorithme.py`) ;
- colonie de fourmis (`algo/aco.py`) ;
- recherche exhaustive pour validation sur petits jeux de données (`algo/bruteforce.py`).

## Structure du dépôt

- `point.py` : définition légère de la classe `Point` (coordonnées et statut express).
- `utils.py` : fonctions utilitaires pour générer des points, calculer des distances/matrices et visualiser une tournée.
- `algo/` : algorithmes principaux
  - `algorithme.py` : heuristique hybride (Christofides + insertion gloutonne minimisant l'objectif pondéré \(I = \alpha T + \beta \sum w_i t_i\)).
  - `christophides.py` : implémentation de Christofides (MST, appariement, raccourcis).
  - `aco.py` : optimisation par colonie de fourmis adaptée au contexte express/normal.
  - `bruteforce.py` : recherche exhaustive pour de très petits jeux de données (contrainte : express avant normaux).
  - `algorithme2.py`, `kruskal.py` : variantes et briques complémentaires.
- `main.ipynb` : carnet Jupyter illustrant l'utilisation des différents modules.

## Pré-requis

- Python 3.10 ou plus récent.
- `pip` afin d'installer les dépendances suivantes :
  ```bash
  pip install numpy matplotlib
  ```
  (Les algorithmes n'utilisent pas de bibliothèques externes supplémentaires.)

## Mise en place rapide

1. Créez et activez un environnement virtuel :
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # sous Windows : .venv\Scripts\activate
   ```
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancer :
   - `python -m pip install jupyter` puis ouvrir `main.ipynb` pour une exploration guidée.

## Résultats attendus
Les scripts affichent la tournée calculée ainsi que les temps d'arrivée. `utils.plot_tour` déclenche une figure matplotlib.

## Exécuter les démonstrations

### 1. Recherche exhaustive

Pour vérifier le comportement sur un petit ensemble (\< 11 points), lancez :

```bash
python -m algo.bruteforce
```

Le script génère un jeu de données aléatoire, calcule la tournée optimale sous contrainte "express d'abord" et imprime la matrice de distances.

## Carnet Jupyter

Le fichier `main.ipynb` rassemble des exemples plus détaillés (visualisations, comparaisons de complexités…). Ouvrez-le dans Jupyter Lab/Notebook après avoir installé les dépendances :
