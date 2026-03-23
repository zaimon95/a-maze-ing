# A-Maze-ing

*This project has been created as part of the 42 curriculum by Otto, Simon.*

---

## Description

**A-Maze-ing** is a maze generator written in Python 3.10+. It reads a configuration file, generates a maze (optionally perfect — meaning exactly one path exists between any two cells), and writes the result to a file using a hexadecimal wall encoding. The maze can also be visualised interactively in the terminal with ASCII rendering and ANSI colours.

Key features:
- Random maze generation with seed-based reproducibility
- Perfect maze mode (single path from entry to exit) via DFS/Recursive Backtracker
- Imperfect maze mode (multiple paths) via loop injection
- Hexadecimal output file with solution path
- Interactive terminal display: regenerate, show/hide path, change colours
- Embedded "42" pattern drawn by fully-closed cells
- Reusable `MazeGenerator` class packaged as a pip-installable wheel (`mazegen`)

---

## Instructions

### Requirements

- Python 3.10 or later
- `pip` or `uv`

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd a_maze_ing

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
make install
```

### Running the program

```bash
make run
# equivalent to: python3 a_maze_ing.py config.txt
```

Or with a custom config file:

```bash
python3 a_maze_ing.py my_config.txt
```

### Debug mode

```bash
make debug
```

### Linting (mandatory)

```bash
make lint         # flake8 + mypy with required flags
make lint-strict  # mypy --strict (optional but recommended)
```

### Running tests

```bash
pytest tests/ -v
```

### Cleaning build artefacts

```bash
make clean
```

---

## Configuration file format

The configuration file uses one `KEY=VALUE` pair per line. Lines starting with `#` are comments.

| Key | Type | Required | Description | Example |
|-----|------|----------|-------------|---------|
| `WIDTH` | int | ✅ | Number of columns (≥ 2) | `WIDTH=20` |
| `HEIGHT` | int | ✅ | Number of rows (≥ 2) | `HEIGHT=15` |
| `ENTRY` | x,y | ✅ | Entry coordinates (on the border) | `ENTRY=0,0` |
| `EXIT` | x,y | ✅ | Exit coordinates (on the border) | `EXIT=19,14` |
| `OUTPUT_FILE` | string | ✅ | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | bool | ✅ | Perfect maze (single path)? | `PERFECT=True` |
| `SEED` | int | ➖ | Random seed for reproducibility | `SEED=42` |
| `ALGORITHM` | string | ➖ | Generation algorithm: `dfs` | `ALGORITHM=dfs` |

**Example config file:**

```
# My maze configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=dfs
```

---

## Maze generation algorithm

We chose the **Recursive Backtracker (DFS)** algorithm.

### How it works

1. Initialise all cells with all 4 walls closed (value `0xF`).
2. Pick a starting cell, push it onto a stack, mark it visited.
3. While the stack is not empty:
   - Look at the top cell.
   - If it has unvisited neighbours → pick one at random, remove the wall between them, push the neighbour.
   - Otherwise → pop (backtrack).
4. Result: a **perfect maze** (spanning tree of the grid graph).

For **imperfect mazes** (`PERFECT=False`), a post-processing step randomly removes ~15% of remaining walls, introducing cycles.

### Why DFS?

- Simple to implement iteratively (no recursion limit issues).
- Produces long, winding corridors — aesthetically interesting.
- Naturally generates perfect mazes (spanning tree property).
- Well-documented; easy to reason about correctness.
- Reproducible with a fixed seed.

Alternative considered: **Prim's algorithm** (produces mazes with shorter dead ends, more uniform texture). May be added as a bonus.

---

## Reusable module — `mazegen`

The maze generation logic is packaged as a standalone pip-installable wheel located at the root of the repository.

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

Or build from source:

```bash
make build-pkg
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

### Basic usage

```python
from mazegen_src.maze_generator import MazeGenerator

# Create and generate a 20×15 perfect maze with a fixed seed
gen = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_pos=(19, 14),
    perfect=True,
    seed=42,
)
gen.generate()

# Access the solution path (string of N/E/S/W letters)
print(gen.solution)          # e.g. "SSEEENNNEE..."

# Access the raw wall data for a cell
cell_value = gen.get_cell(3, 2)   # integer 0x0–0xF
print(cell_value)

# Check if a specific wall is closed
from mazegen_src.maze_generator import NORTH, EAST, SOUTH, WEST
print(gen.has_wall(0, 0, NORTH))  # True (border wall)

# Get the full grid as hex strings (for output file)
hex_grid = gen.to_hex_grid()      # List[List[str]], e.g. [['F','A',...], ...]
```

### Custom parameters

```python
# Imperfect maze (multiple paths), no seed (random each time)
gen = MazeGenerator(
    width=30,
    height=20,
    entry=(0, 10),
    exit_pos=(29, 10),
    perfect=False,
    seed=None,
)
gen.generate()
```

### Wall encoding (4-bit per cell)

| Bit | Direction | Value |
|-----|-----------|-------|
| 0 (LSB) | North | 1 |
| 1 | East | 2 |
| 2 | South | 4 |
| 3 (MSB) | West | 8 |

A wall bit set to `1` means the wall is **closed**; `0` means **open**.
Example: `0xA = 1010` → East and West walls closed, North and South open.

---

## Team and project management

### Roles

| Member | Responsibilities |
|--------|-----------------|
| **Otto** | Entry point (`a_maze_ing.py`), config parser, output writer, Makefile, pip packaging, README, mypy/flake8 compliance |
| **Simon** | `MazeGenerator` class (DFS, BFS solver, 42 pattern), terminal display with interactive menu and ANSI colours, unit tests for generation logic |

### Planning

**Initial plan:** Split infrastructure (Otto) from algorithm (Simon), with a mid-week integration point.

| Day | Milestone |
|-----|-----------|
| Monday | Repo setup, config parser, DFS skeleton, `_init_cells` |
| Tuesday | `output_writer`, BFS solver, border enforcement, `make run` produces `maze.txt` |
| Wednesday | 42 pattern, imperfect maze loops, full ASCII display |
| Thursday | `make lint` passes, README complete, pip wheel builds and installs |
| Friday | Cross-review, regression tests, final push, buffer for bonus |

**How it evolved:** *(to be filled in at the end of the project)*

### What worked well

*(to be filled in at the end of the project)*

### What could be improved

*(to be filled in at the end of the project)*

### Tools used

- **Python 3.10+** — main language
- **pytest** — unit testing
- **mypy** — static type checking
- **flake8** — code style enforcement
- **build / setuptools** — pip package generation
- **Claude (Anthropic)** — used as a productivity tool (see Resources)

---

## Resources

### Maze generation

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Think Labyrinth: Maze algorithms](http://www.astrolog.org/labyrnth/algrithm.htm) — comprehensive reference
- [Buckblog: Maze generation — Recursive backtracker](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Spanning trees and mazes — Computerphile (YouTube)](https://www.youtube.com/watch?v=cQVH4gcb3O4)

### Python / packaging

- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [flake8 documentation](https://flake8.pycqa.org/)

### How AI was used

Claude (Anthropic) was used as a **productivity and structuring tool**, not as a code generator:

- **Project structure:** Claude helped design the module split (config parser / generator / display / output writer) and produced a commented skeleton with `TODO` markers — no implementation was generated, only the scaffolding.
- **Synthesis document:** Claude generated the technical synthesis PDF summarising concepts (DFS, BFS, bit encoding) and the weekly milestone plan.
- **README template:** Claude generated this README skeleton which both team members then completed and adapted.
- **All algorithmic implementations** (DFS, BFS, wall encoding, 42 pattern, ASCII renderer) were written by Otto and Simon after studying the concepts, with peer review between them.
