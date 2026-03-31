"""
maze_generator.py — Cœur du projet : génération du labyrinthe.

RESPONSABLE: Simon
TÂCHE: Implémenter la classe MazeGenerator avec l'algorithme DFS (Recursive Backtracker).

=== RAPPEL ALGORITHME DFS (Recursive Backtracker) ===

1. Initialiser toutes les cellules avec TOUS leurs murs fermés.
2. Choisir une cellule de départ aléatoire → la marquer visitée.
3. Tant qu'il existe des cellules non visitées:
   a. Depuis la cellule courante, choisir un voisin non visité aléatoirement.
   b. Abattre le mur entre la cellule courante et ce voisin.
   c. Avancer vers ce voisin (le marquer visité).
   d. Si aucun voisin non visité → reculer (backtrack) vers la cellule précédente.
4. Résultat: un labyrinthe parfait (arbre couvrant du graphe de la grille).

=== ENCODAGE DES MURS ===
Chaque cellule est un entier 4 bits:
  Bit 0 (LSB) = Nord  (1 si mur fermé, 0 si ouvert)
  Bit 1       = Est
  Bit 2       = Sud
  Bit 3       = Ouest

Exemple: 0xF = 1111 = toutes les murs fermés
         0x0 = 0000 = aucun mur (cellule entièrement ouverte)
         0x3 = 0011 = murs Nord et Est fermés

=== DIRECTIONS ===
Nord: dy=-1, dx=0  → bit 0 de la cellule, bit 2 du voisin (Sud)
Est:  dy=0,  dx=1  → bit 1 de la cellule, bit 3 du voisin (Ouest)
Sud:  dy=1,  dx=0  → bit 2 de la cellule, bit 0 du voisin (Nord)
Ouest:dy=0,  dx=-1 → bit 3 de la cellule, bit 1 du voisin (Est)
"""

# ============================================================
# IMPORTS
# ============================================================
import random
from typing import List, Tuple, Optional
from collections import deque


# ============================================================
# CONSTANTES — bits de direction
# ============================================================
NORTH: int = 0b0001  # bit 0
EAST:  int = 0b0010  # bit 1
SOUTH: int = 0b0100  # bit 2
WEST:  int = 0b1000  # bit 3

# Mapping direction → (dx, dy, bit_opposé)
# Pour abattre un mur entre deux cellules, il faut
# retirer le bit de la cellule courante ET le bit opposé du voisin.
DIRECTIONS: List[Tuple[int, int, int, int]] = [
    # (dx, dy, bit_courant, bit_voisin_opposé)
    (0,  -1, NORTH, SOUTH),
    (1,   0, EAST,  WEST),
    (0,   1, SOUTH, NORTH),
    (-1,  0, WEST,  EAST),
]


# ============================================================
# CLASSE PRINCIPALE
# ============================================================

class MazeGenerator:
    """
    Génère un labyrinthe sur une grille width×height.

    Le labyrinthe est stocké comme une liste 2D d'entiers (cells),
    où chaque entier encode les murs fermés de la cellule via 4 bits.

    Attributes:
        width:   Nombre de colonnes.
        height:  Nombre de lignes.
        entry:   Coordonnées (x, y) de l'entrée.
        exit_pos:Coordonnées (x, y) de la sortie.
        perfect: Si True, génère un labyrinthe parfait (DFS pur).
        seed:    Graine aléatoire pour la reproductibilité.
        cells:   Grille [y][x] → entier 4 bits encodant les murs.
        solution:Chemin solution sous forme de string "NNEESS..."
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_pos: Tuple[int, int],
        perfect: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        """
        Initialise le générateur sans encore générer le labyrinthe.

        Args:
            width:    Nombre de colonnes (≥ 2).
            height:   Nombre de lignes (≥ 2).
            entry:    Coordonnées (x, y) de l'entrée.
            exit_pos: Coordonnées (x, y) de la sortie.
            perfect:  Si True, le labyrinthe sera parfait.
            seed:     Graine pour random.seed() (reproductibilité).
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
        self.perfect = perfect
        self.seed = seed
        # Grille des murs : sera initialisée dans generate()
        # self.cells[y][x] = entier 4 bits
        self.cells: List[List[int]] = []
        self.solution: str = ""

        if seed is not None:
            random.seed(seed)

    # ----------------------------------------------------------
    # MÉTHODE PRINCIPALE
    # ----------------------------------------------------------

    def generate(self) -> None:
        """
        Génère le labyrinthe complet.

        Étapes:
        1. _init_cells()       → toutes les cellules avec 4 murs fermés (0xF)
        2. _carve_passages()   → algorithme DFS pour ouvrir des passages
        3. _apply_42_pattern() → graver le motif "42" (cellules entièrement fermées)
        4. _open_entry_exit()  → ouvrir l'entrée et la sortie sur le bord
        5. _enforce_borders()  → s'assurer que les bords extérieurs sont bien fermés
        6. _solve()            → calculer le chemin le plus court (BFS)

        Si not perfect → appeler aussi _add_loops() après _carve_passages()
        pour créer des chemins supplémentaires (cycles).

        """
        self._init_cells()
        self._carve_passages()
        if not self.perfect:
            self._add_loops()
        self._apply_42_pattern()
        self._open_entry_exit()
        self._enforce_borders()
        self._solve()

    # ----------------------------------------------------------
    # INITIALISATION
    # ----------------------------------------------------------

    def _init_cells(self) -> None:
        """
        Crée la grille avec toutes les cellules fermées (tous les murs à 1).

        Résultat: self.cells[y][x] = 0xF pour tout (x, y).

        Exemple: [[0xF] * width for _ in range(height)]
        """
        self.cells = [[0xF] * self.width for _ in range(self.height)]

    # ----------------------------------------------------------
    # ALGORITHME DE GÉNÉRATION — DFS Recursive Backtracker
    # ----------------------------------------------------------

    def _carve_passages(self) -> None:
        """
        Génère le labyrinthe par DFS itératif (évite la récursion Python trop profonde).

        Algorithme (version itérative avec stack):
        1. Initialiser un tableau visited[y][x] = False.
        2. Choisir une cellule de départ (ex: entrée ou (0,0)).
        3. Empiler la cellule de départ, la marquer visitée.
        4. Tant que la stack n'est pas vide:
           a. Regarder la cellule en sommet de stack.
           b. Trouver ses voisins non visités dans la grille.
           c. S'il y en a → choisir un au hasard, abattre le mur, l'empiler.
           d. Sinon → dépiler (backtrack).

        Pour abattre le mur entre (x, y) et (nx, ny):
          self.cells[y][x]   &= ~bit_courant   (retirer le bit de la direction)
          self.cells[ny][nx] &= ~bit_opposé     (retirer le bit opposé du voisin)
        """
        self._init_cells()

        visited: list[list[bool]] = [[False] * self.width for _ in range(self.height)]

        # Pré-calculer les cellules du motif 42 et les marquer visitées
        # → le DFS ne les touchera jamais
        for x, y in self._get_42_cells():
            if 0 <= x < self.width and 0 <= y < self.height:
                visited[y][x] = True  # bloquer ces cellules

        stack: list[tuple[int, int]] = [self.entry]
        visited[self.entry[1]][self.entry[0]] = True

        while stack:
            x, y = stack[-1]
            neighbors: list[tuple[int, int, int, int]] = [
                (x + dx, y + dy, bit, opp)
                for dx, dy, bit, opp in DIRECTIONS
                if 0 <= x + dx < self.width
                and 0 <= y + dy < self.height
                and not visited[y + dy][x + dx]
            ]
            if neighbors and self._check_open_area(x, y):
                nx, ny, bit, opp = random.choice(neighbors)
                self.cells[y][x] &= ~bit
                self.cells[ny][nx] &= ~opp
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def _add_loops(self) -> None:
        """
        Ajoute des boucles au labyrinthe pour le rendre imparfait.

        Après un DFS pur, tous les passages sont déjà ouverts de façon optimale.
        Pour créer un labyrinthe imparfait, il faut abattre quelques murs supplémentaires
        aléatoirement (environ 10-20% des murs restants).
        """
        cells_42: set[tuple[int, int]] = self._get_42_cells()

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in cells_42:
                    continue

                for dx, dy, bit, opp in DIRECTIONS:
                    nx, ny = x + dx, y + dy

                    # Ignorer les bords extérieurs
                    if not (0 <= nx < self.width and 0 <= ny < self.height):
                        continue

                    # Ignorer si le mur est déjà ouvert
                    if not (self.cells[y][x] & bit):
                        continue

                    # Ignorer les cellules du motif 42
                    if (nx, ny) in cells_42:
                        continue

                    # ~15% de chance d'abattre ce mur
                    if random.random() < 0.1 and self._check_open_area(x, y):
                        self.cells[y][x] &= ~bit
                        self.cells[ny][nx] &= ~opp

    def _check_open_area(self, x: int, y: int) -> bool:
        """
        Vérifie si abattre un mur à (x, y) créerait une zone ouverte > 2×2.

        Returns:
            True si c'est safe (pas de 3×3 ouvert), False sinon.
        """
        for ox in range(-2, 1):
            for oy in range(-2, 1):
                bx, by = x + ox, y + oy
                if not (0 <= bx and bx + 2 < self.width
                        and 0 <= by and by + 2 < self.height):
                    continue
                open_area = True
                for cy in range(by, by + 3):
                    for cx in range(bx, bx + 3):
                        if cx < bx + 2 and (self.cells[cy][cx] & EAST):
                            open_area = False
                        if cy < by + 2 and (self.cells[cy][cx] & SOUTH):
                            open_area = False

                if open_area:
                    return False
        return True

    # ----------------------------------------------------------
    # MOTIF "42"
    # ----------------------------------------------------------

    def _get_42_cells(self) -> set[tuple[int, int]]:
        pat_four: list[tuple[int, int]] = [
            (0, 0), (0, 1), (0, 2),
            (1, 2), (2, 2),
            (2, 3), (2, 4),
        ]
        pat_two: list[tuple[int, int]] = [
            (4, 0), (5, 0), (6, 0),
            (6, 1),
            (6, 2), (5, 2), (4, 2),
            (4, 3),
            (4, 4), (5, 4), (6, 4),
        ]
        origin_x: int = (self.width - 7) // 2
        origin_y: int = (self.height - 5) // 2

        cells: set[tuple[int, int]] = set()
        for dx, dy in pat_four + pat_two:
            cells.add((origin_x + dx, origin_y + dy))

        cells.discard(self.entry)
        cells.discard(self.exit_pos)
        return cells

    def _apply_42_pattern(self) -> None:
        """
        Grave le motif "42" dans le labyrinthe sous forme de cellules entièrement fermées.

        Le motif doit être visible dans l'affichage graphique: un groupe de cellules
        avec tous leurs murs fermés (valeur 0xF) forme les chiffres "4" et "2".

        Contraintes:
        - Les cellules du motif "42" sont des îlots (toutes les murs = 0xF).
        - Elles peuvent briser la connectivité → c'est accepté selon le sujet.
        - Si le labyrinthe est trop petit (< ~15×10), afficher un message d'erreur
          et ne pas appliquer le motif.
        """
        if self.width < 15 or self.height < 10:
            print("Warning: maze too small to display '42' pattern.")
            return

        for x, y in self._get_42_cells():
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            self.cells[y][x] = 0xF
            for dx, dy, bit, opp in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.cells[ny][nx] |= opp

    # ----------------------------------------------------------
    # ENTRÉE / SORTIE ET BORDS
    # ----------------------------------------------------------

    def _open_entry_exit(self) -> None:
        """
        Ouvre le mur extérieur à l'entrée et à la sortie du labyrinthe.

        L'entrée et la sortie sont des cellules sur le bord.
        Il faut identifier quel mur extérieur ouvrir:
        - Si x == 0         → ouvrir le mur Ouest (retirer bit WEST)
        - Si x == width-1   → ouvrir le mur Est   (retirer bit EAST)
        - Si y == 0         → ouvrir le mur Nord   (retirer bit NORTH)
        - Si y == height-1  → ouvrir le mur Sud    (retirer bit SOUTH)

        """
        for x, y in (self.entry, self.exit_pos):
            if x == 0:
                self.cells[y][x] &= ~WEST
            elif x == self.width - 1:
                self.cells[y][x] &= ~EAST
            elif y == 0:
                self.cells[y][x] &= ~NORTH
            elif y == self.height - 1:
                self.cells[y][x] &= ~SOUTH

    def _enforce_borders(self) -> None:
        """
        S'assure que toutes les cellules de bord ont leurs murs extérieurs fermés,
        SAUF les cellules d'entrée et de sortie qui ont été ouvertes.

        Parcourir les 4 bords et fermer les murs extérieurs:
        - Ligne y=0         → bit NORTH doit être 1 pour toutes les cellules sauf entry/exit
        - Ligne y=height-1  → bit SOUTH doit être 1
        - Col x=0          → bit WEST doit être 1
        - Col x=width-1    → bit EAST doit être 1

        """

        exceptions: set[tuple[int, int]] = {self.entry, self.exit_pos}

        for x in range(self.width):
            if (x, 0) not in exceptions:
                self.cells[0][x] |= NORTH
            if (x, self.height - 1) not in exceptions:
                self.cells[self.height - 1][x] |= SOUTH

        for y in range(self.height):
            if (0, y) not in exceptions:
                self.cells[y][0] |= WEST
            if (self.width - 1, y) not in exceptions:
                self.cells[y][self.width - 1] |= EAST

    # ----------------------------------------------------------
    # RÉSOLUTION — BFS
    # ----------------------------------------------------------

    def _solve(self) -> None:
        """
        Calcule le chemin le plus court entre entry et exit_pos par BFS.

        Résultat stocké dans self.solution sous la forme d'une string
        avec les lettres N, E, S, W (ex: "SSEEENNNEE").

        Algorithme BFS:
        1. File d'attente initialisée avec (entry_x, entry_y, chemin="").
        2. Ensemble visited pour ne pas repasser par une cellule.
        3. Pour chaque cellule défilée, essayer les 4 directions:
           - Vérifier que le mur dans cette direction est OUVERT (bit = 0).
           - Vérifier que le voisin est dans la grille et non visité.
           - Enqueue le voisin avec le chemin mis à jour.
        4. Quand exit_pos est atteint → stocker le chemin dans self.solution.
        """
        letter: dict[int, str] = {NORTH: 'N', EAST: 'E', SOUTH: 'S', WEST: 'W'}
        visited: list[list[bool]] = [[False] * self.width for _ in range(self.height)]

        queue: deque[tuple[int, int, str]] = deque()
        queue.append((self.entry[0], self.entry[1], ""))
        visited[self.entry[1]][self.entry[0]] = True
        while queue:
            x, y, path = queue.popleft()
            if (x, y) == self.exit_pos:
                self.solution = path
                return
            for dx, dy, bit, _ in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if not (self.cells[y][x] & bit) \
                        and 0 <= nx < self.width \
                        and 0 <= ny < self.height \
                        and not visited[ny][nx]:
                    visited[ny][nx] = True
                    queue.append((nx, ny, path + letter[bit]))

    # ----------------------------------------------------------
    # ACCESSEURS PUBLICS (pour le module réutilisable)
    # ----------------------------------------------------------

    def get_cell(self, x: int, y: int) -> int:
        """
        Retourne la valeur de la cellule (x, y).

        Args:
            x: Colonne (0 à width-1).
            y: Ligne   (0 à height-1).

        Returns:
            Entier 4 bits encodant les murs fermés.
        """
        return self.cells[y][x]

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        """
        Indique si la cellule (x, y) a un mur fermé dans la direction donnée.

        Args:
            x:         Colonne.
            y:         Ligne.
            direction: NORTH, EAST, SOUTH ou WEST.

        Returns:
            True si le mur est fermé, False s'il est ouvert.
        """
        return bool(self.cells[y][x] & direction)

    def get_solution(self) -> str:
        """Retourne le chemin solution sous forme de string 'NNEESS...'."""
        return self.solution

    def to_hex_grid(self) -> List[List[str]]:
        """
        Retourne la grille sous forme de liste 2D de caractères hexadécimaux.

        Returns:
            Liste [y][x] de strings hexadécimaux en majuscule (ex: "F", "A", "3").

        Utile pour l'écriture du fichier de sortie.
        """
        return [
            [format(self.cells[y][x], 'X') for x in range(self.width)]
            for y in range(self.height)
        ]
