"""
A-Maze-ing: Entry point du programme.
Usage: python3 a_maze_ing.py config.txt

RESPONSABLE: Otto
TÂCHE: Relier tous les modules ensemble, gérer le flux principal.
"""

# ============================================================
# IMPORTS - ajouter les imports nécessaires au fur et à mesure
# ============================================================
import sys
from typing import Optional

# TODO (Otto): importer les modules une fois créés:
# from config_parser import parse_config, MazeConfig
# from mazegen_src.maze_generator import MazeGenerator
# from output_writer import write_output_file
# from display import display_maze_terminal


def main(config_path: str) -> None:
    """
    Point d'entrée principal du programme.

    Args:
        config_path: Chemin vers le fichier de configuration.

    TODO (Otto):
    1. Appeler parse_config(config_path) → obtenir un objet MazeConfig
    2. Instancier MazeGenerator avec les paramètres de config
    3. Appeler generator.generate() pour générer le labyrinthe
    4. Appeler write_output_file(generator, config) pour écrire le fichier de sortie
    5. Appeler display_maze_terminal(generator, config) pour l'affichage interactif
    6. Gérer toutes les exceptions avec des messages clairs (pas de crash)
    """
    # TODO (Otto): implémenter le flux principal ici
    # Exemple de structure:
    # try:
    #     config = parse_config(config_path)
    #     generator = MazeGenerator(
    #         width=config.width,
    #         height=config.height,
    #         entry=config.entry,
    #         exit=config.exit_pos,
    #         perfect=config.perfect,
    #         seed=config.seed,
    #     )
    #     generator.generate()
    #     write_output_file(generator, config.output_file)
    #     display_maze_terminal(generator)
    # except FileNotFoundError:
    #     print(f"Error: config file '{config_path}' not found.")
    #     sys.exit(1)
    # except ValueError as e:
    #     print(f"Error: {e}")
    #     sys.exit(1)
    print("TODO: implémenter main()")


if __name__ == "__main__":
    # TODO (Otto): vérifier qu'exactement 1 argument est passé
    # Afficher un message d'usage clair si ce n'est pas le cas
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    main(sys.argv[1])
