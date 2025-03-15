import gmsh
import math
import sys
from mesh_generators.branching_elements_generator import BranchingElementsGenerator

gmsh.initialize()
gmsh.model.add("branch_element")

r_root=0.5
h_root=4.0
r_branch=0.4
h_branch=3.0
num_branches=4
angle=math.radians(30)

element_generator = BranchingElementsGenerator(r_root, h_root, r_branch, h_branch, num_branches, angle)

all_elements = element_generator.generate_volume(2, 2, 2)

gmsh.model.mesh.setSize(gmsh.model.getEntities(0), 1)

# Генерация сетки
gmsh.model.mesh.generate(3)

# Сохранение в файл
gmsh.write("branch_element.msh")

# Включение GUI для визуализации (если необходимо)
if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
