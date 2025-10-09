"""
Brute force TSP — compatible avec utils.py / point.py
- Dépôt = index 0
- Marche pour tous n <= 12 (au-delà on arrête proprement)
- Option: express_first=True pour tester uniquement (permuts express) x (permuts normaux)
"""

import itertools
import math
from typing import Iterable, List, Optional, Sequence, Tuple, Union

from point import Point
from utils import build_distance_matrix, plot_tour  # build_distance_matrix: utils.py


def _tour_distance(dist: Sequence[Sequence[float]], order: Tuple[int, ...], depot: int = 0) -> float:
    """Somme des distances: depot -> ...order... -> depot."""
    total = 0.0
    cur = depot
    n = len(dist)
    for v in order:
        if not 0 <= v < n:
            raise IndexError(
                f"Indice de sommet invalide dans la permutation: {v} (attendu entre 0 et {n - 1})."
            )
        row = dist[cur]
        if v >= len(row):
            raise IndexError(
                f"Matrice des distances invalide: ligne {cur} de longueur {len(row)}, "
                f"mais tentative d'accès à la colonne {v}."
            )
        total += row[v]
        cur = v
    if not 0 <= depot < len(dist[cur]):
        raise IndexError(
            f"Indice de dépôt invalide lors du retour: {depot} (ligne {cur} de longueur {len(dist[cur])})."
        )
    total += dist[cur][depot]
    return total


def solve_tsp_bruteforce(
    data: Union[Sequence[Point], Sequence[Sequence[float]]],
    speed: float = 30.0,
    *,
    depot: int = 0,
    express_first: bool = False,
    express_clients: Optional[Iterable[int]] = None,
    plot: bool = False,
    return_nb_tours: bool = False,
) -> Union[
    Tuple[Optional[float], Optional[Tuple[int, ...]]],
    Tuple[Optional[float], Optional[Tuple[int, ...]], int],
]:
    """
    Résout le TSP par brute force.

    Args
    ----
    data :
        - liste de Point (dépôt = index 0 par défaut)
        - ou matrice d'adjacence (list[list[float]])
    speed  : vitesse (km/h) pour afficher la durée estimée (ignorée si `data` est une matrice)
    depot  : indice du dépôt (utile si le dépôt n'est pas à l'index 0 ou si on fournit directement
             une matrice d'adjacence)
    express_first : si True, on impose (tous les express) avant (tous les normaux)
    express_clients : indices des clients express lorsqu'on fournit directement une matrice
    plot : si True, trace la tournée optimale (nécessite une liste de `Point`)
    return_nb_tours : si True, renvoie également le nombre de permutations évaluées

    Returns
    -------
    - (best_distance, best_tour)
    - ou (best_distance, best_tour, nb_tours) si ``return_nb_tours`` vaut True
    - (None, None[, 0]) si l'instance est invalide ou trop grande
    """
    data_list = list(data)
    if not data_list:
        print("⚠️  Instance vide: aucun point fourni.")
        return (None, None, 0) if return_nb_tours else (None, None)

    points: Optional[List[Point]]
    if isinstance(data_list[0], Point):
        points = list(data_list)  # type: ignore[arg-type]
        n = len(points)
        if n < 2:
            print("⚠️  Besoin d'au moins dépôt + 1 client.")
            return (None, None, 0) if return_nb_tours else (None, None)

        # Stop propre si instance trop grande
        if n > 12:
            print(f"⚠️  {n} points -> {(n-1)}! permutations : brute force désactivé.")
            return (None, None, 0) if return_nb_tours else (None, None)

        dist = build_distance_matrix(points)
        express_set = {
            i for i, p in enumerate(points) if i != depot and getattr(p, "est_express", False)
        }
    else:
        points = None
        dist = [list(row) for row in data_list]  # type: ignore[list-item]
        n = len(dist)
        if n < 2:
            print("⚠️  Besoin d'au moins dépôt + 1 client.")
            return (None, None, 0) if return_nb_tours else (None, None)
        if any(len(row) != n for row in dist):
            raise ValueError("❌ Matrice des distances non carrée / incomplète.")
        express_set = set()

    if not 0 <= depot < n:
        raise ValueError(f"Indice de dépôt invalide: {depot} (attendu entre 0 et {n - 1}).")

    if express_clients is not None:
        express_set = {idx for idx in express_clients if idx != depot}
        invalid = [idx for idx in express_set if not 0 <= idx < n]
        if invalid:
            raise ValueError(
                "Certains clients express sont hors bornes pour la matrice fournie: "
                + ", ".join(map(str, invalid))
            )

    clients = [i for i in range(n) if i != depot]

    # --- Espace de recherche ---
    if not express_first:
        # toutes les permutations des clients
        perms_iter: Iterable[Tuple[int, ...]] = itertools.permutations(clients)
        nb_tours = math.factorial(len(clients))
    else:
        expr = [i for i in clients if i in express_set]
        norm = [i for i in clients if i not in express_set]
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
    if speed <= 0:
        print("Durée totale estimée       : vitesse invalide (<= 0).")
    else:
        print(f"Durée totale estimée       : {best_distance / speed:.2f} h\n")

    if plot:
        if points is None:
            raise ValueError("Impossible de tracer la tournée sans liste de points.")
        # Traçage de la tournée (marqueurs dépôt/express/normal gérés par utils.plot_tour)
        plot_tour(points, list(best_tour))  # utils.plot_tour

    if return_nb_tours:
        return best_distance, best_tour, nb_tours
    return best_distance, best_tour
