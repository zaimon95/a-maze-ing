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

from mypy.typeops import false_only

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
        solution:Chemin solution sous forme de string "NNEESS...".

    Example:
        >>> gen = MazeGenerator(width=10, height=10, entry=(0,0),
        ...                      exit_pos=(9,9), perfect=True, seed=42)
        >>> gen.generate()
        >>> print(gen.solution)
        'SSSEEENNN...'
        >>> print(gen.cells[0][0])  # murs de la cellule (0,0)
        9
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

        TODO (Simon):
        - Stocker tous les paramètres comme attributs d'instance.
        - Initialiser self.cells = liste vide (sera remplie par generate()).
        - Initialiser self.solution = "" (sera remplie par _solve()).
        - Appeler random.seed(seed) si seed is not None.
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

        TODO (Simon): implémenter cette méthode en appelant les sous-méthodes.
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

        TODO (Simon): créer une liste 2D height×width remplie de 0xF.
        Exemple: [[0xF] * width for _ in range(height)]
        """
        # TODO (Simon)
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

        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        stack: list[tuple[int, int]] = [self.entry]
        visited[self.entry[0]][self.entry[1]] = True
        while stack:
            x, y = stack[-1]
            neighbors: list[tuple[int, int, int, int]] = [
                (x + dx, y + dy, bit, opp)
                for dx, dy, bit, opp in DIRECTIONS
                if 0 <= x + dx < self.width
                   and 0 <= y + dy < self.height
                   and not visited[y + dy][x + dx]
            ]
            if neighbors:
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

        TODO (Simon):
        - Parcourir les cellules internes.
        - Pour chaque cellule, pour chaque mur encore fermé vers un voisin valide,
          l'abattre avec une probabilité de ~15%.
        - Ne pas abattre de murs sur les bords extérieurs.
        - Respecter la contrainte: pas de zone ouverte 3×3 (vérifier _check_open_area).
        """
        # TODO (Simon): implémenter l'ajout de boucles
        pass

    @staticmethod
    def _check_open_area(x: int, y: int) -> bool:
        """
        Vérifie si abattre un mur à (x,y) créerait une zone ouverte > 2×2.

        Returns:
            True si c'est safe (pas de 3×3 ouvert), False sinon.

        TODO (Simon):
        - Après un abattage hypothétique, vérifier les 9 cellules autour de (x,y).
        - Une zone 3×3 est "ouverte" si toutes les cellules internes peuvent se rejoindre
          sans mur (ce calcul peut être simplifié: vérifier si un carré 3×3 n'a aucun mur
          séparant ses cellules).
        - Astuce: vérifier pour chaque carré 3×3 qui contient (x,y) si les 4 passages
          internes sont ouverts.
        """
        # TODO (Simon)
        return True

    # ----------------------------------------------------------
    # MOTIF "42"
    # ----------------------------------------------------------

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

        TODO (Simon):
        - Définir les coordonnées relatives des cellules formant "4" et "2"
          (typiquement ~5 colonnes × 7 lignes chacun, séparés d'un espace).
        - Centrer le motif dans le labyrinthe.
        - Pour chaque cellule du motif: self.cells[y][x] = 0xF
          ET fermer les murs des voisins qui touchent cette cellule
          (pour garder la cohérence: si ma cellule est fermée côté Est,
           mon voisin Est doit l'être aussi côté Ouest).

        Conseil: définir les chiffres comme des bitmaps 5×7.
        Exemple pour "4":
          PATTERN_4 = [
            (0,0),(0,1),(0,2),(0,3),  # colonne gauche
            (1,2),(2,2),(3,2),(4,2),  # barre horizontale
            (4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6),  # colonne droite
          ]
        """
        # TODO (Simon): définir et appliquer le motif
        MIN_WIDTH = 15
        MIN_HEIGHT = 10
        if self.width < MIN_WIDTH or self.height < MIN_HEIGHT:
            print("Warning: maze too small to display '42' pattern.")
            return

        # TODO (Simon): définir PATTERN_4 et PATTERN_2 puis les appliquer
        pass

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
        for y in range(self.width):
            if (0, y) not in exceptions:
                self.cells[y][0] |= WEST
            elif (self.width - 1, y) not in exceptions:
                self.cells[y][self.width - 1] |= EAST
        for x in range(self.height):
            if (x, 0) not in exceptions:
                self.cells[0][x] |= NORTH
            elif (x, self.height - 1) not in exceptions:
                self.cells[self.height - 1][x] |= SOUTH

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

        TODO (Simon): implémenter le BFS.
        IMPORTANT: Le chemin BFS doit passer uniquement par des passages ouverts
        (murs = 0). Ne pas traverser les cellules du motif "42".
        """
        # TODO (Simon): implémenter BFS
        self.solution = ""  # placeholder

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
