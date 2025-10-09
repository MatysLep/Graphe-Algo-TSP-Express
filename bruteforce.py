from __future__ import annotations

import itertools
import math
from typing import Sequence, Tuple

from point import Point


def build_distance_matrix_from_points(points: Sequence[Point]) -> list[list[float]]:
    """Construit la matrice euclidienne complète pour une liste de points."""

    pts = list(points)
    n = len(pts)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = math.hypot(pts[i].x - pts[j].x, pts[i].y - pts[j].y)
            matrix[i][j] = matrix[j][i] = d
    return matrix


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
    express_clients: Sequence[int] | None = None,
    return_nb_tours: bool = False,
) -> Tuple[float, Tuple[int, ...]] | Tuple[float, Tuple[int, ...], int]:
    """
    Résout le TSP par force brute pour un dépôt fixé.

    Explore toutes les permutations des clients (n-1)! et renvoie la meilleure tournée.
    Les clients express sont visités en premier (dans toutes leurs permutations), puis
    les clients normaux.

    Args:
        dist: matrice d'adjacence des distances (symétrique).
        depot: indice du dépôt (par défaut 0).
        express_clients: indices (hors dépôt) devant être visités avant les normaux.
        return_nb_tours: si True, renvoie aussi le nombre de tournées évaluées.

    Returns:
        - best_distance: longueur minimale trouvée.
        - best_tour: tuple représentant la tournée complète (depot, ..., depot).
        - nb_tours (optionnel): nombre de permutations évaluées ((n-1)!).
    """
    n = len(dist)
    clients = [i for i in range(n) if i != depot]

    if len(clients) != 10:
        raise ValueError(
            "La résolution par force brute est définie pour 10 clients (hors dépôt)."
        )

    express_set = set(express_clients or [])

    if depot in express_set:
        raise ValueError("Le dépôt ne peut pas être un client express.")

    if not express_set.issubset(clients):
        raise ValueError("Les clients express doivent appartenir à la matrice fournie.")

    express_order = [i for i in clients if i in express_set]
    normal_order = [i for i in clients if i not in express_set]

    best_distance = math.inf
    best_perm: Tuple[int, ...] | None = None

    nb_tours = 0

    for express_perm in itertools.permutations(express_order):
        for normal_perm in itertools.permutations(normal_order):
            nb_tours += 1
            perm = express_perm + normal_perm
            d = tour_distance(perm, dist, depot)
            if d < best_distance:
                best_distance = d
                best_perm = perm

    assert best_perm is not None, "Aucune permutation évaluée (matrice trop petite ?)"

    best_tour = (depot,) + best_perm + (depot,)
    if return_nb_tours:
        return best_distance, best_tour, nb_tours
    return best_distance, best_tour


def solve_tsp_bruteforce_from_points(
    points: Sequence[Point],
    depot: int = 0,
    *,
    return_nb_tours: bool = False,
) -> Tuple[float, Tuple[int, ...]] | Tuple[float, Tuple[int, ...], int]:
    """Construit la matrice des distances depuis une liste de ``Point``.

    Les clients express sont déduits automatiquement via ``Point.est_express``.
    """

    pts = list(points)
    express_clients = [
        i for i, pt in enumerate(pts) if i != depot and getattr(pt, "est_express", False)
    ]
    dist = build_distance_matrix_from_points(pts)
    return solve_tsp_bruteforce(
        dist,
        depot=depot,
        express_clients=express_clients,
        return_nb_tours=return_nb_tours,
    )


def demo_points() -> Sequence[Point]:
    """Retourne un jeu de démonstration avec 10 clients (+ dépôt)."""

    return [
        Point(0.0, 0.0, est_express=False),  # dépôt
        Point(1.0, 0.0, est_express=True),
        Point(2.0, 1.0, est_express=True),
        Point(3.0, 1.5, est_express=False),
        Point(4.0, 0.5, est_express=False),
        Point(5.0, 0.0, est_express=False),
        Point(1.0, 2.0, est_express=True),
        Point(2.0, 3.0, est_express=True),
        Point(3.0, 3.5, est_express=False),
        Point(4.0, 3.0, est_express=False),
        Point(5.0, 2.0, est_express=False),
    ]


def main() -> None:
    """Exécute la démonstration brute force avec visualisation."""

    points = demo_points()

    best_d, best_tour, nb = solve_tsp_bruteforce_from_points(
        points, return_nb_tours=True
    )

    print("Nombre de tournées testées :", nb)
    print("Meilleure tournée trouvée :")
    print(" Distance totale =", best_d)
    print(" Ordre =", best_tour)

    try:
        from utils import plot_tour  # import tardif pour éviter la dépendance si inutile
    except ModuleNotFoundError as exc:
        print(
            "Impossible d'afficher le graphe : matplotlib n'est pas installé (", exc, ")",
        )
    else:
        plot_tour(list(points), list(best_tour))


if __name__ == "__main__":
    main()
