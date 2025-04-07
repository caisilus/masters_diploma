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
    parser.add_argument("--config", type=str, default="branch_element.yml", help="Путь к конфигурационному файлу (.json или .yaml)")

    parser.add_argument("--r-root", type=float, help="Радиус корневого элемента")
    parser.add_argument("--h-root", type=float, help="Высота корневого элемента")
    parser.add_argument("--r-branch", type=float, help="Радиус ветвей")
    parser.add_argument("--h-branch", type=float, help="Высота ветвей")
    parser.add_argument("--num-branches", type=int, help="Количество ветвей")
    parser.add_argument("--angle", type=float, help="Угол между ветвями в градусах")
    parser.add_argument("--mesh-size", type=float, help="Размер элементов сетки")
    parser.add_argument("--output", type=str, default="branch_element.msh", help="Имя выходного .msh файла")
    parser.add_argument("--no-gui", action="store_true", help="Не запускать GUI визуализации Gmsh")
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

    angle_rad = math.radians(config.get("angle", 30.0))

    element_generator = BranchingElementsGenerator(
        config.get("r_root", 0.5),
        config.get("h_root", 4.0),
        config.get("r_branch", 0.4),
        config.get("h_branch", 3.0),
        config.get("num_branches", 4),
        angle_rad
    )

    all_elements = element_generator.generate_volume(2, 2, 2)

    gmsh.model.mesh.setSize(gmsh.model.getEntities(0), config.get("mesh_size", 1.0))
    gmsh.model.mesh.generate(3)
    gmsh.write(args.output)

    if not args.no_gui:
        gmsh.fltk.run()

    gmsh.finalize()


if __name__ == "__main__":
    main()
