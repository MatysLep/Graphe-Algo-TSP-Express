from typing import Sequence, List, Tuple, Optional, Dict

Edge = Tuple[int, int, float]


def compute_mst_prim(W: Sequence[Sequence[float]], start: int = 0) -> Tuple[List[Edge], float, List[Optional[int]], List[float]]:
    """
    Calcule un arbre couvrant de poids minimal (MST) avec une implémentation dense de Prim en O(n^2).

    :param
    ----------
    W : matrice 2D des poids des arêtes (symétrique, W[i][i] == 0)
    start : indice du sommet de départ pour l'algorithme de Prim

    :return
    --------
    edges : liste de (u, v, w) formant le MST (n-1 arêtes)
    total_w : poids total du MST
    parent : tableau des parents produit par Prim (parent[start] est None)
    key : plus petit poids d'arête pour connecter chaque sommet au MST (key[start] = 0)
    """
    n = len(W)
    in_mst = [False] * n
    key = [float('inf')] * n
    parent: List[Optional[int]] = [None] * n

    key[start] = 0.0

    for _ in range(n):
        # Sélectionne u (non encore dans le MST) avec la plus petite clé key[u]
        u = -1
        min_key = float('inf')
        for i in range(n):
            if not in_mst[i] and key[i] < min_key:
                min_key = key[i]
                u = i
        if u == -1:  # Cas de graphe non connexe (garde-fou)
            break
        in_mst[u] = True
        # Détente (relaxation) des voisins
        Wu = W[u]
        for v in range(n):
            w = Wu[v]
            if not in_mst[v] and w < key[v]:
                key[v] = w
                parent[v] = u

    edges: List[Edge] = []
    total_w = 0.0
    for v in range(n):
        u = parent[v]
        if u is not None:
            w = W[u][v]
            edges.append((u, v, w))
            total_w += w
    return edges, total_w, parent, key


def compute_mst_kruskal(W: Sequence[Sequence[float]]) -> Tuple[List[Edge], float]:
    """
    Calcule un MST avec l'algorithme de Kruskal (adapté aussi aux graphes denses), complexité O(n^2 log n).

    Retourne
    --------
    edges : liste de (u, v, w) formant le MST (n-1 arêtes)
    total_w : poids total du MST
    """
    n = len(W)
    # Construit la liste des arêtes pour la moitié supérieure (i < j)
    edge_list: List[Edge] = []
    for i in range(n):
        Wi = W[i]
        for j in range(i + 1, n):
            edge_list.append((i, j, Wi[j]))

    # Tri par poids croissant
    edge_list.sort(key=lambda e: e[2])

    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        elif rank[ra] > rank[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rank[ra] += 1
        return True

    mst: List[Edge] = []
    total = 0.0
    for u, v, w in edge_list:
        if union(u, v):
            mst.append((u, v, w))
            total += w
            if len(mst) == n - 1:
                break
    return mst, total


def odd_degree_vertices(mst_edges: List[Edge], n: int) -> List[int]:
    """Retourne la liste des sommets de degré impair dans le MST."""
    deg = [0] * n
    for u, v, _ in mst_edges:
        deg[u] += 1
        deg[v] += 1
    return [i for i, d in enumerate(deg) if d % 2 == 1]


def greedy_minimum_perfect_matching(odd_vertices: List[int], W: Sequence[Sequence[float]]) -> List[Edge]:
    """
    Appariement parfait glouton de poids minimal sur l'ensemble des sommets de degré impair.

    Remarque : un MWPM exact nécessiterait Blossom ; on utilise ici une heuristique gloutonne souvent efficace dans Christofides.
    """
    remaining = set(odd_vertices)
    matching: List[Edge] = []
    while remaining:
        u = remaining.pop()
        # trouve le v restant le plus proche de u
        v_best = None
        w_best = float('inf')
        for v in remaining:
            w = W[u][v]
            if w < w_best:
                w_best = w
                v_best = v
        assert v_best is not None  # comme |remaining| était impair avant le pop, il est maintenant pair (≥ 1)
        remaining.remove(v_best)
        matching.append((u, v_best, w_best))
    return matching


def build_multigraph(mst_edges: List[Edge], matching: List[Edge]) -> Dict[int, Dict[int, int]]:
    """
    Construit la matrice d'adjacence d'un multigraphe avec multiplicités.
    Renvoie : adj[u][v] = multiplicité de l'arête (u,v)
    """
    adj: Dict[int, Dict[int, int]] = {}

    def add(u: int, v: int):
        adj.setdefault(u, {}).setdefault(v, 0)
        adj.setdefault(v, {}).setdefault(u, 0)
        adj[u][v] += 1
        adj[v][u] += 1

    for u, v, _ in mst_edges:
        add(u, v)
    for u, v, _ in matching:
        add(u, v)
    return adj


def eulerian_tour(adj: Dict[int, Dict[int, int]], start: int = 0) -> List[int]:
    """Algorithme de Hierholzer pour un tour eulérien dans un multigraphe connexe à degrés tous pairs."""
    # Copie locale des multiplicités (mutable)
    local = {u: dict(vs) for u, vs in adj.items()}
    stack = [start]
    path: List[int] = []

    while stack:
        u = stack[-1]
        if local[u]:
            # prend un voisin avec multiplicité positive
            v, mult = next(((x, m) for x, m in local[u].items() if m > 0), (None, 0))
            if v is None:
                # impasse
                path.append(stack.pop())
                continue
            # consomme l'arête (u, v)
            local[u][v] -= 1
            local[v][u] -= 1
            if local[u][v] == 0:
                del local[u][v]
            if local[v][u] == 0:
                del local[v][u]
            stack.append(v)
        else:
            path.append(stack.pop())
    path.reverse()
    return path


def shortcut_hamiltonian(euler_path: List[int], W: Sequence[Sequence[float]], start: int = 0) -> Tuple[List[int], List[Edge], float]:
    """
    Transforme un chemin eulérien en cycle hamiltonien en sautant les sommets répétés (hypothèse d'inégalité triangulaire).

    Retourne
    --------
    order : ordre de visite des sommets (démarre à `start`)
    edges : arêtes du cycle hamiltonien dans l'ordre de visite
    total : longueur totale du cycle hamiltonien
    """
    n = len(W)
    seen = [False] * n
    order: List[int] = []

    # fait démarrer euler_path au sommet 'start'
    if start in euler_path:
        s_idx = euler_path.index(start)
        euler_path = euler_path[s_idx:] + euler_path[:s_idx]

    for v in euler_path:
        if not seen[v]:
            seen[v] = True
            order.append(v)
    # ferme le cycle en revenant à start
    if order[0] != start:
        # rotation pour placer start en premier
        s_idx = order.index(start)
        order = order[s_idx:] + order[:s_idx]

    edges: List[Edge] = []
    total = 0.0
    for i in range(len(order)):
        u = order[i]
        v = order[(i + 1) % len(order)]
        w = W[u][v]
        edges.append((u, v, w))
        total += w
    return order, edges, total


def christophides(
    W: Sequence[Sequence[float]],
    start: int = 0
) -> Tuple[List[Edge], float, List[Optional[int]], List[float]]:
    """
    Algorithme d'approximation de Christofides pour le TSP métrique.

    Paramètres
    ----------
    W : matrice de distances d'un graphe complet (doit vérifier l'inégalité triangulaire)
    start : sommet de départ du tour

    Retourne
    --------
    tour_edges : liste des arêtes (u, v, w) du cycle hamiltonien dans l'ordre
    tour_cost : longueur totale du tour
    parent : tableau des parents issu du MST (utile pour debug/visualisation)
    key : tableau des clés issu du MST (Prim)
    """
    n = len(W)

    # 1) MST : Prim si n > 100, sinon Kruskal (conforme au squelette demandé)
    if n > 100:
        mst_edges, _, parent, key = compute_mst_prim(W, start)
    else:
        mst_edges, _ = compute_mst_kruskal(W)
        # Construit parent/key en enracinant le MST en 'start'
        parent = [None] * n  # type: ignore[assignment]
        key = [float('inf')] * n
        # Construit l'adjacence du MST puis BFS pour remplir parent/key
        adj: Dict[int, List[int]] = {i: [] for i in range(n)}
        for u, v, w in mst_edges:
            adj[u].append(v)
            adj[v].append(u)
        # BFS simple pour définir les parents et les poids key
        from collections import deque
        dq = deque([start])
        parent[start] = None
        key[start] = 0.0
        visited = {start}
        while dq:
            u = dq.popleft()
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    parent[v] = u
                    key[v] = W[u][v]
                    dq.append(v)

    # 2) Sommets de degré impair dans le MST
    odd = odd_degree_vertices(mst_edges, n)

    # 3) Appariement parfait de poids minimal sur les sommets impairs (heuristique gloutonne)
    matching = greedy_minimum_perfect_matching(odd, W)

    # 4) Combine MST + matching -> multigraphe eulérien
    multi_adj = build_multigraph(mst_edges, matching)

    # 5) Tour eulérien
    euler_path = eulerian_tour(multi_adj, start)

    # 6) Raccourci vers un cycle hamiltonien
    _, tour_edges, tour_cost = shortcut_hamiltonian(euler_path, W, start)

    return tour_edges, tour_cost, parent, key
