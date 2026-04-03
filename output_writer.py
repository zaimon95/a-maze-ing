"""
output_writer.py — Writing the output file in hexadecimal format.

RESPONSIBLE: Otto
TASK: Write the maze to a text file according to the spec format.

=== OUTPUT FILE FORMAT ===

Lines 1 to HEIGHT:  one line per row, each cell encoded as 1 hex digit (uppercase).
Line HEIGHT+1:      blank line
Line HEIGHT+2:      entry coordinates "x,y"
Line HEIGHT+3:      exit coordinates "x,y"
Line HEIGHT+4:      solution path "NNEESSSWW..."

All lines end with \\n.
"""

# ============================================================
# IMPORTS
# ============================================================
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mazegen_src.maze_generator import MazeGenerator


def write_output_file(generator: "MazeGenerator", output_path: str) -> None:
    """
    Writes the maze grid, entry/exit coordinates and solution path to the output file.
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