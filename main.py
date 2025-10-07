# main.py
from __future__ import annotations
from typing import List, Sequence, Tuple, Optional
from dataclasses import dataclass
import argparse
import math
import random
import sys

from point import Point
from christophides import christophides


# ----------------------------
# Utilitaires distances / temps
# ----------------------------
def distance(p1: Point, p2: Point) -> float:
    """Distance euclidienne (units arbitraires)."""
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def build_distance_matrix(points: List[Point]) -> List[List[float]]:
    n = len(points)
    W = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = distance(points[i], points[j])
            W[i][j] = W[j][i] = d
    return W


def dist_to_time(W_dist: Sequence[Sequence[float]], speed: Optional[float]) -> List[List[float]]:
    """
    Convertit distances -> temps si 'speed' (vitesse en unités distance/heure) est fourni.
    Sinon, on considère la matrice déjà exprimée en unités de temps.
    """
    n = len(W_dist)
    if speed is None:
        # On suppose que W_dist est déjà en temps
        return [list(row) for row in W_dist]
    if speed <= 0:
        raise ValueError("La vitesse doit être > 0.")
    return [[(W_dist[i][j] / speed) for j in range(n)] for i in range(n)]


# ----------------------------
# Calcul de l'objectif I
# ----------------------------
def compute_arrival_times(W_time: Sequence[Sequence[float]], tour: List[int]) -> List[float]:
    """
    t[k] = heure d'arrivée au sommet tour[k] (tour[0] est le dépôt avec t=0).
    Hypothèse: pas de temps de service (ajoutez-le ici si besoin).
    """
    t = [0.0] * len(tour)
    for k in range(1, len(tour)):
        a, b = tour[k - 1], tour[k]
        t[k] = t[k - 1] + W_time[a][b]
    return t


def compute_I(W_time: Sequence[Sequence[float]],
              tour: List[int],
              weights: Sequence[float],
              alpha: float,
              beta: float) -> Tuple[float, float, float, List[float]]:
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
def greedy_insert_min_I(W_time: Sequence[Sequence[float]],
                        tour: List[int],
                        weights: Sequence[float],
                        alpha: float,
                        beta: float,
                        node_to_insert: int,
                        max_duration_hours: float = 8.0) -> Optional[List[int]]:
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


def insertion_gloutonne_par_I(W_time: Sequence[Sequence[float]],
                              tour_express_global: List[int],
                              normals_idx: List[int],
                              weights: Sequence[float],
                              alpha: float,
                              beta: float,
                              max_duration_hours: float = 8.0) -> List[int]:
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
def tsp_mixte_backbone_I(points: List[Point],
                         alpha: float,
                         beta: float,
                         w_express: float = 2.0,
                         w_normal: float = 1.0,
                         max_hours: float = 8.0,
                         speed: Optional[float] = None) -> Tuple[List[int], float, float, float, List[float]]:
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
# Visualisation (optionnelle)
# ----------------------------
def plot_tour(points: List[Point], tour: List[int]) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("Matplotlib indisponible, pas de tracé.", file=sys.stderr)
        return

    xs = [points[i].x for i in range(len(points))]
    ys = [points[i].y for i in range(len(points))]

    # Scatter
    for i, p in enumerate(points):
        if i == 0:
            plt.scatter([p.x], [p.y], s=120, marker="s", label="Dépôt (0)")
        elif p.est_express:
            plt.scatter([p.x], [p.y], s=60, marker="o", label="Express" if i == 1 else None)
        else:
            plt.scatter([p.x], [p.y], s=60, marker="^", label="Normal" if i == 1 else None)
        plt.text(p.x, p.y, f" {i}", fontsize=9)

    # Edges
    for i in range(len(tour) - 1):
        a, b = tour[i], tour[i + 1]
        plt.plot([points[a].x, points[b].x], [points[a].y, points[b].y])

    plt.title("Tournée finale (backbone express + insertion gloutonne par I)")
    plt.legend()
    plt.axis("equal")
    plt.tight_layout()
    plt.show()


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
    parser = argparse.ArgumentParser(description="TSP mixte (backbone express + insertion gloutonne par I)")
    parser.add_argument("--alpha", type=float, default=1.0, help="Poids durée totale (alpha)")
    parser.add_argument("--beta", type=float, default=1.0, help="Poids rapidité pondérée (beta)")
    parser.add_argument("--w_express", type=float, default=3.0, help="Poids w_e pour express")
    parser.add_argument("--w_normal", type=float, default=1.0, help="Poids w_n pour normal")
    parser.add_argument("--max_hours", type=float, default=8.0, help="Durée maximale de la tournée (heures)")
    parser.add_argument("--speed", type=float, default=20.0, help="Vitesse (unités distance / heure). Si None, W déjà en temps.")
    parser.add_argument("--random_n", type=int, default=250, help="Nombre total de points (incluant dépôt).")
    parser.add_argument("--ratio_express", type=float, default=0.1, help="Proportion de clients express (0..1).")
    parser.add_argument("--plot", action="store_true", help="Affiche la tournée avec matplotlib.")

    args = parser.parse_args()

    # Crée un petit set de démo si pas encore de lecteur de fichier
    points = make_demo_points(args.random_n, args.ratio_express, seed=42)

    # Exécution
    tour, I_final, alpha_term, beta_term, t_arr = tsp_mixte_backbone_I(
        points=points,
        alpha=args.alpha,
        beta=args.beta,
        w_express=args.w_express,
        w_normal=args.w_normal,
        max_hours=args.max_hours,
        speed=args.speed
    )

    # Affichage résultats
    print("\n--- Résultats ---")
    print("Tour (indices):", tour)
    print("Heures d'arrivée (par position dans le tour):")
    print([round(x, 3) for x in t_arr])
    print(f"I final = {I_final:.3f}  (alpha_term={alpha_term:.3f}, beta_term={beta_term:.3f})")
    print(f"Durée totale = {t_arr[-1]:.3f} h  (contrainte max = {args.max_hours} h)")

    # Détails par noeud (utile pour rapport)
    print("\nDétails des noeuds visités (index, type, t_arr):")
    for pos, node in enumerate(tour):
        typ = "DEPOT" if node == 0 else ("EXPRESS" if points[node].est_express else "NORMAL")
        print(f"  pos {pos:02d}: node {node:02d}  {typ:7s}  t={t_arr[pos]:.3f} h")

    if args.plot:
        plot_tour(points, tour)


if __name__ == "__main__":
    main()