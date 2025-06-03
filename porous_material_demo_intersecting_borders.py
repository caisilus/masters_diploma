import math
import gmsh
import random
from itertools import product
from mesh_generators.porous_material_volume_generator import PorousMaterialVolumeGenerator

gmsh.initialize()
gmsh.model.add("porous_material")

mesh_size = 0.05
min_size = 0.9 * mesh_size
max_size = 1.1 * mesh_size
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", min_size)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", max_size)

generator = PorousMaterialVolumeGenerator(10, 0.1)
volume = generator.generate_volume()

gmsh.model.mesh.generate(3)
filename = "porous.msh"
gmsh.write(filename)

gmsh.fltk.run()

gmsh.finalize()

