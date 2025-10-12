# aco.py — ACO adapté au projet "livreur" (Point, express/normal, alpha/beta, speed, max_hours)
from __future__ import annotations
import math, random
from typing import List, Tuple, Sequence, Optional, Dict, Any
try:
    # compatibilité avec ton projet
    from point import Point
except Exception:
    # fallback minimal si besoin
    class Point:
        def __init__(self, x: float, y: float, est_express: bool=False):
            self.x, self.y, self.est_express = x, y, est_express

# ----------------------------
# Utilitaires
# ----------------------------
def _euclidean(p1: Point, p2: Point) -> float:
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def distance_matrix(points: Sequence[Point]) -> List[List[float]]:
    n = len(points)
    D = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            d = _euclidean(points[i], points[j])
            D[i][j] = D[j][i] = d
    return D

def compute_arrival_times(order: Sequence[int], D: Sequence[Sequence[float]], speed: float) -> List[float]:
    """Temps d'arrivée cumulatifs (h) en partant de 0 (le dépôt)."""
    t = 0.0
    arr = [0.0]*len(order)
    for k in range(1, len(order)):
        i, j = order[k-1], order[k]
        t += D[i][j] / speed
        arr[k] = t
    return arr

def make_weights(points: Sequence[Point], w_express: Optional[float]=None, w_normal: Optional[float]=None) -> List[float]:
    """Poids pour beta * sum w_i * t_i (express > normal).
       Par défaut, balance les classes même si n_e != n_n.
    """
    n_e = sum(1 for p in points if p.est_express)
    n_n = len(points) - 1 - n_e  # dépôt = 0
    if w_express is None or w_normal is None:
        if n_e <= 0:
            w_express = 1.0
            w_normal = 1.0
        else:
            w_normal = 1.0
            w_express = max(2.0, (n_n / max(1, n_e)) * w_normal)
    w = []
    for idx, p in enumerate(points):
        if idx == 0:
            w.append(0.0)  # dépôt
        else:
            w.append(w_express if p.est_express else w_normal)
    return w

def evaluate_objective(order: Sequence[int],
                       points: Sequence[Point],
                       D: Sequence[Sequence[float]],
                       speed: float,
                       alpha: float,
                       beta: float,
                       max_hours: float,
                       penalty_unserved: float = 0.0,
                       weights: Optional[Sequence[float]] = None) -> Dict[str, Any]:
    """I = alpha*T_total + beta*sum_i w_i*t_i + pénalités de dépassement."""
    n = len(points)
    if weights is None:
        weights = make_weights(points)

    # durée totale (aller + retour dépôt)
    T = 0.0
    for a, b in zip(order, order[1:]):
        T += D[a][b] / speed
    T += D[order[-1]][order[0]] / speed

    # temps d'arrivée
    arrival = compute_arrival_times(order, D, speed)

    # priorité (express pondérés)
    tardiness = 0.0
    for pos, i in enumerate(order):
        if i == 0:
            continue
        tardiness += weights[i] * arrival[pos]

    I = alpha * T + beta * tardiness

    # pénalité si T dépasse max_hours (quadratique douce)
    if max_hours is not None and max_hours > 0 and T > max_hours:
        over = T - max_hours
        I += 1000.0 * over * over

    return {"objective": I, "T_total": T, "arrival": arrival, "order": list(order)}

# ----------------------------
# ACO (colonie de fourmis)
# ----------------------------
def aco_solve(points: Sequence[Point],
              alpha: float = 1.0,
              beta: float = 3.0,
              speed: float = 30.0,
              max_hours: float = 8.0,
              ants: Optional[int] = None,
              iterations: int = 200,
              pheromone_init: float = 1.0,
              rho: float = 0.5,
              Q: float = 1.0,
              seed: int = 0,
              w_express: Optional[float]=None,
              w_normal: Optional[float]=None) -> Dict[str, Any]:
    """
    Minimise I = alpha*T_total + beta*sum w_i*t_i.
    Hypothèses: distances symétriques, dépôt = 0.
    """
    rng = random.Random(seed)
    n = len(points)
    if n < 2:
        raise ValueError("Besoin d'au moins dépôt + 1 client")

    D = distance_matrix(points)
    tau = [[pheromone_init]*n for _ in range(n)]  # phéromones
    eta = [[0.0]*n for _ in range(n)]             # heuristique (1/d)
    for i in range(n):
        for j in range(n):
            if i != j:
                eta[i][j] = 1.0 / (D[i][j] + 1e-12)
    ants = ants or n
    weights = make_weights(points, w_express=w_express, w_normal=w_normal)

    def construct_tour() -> List[int]:
        start = 0  # départ forcé au dépôt
        unvisited = list(range(1, n))
        tour = [start]
        cur = start
        while unvisited:
            numerators = []
            for j in unvisited:
                numerators.append((tau[cur][j] ** 1.0) * (eta[cur][j] ** beta))
            s = sum(numerators)
            if s == 0.0:
                nxt = rng.choice(unvisited)
            else:
                probs = [x / s for x in numerators]
                r = rng.random()
                acc = 0.0
                nxt = unvisited[-1]
                for j, p in zip(unvisited, probs):
                    acc += p
                    if r <= acc:
                        nxt = j
                        break
            tour.append(nxt)
            unvisited.remove(nxt)
            cur = nxt
        return tour

    best = None
    for it in range(iterations):
        # évaporation
        for i in range(n):
            for j in range(n):
                tau[i][j] *= (1.0 - rho)

        # génération et sélection du meilleur de l'itération
        batch_best = None
        for _ in range(ants):
            tour = construct_tour()
            metrics = evaluate_objective(tour, points, D, speed, alpha, beta, max_hours, weights=weights)
            if (batch_best is None) or (metrics["objective"] < batch_best["objective"]):
                batch_best = metrics

        # meilleur global
        if (best is None) or (batch_best["objective"] < best["objective"]):
            best = batch_best

        # renforcement sur le meilleur global
        deposit = Q / max(1e-9, best["objective"])
        order = best["order"]
        for a, b in zip(order, order[1:]):
            tau[a][b] += deposit
            tau[b][a] += deposit
        tau[order[-1]][order[0]] += deposit
        tau[order[0]][order[-1]] += deposit

    # métriques finales
    total_distance = 0.0
    for a, b in zip(best["order"], best["order"][1:]):
        total_distance += D[a][b]
    total_distance += D[best["order"][-1]][best["order"][0]]

    return {
        "order": best["order"],
        "objective": best["objective"],
        "T_total": best["T_total"],
        "total_distance": total_distance,
        "arrival": best["arrival"],
        "params": {
            "alpha": alpha, "beta": beta, "speed": speed, "max_hours": max_hours,
            "ants": ants, "iterations": iterations, "rho": rho, "Q": Q, "seed": seed,
            "w_express": w_express, "w_normal": w_normal
        }
    }

# ----------------------------
# Helper affichage (optionnel)
# ----------------------------
def format_solution(sol: Dict[str, Any], points: Sequence[Point]) -> str:
    lines = []
    lines.append(f"Objectif I = {sol['objective']:.3f}")
    lines.append(f"Temps total T = {sol['T_total']:.3f} h ; distance = {sol['total_distance']:.3f} unités")
    lines.append("Ordre de visite (indices): " + " -> ".join(map(str, sol["order"])) + " -> 0")
    visited_express = sum(1 for i in sol["order"] if i != 0 and points[i].est_express)
    visited_normal = sum(1 for i in sol["order"] if i != 0 and not points[i].est_express)
    lines.append(f"Visités: express={visited_express}, normal={visited_normal}")
    return "\n".join(lines)
