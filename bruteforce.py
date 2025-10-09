"""
Brute force TSP — compatible avec utils.py / point.py
- Dépôt = index 0
- Marche pour tous n <= 12 (au-delà on arrête proprement)
- Option: express_first=True pour tester uniquement (permuts express) x (permuts normaux)
"""

import itertools
import math
from typing import List, Tuple, Optional
from point import Point
from utils import build_distance_matrix, plot_tour  # build_distance_matrix: utils.py


def _tour_distance(dist: List[List[float]], order: Tuple[int, ...], depot: int = 0) -> float:
    """Somme des distances: depot -> ...order... -> depot."""
    total = 0.0
    cur = depot
    for v in order:
        total += dist[cur][v]
        cur = v
    total += dist[cur][depot]
    return total


def solve_tsp_bruteforce(
    points: List[Point],
    speed: float = 30.0,
    *,
    express_first: bool = False,
    plot: bool = False,
) -> Tuple[Optional[float], Optional[Tuple[int, ...]]]:
    """
    Résout le TSP par brute force.

    Args
    ----
    points : liste de Point (dépôt = index 0)
    speed  : vitesse (km/h) pour afficher la durée estimée
    express_first : si True, on impose (tous les express) avant (tous les normaux)
    plot : si True, trace la tournée optimale

    Returns
    -------
    (best_distance, best_tour) ou (None, None) si n > 12
    """
    n = len(points)
    if n < 2:
        print("⚠️  Besoin d'au moins dépôt + 1 client.")
        return None, None

    # Stop propre si instance trop grande
    if n > 12:
        print(f"⚠️  {n} points -> {(n-1)}! permutations : brute force désactivé.")
        return None, None

    # --- Matrice des distances ---
    dist = build_distance_matrix(points)  # utils.py
    # sécurité : matrice carrée
    if any(len(row) != n for row in dist):
        raise ValueError("❌ Matrice des distances non carrée / incomplète.")

    depot = 0
    clients = [i for i in range(n) if i != depot]

    # --- Espace de recherche ---
    if not express_first:
        # toutes les permutations des clients
        perms_iter = itertools.permutations(clients)
        nb_tours = math.factorial(len(clients))
    else:
        # (permuts express) x (permuts normaux)
        expr = [i for i in clients if points[i].est_express]
        norm = [i for i in clients if not points[i].est_express]
        perms_iter = (
            e_perm + n_perm
            for e_perm in itertools.permutations(expr)
            for n_perm in itertools.permutations(norm)
        )
        nb_tours = math.factorial(len(expr)) * math.factorial(len(norm))

    print(f"⏳ Brute force: évaluation de {nb_tours:,} tournées (n={n})...")

    # --- Recherche du meilleur ---
    best_distance = math.inf
    best_perm: Optional[Tuple[int, ...]] = None

    for perm in perms_iter:
        d = _tour_distance(dist, perm, depot)
        if d < best_distance:
            best_distance = d
            best_perm = perm

    assert best_perm is not None, "Aucune permutation générée (cas n<2 ?)."
    best_tour = (depot,) + best_perm + (depot,)

    # --- Affichage résumé ---
    print("\n===== Résultats (Brute Force) =====")
    print(f"Nombre de tournées testées : {nb_tours:,}")
    print(f"Distance minimale trouvée  : {best_distance:.3f} km")
    print(f"Tournée optimale           : {best_tour}")
    print(f"Durée totale estimée       : {best_distance / speed:.2f} h\n")

    if plot:
        # Traçage de la tournée (marqueurs dépôt/express/normal gérés par utils.plot_tour)
        plot_tour(points, list(best_tour))  # utils.plot_tour :contentReference[oaicite:1]{index=1}

    return best_distance, best_tour
