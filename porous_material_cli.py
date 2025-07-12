import argparse
import yaml
import gmsh
from pathlib import Path
from mesh_generators.volume_generator import ParamType
from mesh_generators.porous_material_volume_generator import PorousMaterialVolumeGenerator

def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate porous material volume mesh.')

    parser.add_argument('--config', type=str, default="configs/porous.yml", help='Path to YAML config file')
    parser.add_argument('--spheres_count', type=int, help='Number of spheres')
    parser.add_argument('--r', type=float, help='Radius of spheres')
    parser.add_argument('--allowance', type=float, help='Allowance between spheres')
    parser.add_argument("--mesh-size", type=float, help="Размер элементов сетки")
    parser.add_argument('--output', type=str, default='porous.msh', help='Output MSH file')
    parser.add_argument("--no-gui", type=bool, default=False, help="Не запускать GUI визуализации Gmsh")

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
    args = parse_cli_args()
    file_config = load_config(args.config) if args.config else {}
    config = merge_configs(file_config, args)

    gmsh.initialize()
    gmsh.model.add("porous_material")

    min_size = 0.9 * config.get("mesh-size", 1.0)
    max_size = 1.1 * config.get("mesh-size", 1.0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", min_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", max_size)

    gmsh.option.setNumber("Mesh.ElementOrder", 1)
    gmsh.option.setNumber("Mesh.SecondOrderLinear", 0)
    gmsh.option.setNumber("Mesh.HighOrderOptimize", 0)

    generator = PorousMaterialVolumeGenerator.build(config)
    generator.generate_volume()

    gmsh.model.mesh.generate(3)
    filename = config.get("output")
    print(filename)
    gmsh.write(filename)

    if not config.get("no_gui"):
        gmsh.fltk.run()

    gmsh.finalize()


if __name__ == '__main__':
    main()
