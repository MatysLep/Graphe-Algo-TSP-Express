from typing import List, Sequence, Tuple, Optional
import math
import random
import matplotlib.pyplot as plt

from utils import *
from point import Point
from christophides import christophides

# ----------------------------
# Calcul de l'objectif I
# ----------------------------
def compute_arrival_times(W_time: Sequence[Sequence[float]], tour: List[int]) -> List[float]:
    """
    t[k] = heure d'arrivée au sommet tour[k] (tour[0] est le dépôt avec t=0).
    Hypothèse: pas de temps de service.
    """
    t = [0.0] * len(tour)
    for k in range(1, len(tour)):
        a, b = tour[k - 1], tour[k]
        t[k] = t[k - 1] + W_time[a][b]
    return t


def compute_I(W_time: Sequence[Sequence[float]],tour: List[int],weights: Sequence[float],alpha: float, beta: float) -> Tuple[float, float, float, List[float]]:
    """
    Retourne (I, alpha_term, beta_term, arrival_times)
    - total_time = t[-1]
    - alpha_term = alpha * total_time
    - beta_term = beta * sum_{i in L} w_i * t_i  (on ignore dépôt en début/fin)
    """
    t = compute_arrival_times(W_time, tour)
    total_time = t[-1]
    alpha_term = alpha * total_time
    beta_sum = 0.0
    # Ignorer le dépôt initial (pos 0) et, lorsqu'il existe, le dépôt final (dernière pos)
    for pos in range(1, len(tour) - 1):
        node = tour[pos]
        beta_sum += weights[node] * t[pos]
    beta_term = beta * beta_sum
    I = alpha_term + beta_term
    return I, alpha_term, beta_term, t


# -----------------------------------------
# Insertion gloutonne minimisant directement I
# -----------------------------------------
def greedy_insert_min_I(W_time: Sequence[Sequence[float]],tour: List[int],weights: Sequence[float],alpha: float,beta: float,node_to_insert: int,max_duration_hours: float = 8.0) -> Optional[List[int]]:
    """
    Insère 'node_to_insert' dans 'tour' à la position minimisant ΔI, en respectant
    la contrainte de durée totale <= max_duration_hours. Retourne le nouveau tour
    si faisable, sinon None.
    """
    best_tour = None
    best_I = float('inf')

    base_I, _, _, base_t = compute_I(W_time, tour, weights, alpha, beta)

    # Suffixe des poids cumulé pour estimer l'impact de décalage sur t_j
    suffix_sum_w = [0.0] * len(tour)
    running = 0.0
    for k in range(len(tour) - 1, -1, -1):
        running += weights[tour[k]]
        suffix_sum_w[k] = running

    # Durée actuelle
    base_total = base_t[-1]

    for insert_pos in range(len(tour) - 1):  # insérer entre tour[i] et tour[i+1]
        a, b = tour[insert_pos], tour[insert_pos + 1]
        delta_leg = W_time[a][node_to_insert] + W_time[node_to_insert][b] - W_time[a][b]

        # Si on dépasse déjà la durée max, inutile d'aller plus loin
        cand_total = base_total + delta_leg
        if cand_total > max_duration_hours:
            continue

        # Nouvelle heure d'arrivée du noeud inséré
        t_a = base_t[insert_pos]
        t_node = t_a + W_time[a][node_to_insert]

        # Tous les sommets après l'insertion voient leur t_j augmenté de delta_leg
        sum_w_after = suffix_sum_w[insert_pos + 1]

        delta_alpha = alpha * delta_leg
        delta_beta = beta * (weights[node_to_insert] * t_node + sum_w_after * delta_leg)

        cand_I = base_I + delta_alpha + delta_beta
        if cand_I < best_I:
            best_I = cand_I
            best_tour = tour[:insert_pos + 1] + [node_to_insert] + tour[insert_pos + 1:]

    return best_tour


def insertion_gloutonne_par_I(W_time: Sequence[Sequence[float]],tour_express_global: List[int],normals_idx: List[int],weights: Sequence[float],alpha: float,beta: float,max_duration_hours: float = 8.0) -> List[int]:
    """
    Insère chaque point normal (séquentiellement) en minimisant ΔI
    et en respectant la durée max. Lève ValueError si impossible.
    """
    tour = tour_express_global[:]
    for node in normals_idx:
        new_tour = greedy_insert_min_I(W_time, tour, weights, alpha, beta, node, max_duration_hours)
        if new_tour is None:
            raise ValueError(
                f"Aucune insertion faisable (<= {max_duration_hours}h) pour le point normal {node}."
            )
        tour = new_tour
    return tour


# ----------------------------
# Backbone express + insertion
# ----------------------------
def tsp_mixte_backbone_I(points: List[Point],alpha: float,beta: float,w_express: float = 2.0,w_normal: float = 1.0,max_hours: float = 8.0,speed: Optional[float] = None) -> Tuple[List[int], float, float, float, List[float]]:
    """
    Construit la tournée:
      1) Christofides sur (dépôt + express) -> "backbone"
      2) insertion gloutonne des normaux minimisant I
      3) calcule I final et décompose alpha/beta
    Retourne: (tour_final, I_final, alpha_term, beta_term, arrival_times)
    """
    n = len(points)
    if n == 0 or 0 >= n:
        raise ValueError("La liste de points doit contenir au moins le dépôt en position 0.")
    # Matrices
    W_dist = build_distance_matrix(points)
    W_time = dist_to_time(W_dist, speed)

    # Indices express/normaux
    idx_express = [i for i, p in enumerate(points) if (i == 0 or p.est_express)]
    idx_normals = [i for i, p in enumerate(points) if (i != 0 and not p.est_express)]

    # Sous-matrice express (reindexée 0..m-1)
    map_ex = {orig: k for k, orig in enumerate(idx_express)}
    W_ex = [[0.0] * len(idx_express) for _ in range(len(idx_express))]
    for i, oi in enumerate(idx_express):
        for j, oj in enumerate(idx_express):
            W_ex[i][j] = W_time[oi][oj]

    # Christofides sur express
    edges_ex, _, _, _ = christophides(W_ex, start=0)
    if not edges_ex:
        # Cas trivial : seulement dépôt
        tour_express_global = [0, 0]
    else:
        # Les arêtes sont déjà ordonnées en cycle
        tour_local = [u for (u, v, _) in edges_ex] + [edges_ex[-1][1]]
        tour_express_global = [idx_express[i] for i in tour_local]

        # force start=0 au début et fermer le cycle
        if tour_express_global[0] != 0:
            s = tour_express_global.index(0)
            tour_express_global = tour_express_global[s:] + tour_express_global[:s]
        if tour_express_global[-1] != 0:
            tour_express_global.append(0)

    # Poids w_i
    weights = [0.0] * n
    for i, p in enumerate(points):
        if i == 0:
            weights[i] = 0.0
        else:
            weights[i] = (w_express if p.est_express else w_normal)

    # Insertion gloutonne minimisant I (avec contrainte durée)
    tour_final = insertion_gloutonne_par_I(W_time, tour_express_global, idx_normals, weights, alpha, beta, max_hours)

    # Score final
    I_final, alpha_term, beta_term, t_arr = compute_I(W_time, tour_final, weights, alpha, beta)
    return tour_final, I_final, alpha_term, beta_term, t_arr


# ----------------------------
# CLI / Démo
# ----------------------------
def make_demo_points(n_total: int, ratio_express: float, seed: int = 42) -> List[Point]:
    """
    Génère un jeu de points aléatoires (dépôt = (0,0)), 'ratio_express' dans (0..1).
    """
    random.seed(seed)
    pts: List[Point] = [Point(0.0, 0.0, est_express=False)]  # dépôt index 0
    for _ in range(n_total - 1):
        x = random.uniform(0, 10)
        y = random.uniform(0, 10)
        est_ex = (random.random() < ratio_express)
        pts.append(Point(x, y, est_express=est_ex))
    return pts


def main():
    alpha = 1.0
    beta = 1.0
    w_express = 3.0
    w_normal = 1.0
    max_hours = 8.0
    speed = 30
    random_n = 300
    ratio_express = 0.5
    plot = True

    # Crée un petit set de démo si pas encore de lecteur de fichier
    points = make_demo_points(random_n, ratio_express, seed=42)

    # Exécution
    tour, I_final, alpha_term, beta_term, t_arr = tsp_mixte_backbone_I(
        points=points,
        alpha=alpha,
        beta=beta,
        w_express=w_express,
        w_normal=w_normal,
        max_hours=max_hours,
        speed=speed
    )

    # Affichage résultats
    print("\n--- Résultats ---")
    print("Tour (indices):", tour)
    print("Heures d'arrivée (par position dans le tour):")
    print([round(x, 3) for x in t_arr])
    print(f"I final = {I_final:.3f}  (alpha_term={alpha_term:.3f}, beta_term={beta_term:.3f})")
    print(f"Durée totale = {t_arr[-1]:.3f} h  (contrainte max = {max_hours} h)")

    # Détails par noeud (utile pour rapport)
    print("\nDétails des noeuds visités (index, type, t_arr):")
    for pos, node in enumerate(tour):
        typ = "DEPOT" if node == 0 else ("EXPRESS" if points[node].est_express else "NORMAL")
        print(f"  pos {pos:02d}: node {node:02d}  {typ:7s}  t={t_arr[pos]:.3f} h")

    if plot:
        plot_tour(points, tour)


if __name__ == "__main__":
    main()