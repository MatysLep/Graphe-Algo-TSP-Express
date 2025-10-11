from utils import *
from .christophides import *


# ----------------------------
# TSP PONDÉRÉ AVEC BACKBONE (CHRISTOFIDES EXPRESS + NORMAL)
# ----------------------------
def tsp_pondere_backbone(points: List[Point], alpha: float, beta: float, w_express: float, w_normal: float, max_hours: float, speed: Optional[float] = None) -> Tuple[List[int], float, float, float, List[float]]:
    """
    Résolution du TSP pondéré en deux phases :
    1) Christofides sur points express (backbone).
    2) Ajout dernier express aux normaux.
    3) Christofides sur normaux + dépôt.
    4) Calcul score final I = alpha * durée + beta * somme pondérée priorités.
    Retourne : (tour_final, I_final, alpha_term, beta_term, arrival_times)
    """
    print("\n=== DÉBUT TSP PONDÉRÉ ===")

    depot_idx = 0
    n = len(points)

    # Matrices distance et temps
    W_dist = build_distance_matrix(points)
    W_time = dist_to_time(W_dist, speed)

    # Séparation points express et normaux (hors dépôt)
    idx_express = [i for i, p in enumerate(points) if p.est_express and i != depot_idx]
    idx_normals = [i for i, p in enumerate(points) if not p.est_express and i != depot_idx]

    print(f"Dépôt : {points[depot_idx]}")
    print(f"Points express ({len(idx_express)}): {idx_express}")
    print(f"Points normaux ({len(idx_normals)}): {idx_normals}")

    # 1. Phase 1 : Christofides sur points express
    if idx_express:
        subset_express = [depot_idx] + idx_express
        W_express = [[W_time[i][j] for j in subset_express] for i in subset_express]
        edges_ex, _, _, _ = christophides(W_express, start=0)

        tour_local = [u for (u, v, _) in edges_ex] + [edges_ex[-1][1]]
        tour_express = [subset_express[i] for i in tour_local]
        last_express = tour_express[-1]

        print(f"Tour express (indices): {tour_express}")
    else:
        tour_express = []

    # 2. Phase 2 : Christofides sur les points normaux
    subset_normals = [depot_idx] + idx_normals
    W_normal = [[W_time[i][j] for j in subset_normals] for i in subset_normals]
    edges_norm, _, _, _ = christophides(W_normal, start=0)

    tour_local = [u for (u, v, _) in edges_norm] + [edges_norm[-1][1]]
    tour_normals = [subset_normals[i] for i in tour_local]

    # 3. Phase 3 : Combinaison des deux tours
    tour_final = tour_express[:-1] + tour_normals[1:]

    # 4. Calcul du temps d'arrivée cumulé (immédiatement après la création du tour_final)
    arrival_times = [0.0]
    for k in range(1, len(tour_final)):
        a, b = tour_final[k - 1], tour_final[k]
        arrival_times.append(arrival_times[-1] + W_time[a][b])
    duree_totale = arrival_times[-1]

    # 5. Si la durée dépasse max_hours, réduction du tour
    if duree_totale > max_hours:
        print(f"[INFO] Durée totale du tour ({duree_totale:.3f} h) dépasse la limite de {max_hours} h.")
        print("[ACTION] Réduction du tour pour garantir le retour au dépôt avant la fin de la journée...")
        # On retire progressivement les derniers points jusqu’à respecter la contrainte
        while len(tour_final) > 2 and arrival_times[-1] > max_hours:
            removed = tour_final[-2]  # le dernier client avant dépôt
            tour_final.pop(-2)  # supprime ce client
            print(f"  -> Suppression du point {removed} (trop tard).")
            # recalcul du temps de parcours
            arrival_times = [0.0]
            for k in range(1, len(tour_final)):
                a, b = tour_final[k - 1], tour_final[k]
                arrival_times.append(arrival_times[-1] + W_time[a][b])
        print(f"[OK] Nouveau tour valide. Durée = {arrival_times[-1]:.3f} h (≤ {max_hours} h)")
        duree_totale = arrival_times[-1]
        print("[ÉTAPE] Fin de réduction du tour.")

    print(f"Tour final (indices): {tour_final}")
    print("Heures d’arrivée (par position dans le tour):")
    print([round(x, 3) for x in arrival_times])

    # 6. Vérification que tous les points (hors dépôt) sont visités
    points_visited = set(tour_final)
    all_points = set(range(len(points)))
    missing_points = all_points - points_visited
    missing_points.discard(depot_idx)
    if missing_points:
        print(f"[AVERTISSEMENT] Certains points n'ont pas été visités dans le tour final : {sorted(missing_points)}")

    # 7. Calcul score final I avec les valeurs finales (après ajustement)
    somme_priorites = 0.0
    for node in tour_final:
        if node == depot_idx:
            continue
        somme_priorites += w_express if points[node].est_express else w_normal

    I_final = alpha * duree_totale + beta * somme_priorites
    alpha_term = alpha * duree_totale
    beta_term = beta * somme_priorites

    print(f"Score I = alpha * durée_totale + beta * somme_priorites = {I_final:.3f} = {alpha} * {duree_totale:.3f} + {beta} * {somme_priorites:.3f}")
    print("=== FIN TSP PONDÉRÉ ===\n")

    # 8. Retourne les résultats finaux
    return tour_final, I_final, alpha_term, beta_term, arrival_times


def run(points : List[Point], alpha: float, beta: float, w_express: float, w_normal: float, max_hours: float, speed: Optional[float] = None):


    # Exécution
    tour, I_final, alpha_term, beta_term, t_arr = tsp_pondere_backbone(
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

    plot_tour(points, tour, "Tournée finale (Christofides + backbone express)")


if __name__ == "__main__":
    random_n = 300  # Nombre de points de livraison
    ratio_express = 0.4  # Ratio des points de livraison express
    points = make_demo_points(random_n, ratio_express)

    alpha = 1.0  # Influence la durée globale du tour
    beta = 1.0  # Influence la priorité des clients
    max_hours = 8.0  # Durée maximale de la tournée (8 h)
    speed = 30  # Convertit les distances en heures de trajet

    n_express = sum(point.est_express for point in points)
    w_express = ((random_n - n_express - 1) / (
                random_n - (random_n - n_express - 1))) + 1  # Importance des clients prioritaires
    w_normal = 1 / (1 + w_express)  # Importance des clients standards
    run(points, alpha, beta, w_express, w_normal, max_hours, speed)