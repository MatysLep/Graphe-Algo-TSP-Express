from __future__ import annotations
import itertools
import math
from typing import Sequence, Tuple


def tour_distance(order: Sequence[int],
                  dist: Sequence[Sequence[float]],
                  depot: int = 0) -> float:
    """
    Calcule la distance totale pour une tournée.

    Parcours : dépôt -> clients dans `order` -> retour dépôt.

    Args:
        order: permutation des clients (sans le dépôt).
        dist: matrice d'adjacence (symétrique, dist[i][i] == 0).
        depot: indice du sommet jouant le rôle de dépôt.

    Returns:
        Distance totale de la tournée.
    """
    total = 0.0
    cur = depot
    for v in order:
        total += dist[cur][v]
        cur = v
    total += dist[cur][depot]
    return total


def solve_tsp_bruteforce(
    dist: Sequence[Sequence[float]],
    depot: int = 0,
    *,
    return_nb_tours: bool = False,
) -> Tuple[float, Tuple[int, ...]] | Tuple[float, Tuple[int, ...], int]:
    """
    Résout le TSP par force brute pour un dépôt fixé.

    Explore toutes les permutations des clients (n-1)! et renvoie la meilleure tournée.

    Args:
        dist: matrice d'adjacence des distances (symétrique).
        depot: indice du dépôt (par défaut 0).
        return_nb_tours: si True, renvoie aussi le nombre de tournées évaluées.

    Returns:
        - best_distance: longueur minimale trouvée.
        - best_tour: tuple représentant la tournée complète (depot, ..., depot).
        - nb_tours (optionnel): nombre de permutations évaluées ((n-1)!).
    """
    n = len(dist)
    clients = [i for i in range(n) if i != depot]

    best_distance = math.inf
    best_perm: Tuple[int, ...] | None = None

    for perm in itertools.permutations(clients):
        d = tour_distance(perm, dist, depot)
        if d < best_distance:
            best_distance = d
            best_perm = perm

    assert best_perm is not None, "Aucune permutation évaluée (matrice trop petite ?)"

    best_tour = (depot,) + best_perm + (depot,)
    if return_nb_tours:
        return best_distance, best_tour, math.factorial(len(clients))
    return best_distance, best_tour


if __name__ == "__main__":
    # Exemple d'utilisation avec ta matrice :
    example_dist = [
        [0.0, 2.24, 4.24, 4.12, 4.0],
        [2.24, 0.0, 2.24, 3.16, 2.24],
        [4.24, 2.24, 0.0, 2.24, 3.16],
        [4.12, 3.16, 2.24, 0.0, 5.0],
        [4.0, 2.24, 3.16, 5.0, 0.0],
    ]

    best_d, best_tour, nb = solve_tsp_bruteforce(example_dist, depot=0, return_nb_tours=True)
    print("Nombre de tournées testées :", nb)
    print("Meilleure tournée trouvée :")
    print(" Distance totale =", best_d)
    print(" Ordre =", best_tour)