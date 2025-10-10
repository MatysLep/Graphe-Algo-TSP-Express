import random
from typing import Iterable, List, Sequence, Optional, Tuple
import math
import matplotlib.pyplot as plt
import numpy as np
from point import Point

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
# Visualisation
# ----------------------------
def plot_tour(points: List[Point], tour: List[int], title: str) -> None:
    xs = [points[i].x for i in range(len(points))]
    ys = [points[i].y for i in range(len(points))]

    depot_label_done = False
    express_label_done = False
    normal_label_done = False

    # Scatter
    for i, p in enumerate(points):
        if i == 0 and not depot_label_done:
            plt.scatter([p.x], [p.y], s=120, marker="s", label="Dépôt (0)")
            depot_label_done = True
        elif p.est_express:
            label = "Express" if not express_label_done else None
            plt.scatter([p.x], [p.y], s=60, marker="o", label=label)
            express_label_done = True
        else:
            label = "Normal" if not normal_label_done else None
            plt.scatter([p.x], [p.y], s=60, marker="^", label=label)
            normal_label_done = True

        plt.text(p.x, p.y, f" {i}", fontsize=9)


    # Edges
    for i in range(len(tour) - 1):
        a, b = tour[i], tour[i + 1]
        plt.plot([points[a].x, points[b].x], [points[a].y, points[b].y])

    plt.title(title)
    plt.legend()
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

def draw_complete_graph(points: Sequence[Point],
                        *,
                        annotate: bool = False,
                        labels: Optional[Iterable[str]] = None,
                        point_size: int = 40,
                        line_width: float = 1.0,
                        line_alpha: float = 1,
                        figsize: Tuple[int, int] = (6, 6),
                        equal_axis: bool = True,
                        axis_off: bool = False,
                        save_path: Optional[str] = None,
                        show: bool = True) -> plt.Axes:
    """
    Trace un graphe complet reliant tous les points fournis.

    Parameters
    ----------
    points : Sequence[Point]
        Liste/tuple de coordonnées (x, y).
    annotate : bool, optional
        Si True, ajoute une étiquette à chaque point (labels si fournis,
        sinon l'indice). Default: False.
    labels : Optional[Iterable[str]], optional
        Étiquettes à afficher pour chaque point (même longueur que `points`).
    point_size : int, optional
        Taille des marqueurs. Default: 40.
    line_width : float, optional
        Épaisseur des arêtes. Default: 1.0.
    line_alpha : float, optional
        Transparence des arêtes (utile quand il y en a beaucoup). Default: 1.
    figsize : Tuple[int, int], optional
        Taille de la figure en pouces. Default: (6, 6).
    equal_axis : bool, optional
        Si True, impose le même ratio d’échelle pour x et y. Default: True.
    axis_off : bool, optional
        Si True, cache les axes. Default: False.
    save_path : Optional[str], optional
        Chemin de sauvegarde (PNG, PDF, etc.). Si None, ne sauvegarde pas.
    show : bool, optional
        Si True, affiche la figure. Default: True.

    Returns
    -------
    plt.Axes
        Axes matplotlib contenant le tracé.

    Notes
    -----
    - Complexité en O(n^2) arêtes : attention pour n élevé.
    """
    if len(points) == 0:
        raise ValueError("La liste de points est vide.")
    if labels is not None:
        labels = list(labels)
        if len(labels) != len(points):
            raise ValueError("`labels` doit avoir la même longueur que `points`.")

    fig, ax = plt.subplots(figsize=figsize)

    # Tracer toutes les arêtes du graphe complet
    for p1, p2 in compute_complete_edges(points):
        ax.plot([p1.x, p2.x], [p1.y, p2.y], linewidth=line_width, alpha=line_alpha)
        dist = distance(p1, p2)
        mid_x, mid_y = (p1.x + p2.x) / 2, (p1.y + p2.y) / 2
        ax.annotate(f"{dist:.2f}", (mid_x, mid_y), ha="center", va="center", fontsize=8, color="blue")

    # Tracer les points
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    ax.scatter(xs, ys, s=point_size)

    # Options d’axes
    if equal_axis:
        ax.set_aspect('equal', adjustable='box')
    if axis_off:
        ax.axis('off')

    # Annotations
    if annotate:
        if labels is None:
            for i, p in enumerate(points):
                ax.annotate(str(i), (p.x, p.y), xytext=(5, 5), textcoords='offset points')
        else:
            for lab, p in zip(labels, points):
                ax.annotate(str(lab), (p.x, p.y), xytext=(5, 5), textcoords='offset points')

    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    if show:
        plt.show()

    return ax

def compute_complete_edges(points: Sequence[Point]) -> List[Tuple[Point, Point]]:
    """
    Génère toutes les arêtes du graphe complet pour une liste de points.

    Parameters
    ----------
    points : Sequence[Point]
        Liste/tuple de points (x, y).

    Returns
    -------
    List[Tuple[Point, Point]]
        Liste des paires (p_i, p_j) avec i < j.
    """
    edges: List[Tuple[Point, Point]] = []
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((points[i], points[j]))
    return edges

def compute_adjacence_matrix(points: Sequence[Point]) -> List[List[float]]:
    """
    Construit la matrice d'adjacence pondérée d'un graphe complet
    basé sur une liste de points.

    Parameters
    ----------
    points : Sequence[Point]
        Liste de coordonnées (x, y).

    Returns
    -------
    List[List[float]]
        Matrice d'adjacence (n x n) où chaque élément [i][j] représente
        le poids (distance euclidienne) entre le point i et le point j.
        La diagonale est nulle.
    """
    n = len(points)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            dist = round(math.hypot(points[j].x - points[i].x, points[j].y - points[i].y), 2)
            matrix[i][j] = dist
            matrix[j][i] = dist
    return matrix

def show_adjacence_matrix(m: List[List[float]]):
    for i, row in enumerate(m):
        print(f"{i} {row}")

# ----------------------------
# Démo
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

# ----------------------------
# Complexité
# ----------------------------
def plot_complexity_comparison(complexities: list, labels: list, n_max: int = 15):
    """
    Affiche la croissance des complexités asymptotiques données en fonction de n.

    Paramètres
    ----------
    complexities : list
        Liste de fonctions lambda prenant n en entrée (ex: [lambda n: n**2, lambda n: n**2*math.log(n)]).
    labels : list
        Noms correspondants aux complexités (ex: ["O(n²)", "O(n² log n)", "O(n!)"]).
    n_max : int
        Taille maximale de n pour l'affichage (par défaut : 15, car n! devient vite énorme).

    Exemple
    -------
    >>> plot_complexity_comparison(
    ...     [lambda n: n**2, lambda n: n**2*math.log(n), lambda n: math.factorial(n)],
    ...     ["O(n²)", "O(n² log n)", "O(n!)"],
    ...     n_max=10
    ... )
    """
    n_values = np.arange(1, n_max + 1)
    plt.figure(figsize=(10, 6))

    for func, label in zip(complexities, labels):
        y = [func(n) for n in n_values]
        plt.plot(n_values, y, label=label, linewidth=2)

    plt.yscale('log')  # Échelle logarithmique pour visualiser les écarts
    plt.xlabel("Nombre de sommets (n)")
    plt.ylabel("Coût (croissance asymptotique)")
    plt.title("Comparaison des complexités algorithmiques")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    plt.show()
