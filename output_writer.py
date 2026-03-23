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
    Écrit le labyrinthe dans le fichier de sortie.

    Args:
        generator:   Instance de MazeGenerator après generate().
        output_path: Chemin du fichier de sortie (ex: "maze.txt").

    Raises:
        OSError: Si l'écriture échoue (disque plein, droits insuffisants...).

    TODO (Otto):
    1. Ouvrir output_path en écriture avec context manager.
    2. Pour chaque ligne y de 0 à height-1:
       - Récupérer generator.to_hex_grid()[y]
       - Écrire la ligne: "".join(row) + "\\n"
    3. Écrire une ligne vide ("\\n").
    4. Écrire l'entrée: f"{ex},{ey}\\n" (generator.entry)
    5. Écrire la sortie: f"{sx},{sy}\\n" (generator.exit_pos)
    6. Écrire la solution: generator.solution + "\\n"

    ATTENTION: Vérifier que generator.solution n'est pas vide.
    Si vide → afficher un warning mais continuer (le sujet demande quand même la ligne).
    """
    # TODO (Otto): implémenter write_output_file
    # Exemple de squelette:
    # ex, ey = generator.entry
    # sx, sy = generator.exit_pos
    # hex_grid = generator.to_hex_grid()
    # try:
    #     with open(output_path, "w") as f:
    #         for row in hex_grid:
    #             f.write("".join(row) + "\n")
    #         f.write("\n")
    #         f.write(f"{ex},{ey}\n")
    #         f.write(f"{sx},{sy}\n")
    #         f.write(generator.solution + "\n")
    # except OSError as e:
    #     raise OSError(f"Failed to write output file '{output_path}': {e}") from e
    raise NotImplementedError("write_output_file() non implémenté")
