from mazegen_src.maze_generator import MazeGenerator
import sys
from config_parser import parse_config
from output_writer import write_output_file
from display import display_maze_terminal


def main(config_path: str) -> None:
    config = parse_config(config_path)
    generator = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit_pos=config.exit_pos,
        perfect=config.perfect,
        seed=config.seed,
    )
    generator.generate()
    write_output_file(generator, config_path)
    display_maze_terminal(generator)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    main(sys.argv[1])
