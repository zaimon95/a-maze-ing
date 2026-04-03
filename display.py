"""
display.py — Interactive terminal display of the maze.

RESPONSIBLE: Otto
TASK: Display the maze in colour ASCII in the terminal,
      with an interactive menu allowing:
      1. Regenerate a new maze
      2. Show/hide the solution path
      3. Change the wall colour
      4. Quit

=== ASCII RENDERING TECHNIQUE ===

Each cell is represented over 2 lines and 2 columns of characters:
- The "top-left" of cell (x,y) in ASCII space is at (2*x, 2*y).
- We first draw a grid of '+' at intersections,
  then add horizontal walls ('---') and vertical walls ('|').

Example for a 3x2 grid (width=3, height=2):
  +--+--+--+
  |        |
  +  +--+  +
  |        |
  +--+--+--+

=== ANSI COLOUR CODES ===
To colour the terminal, use ANSI codes:
  \\033[XXm  where XX is a colour code.
  \\033[0m   = reset
  \\033[31m  = red
  \\033[32m  = green
  \\033[33m  = yellow
  \\033[34m  = blue
  \\033[37m  = white
  \\033[1m   = bold

For background colours:
  \\033[41m  = red background
  \\033[42m  = green background
  \\033[44m  = blue background
  \\033[47m  = white/grey background
"""

# ============================================================
# IMPORTS
# ============================================================
from typing import TYPE_CHECKING, List, Tuple
import os
if TYPE_CHECKING:
    from mazegen_src.maze_generator import MazeGenerator

# Direction bit constants (duplicated here to avoid circular imports)
NORTH: int = 0b0001
EAST:  int = 0b0010
SOUTH: int = 0b0100
WEST:  int = 0b1000

# ============================================================
# AVAILABLE COLOUR PALETTES
# ============================================================
# Each palette = (wall_colour, path_colour, entry_colour, exit_colour)
COLOR_PALETTES = [
    # (wall_code, path_code, entry_code, exit_code, name)
    ("\033[37m", "\033[36m", "\033[35m", "\033[31m", "Default (white/cyan)"),
    ("\033[33m", "\033[36m", "\033[35m", "\033[31m", "Yellow/cyan"),
    ("\033[32m", "\033[34m", "\033[35m", "\033[31m", "Green/blue"),
    ("\033[34m", "\033[33m", "\033[35m", "\033[31m", "Blue/yellow"),
]
RESET = "\033[0m"


# ============================================================
# MAIN INTERACTIVE DISPLAY FUNCTION
# ============================================================

def display_maze_terminal(generator: "MazeGenerator") -> None:
    """
    Launches the interactive maze display in the terminal.

    Main loop:
    1. Render the maze in ASCII and display it.
    2. Show the menu: 1. Regen | 2. Path | 3. Colour | 4. Quit
    3. Read the user's choice.
    4. Perform the corresponding action.
    5. Repeat.

    Args:
        generator: MazeGenerator instance after generate() has been called.

    """
    show_path: bool = False
    palette_idx: int = 0

    while True:
        os.system("clear")

        lines = render_maze(generator, show_path=show_path,
                            palette_idx=palette_idx)
        print("\n".join(lines))

        print("\n==== A-Maze-ing ====")
        print("1. Regenerate a new maze")
        print("2. Show/Hide solution path")
        print("3. Change wall colour")
        print("4. Quit")
        choice = input("Choice (1-4): ").strip()

        if choice == "1":
            generator.generate()
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            palette_idx = (palette_idx + 1) % len(COLOR_PALETTES)
        elif choice == "4":
            break
        else:
            input("Invalid choice. Press Enter to continue...")


def render_maze(
    generator: "MazeGenerator",
    show_path: bool = False,
    palette_idx: int = 0,
) -> List[str]:
    """
    Renders the maze visually and sets its visual value for the output.
    """
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
    """
    Builds the list of (x, y) cells along the solution path.
    """
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