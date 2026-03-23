"""
display.py — Affichage terminal interactif du labyrinthe.

RESPONSABLE: Simon
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
from typing import TYPE_CHECKING, Optional, List, Tuple
import os
import sys

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
        print(f"\n==== A-Maze-ing ====")
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
    """
    Rend le labyrinthe en une liste de strings ASCII colorées.

    Args:
        generator:   Labyrinthe généré.
        show_path:   Si True, dessiner le chemin solution.
        palette_idx: Index dans COLOR_PALETTES.

    Returns:
        Liste de strings (une par ligne ASCII), à joindre avec \\n pour afficher.

    TODO (Simon):
    Approche recommandée — grille de caractères:
    1. Créer une grille de chars de taille (2*height+1) × (2*width+1),
       initialisée avec des espaces.
    2. Placer les coins '+' à chaque position (2*x, 2*y) pour 0≤x≤width, 0≤y≤height.
    3. Pour chaque cellule (cx, cy):
       - Si mur Nord fermé  → placer '--' en (2*cx, 2*cy)   et (2*cx+1, 2*cy) [horizontal]
         Note: le mur nord de (cx, cy) est la ligne y=2*cy dans la grille de chars
       - Si mur Ouest fermé → placer '|'  en (2*cx, 2*cy+1) [vertical]
       - Si mur Sud fermé   → placer '--' en (2*cx, 2*cy+2) ...
       - Si mur Est fermé   → placer '|'  en (2*cx+2, 2*cy+1)
    4. Si show_path: récupérer les cellules du chemin (via _path_cells())
       et les marquer d'un caractère spécial.
    5. Marquer l'entrée et la sortie avec des caractères distincts.
    6. Appliquer les couleurs ANSI.

    CONSEIL: commencer SANS les couleurs, vérifier que le rendu est correct,
    puis ajouter les couleurs ANSI autour des murs et du chemin.
    """
    # TODO (Simon): implémenter render_maze
    # Squelette vide pour permettre à l'ensemble de compiler:
    wall_color = COLOR_PALETTES[palette_idx][0]
    path_color = COLOR_PALETTES[palette_idx][1]
    entry_color = COLOR_PALETTES[palette_idx][2]
    exit_color = COLOR_PALETTES[palette_idx][3]

    h = generator.height
    w = generator.width

    # Grille de chars: (2h+1) lignes × (2w+1) colonnes
    grid: List[List[str]] = [[" "] * (2 * w + 1) for _ in range(2 * h + 1)]

    # Coins
    for gy in range(0, 2 * h + 1, 2):
        for gx in range(0, 2 * w + 1, 2):
            grid[gy][gx] = "+"

    # TODO (Simon): remplir les murs horizontaux et verticaux
    # Pour chaque cellule (cx, cy):
    #   gx, gy = 2*cx, 2*cy  (coin supérieur gauche dans la grille)
    #   if generator.has_wall(cx, cy, NORTH): grid[gy][gx+1] = "-"
    #   if generator.has_wall(cx, cy, SOUTH): grid[gy+2][gx+1] = "-"
    #   if generator.has_wall(cx, cy, WEST):  grid[gy+1][gx] = "|"
    #   if generator.has_wall(cx, cy, EAST):  grid[gy+1][gx+2] = "|"

    # TODO (Simon): marquer l'entrée et la sortie
    # ex, ey = generator.entry
    # sx, sy = generator.exit_pos
    # grid[2*ey+1][2*ex+1] = "E"  (entrée)
    # grid[2*sy+1][2*sx+1] = "X"  (sortie)

    # TODO (Simon): si show_path, marquer le chemin
    # path_cells = _path_cells(generator)
    # for (px, py) in path_cells:
    #     grid[2*py+1][2*px+1] = "."

    # TODO (Simon): assembler les lignes avec couleurs ANSI
    lines: List[str] = []
    for row in grid:
        lines.append("".join(row))
    return lines


def _path_cells(generator: "MazeGenerator") -> List[Tuple[int, int]]:
    """
    Convertit la solution string en liste de cellules (x, y).

    Args:
        generator: Labyrinthe avec solution calculée.

    Returns:
        Liste ordonnée de (x, y) depuis l'entrée jusqu'à la sortie.

    TODO (Simon):
    - Partir de generator.entry.
    - Pour chaque lettre dans generator.solution:
        'N' → dy=-1, 'S' → dy=+1, 'E' → dx=+1, 'W' → dx=-1
    - Accumuler les positions dans une liste.
    """
    path: List[Tuple[int, int]] = []
    x, y = generator.entry
    path.append((x, y))

    # TODO (Simon): parcourir generator.solution
    direction_map = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    for ch in generator.solution:
        if ch in direction_map:
            dx, dy = direction_map[ch]
            x += dx
            y += dy
            path.append((x, y))

    return path
