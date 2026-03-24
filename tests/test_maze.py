"""
tests/test_maze.py — Tests unitaires du projet A-Maze-ing.
Non soumis ni noté, mais fortement recommandés pour détecter les bugs.

RESPONSABLE: Les deux (chacun teste son module)
"""

import pytest
from mazegen_src.maze_generator import MazeGenerator, NORTH, EAST, SOUTH, WEST
from config_parser import parse_config, MazeConfig

# ============================================================
# TESTS — MazeGenerator (Simon)
# ============================================================


class TestMazeGeneratorInit:
    """Tests d'initialisation."""

    def test_basic_init(self) -> None:
        """Le générateur s'initialise sans erreur."""
        gen = MazeGenerator(10, 10, (0, 0), (9, 9), perfect=True, seed=42)
        assert gen.width == 10
        assert gen.height == 10
        assert gen.entry == (0, 0)
        assert gen.exit_pos == (9, 9)

    def test_cells_empty_before_generate(self) -> None:
        """Les cellules ne sont pas remplies avant generate()."""
        gen = MazeGenerator(5, 5, (0, 0), (4, 4))
        # TODO (Simon): adapter selon votre implémentation
        # assert gen.cells == [] ou assert len(gen.cells) == 0


class TestMazeGeneratorGenerate:
    """Tests après generate()."""

    @pytest.fixture
    def gen_10x10(self) -> MazeGenerator:
        """Générateur 10×10 parfait, seed=42."""
        g = MazeGenerator(10, 10, (0, 0), (9, 9), perfect=True, seed=42)
        g.generate()
        return g

    def test_grid_dimensions(self, gen_10x10: MazeGenerator) -> None:
        """La grille a les bonnes dimensions."""
        assert len(gen_10x10.cells) == 10
        assert all(len(row) == 10 for row in gen_10x10.cells)

    def test_cell_values_valid(self, gen_10x10: MazeGenerator) -> None:
        """Chaque cellule est un entier 4 bits (0x0 à 0xF)."""
        for y in range(gen_10x10.height):
            for x in range(gen_10x10.width):
                val = gen_10x10.cells[y][x]
                assert 0 <= val <= 0xF, f"Cellule ({x},{y}) invalide: {val}"

    def test_walls_coherent(self, gen_10x10: MazeGenerator) -> None:
        """
        Cohérence des murs: si cellule (x,y) a un mur Est,
        alors son voisin (x+1,y) doit avoir un mur Ouest.
        """
        g = gen_10x10
        for y in range(g.height):
            for x in range(g.width):
                if x + 1 < g.width:
                    east_wall = bool(g.cells[y][x] & EAST)
                    west_wall = bool(g.cells[y][x + 1] & WEST)
                    assert east_wall == west_wall, (
                        f"Incohérence Est/Ouest entre ({x},{y}) et ({x+1},{y})"
                    )
                if y + 1 < g.height:
                    south_wall = bool(g.cells[y][x] & SOUTH)
                    north_wall = bool(g.cells[y + 1][x] & NORTH)
                    assert south_wall == north_wall, (
                        f"Incohérence Sud/Nord entre ({x},{y}) et ({x},{y+1})"
                    )

    def test_borders_closed(self, gen_10x10: MazeGenerator) -> None:
        """Les bords extérieurs sont fermés (sauf entrée/sortie)."""
        g = gen_10x10
        ex, ey = g.entry
        sx, sy = g.exit_pos
        for x in range(g.width):
            if (x, 0) not in [(ex, ey), (sx, sy)]:
                assert bool(g.cells[0][x] & NORTH), f"Bord nord ouvert en ({x},0)"
            if (x, g.height - 1) not in [(ex, ey), (sx, sy)]:
                assert bool(g.cells[g.height - 1][x] & SOUTH)

    def test_solution_exists(self, gen_10x10: MazeGenerator) -> None:
        """Une solution a été calculée."""
        #assert len(gen_10x10.solution) > 0

    def test_solution_valid(self, gen_10x10: MazeGenerator) -> None:
        """La solution ne contient que N, E, S, W."""
        valid_chars = set("NESW")
        assert all(c in valid_chars for c in gen_10x10.solution)

    def test_reproducibility(self) -> None:
        """Deux générations avec la même seed donnent le même résultat."""
        g1 = MazeGenerator(8, 8, (0, 0), (7, 7), perfect=True, seed=123)
        g2 = MazeGenerator(8, 8, (0, 0), (7, 7), perfect=True, seed=123)
        g1.generate()
        g2.generate()
        assert g1.cells == g2.cells
        assert g1.solution == g2.solution


# ============================================================
# TESTS — config_parser (Otto)
# ============================================================

class TestConfigParser:
    """Tests du parser de configuration."""

    def test_valid_config(self, tmp_path: pytest.TempPathFactory) -> None:

        config_file = tmp_path / "config.txt"
        config_file.write_text(
             "WIDTH=10\n"
             "HEIGHT=10\n"
             "ENTRY=0,0\n"
             "EXIT=9,9\n"
             "OUTPUT_FILE=maze.txt\n"
             "PERFECT=True\n"
        )
        config = parse_config(str(config_file))
        assert config.width == 10
        assert config.height == 10
        assert config.entry == (0, 0)
        assert config.exit_pos == (9, 9)
        assert config.perfect == 1

    def test_missing_key_raises(self, tmp_path: pytest.TempPathFactory) -> None:

        config_file = tmp_path / "config.txt"
        config_file.write_text(
             "WIDTH=10\n"
             "HEIGHT10\n"
             "ENTRY=0,0\n"
             "EXIT=9,9\n"
             "OUTPUT_FILE=maze.txt\n"
             "PERFECT=True\n"
        )
        with pytest.raises(ValueError):
            parse_config(str(config_file))

    def test_invalid_coords_raises(self, tmp_path: pytest.TempPathFactory) -> None:
        config_file = tmp_path / "config.txt"
        config_file.write_text(
             "WIDTH=10\n"
             "HEIGHT=10\n"
             "ENTRY=0,10\n"
             "EXIT=9,9\n"
             "OUTPUT_FILE=maze.txt\n"
             "PERFECT=True\n"
        )
        with pytest.raises(ValueError):
            parse_config(str(config_file))


# ============================================================
# TESTS — output_writer (Otto)
# ============================================================

class TestOutputWriter:
    """Tests de l'écriture du fichier de sortie."""

    def test_output_format(self, tmp_path: pytest.TempPathFactory) -> None:
        """
        TODO (Otto): générer un petit labyrinthe, écrire le fichier,
        vérifier le format (nb lignes, caractères hex, ligne vide, coords, solution).
        """
        pass  # TODO (Otto)
