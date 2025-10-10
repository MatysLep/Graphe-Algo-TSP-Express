"""
bruteforce.py - version minimale
- N_POINTS = 10 (dépôt = 0)
- Contrainte : tous les express doivent être visités avant tous les normaux
- Objectif : minimiser la distance totale (Euclidienne)
- Sorties console : tournée optimale, distances entre arrêts, matrice de distances,
  liste d'arêtes pondérées et coordonnées des points (pour représentation graphique)
"""

from itertools import permutations
import math
import random
from typing import List, Tuple

# ---------- Paramètres (modifie si besoin) ----------
N_POINTS = 10        # total points (inclut dépôt à l'indice 0). Doit rester < 11.
RATIO_EXPRESS = 0.4  # fraction de clients express (hors dépôt)
SEED = 123           # pour reproductibilité

# ---------- Classe simple Point ----------
class Point:
    def __init__(self, x: float, y: float, est_express: bool = False, name: str = ""):
        self.x = x
        self.y = y
        self.est_express = est_express
        self.name = name or f"P({x:.1f},{y:.1f})"
    def __repr__(self):
        return f"{self.name}{'*' if self.est_express else ''}"

# ---------- Génération de points ----------
def make_demo_points(n: int, ratio_express: float = 0.4, seed: int | None = None) -> List[Point]:
    if seed is not None:
        random.seed(seed)
    pts = []
    # dépôt au centre
    pts.append(Point(0.0, 0.0, est_express=False, name="Depot"))
    for i in range(1, n):
        x = random.uniform(-50, 50)
        y = random.uniform(-50, 50)
        is_ex = random.random() < ratio_express
        pts.append(Point(x, y, est_express=is_ex, name=f"P{i}"))
    return pts

# ---------- Distances ----------
def euclid_distance(a: Point, b: Point) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)

def build_distance_matrix(points: List[Point]) -> List[List[float]]:
    n = len(points)
    W = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                W[i][j] = euclid_distance(points[i], points[j])
    return W

# ---------- Brute-force (simplifié) ----------
def permutation_respects_express_first(perm: Tuple[int, ...], points: List[Point]) -> bool:
    seen_normal = False
    for node in perm:
        if points[node].est_express:
            if seen_normal:
                return False
        else:
            seen_normal = True
    return True

def brute_force_min_distance(points: List[Point]) -> Tuple[float, List[int], List[float]]:
    n = len(points)
    if n < 2:
        raise ValueError("Au moins dépôt + 1 point requis.")
    if n >= 11:
        raise ValueError("N trop grand pour brute-force (>=11).")

    W = build_distance_matrix(points)
    nodes = list(range(1, n))
    best_dist = float("inf")
    best_tour = []
    best_leg_distances = []

    for perm in permutations(nodes):
        # respect express-first constraint
        if not permutation_respects_express_first(perm, points):
            continue

        tour = [0] + list(perm) + [0]
        leg_distances = []
        total = 0.0
        for k in range(1, len(tour)):
            a, b = tour[k-1], tour[k]
            d = W[a][b]
            leg_distances.append(d)
            total += d

        if total < best_dist:
            best_dist = total
            best_tour = tour
            best_leg_distances = leg_distances

    return best_dist, best_tour, best_leg_distances

# ---------- Affichage utile pour le rapport ----------
def print_distance_matrix(W):
    n = len(W)
    print("\nMatrice de distances (W_dist) :")
    for i in range(n):
        row = ", ".join(f"{W[i][j]:6.2f}" for j in range(n))
        print(f"[{row}]")

def print_graph_representation(points, W):
    n = len(points)
    print("\nCoordonnées des nœuds :")
    for i, p in enumerate(points):
        typ = "EXPRESS" if p.est_express else "NORMAL" if i!=0 else "DEPOT"
        print(f"  {i}: {p.name}  ({p.x:.2f}, {p.y:.2f})  {typ}")

    print("\nListe d'arêtes (i, j, distance) pour i < j :")
    for i in range(n):
        for j in range(i+1, n):
            print(f"  ({i}, {j}, {W[i][j]:.3f})")

# ---------- MAIN ----------
def main():
    n = N_POINTS
    if n >= 11:
        print("N_POINTS must be < 11 for brute-force. Change N_POINTS.")
        return

    points = make_demo_points(n, ratio_express=RATIO_EXPRESS, seed=SEED)
    W = build_distance_matrix(points)

    print(f"Graph généré avec N={n} points (0 = dépôt).")
    for i,p in enumerate(points):
        tag = "DEPOT" if i==0 else ("EXPRESS" if p.est_express else "NORMAL")
        print(f"  {i:02d} : {p.name}  coords=({p.x:.2f},{p.y:.2f})  {tag}")

    best_dist, best_tour, best_leg_distances = brute_force_min_distance(points)

    if not best_tour:
        print("Aucune tournée valide trouvée (contrainte express-first trop restrictive).")
        return

    print("\n--- Résultat bruteforce (min distance) ---")
    tour_str = " -> ".join(f"{i}({'D' if i==0 else ('E' if points[i].est_express else 'N')})" for i in best_tour)
    print("Tournée optimale (indices):", best_tour)
    print("Tournée (format index(type)):", tour_str)
    print("Distances entre arrêts :", [round(d, 4) for d in best_leg_distances])
    print(f"Distance totale = {best_dist:.4f}")

    # matrice et représentation pour rapport
    print_distance_matrix(W)
    print_graph_representation(points, W)

if __name__ == "__main__":
    main()
