import itertools, math

# Définition du graphe

# Matrice des distances entre les sommets (symétrique)
# dist[i][j] = distance entre le sommet i et le sommet j
dist = [
    [0.0, 2.24, 4.24, 4.12, 4.0],
    [2.24, 0.0, 2.24, 3.16, 2.24],
    [4.24, 2.24, 0.0, 2.24, 3.16],
    [4.12, 3.16, 2.24, 0.0, 5.0],
    [4.0, 2.24, 3.16, 5.0, 0.0],
]

n = len(dist)       # Nombre total de sommets
depot = 0           # On fixe le dépôt comme sommet 0
clients = list(range(1, n))  # Les sommets clients (1 à n-1)

def tour_distance(order, dist):
    """
    Calcule la distance totale d'une tournée donnée.
    order = permutation des clients (sans le dépôt).
    Le parcours est : dépôt -> clients dans 'order' -> retour au dépôt.
    """
    total = 0.0
    cur = depot
    for v in order:                 # On parcourt chaque client dans l'ordre donné
        total += dist[cur][v]       # On ajoute la distance depuis le point courant
        cur = v                     # On avance au client suivant
    total += dist[cur][depot]       # On ajoute le retour final vers le dépôt
    return total


best = None  # meilleure solution trouvée (distance, permutation)
for perm in itertools.permutations(clients):
    # On génère toutes les permutations possibles des clients
    d = tour_distance(perm, dist)  # On calcule la distance de cette tournée
    if best is None or d < best[0]:
        # Si c'est la première solution ou si elle est meilleure que l'actuelle
        best = (d, perm)

# =============================
# Affichage du résultat
# =============================

print("Nombre de tournées testées :", math.factorial(len(clients)))
print("Meilleure tournée trouvée :")
print(" Distance totale =", best[0])
print(" Ordre =", (0,) + best[1] + (0,))
