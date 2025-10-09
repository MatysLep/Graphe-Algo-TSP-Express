from __future__ import annotations

import itertools
import importlib.util
import math
from typing import List, Sequence, Tuple

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


def convert_dist_to_time(
    W_dist: Sequence[Sequence[float]], speed: float | None
) -> List[List[float]]:
    """Convertit une matrice de distances en temps (en fonction de la vitesse)."""

    n = len(W_dist)
    if speed is None:
        return [list(row) for row in W_dist]
    if speed <= 0:
        raise ValueError("La vitesse doit être strictement positive.")
    return [[W_dist[i][j] / speed for j in range(n)] for i in range(n)]


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


def compute_arrival_times(W_time: Sequence[Sequence[float]],
                          tour: Sequence[int]) -> List[float]:
    """Calcule les temps d'arrivée cumulés le long d'un tour complet."""

    t = [0.0] * len(tour)
    for k in range(1, len(tour)):
        a, b = tour[k - 1], tour[k]
        t[k] = t[k - 1] + W_time[a][b]
    return t


def compute_objective(arrival_times: Sequence[float],
                      tour: Sequence[int],
                      weights: Sequence[float],
                      alpha: float,
                      beta: float) -> Tuple[float, float, float]:
    """Retourne (I, alpha_term, beta_term) pour un tour donné."""

    total_time = arrival_times[-1]
    alpha_term = alpha * total_time
    beta_sum = 0.0
    for pos in range(1, len(tour) - 1):
        node = tour[pos]
        beta_sum += weights[node] * arrival_times[pos]
    beta_term = beta * beta_sum
    I = alpha_term + beta_term
    return I, alpha_term, beta_term


def solve_tsp_bruteforce(
    dist: Sequence[Sequence[float]],
    depot: int = 0,
    *,
    express_clients: Sequence[int] | None = None,
    travel_time: Sequence[Sequence[float]] | None = None,
    weights: Sequence[float] | None = None,
    alpha: float = 1.0,
    beta: float = 1.0,
    max_hours: float | None = None,
    return_nb_tours: bool = False,
) -> Tuple[float, Tuple[int, ...]] | Tuple[float, Tuple[int, ...], int]:
    """
    Résout le TSP par force brute pour un dépôt fixé.

    Explore toutes les permutations des clients (n-1)! et renvoie la meilleure tournée
    selon l'objectif ``I = alpha * durée_totale + beta * Σ w_i t_i``. Les clients
    express sont visités en premier (dans toutes leurs permutations), puis les clients
    normaux. Une contrainte de durée maximale (``max_hours``) peut être imposée.

    Args:
        dist: matrice d'adjacence des distances (symétrique).
        depot: indice du dépôt (par défaut 0).
        express_clients: indices (hors dépôt) devant être visités avant les normaux.
        travel_time: matrice des temps de trajet (même dimensions que ``dist``).
        weights: poids w_i associés à chaque client (indice global).
        alpha: coefficient de la durée totale.
        beta: coefficient de la somme pondérée des temps d'arrivée.
        max_hours: durée maximale autorisée (None pour aucune contrainte).
        return_nb_tours: si True, renvoie aussi le nombre de permutations évaluées.

    Returns:
        - best_distance: longueur minimale associée au meilleur tour selon I.
        - best_tour: tuple représentant la tournée complète (depot, ..., depot).
        - nb_tours (optionnel): nombre de permutations évaluées.
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

    if travel_time is None:
        travel_time = dist

    if weights is None:
        weights = [0.0] * n

    best_distance = math.inf
    best_perm: Tuple[int, ...] | None = None
    best_objective = math.inf

    nb_tours = 0

    for express_perm in itertools.permutations(express_order):
        for normal_perm in itertools.permutations(normal_order):
            nb_tours += 1
            perm = express_perm + normal_perm
            tour = (depot,) + perm + (depot,)
            arrival_times = compute_arrival_times(travel_time, tour)
            total_time = arrival_times[-1]

            if max_hours is not None and total_time > max_hours:
                continue

            I, alpha_term, beta_term = compute_objective(
                arrival_times, tour, weights, alpha, beta
            )

            distance = tour_distance(perm, dist, depot)

            if I < best_objective:
                best_objective = I
                best_perm = perm
                best_distance = distance
            elif math.isclose(I, best_objective) and best_perm is not None:
                # En cas d'ex aequo, privilégier la plus courte distance.
                if distance < best_distance:
                    best_perm = perm
                    best_distance = distance

    if best_perm is None:
        if max_hours is not None:
            raise ValueError(
                "Aucune tournée ne respecte la contrainte de durée maximale fournie."
            )
        raise ValueError("Aucune permutation évaluée : matrice trop petite ?")

    best_tour = (depot,) + best_perm + (depot,)
    if return_nb_tours:
        return best_distance, best_tour, nb_tours
    return best_distance, best_tour


def solve_tsp_bruteforce_from_points(
    points: Sequence[Point],
    depot: int = 0,
    *,
    alpha: float = 1.0,
    beta: float = 1.0,
    w_express: float = 3.0,
    w_normal: float = 1.0,
    max_hours: float | None = None,
    speed: float | None = None,
    return_nb_tours: bool = False,
) -> Tuple[float, Tuple[int, ...]] | Tuple[float, Tuple[int, ...], int]:
    """Construit matrices et paramètres depuis une liste de ``Point``.

    Les clients express sont déduits automatiquement via ``Point.est_express`` et le
    problème est résolu selon l'objectif composite utilisé par ``algorithme.py``.
    """

    pts = list(points)
    express_clients = [
        i for i, pt in enumerate(pts) if i != depot and getattr(pt, "est_express", False)
    ]
    dist = build_distance_matrix_from_points(pts)
    W_time = convert_dist_to_time(dist, speed)
    weights = [0.0] * len(pts)
    for i, pt in enumerate(pts):
        if i == depot:
            continue
        weights[i] = w_express if getattr(pt, "est_express", False) else w_normal
    return solve_tsp_bruteforce(
        dist,
        depot=depot,
        express_clients=express_clients,
        travel_time=W_time,
        weights=weights,
        alpha=alpha,
        beta=beta,
        max_hours=max_hours,
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


def run(
    points: Sequence[Point],
    alpha: float,
    beta: float,
    w_express: float,
    w_normal: float,
    max_hours: float,
    speed: float | None = None,
) -> None:
    """Lance la résolution brute force avec affichage des métriques et du graphe."""

    pts = list(points)
    if len(pts) - 1 != 10:
        raise ValueError(
            "L'algorithme brute force nécessite exactement 10 clients (hors dépôt)."
        )

    dist = build_distance_matrix_from_points(pts)
    W_time = convert_dist_to_time(dist, speed)
    weights = [0.0] * len(pts)
    for i, pt in enumerate(pts):
        if i == 0:
            continue
        weights[i] = w_express if pt.est_express else w_normal

    result = solve_tsp_bruteforce(
        dist,
        express_clients=[i for i, pt in enumerate(pts) if i != 0 and pt.est_express],
        travel_time=W_time,
        weights=weights,
        alpha=alpha,
        beta=beta,
        max_hours=max_hours,
        return_nb_tours=True,
    )

    best_distance, best_tour, nb_tours = result
    arrival_times = compute_arrival_times(W_time, best_tour)
    I, alpha_term, beta_term = compute_objective(arrival_times, best_tour, weights, alpha, beta)

    print("\n--- Résultats brute force ---")
    print(f"Nombre de tournées évaluées : {nb_tours}")
    print("Tour (indices):", best_tour)
    print("Heures d'arrivée (par position dans le tour):")
    print([round(x, 3) for x in arrival_times])
    print(
        f"I final = {I:.3f}  (alpha_term={alpha_term:.3f}, beta_term={beta_term:.3f})"
    )
    print(
        f"Durée totale = {arrival_times[-1]:.3f} h  (contrainte max = {max_hours} h)"
    )
    print(f"Distance totale = {best_distance:.3f}")

    print("\nDétails des noeuds visités (index, type, t_arr):")
    for pos, node in enumerate(best_tour):
        typ = "DEPOT" if node == 0 else ("EXPRESS" if pts[node].est_express else "NORMAL")
        print(f"  pos {pos:02d}: node {node:02d}  {typ:7s}  t={arrival_times[pos]:.3f} h")

    if importlib.util.find_spec("matplotlib") is None:
        print("Impossible d'afficher le graphe : matplotlib n'est pas installé.")
    else:
        from utils import plot_tour  # import tardif (matplotlib garanti disponible)

        plot_tour(list(pts), list(best_tour))


def main() -> None:
    """Démonstration de la résolution brute force avec les paramètres par défaut."""

    points = demo_points()
    run(points, alpha=1.0, beta=1.0, w_express=3.0, w_normal=1.0, max_hours=8.0, speed=30)


if __name__ == "__main__":
    main()
