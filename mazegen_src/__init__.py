"""
mazegen — Reusable maze generation package.

Usage:
    from mazegen_src.maze_generator import MazeGenerator

    gen = MazeGenerator(width=20, height=15, entry=(0, 0),
                        exit_pos=(19, 14), perfect=True, seed=42)
    gen.generate()
    print(gen.solution)      # "SSEEENNN..."
    print(gen.get_cell(0,0)) # 4-bit integer
"""