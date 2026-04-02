"""
display.py — Affichage terminal interactif du labyrinthe.

RESPONSABLE: Otto
TÂCHE: Afficher le labyrinthe en ASCII couleurs dans le terminal,
       avec un menu interactif permettant:
       1. Re-générer un nouveau labyrinthe
       2. Afficher/cacher le chemin solution
       3. Changer la couleur des murs
       4. Quitter

=== TECHNIQUE DE RENDU ASCII ===

Chaque cellule est représentée sur 2 lignes et 2 colonnes de caractères:
- La "top-left" d'une cellule (x,y) dans l'espace ASCII est à (2*x, 2*y).
- On dessine d'abord une grille de '+' aux intersections,
  puis on ajoute les murs horizontaux ('---') et verticaux ('|').

Exemple pour une grille 3×2 (largeur=3, hauteur=2):
  +--+--+--+
  |        |
  +  +--+  +
  |        |
  +--+--+--+

=== CODES COULEUR ANSI ===
Pour colorer le terminal, utiliser les codes ANSI:
  \\033[XXm  où XX est un code couleur.
  \\033[0m   = reset
  \\033[31m  = rouge
  \\033[32m  = vert
  \\033[33m  = jaune
  \\033[34m  = bleu
  \\033[37m  = blanc
  \\033[1m   = gras

Pour les couleurs de fond (background):
  \\033[41m  = fond rouge
  \\033[42m  = fond vert
  \\033[44m  = fond bleu
  \\033[47m  = fond blanc/gris
"""

# ============================================================
# IMPORTS
# ============================================================
from typing import TYPE_CHECKING, List, Tuple
import os
if TYPE_CHECKING:
    from mazegen_src.maze_generator import MazeGenerator

# Constantes des bits de direction (dupliquées ici pour éviter l'import circulaire)
NORTH: int = 0b0001
EAST:  int = 0b0010
SOUTH: int = 0b0100
WEST:  int = 0b1000

# ============================================================
# PALETTES DE COULEURS DISPONIBLES
# ============================================================
# Chaque palette = (couleur_mur, couleur_chemin, couleur_entrée, couleur_sortie)
COLOR_PALETTES = [
    # (code_mur, code_chemin, code_entrée, code_sortie, nom)
    ("\033[37m", "\033[36m", "\033[35m", "\033[31m", "Défaut (blanc/cyan)"),
    ("\033[33m", "\033[36m", "\033[35m", "\033[31m", "Jaune/cyan"),
    ("\033[32m", "\033[34m", "\033[35m", "\033[31m", "Vert/bleu"),
    ("\033[34m", "\033[33m", "\033[35m", "\033[31m", "Bleu/jaune"),
]
RESET = "\033[0m"


# ============================================================
# FONCTION PRINCIPALE D'AFFICHAGE INTERACTIF
# ============================================================

def display_maze_terminal(generator: "MazeGenerator") -> None:
    """
    Lance l'affichage interactif du labyrinthe dans le terminal.

    Boucle principale:
    1. Rendre le labyrinthe en ASCII et l'afficher.
    2. Afficher le menu: 1. Regen | 2. Chemin | 3. Couleur | 4. Quitter
    3. Lire le choix de l'utilisateur.
    4. Effectuer l'action correspondante.
    5. Répéter.

    Args:
        generator: Instance de MazeGenerator après generate().

    TODO (Simon):
    - Initialiser show_path = False, palette_idx = 0.
    - Dans la boucle: appeler render_maze() puis afficher le menu.
    - Choix 1: appeler generator.generate() et continuer.
    - Choix 2: toggle show_path.
    - Choix 3: incrémenter palette_idx % len(COLOR_PALETTES).
    - Choix 4: quitter la boucle.
    - Gérer les entrées invalides gracieusement (pas de crash).
    """
    show_path: bool = False
    palette_idx: int = 0

    while True:
        # Effacer l'écran (compatible Unix/Mac)
        os.system("clear")

        # TODO (Simon): appeler render_maze() et afficher le résultat
        lines = render_maze(generator, show_path=show_path,
                            palette_idx=palette_idx)
        print("\n".join(lines))

        # TODO (Simon): afficher le menu
        print("\n==== A-Maze-ing ====")
        print("1. Re-générer un nouveau labyrinthe")
        print("2. Afficher/Cacher le chemin solution")
        print("3. Changer la couleur des murs")
        print("4. Quitter")
        choice = input("Choix (1-4): ").strip()

        # TODO (Simon): gérer les choix
        if choice == "1":
            generator.generate()
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            palette_idx = (palette_idx + 1) % len(COLOR_PALETTES)
        elif choice == "4":
            break
        else:
            input("Choix invalide. Appuyer sur Entrée pour continuer...")


# ============================================================
# RENDU ASCII DU LABYRINTHE
# ============================================================

def render_maze(
    generator: "MazeGenerator",
    show_path: bool = False,
    palette_idx: int = 0,
) -> List[str]:
    w = generator.width
    h = generator.height

    grid = [[" " for _ in range(2 * w + 1)] for _ in range(2 * h + 1)]

    BLOCK = "█"
    for gy in range(0, 2 * h + 1, 2):
        for gx in range(0, 2 * w + 1, 2):
            grid[gy][gx] = BLOCK
    for cy in range(h):
        for cx in range(w):
            if generator.has_wall(cx, cy, NORTH):
                grid[2 * cy][2 * cx + 1] = BLOCK
            if generator.has_wall(cx, cy, WEST):
                grid[2 * cy + 1][2 * cx] = BLOCK
            if generator.has_wall(cx, cy, SOUTH):
                grid[2 * cy + 2][2 * cx + 1] = BLOCK
            if generator.has_wall(cx, cy, EAST):
                grid[2 * cy + 1][2 * cx + 2] = BLOCK
    ex, ey = generator.entry
    sx, sy = generator.exit_pos
    grid[2 * ey + 1][2 * ex + 1] = "\033[34mE"
    grid[2 * sy + 1][2 * sx + 1] = "\033[37m▒"
    if show_path:
        path_cells = _path_cells(generator)
        SHADE = "\033[31m█"
        for (px, py) in path_cells:
            if (px, py) != generator.entry and (px, py) != generator.exit_pos:
                grid[2 * py + 1][2 * px + 1] = SHADE

    c_wall, c_path, c_entry, c_exit, _ = COLOR_PALETTES[palette_idx]
    lines = []
    for row in grid:
        line_str = ""
        for char in row:
            if char == BLOCK:
                line_str += f"{c_wall}{char}{RESET}"
            elif char == "█":
                line_str += f"{c_path}{char}{RESET}"
            elif char == "E":
                line_str += f"{c_entry}{char}{RESET}"
            elif char == "▒":
                line_str += f"{c_exit}{char}{RESET}"
            else:
                line_str += char

        lines.append(line_str)
    return lines


def _path_cells(generator: "MazeGenerator") -> List[Tuple[int, int]]:

    path = []
    x, y = generator.entry
    path.append((x, y))
    for direction in generator.solution:
        if direction == "N":
            y -= 1
        elif direction == "S":
            y += 1
        elif direction == "E":
            x += 1
        elif direction == "W":
            x -= 1
        path.append((x, y))
    return path
