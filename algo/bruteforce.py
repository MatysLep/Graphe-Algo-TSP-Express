"""
algo/bruteforce.py — Brute-force adapté au projet "livreur"
- N'utilise BF que si n_points <= 10.
- Optimise I = alpha*T_total + beta*sum(w_i * t_i) sous contrainte "express before normal".
- Fournit affichage : matrice de distances ou graphe matplotlib.
"""

from itertools import permutations
import math, random
from typing import List, Tuple, Optional, Dict, Any

# ---------- PARAMÈTRES PAR DÉFAUT (modifiable) ----------
DEFAULT_MAX_N_FOR_BF = 10  # si >10, on ne lance pas BF (évite explosion combinatoire)

# ---------- CLASSE POINT (simple fallback si tu utilises point.py ailleurs) ----------
class Point:
    def __init__(self, x: float, y: float, est_express: bool = False, name: str = ""):
        self.x = x
        self.y = y
        self.est_express = est_express
        self.name = name or f"P({x:.1f},{y:.1f})"
    def __repr__(self):
        return f"{self.name}{'*' if self.est_express else ''}"

# ---------- GÉNÉRATION / DISTANCES ----------
def make_demo_points(n: int, ratio_express: float = 0.4, seed: Optional[int] = None) -> List[Point]:
    if seed is not None:
        random.seed(seed)
    pts = [Point(0.0, 0.0, est_express=False, name="Depot")]
    for i in range(1, n):
        x = random.uniform(-50, 50)
        y = random.uniform(-50, 50)
        is_ex = random.random() < ratio_express
        pts.append(Point(x, y, est_express=is_ex, name=f"P{i}"))
    return pts

def euclid_distance(a: Point, b: Point) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)

def build_distance_matrix(points: List[Point]) -> List[List[float]]:
    n = len(points)
    W = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            d = euclid_distance(points[i], points[j])
            W[i][j] = W[j][i] = d
    return W

# ---------- CONTRAINTE : EXPRESS AVANT NORMAL ----------
def permutation_respects_express_first(perm: Tuple[int, ...], points: List[Point]) -> bool:
    seen_normal = False
    for node in perm:
        if points[node].est_express:
            if seen_normal:
                return False
        else:
            seen_normal = True
    return True

# ---------- OBJECTIF ----------
def evaluate_objective(order: List[int], points: List[Point], W: List[List[float]],
                       speed: float, alpha: float, beta: float, max_hours: float,
                       w_express: float, w_normal: float, hard_constraint: bool = False) -> Tuple[float, float, float, float, List[float]]:
    """
    Calcule I, alpha_term, beta_term, T_total, arrival.
    Si hard_constraint=True et T > max_hours, retourne I = +inf (solution rejetée).
    """
    # poids
    w = [0.0] + [ (w_express if p.est_express else w_normal) for p in points[1:] ]

    # temps cumulés
    T = 0.0
    arrival = [0.0] * len(order)
    for k in range(1, len(order)):
        a, b = order[k-1], order[k]
        T += W[a][b] / speed
        arrival[k] = T

    if hard_constraint and (max_hours is not None) and (T > max_hours):
        return float("inf"), alpha * T, 0.0, T, arrival

    alpha_term = alpha * T
    beta_raw = sum(w[order[k]] * arrival[k] for k in range(1, len(order)))
    beta_term = beta * beta_raw
    I = alpha_term + beta_term

    # si on garde la pénalité douce (par défaut hard_constraint=False), on peut ajouter :
    if not hard_constraint and (max_hours is not None) and (T > max_hours):
        over = T - max_hours
        I += 1000.0 * over * over

    return I, alpha_term, beta_term, T, arrival

# ---------- BRUTE FORCE ----------
def brute_force_objective(points: List[Point], alpha: float = 1.0, beta: float = 1.0,
                          speed: float = 30.0, max_hours: float = 8.0,
                          w_express: float = 2.0, w_normal: float = 1.0,
                          hard_constraint: bool = False) -> Tuple[Optional[Dict[str, Any]], List[List[float]]]:
    """
    Teste toutes les permutations (si n <= DEFAULT_MAX_N_FOR_BF).
    Retourne (best_dict_or_None, W).
    best_dict contient: order, I, alpha_term, beta_term, T, arrival.
    """
    n = len(points)
    W = build_distance_matrix(points)

    if n > DEFAULT_MAX_N_FOR_BF:
        print(f"[bruteforce] instance trop grande pour BF (n={n} > {DEFAULT_MAX_N_FOR_BF}). Skip BF.")
        return None, W

    nodes = list(range(1, n))
    best_I = float("inf")
    best = None

    for perm in permutations(nodes):
        if not permutation_respects_express_first(perm, points):
            continue
        order = [0] + list(perm) + [0]
        I, a_term, b_term, T, arrival = evaluate_objective(order, points, W, speed, alpha, beta, max_hours, w_express, w_normal, hard_constraint)
        if I < best_I:
            best_I = I
            best = {"order": order, "I": I, "alpha_term": a_term, "beta_term": b_term, "T": T, "arrival": arrival}

    return best, W

# ---------- AFFICHAGE UTILITAIRE ----------
def print_distance_matrix(W: List[List[float]]):
    n = len(W)
    print("\nMatrice de distances (W) :")
    for i in range(n):
        row = ", ".join(f"{W[i][j]:6.2f}" for j in range(n))
        print(f"[{row}]")

# ---------- PLOTTING (matplotlib) ----------
def plot_tour(points: List[Point], W: List[List[float]], order: List[int], show_labels: bool = True, figsize=(8,8)):
    """
    Trace la tournée avec matplotlib :
    - points express en rouge, normal en blue, dépôt en vert.
    - flèches suivant l'ordre.
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib import collections as mc
    except Exception as e:
        print("plot_tour : matplotlib non disponible:", e)
        return

    xs = [p.x for p in points]
    ys = [p.y for p in points]

    fig, ax = plt.subplots(figsize=figsize)
    # points
    for i, p in enumerate(points):
        if i == 0:
            ax.scatter(p.x, p.y, marker="s", s=120, label="Depot", zorder=5, edgecolors='k')
        else:
            c = "red" if p.est_express else "blue"
            ax.scatter(p.x, p.y, color=c, s=60, zorder=4)
        if show_labels:
            ax.text(p.x + 0.5, p.y + 0.5, f"{i}", fontsize=9)

    # edges
    segs = []
    for a,b in zip(order, order[1:]):
        segs.append([(points[a].x, points[a].y), (points[b].x, points[b].y)])
    lc = mc.LineCollection(segs, linewidths=1.0, linestyles='solid', alpha=0.7)
    ax.add_collection(lc)

    # flèches : un arrow à mi-seg pour chaque arête
    for a,b in zip(order, order[1:]):
        x0, y0 = points[a].x, points[a].y
        x1, y1 = points[b].x, points[b].y
        dx, dy = x1 - x0, y1 - y0
        ax.arrow(x0, y0, dx*0.9, dy*0.9, head_width=1.0, length_includes_head=True, color='gray', alpha=0.7)

    ax.set_aspect('equal', adjustable='box')
    ax.set_title("Tournée brute-force")
    plt.grid(True)
    plt.show()

# ---------- UTILITAIRE D'EXECUTION SIMPLE ----------
def run_bruteforce_if_small(points: List[Point], alpha: float = 1.0, beta: float = 1.0,
                            speed: float = 30.0, max_hours: float = 8.0,
                            w_express: float = 2.0, w_normal: float = 1.0,
                            hard_constraint: bool = False, plot: bool = False) -> Optional[Dict[str, Any]]:
    """
    Lance brute_force_objective si len(points) <= DEFAULT_MAX_N_FOR_BF.
    Retourne le best dict (ou None si skip).
    Si plot=True et best trouvé : affiche matrice ET graphe.
    """
    best, W = brute_force_objective(points, alpha, beta, speed, max_hours, w_express, w_normal, hard_constraint)
    if best is None:
        print("[run_bruteforce_if_small] Aucun résultat (BF non lancé ou pas de solution faisable).")
        return None

    print("\n--- Résultat brute force (complet) ---")
    print(f"I = {best['I']:.3f}  (alpha_term={best['alpha_term']:.3f}, beta_term={best['beta_term']:.3f})")
    print(f"T_total = {best['T']:.3f} h  (max = {max_hours})")
    tour_str = " -> ".join(f"{i}({'D' if i==0 else ('E' if points[i].est_express else 'N')})" for i in best["order"])
    print("Ordre :", best["order"])
    print("Tournée :", tour_str)

    if plot:
        print_distance_matrix(W)
        try:
            plot_tour(points, W, best["order"])
        except Exception as e:
            print("Erreur lors du plot :", e)

    return best

# ---------- si exécuté en script (test) ----------
if __name__ == "__main__":
    pts = make_demo_points(8, ratio_express=0.4, seed=123)
    run_bruteforce_if_small(pts, alpha=1.0, beta=30.0, speed=30.0, max_hours=8.0,
                            w_express=2.0, w_normal=1.0, hard_constraint=False, plot=True)
