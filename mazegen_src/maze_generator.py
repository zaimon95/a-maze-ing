"""
maze_generator.py — Project core: maze generation.

=== DFS ALGORITHM OVERVIEW (Recursive Backtracker) ===

1. Initialise all cells with ALL walls closed.
2. Choose a random starting cell → mark it visited.
3. While unvisited cells remain:
   a. From the current cell, randomly pick an unvisited neighbour.
   b. Knock down the wall between the current cell and that neighbour.
   c. Move to that neighbour (mark it visited).
   d. If no unvisited neighbour exists → backtrack to the previous cell.
4. Result: a perfect maze (spanning tree of the grid graph).

=== WALL ENCODING ===
Each cell is a 4-bit integer:
  Bit 0 (LSB) = North  (1 = wall closed, 0 = wall open)
  Bit 1       = East
  Bit 2       = South
  Bit 3       = West

Example: 0xF = 1111 = all walls closed
         0x0 = 0000 = no walls (cell fully open)
         0x3 = 0011 = North and East walls closed

=== DIRECTIONS ===
North: dy=-1, dx=0  → bit 0 of current cell, bit 2 of neighbour (South)
East:  dy=0,  dx=1  → bit 1 of current cell, bit 3 of neighbour (West)
South: dy=1,  dx=0  → bit 2 of current cell, bit 0 of neighbour (North)
West:  dy=0,  dx=-1 → bit 3 of current cell, bit 1 of neighbour (East)
"""

# ============================================================
# IMPORTS
# ============================================================
import random
from typing import List, Tuple, Optional
from collections import deque


# ============================================================
# CONSTANTS — direction bits
# ============================================================
NORTH: int = 0b0001  # bit 0
EAST:  int = 0b0010  # bit 1
SOUTH: int = 0b0100  # bit 2
WEST:  int = 0b1000  # bit 3

# Direction mapping → (dx, dy, opposite_bit)
# To knock down a wall between two cells, we must
# clear the bit on the current cell AND the opposite bit on the neighbour.
DIRECTIONS: List[Tuple[int, int, int, int]] = [
    # (dx, dy, current_bit, opposite_neighbour_bit)
    (0,  -1, NORTH, SOUTH),
    (1,   0, EAST,  WEST),
    (0,   1, SOUTH, NORTH),
    (-1,  0, WEST,  EAST),
]


# ============================================================
# MAIN CLASS
# ============================================================

class MazeGenerator:
    """
    Generates a maze on a width×height grid.

    The maze is stored as a 2D list of integers (cells),
    where each integer encodes the closed walls of a cell via 4 bits.

    Attributes:
        width:    Number of columns.
        height:   Number of rows.
        entry:    Coordinates (x, y) of the entry point.
        exit_pos: Coordinates (x, y) of the exit point.
        perfect:  If True, generates a perfect maze (pure DFS).
        seed:     Random seed for reproducibility.
        cells:    Grid [y][x] → 4-bit integer encoding the walls.
        solution: Solution path as a string "NNEESS..."
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_pos: Tuple[int, int],
        perfect: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        """
        Initialises the generator without yet generating the maze.

        Args:
            width:    Number of columns (≥ 2).
            height:   Number of rows (≥ 2).
            entry:    Coordinates (x, y) of the entry point.
            exit_pos: Coordinates (x, y) of the exit point.
            perfect:  If True, the maze will be perfect.
            seed:     Seed for random.seed() (reproducibility).
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
        self.perfect = perfect
        self.seed = seed
        # Wall grid: initialised in generate()
        # self.cells[y][x] = 4-bit integer
        self.cells: List[List[int]] = []
        self.solution: str = ""

    # ----------------------------------------------------------
    # MAIN METHOD
    # ----------------------------------------------------------

    def generate(self) -> None:
        """
        Generates the complete maze.

        Steps:
        1. _init_cells()       → all cells with 4 closed walls (0xF)
        2. _carve_passages()   → DFS algorithm to open passages
        3. _apply_42_pattern() → carve the "42" pattern (fully closed cells)
        4. _open_entry_exit()  → open the entry and exit on the border
        5. _enforce_borders()  → ensure outer borders are properly closed
        6. _solve()            → compute the shortest path (BFS)

        If not perfect → also call _add_loops() after _carve_passages()
        to create additional paths (cycles).

        """
        if self.seed is not None:
            random.seed(self.seed)
        self._init_cells()
        self._carve_passages()
        if not self.perfect:
            self._add_loops()
        self._apply_42_pattern()
        self._open_entry_exit()
        self._enforce_borders()
        self._solve()

    # ----------------------------------------------------------
    # INITIALISATION
    # ----------------------------------------------------------

    def _init_cells(self) -> None:
        """
        Creates the grid with all cells closed (all walls set to 1).

        Result: self.cells[y][x] = 0xF for all (x, y).

        Example: [[0xF] * width for _ in range(height)]
        """
        self.cells = [[0xF] * self.width for _ in range(self.height)]

    # ----------------------------------------------------------
    # GENERATION ALGORITHM — DFS Recursive Backtracker
    # ----------------------------------------------------------

    def _carve_passages(self) -> None:
        """
        Generates the maze using iterative DFS (avoids deep Python recursion).

        Algorithm (iterative version with stack):
        1. Initialise a visited[y][x] = False array.
        2. Choose a starting cell (e.g. entry or (0,0)).
        3. Push the starting cell onto the stack, mark it visited.
        4. While the stack is not empty:
           a. Look at the cell on top of the stack.
           b. Find its unvisited neighbours in the grid.
           c. If any exist → pick one at random, knock down the wall, push it.
           d. Otherwise → pop (backtrack).

        To knock down the wall between (x, y) and (nx, ny):
          self.cells[y][x]   &= ~current_bit   (clear the direction bit)
          self.cells[ny][nx] &= ~opposite_bit   (clear the opposite bit on the neighbour)
        """
        self._init_cells()

        visited: list[list[bool]] = [[False] * self.width for _ in range(self.height)]

        # Pre-compute the "42" pattern cells and mark them visited
        # → DFS will never touch them
        for x, y in self._get_42_cells():
            if 0 <= x < self.width and 0 <= y < self.height:
                visited[y][x] = True  # block these cells

        stack: list[tuple[int, int]] = [self.entry]
        visited[self.entry[1]][self.entry[0]] = True

        while stack:
            x, y = stack[-1]
            neighbors: list[tuple[int, int, int, int]] = [
                (x + dx, y + dy, bit, opp)
                for dx, dy, bit, opp in DIRECTIONS
                if 0 <= x + dx < self.width
                and 0 <= y + dy < self.height
                and not visited[y + dy][x + dx]
            ]
            if neighbors and self._check_open_area(x, y):
                nx, ny, bit, opp = random.choice(neighbors)
                self.cells[y][x] &= ~bit
                self.cells[ny][nx] &= ~opp
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def _add_loops(self) -> None:
        """
        Adds loops to the maze to make it imperfect.

        After a pure DFS, all passages are already opened optimally.
        To create an imperfect maze, we randomly knock down some additional walls
        (approximately 10–20% of remaining walls).
        """
        cells_42: set[tuple[int, int]] = self._get_42_cells()

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in cells_42:
                    continue

                for dx, dy, bit, opp in DIRECTIONS:
                    nx, ny = x + dx, y + dy

                    # Skip outer borders
                    if not (0 <= nx < self.width and 0 <= ny < self.height):
                        continue

                    # Skip if wall is already open
                    if not (self.cells[y][x] & bit):
                        continue

                    # Skip cells belonging to the "42" pattern
                    if (nx, ny) in cells_42:
                        continue

                    # ~15% chance to knock down this wall
                    if random.random() < 0.1 and self._check_open_area(x, y):
                        self.cells[y][x] &= ~bit
                        self.cells[ny][nx] &= ~opp

    def _check_open_area(self, x: int, y: int) -> bool:
        """
        Checks whether knocking down a wall at (x, y) would create an open area > 2×2.

        Returns:
            True if safe (no 3×3 open area), False otherwise.
        """
        for ox in range(-2, 1):
            for oy in range(-2, 1):
                bx, by = x + ox, y + oy
                if not (0 <= bx and bx + 2 < self.width
                        and 0 <= by and by + 2 < self.height):
                    continue
                open_area = True
                for cy in range(by, by + 3):
                    for cx in range(bx, bx + 3):
                        if cx < bx + 2 and (self.cells[cy][cx] & EAST):
                            open_area = False
                        if cy < by + 2 and (self.cells[cy][cx] & SOUTH):
                            open_area = False

                if open_area:
                    return False
        return True

    # ----------------------------------------------------------
    # "42" PATTERN
    # ----------------------------------------------------------

    def _get_42_cells(self) -> set[tuple[int, int]]:
        pat_four: list[tuple[int, int]] = [
            (0, 0), (0, 1), (0, 2),
            (1, 2), (2, 2),
            (2, 3), (2, 4),
        ]
        pat_two: list[tuple[int, int]] = [
            (4, 0), (5, 0), (6, 0),
            (6, 1),
            (6, 2), (5, 2), (4, 2),
            (4, 3),
            (4, 4), (5, 4), (6, 4),
        ]
        origin_x: int = (self.width - 7) // 2
        origin_y: int = (self.height - 5) // 2

        cells: set[tuple[int, int]] = set()
        for dx, dy in pat_four + pat_two:
            cells.add((origin_x + dx, origin_y + dy))

        cells.discard(self.entry)
        cells.discard(self.exit_pos)
        return cells

    def _apply_42_pattern(self) -> None:
        """
        Carves the "42" pattern into the maze as fully closed cells.

        The pattern must be visible in the graphical display: a group of cells
        with all walls closed (value 0xF) forms the digits "4" and "2".

        Constraints:
        - The "42" pattern cells are islands (all walls = 0xF).
        - They may break connectivity → this is accepted per the spec.
        - If the maze is too small (< ~15×10), print a warning
          and skip applying the pattern.
        """
        if self.width < 15 or self.height < 10:
            print("Warning: maze too small to display '42' pattern.")
            return

        for x, y in self._get_42_cells():
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            self.cells[y][x] = 0xF
            for dx, dy, bit, opp in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.cells[ny][nx] |= opp

    # ----------------------------------------------------------
    # ENTRY / EXIT AND BORDERS
    # ----------------------------------------------------------

    def _open_entry_exit(self) -> None:
        """
        Opens the outer wall at the entry and exit of the maze.

        The entry and exit are cells on the border.
        We identify which outer wall to open:
        - If x == 0         → open the West wall  (clear WEST bit)
        - If x == width-1   → open the East wall   (clear EAST bit)
        - If y == 0         → open the North wall  (clear NORTH bit)
        - If y == height-1  → open the South wall  (clear SOUTH bit)

        """
        for x, y in (self.entry, self.exit_pos):
            if x == 0:
                self.cells[y][x] &= ~WEST
            elif x == self.width - 1:
                self.cells[y][x] &= ~EAST
            elif y == 0:
                self.cells[y][x] &= ~NORTH
            elif y == self.height - 1:
                self.cells[y][x] &= ~SOUTH

    def _enforce_borders(self) -> None:
        """
        Ensures all border cells have their outer walls closed,
        EXCEPT the entry and exit cells which have been opened.

        Iterates over the 4 borders and closes outer walls:
        - Row y=0         → NORTH bit must be 1 for all cells except entry/exit
        - Row y=height-1  → SOUTH bit must be 1
        - Col x=0         → WEST bit must be 1
        - Col x=width-1   → EAST bit must be 1

        """
        exceptions: set[tuple[int, int]] = {self.entry, self.exit_pos}

        for x in range(self.width):
            if (x, 0) not in exceptions:
                self.cells[0][x] |= NORTH
            if (x, self.height - 1) not in exceptions:
                self.cells[self.height - 1][x] |= SOUTH

        for y in range(self.height):
            if (0, y) not in exceptions:
                self.cells[y][0] |= WEST
            if (self.width - 1, y) not in exceptions:
                self.cells[y][self.width - 1] |= EAST

    # ----------------------------------------------------------
    # SOLVER — BFS
    # ----------------------------------------------------------

    def _solve(self) -> None:
        """
        Computes the shortest path between entry and exit_pos using BFS.

        Result stored in self.solution as a string
        of letters N, E, S, W (e.g. "SSEEENNNEE").

        BFS algorithm:
        1. Queue initialised with (entry_x, entry_y, path="").
        2. Visited set to avoid revisiting cells.
        3. For each dequeued cell, try all 4 directions:
           - Check that the wall in that direction is OPEN (bit = 0).
           - Check that the neighbour is in the grid and not visited.
           - Enqueue the neighbour with the updated path.
        4. When exit_pos is reached → store the path in self.solution.
        """
        letter: dict[int, str] = {NORTH: 'N', EAST: 'E', SOUTH: 'S', WEST: 'W'}
        visited: list[list[bool]] = [[False] * self.width for _ in range(self.height)]

        queue: deque[tuple[int, int, str]] = deque()
        queue.append((self.entry[0], self.entry[1], ""))
        visited[self.entry[1]][self.entry[0]] = True
        while queue:
            x, y, path = queue.popleft()
            if (x, y) == self.exit_pos:
                self.solution = path
                return
            for dx, dy, bit, _ in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if not (self.cells[y][x] & bit) \
                        and 0 <= nx < self.width \
                        and 0 <= ny < self.height \
                        and not visited[ny][nx]:
                    visited[ny][nx] = True
                    queue.append((nx, ny, path + letter[bit]))

    # ----------------------------------------------------------
    # PUBLIC ACCESSORS (for the reusable module)
    # ----------------------------------------------------------

    def get_cell(self, x: int, y: int) -> int:
        """
        Returns the value of cell (x, y).

        Args:
            x: Column (0 to width-1).
            y: Row    (0 to height-1).

        Returns:
            4-bit integer encoding the closed walls.
        """
        return self.cells[y][x]

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        """
        Indicates whether cell (x, y) has a closed wall in the given direction.

        Args:
            x:         Column.
            y:         Row.
            direction: NORTH, EAST, SOUTH or WEST.

        Returns:
            True if the wall is closed, False if open.
        """
        return bool(self.cells[y][x] & direction)

    def get_solution(self) -> str:
        """Returns the solution path as a string 'NNEESS...'."""
        return self.solution

    def to_hex_grid(self) -> List[List[str]]:
        """
        Returns the grid as a 2D list of hexadecimal characters.

        Returns:
            List [y][x] of uppercase hex strings (e.g. "F", "A", "3").

        Useful for writing the output file.
        """
        return [
            [format(self.cells[y][x], 'X') for x in range(self.width)]
            for y in range(self.height)
        ]