"""
config_parser.py — Lecture et validation du fichier de configuration.

RESPONSABLE: Otto
TÂCHE: Parser le fichier config.txt, valider les valeurs, retourner un objet MazeConfig.
"""

# ============================================================
# IMPORTS
# ============================================================
from dataclasses import dataclass
from typing import Optional, Tuple
import os

# ============================================================
# DATACLASS DE CONFIGURATION
# ============================================================


@dataclass
class MazeConfig:

    width: int = 0
    height: int = 0
    entry: Tuple[int, int] = (0, 0)
    exit_pos: Tuple[int, int] = (0, 0)
    output_file: str = "maze.txt"
    perfect: bool = True
    seed: Optional[int] = None
    algorithm: str = "dfs"


# ============================================================
# FONCTION PRINCIPALE DE PARSING
# ============================================================

def parse_config(path: str) -> MazeConfig:

    """
    Main function for the parsing which opens the config.txt file and calls the
    necessary tools to return the config
    """
    raw: dict[str, str] = {}

    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found: {path}")
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(f"Invalid config line: '{line}': Missing '='")
                key, value = line.split("=", 1)
                raw[key.strip()] = value.strip()

        mandatory = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
        for m in mandatory:
            if m not in raw:
                raise ValueError(f"Missing mandatory configurations key: {m}")

        config = _build_config(raw)
        _validate_config(config)
        return (config)
    except Exception as e:
        print(f"[ERROR] {e}")


def _build_config(raw: dict) -> MazeConfig:
    """
    This function initiates and configures all the neccesary key values to manipulate
    """
    width = int(raw["WIDTH"])
    height = int(raw["HEIGHT"])
    entry = _parse_coords(raw["ENTRY"], "ENTRY")
    exit_pos = _parse_coords(raw["EXIT"], "EXIT")
    output_file = str(raw["OUTPUT_FILE"])
    perfect = raw["PERFECT"].lower() == "true"
    seed = raw.get("SEED", None)
    algorithm = raw.get("ALGORITHM", "dfs")
    if seed is None or seed == "":
        return MazeConfig(
            width=width,
            height=height,
            entry=entry,
            exit_pos=exit_pos,
            output_file=output_file,
            perfect=perfect,
            algorithm=algorithm
        )

    elif seed is not None:
        seed = int(seed)
    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit_pos=exit_pos,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
        algorithm=algorithm
    )


def _validate_config(config: MazeConfig) -> None:
    """
    Validates my config whith exceptions
    """
    try:
        ex, ey = config.entry
        xx, xy = config.exit_pos
        if config.width < 2 or config.height < 2:
            raise ValueError(f"{config} doesn't meet minimum requirements - expected x and y >= 2")
        if config.entry == config.exit_pos:
            raise ValueError(f"{config} cannot be in the same position")
        if ex < 0 or ex > config.width - 1:
            raise ValueError("ENTRY WIDTH is out of bounds")
        if ey < 0 or ey > config.height - 1:
            raise ValueError("ENTRY HEIGHT is out of bounds")
        if xx < 0 or xx > config.width - 1:
            raise ValueError("EXIT WIDTH is out of bounds")
        if xy < 0 or xy > config.height - 1:
            raise ValueError("EXIT HEIGHT is out of bounds")
        if ex != 0 and ex != config.width - 1 and ey != 0 and ey != config.height - 1:
            raise ValueError("ENTRY position is not on borders")
        if xx != 0 and xx != config.width - 1 and xy != 0 and xy != config.height - 1:
            raise ValueError("EXIT position is not on borders")
    except ValueError as e:
        print(e)


def _parse_coords(value: str, label: str) -> Tuple[int, int]:
    """
    Parses the coordinates and checks its value to return valid values
    """
    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError(f"'{label}' has invalid format '{value}' - expected 'x,y'")
    try:
        x = int(parts[0])
        y = int(parts[1])
        return (x, y)

    except ValueError:
        raise ValueError(
            f"'{label}' contains non-integer values: '{value}'"
        )
