import math
import gmsh
from mesh_generators.branching_element_generator import BranchingElementGenerator
from mesh_generators.branching_elements_welder import BranchingElementsWelder

gmsh.initialize()
gmsh.model.add("branch_element")

mesh_size = 1.0
min_size = 0.9 * mesh_size
max_size = 1.1 * mesh_size
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", min_size)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", max_size)

element_generator = BranchingElementGenerator(
    4.0, 6.0,
    h_root=4.0,
    r_root=0.5,
    r_branch=0.4,
    num_branches=4,
)
welder = BranchingElementsWelder()

_, element1 = element_generator.generate_at(0, 0, 0)
_, element2 = element_generator.generate_at(4, 0, 0)

_, res = welder.weld(element1, element2, cutting_plane_at=6.0)
print(res)

gmsh.model.mesh.generate(3)
gmsh.write("branch_element_welding.msh")

gmsh.fltk.run()

gmsh.finalize()
