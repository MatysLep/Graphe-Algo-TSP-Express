# Graphe Algo TSP Express

Ce dépôt regroupe plusieurs implémentations d'algorithmes pour résoudre des variantes du **problème du voyageur de commerce (TSP)** avec des clients prioritaires ("express") et des contraintes de temps. Il a été conçu dans le cadre d'un projet pédagogique et fournit à la fois du code réutilisable et des démonstrations prêtes à l'emploi.

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
   Si aucun fichier `requirements.txt` n'est fourni, installez simplement `numpy` et `matplotlib` comme indiqué plus haut.

## Exécuter les démonstrations

### 1. Algorithme hybride (Christofides + insertion gloutonne)

L'algorithme principal est exposé via la fonction `run` de `algo/algorithme.py`. Exemple minimal :

```bash
python - <<'PY'
from point import Point
from utils import make_demo_points
from algo.algorithme import run

points = make_demo_points(n_total=12, ratio_express=0.4, seed=42)
run(points, alpha=1.0, beta=0.2, w_express=2.0, w_normal=1.0, max_hours=8.0, speed=30.0)
PY
```

La commande affiche la tournée calculée, les temps d'arrivée et génère une visualisation matplotlib.

### 2. Recherche exhaustive

Pour vérifier le comportement sur un petit ensemble (\< 11 points), lancez :

```bash
python -m algo.bruteforce
```

Le script génère un jeu de données aléatoire, calcule la tournée optimale sous contrainte "express d'abord" et imprime la matrice de distances.

### 3. Colonie de fourmis (ACO)

L'algorithme ACO peut être exécuté depuis un script Python ou une session interactive :

```bash
python - <<'PY'
from point import Point
from utils import make_demo_points
from algo.aco import aco_solve, format_solution

points = make_demo_points(n_total=15, ratio_express=0.5, seed=21)
solution = aco_solve(points, alpha=1.0, beta=2.5, speed=30.0, max_hours=8.0, iterations=150)
print(format_solution(solution, points))
PY
```

Ajustez `iterations`, `ants` ou les poids `w_express` / `w_normal` pour explorer d'autres configurations.

## Carnet Jupyter

Le fichier `main.ipynb` rassemble des exemples plus détaillés (visualisations, comparaisons de complexités…). Ouvrez-le dans Jupyter Lab/Notebook après avoir installé les dépendances :

```bash
jupyter lab  # ou jupyter notebook
```

## Tests et validation

Aucun test automatisé n'est fourni. Pour vérifier rapidement que tout fonctionne, exécutez les scripts ci-dessus et assurez-vous que les figures s'affichent sans erreur.

## Licence

Ce projet est destiné à un usage pédagogique. Adaptez-le librement dans le cadre de vos travaux, en citant la source si nécessaire.

## Remarque importante

> Remarque : vous pouvez utiliser d’autres langages que Python si vous le souhaitez mais vous devez vous assurer que nous puissions l’exécuter (avec des instructions).
