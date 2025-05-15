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

angle_rad = math.radians(30.0)

element_generator = BranchingElementGenerator(
    r_root=0.5,
    h_root=4.0,
    r_branch=0.4,
    h_branch=3.0,
    num_branches=4,
    angle=angle_rad
)
welder = BranchingElementsWelder()

_, element1 = element_generator.generate_at(0, 0, 0)
_, element2 = element_generator.generate_at(4, 0, 0)

_, res = welder.weld(element1, element2)
print(res)

gmsh.model.mesh.generate(3)
gmsh.write("branch_element_welding.msh")

gmsh.fltk.run()

gmsh.finalize()
