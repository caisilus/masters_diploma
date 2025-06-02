import math
import gmsh
from mesh_generators.branching_element_generator import BranchingElementGenerator
from mesh_generators.branching_elements_welder import BranchingElementsWelder

gmsh.initialize()
gmsh.model.add("branch_element")

mesh_size = 0.5
min_size = 0.9 * mesh_size
max_size = 1.1 * mesh_size
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", min_size)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", max_size)

element_generator = BranchingElementGenerator(
    0.25, 0.5,
    h_root=0.2835,
    r_root=0.05,
    r_branch=0.05,
    num_branches=4,
)
welder = BranchingElementsWelder()

_, element1 = element_generator.generate_at(-0.125, 0, 0)
_, element2 = element_generator.generate_at(0.125, 0, 0)

# _, res = welder.weld(element1, element2, cutting_plane_at=0.5133977999757995)
_, res = welder.weld(element1, element2, cutting_plane_at=0.5)
print(res)

gmsh.model.mesh.generate(3)
gmsh.write("branch_element_welding.msh")

gmsh.fltk.run()

gmsh.finalize()
