def build_edges(matrix):
    """Construit la liste des arêtes à partir de la matrice d'adjacence."""
    n = len(matrix)
    return [(i, j, matrix[i][j])
            for i in range(n)
            for j in range(i + 1, n)
            if matrix[i][j] != 0]

def find(parent, u):
    """Trouve le représentant de l'ensemble contenant u avec compression de chemin."""
    if parent[u] != u:
        parent[u] = find(parent, parent[u])
    return parent[u]

def union(parent, rank, u, v):
    """Union des ensembles contenant u et v selon le rang."""
    u_root = find(parent, u)
    v_root = find(parent, v)
    if u_root == v_root:
        return
    if rank[u_root] < rank[v_root]:
        parent[u_root] = v_root
    elif rank[u_root] > rank[v_root]:
        parent[v_root] = u_root
    else:
        parent[v_root] = u_root
        rank[u_root] += 1

def kruskal(matrix):
    """Retourne l'arbre couvrant minimum (MST) à partir d'une matrice d'adjacence."""
    n = len(matrix)
    edges = build_edges(matrix)
    edges.sort(key=lambda e: e[2])

    parent = list(range(n))
    rank = [0] * n

    mst = []
    for u, v, w in edges:
        if find(parent, u) != find(parent, v):
            mst.append((u, v, w))
            union(parent, rank, u, v)

    return mst

if __name__ == "__main__":
    matrix = [
        [0.0, 2.24, 4.24, 4.12, 4.0],
        [2.24, 0.0, 2.24, 3.16, 2.24],
        [4.24, 2.24, 0.0, 2.24, 3.16],
        [4.12, 3.16, 2.24, 0.0, 5.0],
        [4.0, 2.24, 3.16, 5.0, 0.0]
    ]

    mst = kruskal(matrix)
    print("Arbre couvrant minimum:", mst)