import argparse
import math
import gmsh
import yaml
from pathlib import Path
from mesh_generators.branching_elements_generator import BranchingElementsGenerator


def parse_args():
    parser = argparse.ArgumentParser(
        description="Генератор ветвящихся элементов и сетки с использованием Gmsh"
    )
    parser.add_argument("--config", type=str, default="branch_element_4_4_2.yml", help="Путь к конфигурационному файлу (.json или .yaml)")

    parser.add_argument("--r-root", type=float, help="Радиус корневого элемента")
    parser.add_argument("--h-root", type=float, help="Высота корневого элемента")
    parser.add_argument("--r-branch", type=float, help="Радиус ветвей")
    parser.add_argument("--h-branch", type=float, help="Высота ветвей")
    parser.add_argument("--num-branches", type=int, help="Количество ветвей")
    parser.add_argument("--angle", type=float, help="Угол между ветвями в градусах")
    parser.add_argument("--num-x", type=int, help="Количество элементов в сетке по оси x")
    parser.add_argument("--num-y", type=int, help="Количество элементов в сетке по оси y")
    parser.add_argument("--num-z", type=int, help="Количество элементов в сетке по оси z")
    parser.add_argument("--mesh-size", type=float, help="Размер элементов сетки")
    parser.add_argument("--output", type=str, help="Имя выходного .msh файла")
    parser.add_argument("--no-gui", type=bool, help="Не запускать GUI визуализации Gmsh")
    parser.add_argument("--debug", type=bool, help="Debug режим, в котором строятся дополнительные копии сетки рядом с оригинальной")
    return parser.parse_args()

def load_config(path: str) -> dict:
    path = Path(path)
    with open(path, "r") as f:
        if path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(f)
        else:
            raise ValueError("Неподдерживаемый формат конфигурационного файла (поддерживаются .json и .yaml)")

def merge_configs(file_config: dict, cli_args: argparse.Namespace) -> dict:
    merged = file_config.copy() if file_config else {}
    for key, value in vars(cli_args).items():
        if value is not None:
            merged[key] = value
    return merged

def main():
    args = parse_args()

    file_config = load_config(args.config) if args.config else {}
    config = merge_configs(file_config, args)

    gmsh.initialize()
    gmsh.model.add("branch_element")

    element_generator = BranchingElementsGenerator(
        config.get("r-root", 0.5),
        config.get("h-root", 4.0),
        config.get("r-branch", 0.4),
        config.get("h-branch", 3.0),
        config.get("num-branches", 4),
        config.get("num-x", 4),
        config.get("num-y", 5),
        config.get("num-z", 2)
    )

    min_size = 0.9 * config.get("mesh-size", 1.0)
    max_size = 1.1 * config.get("mesh-size", 1.0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", min_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", max_size)

    all_elements = element_generator.generate_volume()

    # DEBUG
    if config.get("debug", False):
        copies = gmsh.model.occ.copy(all_elements)
        gmsh.model.occ.translate(copies, 0, 0, 1.1)
        gmsh.model.occ.synchronize()

    gmsh.model.mesh.generate(3)
    filename = config.get("output")
    print(filename)
    gmsh.write(filename)

    if not config.get("no_gui"):
        gmsh.fltk.run()

    gmsh.finalize()


if __name__ == "__main__":
    main()
