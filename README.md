# 🚚 Graphe-Algo-TSP-Express
> **Optimiser la logistique grâce à la théorie des graphes : une solution hybride pour le Problème du Voyageur de Commerce (TSP) avec gestion de contraintes "Express".**

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Visualization-Matplotlib-11557c?logo=python)
![NumPy](https://img.shields.io/badge/Computation-NumPy-013243?logo=numpy)

---

## 🎯 Contexte & Objectif
Projet réalisé dans le cadre du module "Graphes et Algorithmes" à l'**IMT Nord Europe**.

**Le Défi : Dompter la complexité NP-Difficile**
Le problème du Voyageur de Commerce (TSP) est notoirement **NP-Difficile** : le temps de calcul pour trouver la solution optimale explose factoriellement ($O(n!)$) avec le nombre de villes, rendant les méthodes exactes inutilisables pour le passage à l'échelle.

**Pourquoi ces choix algorithmiques ?**
Comme détaillé dans le *Rapport de Projet*, nous avons implémenté une double approche pour analyser ce compromis coût/performance :
1.  **Brute Force** : Sert de "vérité terrain" pour valider la correction des résultats sur de petites instances ($n < 10$).
2.  **Algorithme de Christofides** : Choisi spécifiquement car il constitue la **référence théorique** pour le TSP métrique. Il garantit une solution au pire 1.5 fois plus longue que l'optimale (ratio 3/2), surclassant la simple approximation MST (ratio 2) ou les approches purement gloutonnes, offrant ainsi le meilleur équilibre entre temps d'exécution polynomial et qualité de résultat.

## 🏗️ Aperçu Technique & Architecture
Ce projet implémente une approche modulaire pour résoudre le TSP (Traveling Salesperson Problem), en comparant des méthodes exactes et approximatives. L'architecture sépare clairement la **logique algorithmique** (`algo/`), les **structures de données** (`point.py`) et les **outils de visualisation/analyse** (`utils.py`).

L'implémentation phare est l'**Algorithme de Christofides**, une méthode sophistiquée offrant une approximation garantie (factor 1.5) pour le TSP métrique, construite via un pipeline de transformations de graphes (MST -> Matching -> Eulerian -> Hamiltonian).

## ✨ Fonctionnalités Clés
- 🎯 **Résolution Hybride** : Comparaison directe entre une solution exacte (**Brute Force** O(n!)) et une approximation rapide (**Christofides** polynomial).
- 📦 **Gestion "Express"** : Prise en charge de points de livraison prioritaires ("Express") modifiant la logique de coût et de tournée (`utils.py`).
- 📊 **Visualisation Interactive** : Génération automatique de graphiques matplotlib pour visualiser les tournées finales et comparer les courbes de complexité asymptotique.
- 🧮 **Algorithmes Avancés** : Implémentation "from scratch" de Prim (MST), Hierholzer (Tour Eulérien) et d'un Matching Glouton.

## 🛠️ Stack Technique

| Catégorie | Technologies |
| :--- | :--- |
| **Langage** | Python 3 |
| **Algorithmes** | Christofides, Prim, Kruskal, Hierholzer, Brute Force |
| **Calcul Scientifique** | NumPy |
| **Visualisation** | Matplotlib |
| **Format** | Jupyter Noteook (`main.ipynb`) & Scripts modulaires |

## 🚀 Installation & Usage

Cloner le projet et installer les dépendances nécessaires.

```bash
# Cloner le dépôt
git clone https://github.com/MatysLep/Graphe-Algo-TSP-Express.git
cd Graphe-Algo-TSP-Express

# Créer un environnement virtuel (recommandé)
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows : .venv\Scripts\activate

# Installer les dépendances
pip install matplotlib numpy

# Lancer le notebook de démonstration ou le script principal
# (Exemple si lancement via script)
python algo/christophides.py 
# Ou ouvrir main.ipynb via Jupyter
```

## 💡 Challenge & Apprentissage

Un défi majeur de ce projet a été l'implémentation de **l'étape de couplage (Matching) dans l'algorithme de Christofides**.

L'algorithme théorique requiert un *Minimum Weight Perfect Matching* (MWPM), dont la résolution exacte passe généralement par l'algorithme des "Blossom" (Edmonds), excessivement complexe à implémenter pour un projet de cette échelle.

**Solution :**
J'ai opté pour une approche pragmatique en implémentant une **heuristique gloutonne (Greedy Heuristic)** pour le couplage des sommets de degré impair. 
- Au lieu de chercher le matching global optimal, l'algorithme sélectionne itérativement l'arête la moins coûteuse connectant deux sommets non appariés.
- **Résultat** : Une réduction drastique de la complexité du code tout en maintenant une approximation très proche de l'optimale pour les instances de test, un compromis ingénierie réaliste entre perfection théorique et maintenabilité.
