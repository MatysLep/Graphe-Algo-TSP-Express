from typing import List, Optional, Sequence, Tuple
import matplotlib.pyplot as plt
import math

def prim_mst_complete(
    W: Sequence[Sequence[float]],
    start: int = 0
) -> Tuple[List[Tuple[int, int, float]], float, List[Optional[int]], List[float]]:
    """
    Algorithme de Prim pour graphe complet (matrice d'adjacence).

    Paramètres
    ----------
    W : Sequence[Sequence[float]]
        Matrice d'adjacence (symétrique, diagonale nulle, poids finis).
    start : int
        Sommet de départ (par défaut 0).

    Renvoie
    -------
    edges : List[Tuple[int,int,float]]
        Arêtes de l'ASM sous forme (u, v, w) avec u = parent[v].
    total_weight : float
        Somme des poids de l'ASM.
    parent : List[Optional[int]]
        parent[v] = u, None pour la racine.
    key : List[float]
        Clés finales (meilleur coût pour connecter chaque sommet).
    """
    n = len(W)

    in_mst = [False] * n
    parent: List[Optional[int]] = [None] * n
    key: List[float] = [float("inf")] * n
    key[start] = 0.0

    for _ in range(n):
        u = _argmin_not_in_mst(key, in_mst)
        in_mst[u] = True

        Wu = W[u]
        for v in range(n):
            if not in_mst[v] and Wu[v] < key[v]:
                key[v] = Wu[v]
                parent[v] = u

    edges = _edges_from_parent(parent, W)
    total = _total_weight(edges)
    return edges, total, parent, key

# ------------------------------ Helpers ------------------------------ #

def _argmin_not_in_mst(key: Sequence[float], in_mst: Sequence[bool]) -> int:
    """Retourne l'indice du sommet non sélectionné avec clé minimale."""
    best = float("inf")
    idx = -1
    for i, (k, used) in enumerate(zip(key, in_mst)):
        if not used and k < best:
            best = k
            idx = i
    if idx < 0:
        # Dans un graphe complet, cela ne doit pas arriver
        raise RuntimeError("Sélection de sommet impossible (état invalide).")
    return idx

def _edges_from_parent(parent: Sequence[Optional[int]], W: Sequence[Sequence[float]]) -> List[Tuple[int,int,float]]:
    """Construit la liste (u, v, w) à partir du tableau parent."""
    edges: List[Tuple[int,int,float]] = []
    for v, u in enumerate(parent):
        if u is not None:
            edges.append((u, v, W[u][v]))
    return edges

def _total_weight(edges: Sequence[Tuple[int,int,float]]) -> float:
    """Somme des poids des arêtes."""
    return float(sum(w for _, _, w in edges))


# ------------------------------ Plotting Function ------------------------------ #

def plot_prim_graph(points: List[Tuple[float, float]], edges: List[Tuple[int, int, float]]) -> None:
    """
    Affiche le graphe complet et son arbre couvrant minimal (Prim) à partir des coordonnées.

    points : liste des coordonnées (x, y) des sommets
    edges : liste des arêtes du MST [(u, v, w), ...]
    """
    n = len(points)
    # Tracer toutes les arêtes du graphe complet (en gris clair)
    for i in range(n):
        xi, yi = points[i]
        for j in range(i+1, n):
            xj, yj = points[j]
            plt.plot([xi, xj], [yi, yj], color='lightgray', linewidth=1, zorder=1)
    # Tracer les arêtes de l'arbre couvrant minimal (en rouge, plus épais)
    for u, v, _ in edges:
        x1, y1 = points[u]
        x2, y2 = points[v]
        plt.plot([x1, x2], [y1, y2], color='red', linewidth=2.5, zorder=3)
    # Tracer les sommets (points bleus)
    xs, ys = zip(*points)
    plt.scatter(xs, ys, color='blue', s=50, zorder=4)
    # Annoter les sommets avec leur indice
    for idx, (x, y) in enumerate(points):
        plt.text(x, y, str(idx), fontsize=10, color='black', ha='right', va='bottom', zorder=5)
    plt.title("Arbre couvrant minimal (Algorithme de Prim)")
    plt.axis('equal')
    plt.axis('off')
    plt.tight_layout()
    plt.show()