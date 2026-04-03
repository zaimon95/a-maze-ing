"""
output_writer.py — Écriture du fichier de sortie au format hexadécimal.

RESPONSABLE: Otto
TÂCHE: Écrire le labyrinthe dans un fichier texte selon le format du sujet.

=== FORMAT DU FICHIER DE SORTIE ===

Ligne 1 à HEIGHT:  une ligne par rangée, chaque cellule encodée en 1 hex (majuscule).
Ligne HEIGHT+1:    ligne vide
Ligne HEIGHT+2:    coordonnées de l'entrée "x,y"
Ligne HEIGHT+3:    coordonnées de la sortie "x,y"
Ligne HEIGHT+4:    chemin solution "NNEESSSWW..."

Toutes les lignes se terminent par \\n.
"""

# ============================================================
# IMPORTS
# ============================================================
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mazegen_src.maze_generator import MazeGenerator


def write_output_file(generator: "MazeGenerator", output_path: str) -> None:
    """
    This function writes the Ascii output
    """

    f1 = open(output_path, "r")
    f2 = open('output_maze.txt', 'w')
    for line in f1:
        f2.write(line)
    f1.close()
    f2.close()
    ex, ey = generator.entry
    sx, sy = generator.exit_pos
    hex_grid = generator.to_hex_grid()
    solution = generator.get_solution()
    with open('output_maze.txt', "w") as f:
        for row in hex_grid:
            f.write("".join(row))
            f.write("\n")
        f.write(f"\n{ex},{ey}\n")
        f.write(f"{sx},{sy}\n")
        f.write(solution)
