"""
config_parser.py — Lecture et validation du fichier de configuration.

RESPONSABLE: Otto
TÂCHE: Parser le fichier config.txt, valider les valeurs, retourner un objet MazeConfig.
"""

# ============================================================
# IMPORTS
# ============================================================
from dataclasses import dataclass, field
from typing import Optional, Tuple
import os


# ============================================================
# DATACLASS DE CONFIGURATION
# ============================================================

@dataclass
class MazeConfig:
    """
    Représente la configuration complète du labyrinthe.

    Attributes:
        width:       Nombre de colonnes du labyrinthe.
        height:      Nombre de lignes du labyrinthe.
        entry:       Coordonnées (x, y) de l'entrée.
        exit_pos:    Coordonnées (x, y) de la sortie.
        output_file: Nom du fichier de sortie.
        perfect:     True = labyrinthe parfait (un seul chemin entrée→sortie).
        seed:        Graine aléatoire pour la reproductibilité (optionnel).
        algorithm:   Algorithme de génération (optionnel, ex: "dfs", "prim").
    """
    width: int = 0
    height: int = 0
    entry: Tuple[int, int] = (0, 0)
    exit_pos: Tuple[int, int] = (0, 0)
    output_file: str = "maze.txt"
    perfect: bool = True
    seed: Optional[int] = None
    algorithm: str = "dfs"  # valeur par défaut

    # TODO (Otto): ajouter d'autres champs optionnels si besoin
    # ex: display_mode: str = "terminal"


# ============================================================
# FONCTION PRINCIPALE DE PARSING
# ============================================================

def parse_config(path: str) -> MazeConfig:
    """
    Lit et valide un fichier de configuration KEY=VALUE.

    Args:
        path: Chemin vers le fichier de configuration.

    Returns:
        Un objet MazeConfig rempli et validé.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
        ValueError: Si une clé obligatoire est manquante ou invalide.

    TODO (Otto):
    1. Ouvrir le fichier avec un context manager (with open(...))
    2. Ignorer les lignes vides et les lignes commençant par '#'
    3. Splitter chaque ligne sur '=' (max 1 split) → clé / valeur
    4. Remplir un dict, puis construire un MazeConfig
    5. Appeler _validate_config() à la fin
    """
    # TODO (Otto): implémenter le parsing ligne par ligne
    # Exemple de squelette:
    # raw: dict[str, str] = {}
    # with open(path, "r") as f:
    #     for line in f:
    #         line = line.strip()
    #         if not line or line.startswith("#"):
    #             continue
    #         if "=" not in line:
    #             raise ValueError(f"Invalid config line: '{line}'")
    #         key, value = line.split("=", 1)
    #         raw[key.strip().upper()] = value.strip()
    # return _build_config(raw)
    raise NotImplementedError("parse_config() non implémenté")


def _build_config(raw: dict) -> MazeConfig:
    """
    Construit un MazeConfig depuis un dictionnaire brut KEY→VALUE (strings).

    Args:
        raw: Dictionnaire des paires clé/valeur lues du fichier.

    Returns:
        MazeConfig validé.

    Raises:
        ValueError: Si une clé obligatoire est absente ou a un type invalide.

    TODO (Otto):
    - Vérifier les clés obligatoires: WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT
    - Convertir WIDTH et HEIGHT en int (lever ValueError si non-entier ou ≤ 0)
    - Parser ENTRY et EXIT comme "x,y" → Tuple[int, int]
    - Parser PERFECT comme "True"/"False" (case-insensitive)
    - Parser SEED si présent → int ou None
    """
    # TODO (Otto): implémenter _build_config
    raise NotImplementedError("_build_config() non implémenté")


def _validate_config(config: MazeConfig) -> None:
    """
    Vérifie la cohérence logique de la configuration.

    Raises:
        ValueError: Si une contrainte métier est violée.

    TODO (Otto): vérifier:
    - width >= 2 et height >= 2 (minimum pour avoir un labyrinthe)
    - entry != exit_pos
    - entry et exit_pos dans les bornes [0, width-1] x [0, height-1]
    - L'entrée et la sortie sont bien sur le bord extérieur du labyrinthe
      (car des murs extérieurs doivent exister : x==0 ou x==width-1 ou y==0 ou y==height-1)
    """
    # TODO (Otto): implémenter les vérifications
    pass


def _parse_coords(value: str, label: str) -> Tuple[int, int]:
    """
    Parse une chaîne "x,y" en Tuple[int, int].

    Args:
        value: Chaîne du style "3,7".
        label: Nom de la clé (pour les messages d'erreur).

    Returns:
        Tuple (x, y).

    Raises:
        ValueError: Si le format est invalide.

    TODO (Otto): split sur ',', convertir en int, gérer les erreurs proprement.
    """
    # TODO (Otto): implémenter _parse_coords
    raise NotImplementedError("_parse_coords() non implémenté")
